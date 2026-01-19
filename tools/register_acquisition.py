#!/usr/bin/env python3
"""
JumpServer Acquisition Registration Tool

This tool registers evidence acquisition events with JumpServer,
creating a Chain of Custody record at the point of acquisition.

Usage:
    python register_acquisition.py --file evidence.dd --case CASE-2026-001

Requirements:
    - Python 3.7+
    - requests library (pip install requests)
"""

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found.")
    print("Install with: pip install requests")
    sys.exit(1)


class AcquisitionRegistrar:
    """Handles registration of evidence acquisition with JumpServer"""

    def __init__(self, jumpserver_url, api_token):
        self.jumpserver_url = jumpserver_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }

    def calculate_file_hash(self, file_path, algorithm='sha256', block_size=65536):
        """Calculate hash of file"""
        print(f"Calculating {algorithm.upper()} hash of {file_path}...")
        hash_obj = hashlib.new(algorithm)
        file_size = os.path.getsize(file_path)
        bytes_read = 0

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hash_obj.update(data)
                bytes_read += len(data)
                # Show progress
                progress = (bytes_read / file_size) * 100
                print(f"\rProgress: {progress:.1f}%", end='', flush=True)

        print()  # New line after progress
        return hash_obj.hexdigest()

    def collect_device_metadata(self, device_info=None):
        """Collect device metadata (can be overridden with custom data)"""
        if device_info:
            return device_info

        # Default: collect from command line arguments or environment
        return {
            'workstation': platform.node(),
            'os': platform.system(),
            'platform': platform.platform(),
        }

    def collect_tool_metadata(self, tool_name, tool_version):
        """Collect tool metadata"""
        return {
            'name': tool_name,
            'version': tool_version,
            'platform': platform.system(),
        }

    def register_acquisition(self, evidence_hash, acquisition_timestamp, device_info, tool_info, case_number, notes=''):
        """Register acquisition event with JumpServer"""
        endpoint = f"{self.jumpserver_url}/api/v1/blockchain/acquisition-events/"

        payload = {
            'evidence_hash': evidence_hash,
            'acquisition_timestamp': acquisition_timestamp,
            'device_make': device_info.get('make', ''),
            'device_model': device_info.get('model', ''),
            'device_serial': device_info.get('serial', ''),
            'storage_id': device_info.get('storage_id', ''),
            'device_metadata': device_info,
            'tool_name': tool_info.get('name', 'Unknown'),
            'tool_version': tool_info.get('version', 'Unknown'),
            'tool_metadata': tool_info,
            'case_number': case_number,
            'notes': notes,
        }

        print(f"\nRegistering acquisition with JumpServer...")
        print(f"Endpoint: {endpoint}")

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to register acquisition: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            sys.exit(1)

    def save_receipt(self, acquisition_data, output_dir):
        """Save acquisition receipt to file"""
        receipt_file = Path(output_dir) / f"acquisition_receipt_{acquisition_data['id']}.json"

        receipt = {
            'acquisition_event_id': acquisition_data['id'],
            'evidence_hash': acquisition_data['evidence_hash'],
            'blockchain_tx_hash': acquisition_data['blockchain_tx_hash'],
            'blockchain_block': acquisition_data['blockchain_block'],
            'receipt_token': acquisition_data['receipt_token'],
            'acquisition_timestamp': acquisition_data['acquisition_timestamp'],
            'registered_at': acquisition_data['created_at'],
            'investigator': acquisition_data['investigator_name'],
            'case_number': acquisition_data['case_number'],
        }

        with open(receipt_file, 'w') as f:
            json.dump(receipt, f, indent=2)

        print(f"\n✓ Receipt saved to: {receipt_file}")
        return receipt_file


