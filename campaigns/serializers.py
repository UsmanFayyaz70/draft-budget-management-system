"""
Serializers for campaigns app.
"""
from rest_framework import serializers
from .models import Campaign, DaypartingSchedule
from brands.serializers import BrandSerializer


class DaypartingScheduleSerializer(serializers.ModelSerializer):
    """Serializer for DaypartingSchedule model."""
    active_hours = serializers.SerializerMethodField()
    days_display = serializers.SerializerMethodField()
    is_currently_active = serializers.SerializerMethodField()
    
    class Meta:
        model = DaypartingSchedule
        fields = [
            'id', 'name', 'start_hour', 'end_hour', 'days_of_week',
            'is_active', 'active_hours', 'days_display', 'is_currently_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_hours(self, obj: DaypartingSchedule) -> list:
        return list(obj.get_active_hours())
    
    def get_days_display(self, obj: DaypartingSchedule) -> str:
        return obj.get_days_display()
    
    def get_is_currently_active(self, obj: DaypartingSchedule) -> bool:
        return obj.is_currently_active()


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model."""
    brand = BrandSerializer(read_only=True)
    dayparting_schedule = DaypartingScheduleSerializer(read_only=True)
    daily_spend = serializers.SerializerMethodField()
    monthly_spend = serializers.SerializerMethodField()
    daily_budget_remaining = serializers.SerializerMethodField()
    monthly_budget_remaining = serializers.SerializerMethodField()
    has_daily_budget_available = serializers.SerializerMethodField()
    has_monthly_budget_available = serializers.SerializerMethodField()
    is_within_dayparting_schedule = serializers.SerializerMethodField()
    can_be_activated = serializers.SerializerMethodField()
    should_be_paused = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'brand', 'status', 'is_active', 'dayparting_schedule',
            'daily_budget', 'monthly_budget', 'daily_spend', 'monthly_spend',
            'daily_budget_remaining', 'monthly_budget_remaining',
            'has_daily_budget_available', 'has_monthly_budget_available',
            'is_within_dayparting_schedule', 'can_be_activated', 'should_be_paused',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_daily_spend(self, obj: Campaign) -> float:
        return float(obj.get_daily_spend())
    
    def get_monthly_spend(self, obj: Campaign) -> float:
        return float(obj.get_monthly_spend())
    
    def get_daily_budget_remaining(self, obj: Campaign) -> float:
        return float(obj.get_daily_budget_remaining())
    
    def get_monthly_budget_remaining(self, obj: Campaign) -> float:
        return float(obj.get_monthly_budget_remaining())
    
    def get_has_daily_budget_available(self, obj: Campaign) -> bool:
        return obj.has_daily_budget_available()
    
    def get_has_monthly_budget_available(self, obj: Campaign) -> bool:
        return obj.has_monthly_budget_available()
    
    def get_is_within_dayparting_schedule(self, obj: Campaign) -> bool:
        return obj.is_within_dayparting_schedule()
    
    def get_can_be_activated(self, obj: Campaign) -> bool:
        return obj.can_be_activated()
    
    def get_should_be_paused(self, obj: Campaign) -> bool:
        return obj.should_be_paused()


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Campaign model."""
    
    class Meta:
        model = Campaign
        fields = [
            'name', 'brand', 'status', 'is_active', 'dayparting_schedule',
            'daily_budget', 'monthly_budget'
        ] 