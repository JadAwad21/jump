import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Investigation(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('archived', 'Archived'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investigations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    blockchain_block = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'blockchain_investigation'
        ordering = ['-created_at']

class AcquisitionEvent(models.Model):
    """Records evidence acquisition at the point of capture (before upload)"""
    STATUS_CHOICES = [
        ('recorded', 'Recorded'),
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evidence_hash = models.CharField(max_length=64, unique=True, db_index=True)
    acquisition_timestamp = models.DateTimeField()

    # Source device metadata
    device_make = models.CharField(max_length=100, blank=True)
    device_model = models.CharField(max_length=100, blank=True)
    device_serial = models.CharField(max_length=255, blank=True)
    storage_id = models.CharField(max_length=255, blank=True)
    device_metadata = models.JSONField(default=dict, blank=True)

    # Acquisition tool information
    tool_name = models.CharField(max_length=100)
    tool_version = models.CharField(max_length=50)
    tool_verification_hash = models.CharField(max_length=64, blank=True)
    tool_metadata = models.JSONField(default=dict, blank=True)

    # Investigator and case info
    investigator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acquisitions')
    case_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Blockchain record
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    blockchain_block = models.IntegerField(blank=True, null=True)

    # Receipt token for verification
    receipt_token = models.TextField(blank=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recorded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blockchain_acquisition_event'
        ordering = ['-acquisition_timestamp']
        indexes = [
            models.Index(fields=['evidence_hash']),
            models.Index(fields=['case_number']),
            models.Index(fields=['acquisition_timestamp']),
        ]

    def __str__(self):
        return f"Acquisition {self.id} - {self.tool_name} - {self.acquisition_timestamp}"

class Evidence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name='evidence')
    acquisition_event = models.ForeignKey(AcquisitionEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name='evidence')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64)
    file_size = models.BigIntegerField()
    ipfs_hash = models.CharField(max_length=100, blank=True, null=True)
    ipfs_uploaded = models.BooleanField(default=False)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    blockchain_block = models.IntegerField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evidence_uploaded')
    uploaded_anonymously = models.BooleanField(default=False)
    anonymous_guid = models.UUIDField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blockchain_evidence'
        ordering = ['-uploaded_at']

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blockchain_tag'

class InvestigationTag(models.Model):
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'blockchain_investigation_tag'
        unique_together = ('investigation', 'tag')

class InvestigationNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blockchain_investigation_note'
        ordering = ['-created_at']

class InvestigationActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blockchain_investigation_activity'
        ordering = ['-created_at']

class GUIDMapping(models.Model):
    """Maps anonymous GUID to actual investigator for Court/Admin access"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guid = models.UUIDField(unique=True, db_index=True)
    investigator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guid_mappings', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blockchain_guid_mapping'

class BlockchainTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tx_hash = models.CharField(max_length=66, unique=True)
    block_number = models.IntegerField()
    tx_type = models.CharField(max_length=50)
    data = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blockchain_transactions')
    user_guid = models.UUIDField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blockchain_transaction'
        ordering = ['-timestamp']

# Update GUIDMapping in the file above - find and change:
# investigator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guid_mappings', null=True, blank=True)
# TO:
# investigator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guid_mappings', null=True, blank=True)