def main():
    parser = argparse.ArgumentParser(
        description='Register evidence acquisition with JumpServer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register acquisition of evidence file
  python register_acquisition.py --file evidence.dd --case CASE-2026-001

  # Register with device metadata
  python register_acquisition.py --file evidence.dd --case CASE-2026-001 \\
    --device-make Samsung --device-model "Galaxy S21" --device-serial IMEI123456

  # Register with custom tool info
  python register_acquisition.py --file evidence.dd --case CASE-2026-001 \\
    --tool-name "FTK Imager" --tool-version "4.7.1.2"

  # Register with notes
  python register_acquisition.py --file evidence.dd --case CASE-2026-001 \\
    --notes "Evidence seized from suspect's residence"
        """
    )

    # Required arguments
    parser.add_argument('--file', required=True, help='Path to evidence file')
    parser.add_argument('--case', required=True, help='Case number')

    # JumpServer connection
    parser.add_argument('--url', default='http://localhost:8080', help='JumpServer URL (default: http://localhost:8080)')
    parser.add_argument('--token', help='API token (or set JUMPSERVER_TOKEN env var)')

    # Device metadata
    parser.add_argument('--device-make', help='Device manufacturer')
    parser.add_argument('--device-model', help='Device model')
    parser.add_argument('--device-serial', help='Device serial number')
    parser.add_argument('--storage-id', help='Storage identifier')

    # Tool metadata
    parser.add_argument('--tool-name', default='Manual Acquisition', help='Acquisition tool name')
    parser.add_argument('--tool-version', default='1.0', help='Tool version')

    # Optional
    parser.add_argument('--notes', default='', help='Additional notes')
    parser.add_argument('--output-dir', default='.', help='Directory to save receipt (default: current directory)')
    parser.add_argument('--timestamp', help='Custom acquisition timestamp (ISO format)')

    args = parser.parse_args()

    # Validate file exists
    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    # Get API token
    api_token = args.token or os.environ.get('JUMPSERVER_TOKEN')
    if not api_token:
        print("ERROR: API token required. Use --token or set JUMPSERVER_TOKEN environment variable")
        sys.exit(1)

    # Initialize registrar
    registrar = AcquisitionRegistrar(args.url, api_token)

    # Calculate file hash
    evidence_hash = registrar.calculate_file_hash(args.file)
    print(f"✓ Evidence hash: {evidence_hash}")

    # Collect device metadata
    device_info = {
        'make': args.device_make or '',
        'model': args.device_model or '',
        'serial': args.device_serial or '',
        'storage_id': args.storage_id or '',
        'workstation': platform.node(),
    }

    # Collect tool metadata
    tool_info = {
        'name': args.tool_name,
        'version': args.tool_version,
        'platform': platform.system(),
    }

    # Get timestamp
    acquisition_timestamp = args.timestamp or datetime.utcnow().isoformat() + 'Z'

    # Register acquisition
    print(f"\n{'='*60}")
    print(f"ACQUISITION REGISTRATION")
    print(f"{'='*60}")
    print(f"File:      {args.file}")
    print(f"Hash:      {evidence_hash}")
    print(f"Case:      {args.case}")
    print(f"Tool:      {args.tool_name} {args.tool_version}")
    print(f"Timestamp: {acquisition_timestamp}")
    if args.device_make:
        print(f"Device:    {args.device_make} {args.device_model}")
    print(f"{'='*60}")

    acquisition_data = registrar.register_acquisition(
        evidence_hash=evidence_hash,
        acquisition_timestamp=acquisition_timestamp,
        device_info=device_info,
        tool_info=tool_info,
        case_number=args.case,
        notes=args.notes
    )

    # Print results
    print(f"\n{'='*60}")
    print(f"✓ ACQUISITION REGISTERED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"Acquisition ID:    {acquisition_data['id']}")
    print(f"Blockchain TX:     {acquisition_data['blockchain_tx_hash']}")
    print(f"Block Number:      {acquisition_data['blockchain_block']}")
    print(f"Status:            {acquisition_data['status']}")
    print(f"{'='*60}")

    # Save receipt
    receipt_file = registrar.save_receipt(acquisition_data, args.output_dir)

    print(f"\n✓ Chain of Custody established at acquisition time!")
    print(f"✓ Keep the receipt file with your evidence: {receipt_file.name}")
    print(f"\nNext steps:")
    print(f"  1. Upload evidence file to JumpServer")
    print(f"  2. Link to acquisition event using ID: {acquisition_data['id']}")
    print(f"  3. Hash will be verified automatically")


if __name__ == '__main__':
    main()
