#!/bin/bash
set -e

FILE="src/components/admin/CertificateManagement.jsx"

echo "[1] Adding handleIssueCert function..."

sed -i '/export default function CertificateManagement()/a \
  const handleIssueCert = async () => {\
    try {\
      const r = await apiClient.post("/pki/certificates/issue/", {});\
      alert("Certificate issued successfully!");\
      window.location.reload();\
    } catch (err) {\
      alert(err.response?.data?.error || "Failed to issue certificate");\
    }\
  };\
' "$FILE"

echo "[2] Adding onClick to Issue Certificate button..."
sed -i 's|<Button>Issue Certificate|<Button onClick={handleIssueCert}>Issue Certificate|' "$FILE"

echo "[3] Adding onClick to Issue First Certificate button..."
sed -i 's|<Button className="mt-4">Issue First Certificate|<Button className="mt-4" onClick={handleIssueCert}>Issue First Certificate|' "$FILE"

echo "[DONE] Patch applied successfully!"
