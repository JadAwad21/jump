#!/bin/bash

FILE="apps/pki/api/urls.py"

echo "[1] Fixing PKI urls.py to point to REAL viewsets..."

cat > $FILE << 'EOF2'
"""
PKI API URLs
"""
from rest_framework.routers import DefaultRouter
from .views import UserCertificateViewSet, CertificateAuthorityViewSet, CertificateRevocationListView

app_name = 'pki'

router = DefaultRouter()
router.register('certificates', UserCertificateViewSet, basename='certificate')
router.register('ca', CertificateAuthorityViewSet, basename='ca')
router.register('crl', CertificateRevocationListView, basename='crl')

urlpatterns = router.urls
EOF2

echo "[DONE] PKI routing repaired. Restart backend."
