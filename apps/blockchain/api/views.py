import hashlib
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Investigation, Evidence, Tag, InvestigationTag, InvestigationNote, GUIDMapping, BlockchainTransaction
from .serializers import InvestigationSerializer, EvidenceSerializer, TagSerializer, InvestigationNoteSerializer, GUIDMappingSerializer

def mock_upload_to_ipfs(file_content):
    """Mock IPFS upload - returns fake CID"""
    fake_hash = hashlib.sha256(file_content).hexdigest()
    return f"Qm{fake_hash[:44]}"

def mock_blockchain_transaction(tx_type, data, user):
    """Mock blockchain transaction"""
    tx_hash = f"0x{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()}"
    block_number = BlockchainTransaction.objects.count() + 1000
    
    BlockchainTransaction.objects.create(
        tx_hash=tx_hash,
        block_number=block_number,
        tx_type=tx_type,
        data=data,
        user=user
    )
    return tx_hash, block_number

class InvestigationViewSet(viewsets.ModelViewSet):
    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role_bindings.filter(role__name__in=['Auditor', 'Court']).exists() or user.is_superuser:
            return Investigation.objects.all()
        return Investigation.objects.filter(created_by=user)
    
    def perform_create(self, serializer):
        investigation = serializer.save(created_by=self.request.user)
        
        tx_hash, block = mock_blockchain_transaction(
            'investigation_create',
            {'investigation_id': str(investigation.id), 'title': investigation.title},
            self.request.user
        )
        investigation.blockchain_tx_hash = tx_hash
        investigation.blockchain_block = block
        investigation.save()
        
        tag_ids = self.request.data.get('tag_ids', [])
        for tag_id in tag_ids:
            InvestigationTag.objects.create(investigation=investigation, tag_id=tag_id)

class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = Evidence.objects.all()
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role_bindings.filter(role__name__in=['Auditor', 'Court']).exists() or user.is_superuser:
            return Evidence.objects.all()
        return Evidence.objects.filter(investigation__created_by=user)
    
    def create(self, request, *args, **kwargs):
        # Get form data
        investigation_id = request.data.get('investigation')
        title = request.data.get('title')
        description = request.data.get('description', '')
        uploaded_anonymously = request.data.get('uploaded_anonymously', 'false').lower() == 'true'
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not investigation_id or not title:
            return Response({'error': 'investigation and title are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Read and process file
        file_content = file_obj.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        ipfs_hash = mock_upload_to_ipfs(file_content)
        
        # Create evidence
        evidence = Evidence.objects.create(
            investigation_id=investigation_id,
            title=title,
            description=description,
            file_name=file_obj.name,
            file_hash=file_hash,
            file_size=file_obj.size,
            ipfs_hash=ipfs_hash,
            ipfs_uploaded=True,
            uploaded_by=request.user,
            uploaded_anonymously=uploaded_anonymously,
            anonymous_guid=uuid.uuid4() if uploaded_anonymously else None
        )
        
        # Create GUID mapping if anonymous
        if uploaded_anonymously:
            GUIDMapping.objects.create(guid=evidence.anonymous_guid, investigator=request.user)
        
        # Mock blockchain
        tx_hash, block = mock_blockchain_transaction(
            'evidence_upload',
            {
                'evidence_id': str(evidence.id),
                'file_hash': file_hash,
                'ipfs_hash': ipfs_hash,
                'anonymous': uploaded_anonymously
            },
            request.user
        )
        evidence.blockchain_tx_hash = tx_hash
        evidence.blockchain_block = block
        evidence.save()
        
        serializer = self.get_serializer(evidence)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class GUIDResolverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GUIDMapping.objects.all()
    serializer_class = GUIDMappingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role_bindings.filter(role__name='Court').exists() or user.is_superuser:
            return GUIDMapping.objects.all()
        return GUIDMapping.objects.none()
    
    @action(detail=False, methods=['get'])
    def resolve(self, request):
        guid = request.query_params.get('guid')
        if not guid:
            return Response({'error': 'GUID required'}, status=400)
        
        try:
            mapping = GUIDMapping.objects.get(guid=guid)
            return Response({
                'guid': str(mapping.guid),
                'investigator': mapping.investigator.username,
                'investigator_name': mapping.investigator.name
            })
        except GUIDMapping.DoesNotExist:
            return Response({'error': 'GUID not found'}, status=404)
