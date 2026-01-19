# JumpServer Acquisition Registration Tool

Python CLI tool for registering evidence acquisition events with JumpServer, establishing Chain of Custody at the point of acquisition.

## 🎯 Purpose

This tool bridges the gap between **evidence acquisition** and **evidence upload** in forensic investigations:

1. Investigator acquires evidence using **FTK Imager** (or any tool)
2. **Immediately** run this script to register acquisition with JumpServer
3. Script creates blockchain record at **acquisition time**
4. Later, when evidence is uploaded, hash is verified against acquisition record
5. Complete Chain of Custody from acquisition → upload

## 📋 Requirements

- Python 3.7+
- JumpServer running and accessible
- API token from JumpServer

## 🔧 Installation

### Windows (for use with FTK Imager)

```cmd
REM 1. Install Python (if not already installed)
REM Download from https://www.python.org/downloads/

REM 2. Install dependencies
pip install -r requirements.txt

REM 3. Set API token (one-time setup)
setx JUMPSERVER_TOKEN "your-api-token-here"
```

### Linux (CSI Linux, Kali, etc)

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Set API token (add to ~/.bashrc for persistence)
export JUMPSERVER_TOKEN="your-api-token-here"
```

## 🚀 Usage

### Basic Usage

```bash
python register_acquisition.py --file evidence.dd --case CASE-2026-001
```

### With Device Metadata (Recommended)

```bash
python register_acquisition.py \
  --file evidence.dd \
  --case CASE-2026-001 \
  --device-make Samsung \
  --device-model "Galaxy S21" \
  --device-serial IMEI123456789 \
  --storage-id internal_storage_001
```

### With FTK Imager

```cmd
REM 1. Use FTK Imager to acquire evidence normally
REM    Output: E:\cases\CASE-2026-001\evidence.dd

REM 2. Register acquisition immediately after
python register_acquisition.py ^
  --file "E:\cases\CASE-2026-001\evidence.dd" ^
  --case CASE-2026-001 ^
  --tool-name "FTK Imager" ^
  --tool-version "4.7.1.2" ^
  --device-make Samsung ^
  --device-model "Galaxy S21" ^
  --device-serial IMEI123456789 ^
  --notes "Seized from suspect's residence, warrant #2026-001"
```

### With Custom JumpServer URL

```bash
python register_acquisition.py \
  --file evidence.dd \
  --case CASE-2026-001 \
  --url http://jumpserver.example.com:8080 \
  --token your-api-token-here
```

## 📝 Command Line Arguments

### Required

| Argument | Description | Example |
|----------|-------------|---------|
| `--file` | Path to evidence file | `evidence.dd` |
| `--case` | Case number | `CASE-2026-001` |

### Optional

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | JumpServer URL | `http://localhost:8080` |
| `--token` | API token (or use env var) | `$JUMPSERVER_TOKEN` |
| `--device-make` | Device manufacturer | - |
| `--device-model` | Device model | - |
| `--device-serial` | Device serial number | - |
| `--storage-id` | Storage identifier | - |
| `--tool-name` | Acquisition tool name | `Manual Acquisition` |
| `--tool-version` | Tool version | `1.0` |
| `--notes` | Additional notes | - |
| `--output-dir` | Receipt output directory | `.` (current dir) |
| `--timestamp` | Custom timestamp (ISO format) | Current UTC time |

## 📤 Output

The tool generates an **acquisition receipt** JSON file:

```json
{
  "acquisition_event_id": "uuid-here",
  "evidence_hash": "abc123...",
  "blockchain_tx_hash": "0x123...",
  "blockchain_block": 1042,
  "receipt_token": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "acquisition_timestamp": "2026-01-19T18:30:00Z",
  "registered_at": "2026-01-19T18:30:15Z",
  "investigator": "john.doe",
  "case_number": "CASE-2026-001"
}
```

**IMPORTANT:** Keep this receipt file with your evidence!

## 🔄 Complete Workflow

### Step 1: Acquire Evidence (FTK Imager)

```
1. Open FTK Imager
2. Create Disk Image
3. Source: Physical Drive (Samsung Galaxy S21)
4. Destination: E:\cases\CASE-2026-001\evidence.dd
5. Wait for acquisition to complete
6. FTK Imager shows: "Image created successfully"
```

### Step 2: Register Acquisition (This Tool)

