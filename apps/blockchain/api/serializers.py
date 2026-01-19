from rest_framework import serializers
from ..models import Investigation, Evidence, AcquisitionEvent, Tag, InvestigationTag, InvestigationNote, InvestigationActivity, GUIDMapping, BlockchainTransaction
from users.models import User

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']

class AcquisitionEventSerializer(serializers.ModelSerializer):
    """Serializer for evidence acquisition events (registered before upload)"""
    investigator_name = serializers.CharField(source='investigator.username', read_only=True)

    # Nested fields for device metadata
    device_make = serializers.CharField(required=False, allow_blank=True)
    device_model = serializers.CharField(required=False, allow_blank=True)
    device_serial = serializers.CharField(required=False, allow_blank=True)
    storage_id = serializers.CharField(required=False, allow_blank=True)
    device_metadata = serializers.JSONField(required=False, default=dict)

    # Nested fields for tool metadata
    tool_name = serializers.CharField(required=True)
    tool_version = serializers.CharField(required=True)
    tool_verification_hash = serializers.CharField(required=False, allow_blank=True)
    tool_metadata = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = AcquisitionEvent
        fields = [
            'id', 'evidence_hash', 'acquisition_timestamp',
            'device_make', 'device_model', 'device_serial', 'storage_id', 'device_metadata',
            'tool_name', 'tool_version', 'tool_verification_hash', 'tool_metadata',
            'investigator', 'investigator_name', 'case_number', 'notes',
            'blockchain_tx_hash', 'blockchain_block', 'receipt_token',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['investigator', 'blockchain_tx_hash', 'blockchain_block', 'receipt_token', 'status']

    def create(self, validated_data):
        # Set investigator from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['investigator'] = request.user
        return super().create(validated_data)

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
    acquisition_event_details = serializers.SerializerMethodField()

    class Meta:
        model = Evidence
        fields = ['id', 'investigation', 'acquisition_event', 'acquisition_event_details', 'title', 'description', 'file_name', 'file_hash',
                  'file_size', 'ipfs_hash', 'ipfs_uploaded', 'blockchain_tx_hash', 'blockchain_block',
                  'uploaded_by', 'uploaded_by_display', 'uploaded_anonymously', 'anonymous_guid', 'uploaded_at']
        read_only_fields = ['ipfs_hash', 'blockchain_tx_hash', 'blockchain_block', 'uploaded_by']

    def get_acquisition_event_details(self, obj):
        if obj.acquisition_event:
            return {
                'id': str(obj.acquisition_event.id),
                'acquisition_timestamp': obj.acquisition_event.acquisition_timestamp,
                'tool_name': obj.acquisition_event.tool_name,
                'tool_version': obj.acquisition_event.tool_version,
                'device_make': obj.acquisition_event.device_make,
                'device_model': obj.acquisition_event.device_model,
                'blockchain_tx_hash': obj.acquisition_event.blockchain_tx_hash,
            }
        return None
    
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
