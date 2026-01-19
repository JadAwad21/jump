#!/bin/bash
set -e

FILE="apps/pki/api/urls.py"

echo "[1] Fixing pki/api/urls.py to use UserCertificateViewSet..."

sed -i "s/CertificateViewSet/UserCertificateViewSet/g" "$FILE"
sed -i "s/from . import certificate/from . import certificate/g" "$FILE"

echo "[DONE] PKI URL routing fixed!"
echo
echo "Now restart backend:"
echo "    cd ~/Desktop/truefypjs/apps"
echo "    python manage.py runserver 0.0.0.0:8080"