```cmd
cd E:\cases\CASE-2026-001

python C:\tools\register_acquisition.py ^
  --file evidence.dd ^
  --case CASE-2026-001 ^
  --tool-name "FTK Imager" ^
  --tool-version "4.7.1.2" ^
  --device-make Samsung ^
  --device-model "Galaxy S21" ^
  --device-serial IMEI123456789 ^
  --output-dir .

REM Output: acquisition_receipt_<uuid>.json
```

### Step 3: Upload Evidence to JumpServer

**Option A: Via Web UI**
1. Login to JumpServer
2. Navigate to Investigation: CASE-2026-001
3. Click "Upload Evidence"
4. Select file: evidence.dd
5. Paste Acquisition Event ID from receipt
6. Submit

**Option B: Via API**

```bash
curl -X POST http://localhost:8080/api/v1/blockchain/evidence/ \
  -H "Authorization: Token your-token" \
  -F "investigation=<investigation-id>" \
  -F "acquisition_event_id=<uuid-from-receipt>" \
  -F "title=Samsung Galaxy S21 Image" \
  -F "file=@evidence.dd"
```

### Step 4: Verify Chain of Custody

```bash
curl http://localhost:8080/api/v1/blockchain/evidence/<evidence-id>/ \
  -H "Authorization: Token your-token"
```

Response shows complete chain:
- **Acquisition event**: When evidence was acquired
- **Upload event**: When evidence was uploaded
- **Hash verification**: Confirms file integrity

## 🔐 Security

### API Token Management

**Generate token in JumpServer:**
1. Login as admin/investigator
2. Go to Profile → API Tokens
3. Create new token
4. Copy and save securely

**Store token securely:**

Windows:
```cmd
setx JUMPSERVER_TOKEN "your-token-here"
```

Linux:
```bash
echo 'export JUMPSERVER_TOKEN="your-token-here"' >> ~/.bashrc
source ~/.bashrc
```

**Never commit tokens to git or share in plaintext!**

## 🛠️ Troubleshooting

### Error: "requests library not found"

```bash
pip install requests
```

### Error: "API token required"

```bash
# Check if token is set
echo $JUMPSERVER_TOKEN  # Linux
echo %JUMPSERVER_TOKEN%  # Windows

# Set token
export JUMPSERVER_TOKEN="your-token"  # Linux
setx JUMPSERVER_TOKEN "your-token"    # Windows (restart terminal)
```

### Error: "Connection refused"

- Check JumpServer is running: `http://localhost:8080`
- Use `--url` to specify correct address
- Check firewall/network connectivity

### Error: "File hash does not match"

- Evidence file was modified after acquisition registration
- **Chain of Custody broken!** Investigate immediately

## 📚 Examples

### Example 1: Simple Acquisition

```bash
python register_acquisition.py \
  --file /mnt/evidence/disk.img \
  --case CASE-2026-042
```

### Example 2: Mobile Device with FTK Imager

```cmd
python register_acquisition.py ^
  --file "D:\cases\phone_image.dd" ^
  --case CASE-2026-055 ^
  --tool-name "FTK Imager" ^
  --tool-version "4.7.1.2" ^
  --device-make Apple ^
  --device-model "iPhone 14 Pro" ^
  --device-serial C02XL4ABCD ^
  --storage-id iphone_internal ^
  --notes "Device seized under warrant W-2026-055, powered on at scene"
```

### Example 3: Network Evidence with dd

```bash
python register_acquisition.py \
  --file /evidence/network_capture.pcap \
  --case CASE-2026-078 \
  --tool-name "tcpdump" \
  --tool-version "4.99.1" \
  --device-make "Cisco" \
  --device-model "Router 2900" \
  --storage-id "eth0_capture" \
  --notes "Network traffic captured during incident response"
```

## 🤝 Integration with Other Tools

### EnCase

```cmd
REM After EnCase acquisition
python register_acquisition.py ^
  --file "C:\cases\evidence.e01" ^
  --case CASE-2026-001 ^
  --tool-name "EnCase" ^
  --tool-version "8.11"
```

### dc3dd

```bash
# Acquire with dc3dd
dc3dd if=/dev/sdb of=/evidence/disk.dd hash=sha256 log=/evidence/acquisition.log

# Register with JumpServer
python register_acquisition.py \
  --file /evidence/disk.dd \
  --case CASE-2026-001 \
  --tool-name "dc3dd" \
  --tool-version "7.2.646"
```

### Guymager

```bash
# After Guymager acquisition
python register_acquisition.py \
  --file /evidence/disk.img \
  --case CASE-2026-001 \
  --tool-name "Guymager" \
  --tool-version "0.8.13"
```

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/your-repo/jump/issues
- Documentation: See main README.md

## 📄 License

See LICENSE file in project root.
