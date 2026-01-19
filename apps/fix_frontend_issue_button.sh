#!/bin/bash

FILE="frontend/src/components/admin/CertificateManagement.jsx"

echo "[1] Adding onClick handler to Issue Certificate button..."

# Replace the button with API-connected version
sed -i 's|<Button>Issue Certificate</Button>|<Button onClick={handleIssueCert}>Issue Certificate</Button>|' "$FILE"

# Add handleIssueCert function if missing
grep -q "handleIssueCert" "$FILE" || sed -i '/export default function/i \
\
const handleIssueCert = async () => {\
  try {\
    const r = await apiClient.post("/pki/certificates/issue/");\
    alert("Certificate issued successfully!");\
  } catch (err) {\
    alert("Error issuing certificate: " + (err.response?.data?.error || err.message));\
  }\
};\
' "$FILE"

echo "[DONE] Frontend Issue button connected."
