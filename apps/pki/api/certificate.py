from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.management import call_command
from pki.models import Certificate
from pki.api.serializers import UserCertificateSerializer
from users.models import User
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from cryptography import x509
import io

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = UserCertificateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Certificate.objects.all() if user.is_superuser else Certificate.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def issue(self, request):
        target_user = request.user
        if request.user.is_superuser and 'username' in request.data:
            try:
                target_user = User.objects.get(username=request.data['username'])
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
        
        if Certificate.objects.filter(user=target_user, revoked=False).exists():
            return Response({'error': f'{target_user.username} already has certificate'}, status=400)
        
        try:
            call_command('issue_user_cert', '--username', target_user.username, stdout=io.StringIO())
            new_cert = Certificate.objects.filter(user=target_user).order_by('-created_at').first()
            return Response({'success': True, 'certificate': self.get_serializer(new_cert).data}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        cert = self.get_object()
        if not request.user.is_superuser and cert.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        
        try:
            certificate = x509.load_pem_x509_certificate(cert.certificate.encode(), default_backend())
            private_key = serialization.load_pem_private_key(cert.private_key.encode(), password=None, backend=default_backend())
            ca_cert = x509.load_pem_x509_certificate(cert.ca.certificate.encode(), default_backend())
            
            p12_data = pkcs12.serialize_key_and_certificates(
                name=f"{cert.user.username}@jumpserver".encode(),
                key=private_key,
                cert=certificate,
                cas=[ca_cert],
                encryption_algorithm=serialization.NoEncryption()
            )
            
            response = HttpResponse(p12_data, content_type='application/x-pkcs12')
            response['Content-Disposition'] = f'attachment; filename="{cert.user.username}.p12"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=500)
