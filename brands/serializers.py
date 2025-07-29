"""
Serializers for brands app.
"""
from rest_framework import serializers
from .models import Brand


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model."""
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'daily_budget', 'monthly_budget', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BrandSummarySerializer(serializers.ModelSerializer):
    """Serializer for Brand summary with spend information."""
    daily_spend = serializers.SerializerMethodField()
    monthly_spend = serializers.SerializerMethodField()
    daily_budget_remaining = serializers.SerializerMethodField()
    monthly_budget_remaining = serializers.SerializerMethodField()
    has_daily_budget_available = serializers.SerializerMethodField()
    has_monthly_budget_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'daily_budget', 'monthly_budget', 
            'is_active', 'daily_spend', 'monthly_spend',
            'daily_budget_remaining', 'monthly_budget_remaining',
            'has_daily_budget_available', 'has_monthly_budget_available'
        ]
    
    def get_daily_spend(self, obj: Brand) -> float:
        return float(obj.get_daily_spend())
    
    def get_monthly_spend(self, obj: Brand) -> float:
        return float(obj.get_monthly_spend())
    
    def get_daily_budget_remaining(self, obj: Brand) -> float:
        return float(obj.get_daily_budget_remaining())
    
    def get_monthly_budget_remaining(self, obj: Brand) -> float:
        return float(obj.get_monthly_budget_remaining())
    
    def get_has_daily_budget_available(self, obj: Brand) -> bool:
        return obj.has_daily_budget_available()
    
    def get_has_monthly_budget_available(self, obj: Brand) -> bool:
        return obj.has_monthly_budget_available() 