from rest_framework import serializers
from ..models import Investigation, Evidence, Tag, InvestigationTag, InvestigationNote, InvestigationActivity, GUIDMapping, BlockchainTransaction
from users.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']

class InvestigationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    tags = TagSerializer(many=True, read_only=True, source='investigationtag_set.tag')
    
    class Meta:
        model = Investigation
        fields = ['id', 'title', 'description', 'status', 'created_by', 'created_by_name', 
                  'created_at', 'updated_at', 'blockchain_tx_hash', 'blockchain_block', 'tags']
        read_only_fields = ['created_by', 'blockchain_tx_hash', 'blockchain_block']

class EvidenceSerializer(serializers.ModelSerializer):
    uploaded_by_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Evidence
        fields = ['id', 'investigation', 'title', 'description', 'file_name', 'file_hash', 
                  'file_size', 'ipfs_hash', 'ipfs_uploaded', 'blockchain_tx_hash', 'blockchain_block',
                  'uploaded_by', 'uploaded_by_display', 'uploaded_anonymously', 'anonymous_guid', 'uploaded_at']
        read_only_fields = ['ipfs_hash', 'blockchain_tx_hash', 'blockchain_block', 'uploaded_by']
    
    def get_uploaded_by_display(self, obj):
        request = self.context.get('request')
        if obj.uploaded_anonymously:
            # Only Court and Admin can see real names
            if request and (request.user.is_superuser or 
                           request.user.role_bindings.filter(role__name='Court').exists()):
                return obj.uploaded_by.username if obj.uploaded_by else f"GUID-{obj.anonymous_guid}"
            return f"Anonymous-{str(obj.anonymous_guid)[:8]}"
        return obj.uploaded_by.username if obj.uploaded_by else "Unknown"

class InvestigationNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = InvestigationNote
        fields = ['id', 'investigation', 'content', 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by']

class GUIDMappingSerializer(serializers.ModelSerializer):
    investigator_name = serializers.CharField(source='investigator.username', read_only=True)
    
    class Meta:
        model = GUIDMapping
        fields = ['id', 'guid', 'investigator', 'investigator_name', 'created_at']
