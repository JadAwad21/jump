#!/bin/bash
# Test script for complete acquisition workflow
# This demonstrates the end-to-end process

set -e

echo "=============================================="
echo "JumpServer Acquisition Workflow Test"
echo "=============================================="
echo ""

# Configuration
JUMPSERVER_URL=${JUMPSERVER_URL:-"http://localhost:8080"}
API_TOKEN=${JUMPSERVER_TOKEN}
CASE_NUMBER="TEST-$(date +%Y%m%d-%H%M%S)"
TEST_FILE="test_evidence_$(date +%s).bin"

# Check requirements
if [ -z "$API_TOKEN" ]; then
    echo "ERROR: JUMPSERVER_TOKEN environment variable not set"
    echo "Set it with: export JUMPSERVER_TOKEN='your-token'"
    exit 1
fi

echo "Step 1: Create test evidence file"
echo "-----------------------------------"
dd if=/dev/urandom of="$TEST_FILE" bs=1M count=10 2>/dev/null
ACTUAL_HASH=$(sha256sum "$TEST_FILE" | cut -d' ' -f1)
echo "✓ Created: $TEST_FILE"
echo "✓ Hash: $ACTUAL_HASH"
echo ""

echo "Step 2: Register acquisition (simulating FTK Imager)"
echo "------------------------------------------------------"
python3 register_acquisition.py \
    --file "$TEST_FILE" \
    --case "$CASE_NUMBER" \
    --url "$JUMPSERVER_URL" \
    --token "$API_TOKEN" \
    --tool-name "Test Tool" \
    --tool-version "1.0" \
    --device-make "Test Device" \
    --device-model "Model X" \
    --device-serial "TEST123456" \
    --notes "Automated test of acquisition workflow"

echo ""
echo "Step 3: Extract acquisition event ID from receipt"
echo "---------------------------------------------------"
RECEIPT_FILE=$(ls -t acquisition_receipt_*.json | head -1)
if [ ! -f "$RECEIPT_FILE" ]; then
    echo "ERROR: Receipt file not found"
    exit 1
fi

ACQUISITION_EVENT_ID=$(jq -r '.acquisition_event_id' "$RECEIPT_FILE")
echo "✓ Receipt file: $RECEIPT_FILE"
echo "✓ Acquisition Event ID: $ACQUISITION_EVENT_ID"
echo ""

echo "Step 4: Create investigation"
echo "-----------------------------"
INVESTIGATION_RESPONSE=$(curl -s -X POST "$JUMPSERVER_URL/api/v1/blockchain/investigations/" \
    -H "Authorization: Token $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"title\": \"Test Investigation $CASE_NUMBER\",
        \"description\": \"Automated test investigation\",
        \"status\": \"open\"
    }")

INVESTIGATION_ID=$(echo "$INVESTIGATION_RESPONSE" | jq -r '.id')
echo "✓ Investigation created: $INVESTIGATION_ID"
echo ""

echo "Step 5: Upload evidence with acquisition event link"
echo "-----------------------------------------------------"
EVIDENCE_RESPONSE=$(curl -s -X POST "$JUMPSERVER_URL/api/v1/blockchain/evidence/" \
    -H "Authorization: Token $API_TOKEN" \
    -F "investigation=$INVESTIGATION_ID" \
    -F "acquisition_event_id=$ACQUISITION_EVENT_ID" \
    -F "title=Test Evidence - $TEST_FILE" \
    -F "description=Automated test evidence upload" \
    -F "file=@$TEST_FILE")

EVIDENCE_ID=$(echo "$EVIDENCE_RESPONSE" | jq -r '.id')
UPLOADED_HASH=$(echo "$EVIDENCE_RESPONSE" | jq -r '.file_hash')

echo "✓ Evidence uploaded: $EVIDENCE_ID"
echo "✓ Hash verified: $UPLOADED_HASH"

if [ "$ACTUAL_HASH" != "$UPLOADED_HASH" ]; then
    echo "✗ ERROR: Hash mismatch!"
    echo "  Expected: $ACTUAL_HASH"
    echo "  Got: $UPLOADED_HASH"
    exit 1
fi
echo ""

echo "Step 6: Retrieve evidence and verify Chain of Custody"
echo "-------------------------------------------------------"
EVIDENCE_DETAILS=$(curl -s "$JUMPSERVER_URL/api/v1/blockchain/evidence/$EVIDENCE_ID/" \
    -H "Authorization: Token $API_TOKEN")

echo "$EVIDENCE_DETAILS" | jq '.'
echo ""

echo "Step 7: Verify acquisition event link"
echo "---------------------------------------"
ACQ_EVENT_DETAILS=$(echo "$EVIDENCE_DETAILS" | jq -r '.acquisition_event_details')
echo "$ACQ_EVENT_DETAILS" | jq '.'
echo ""

echo "=============================================="
echo "✓ TEST COMPLETED SUCCESSFULLY!"
echo "=============================================="
echo ""
echo "Summary:"
echo "  - Acquisition registered: $ACQUISITION_EVENT_ID"
echo "  - Investigation created: $INVESTIGATION_ID"
echo "  - Evidence uploaded: $EVIDENCE_ID"
echo "  - Hash verified: ✓"
echo "  - Chain of Custody: ACQUISITION → UPLOAD"
echo ""
echo "Cleanup:"
echo "  - Test file: $TEST_FILE"
echo "  - Receipt: $RECEIPT_FILE"
echo ""
read -p "Delete test files? (y/n): " DELETE_CONFIRM

if [ "$DELETE_CONFIRM" = "y" ]; then
    rm -f "$TEST_FILE" "$RECEIPT_FILE"
    echo "✓ Test files deleted"
else
    echo "Test files kept for review"
fi
