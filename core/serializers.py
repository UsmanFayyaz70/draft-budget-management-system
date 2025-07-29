"""
Serializers for core app.
"""
from rest_framework import serializers
from .models import Spend
from campaigns.serializers import CampaignSerializer


class SpendSerializer(serializers.ModelSerializer):
    """Serializer for Spend model."""
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = Spend
        fields = [
            'id', 'campaign', 'amount', 'date', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SpendCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Spend model."""
    
    class Meta:
        model = Spend
        fields = ['campaign', 'amount', 'date', 'description'] 