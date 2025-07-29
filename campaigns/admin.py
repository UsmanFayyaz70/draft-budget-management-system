"""
Admin configuration for campaigns app.
"""
from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from .models import Campaign, DaypartingSchedule


@admin.register(DaypartingSchedule)
class DaypartingScheduleAdmin(admin.ModelAdmin):
    """Admin interface for DaypartingSchedule model."""
    list_display = [
        'name', 
        'start_hour', 
        'end_hour', 
        'days_display',
        'is_currently_active_display',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Schedule Settings', {
            'fields': ('start_hour', 'end_hour', 'days_of_week')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def days_display(self, obj: DaypartingSchedule) -> str:
        """Display active days."""
        return obj.get_days_display()
    days_display.short_description = 'Active Days'

    def is_currently_active_display(self, obj: DaypartingSchedule) -> str:
        """Display current active status."""
        is_active = obj.is_currently_active()
        color = 'green' if is_active else 'red'
        text = 'Active' if is_active else 'Inactive'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    is_currently_active_display.short_description = 'Currently Active'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for Campaign model."""
    list_display = [
        'name', 
        'brand', 
        'status', 
        'is_active_display',
        'daily_budget_display',
        'monthly_budget_display',
        'daily_spend_display',
        'monthly_spend_display',
        'dayparting_status_display',
        'created_at'
    ]
    list_filter = [
        'status', 
        'is_active', 
        'brand', 
        'dayparting_schedule',
        'created_at'
    ]
    search_fields = ['name', 'brand__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    autocomplete_fields = ['brand', 'dayparting_schedule']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand', 'status', 'is_active')
        }),
        ('Budget Settings', {
            'fields': ('daily_budget', 'monthly_budget'),
            'description': 'Leave blank to use brand-level budgets'
        }),
        ('Dayparting', {
            'fields': ('dayparting_schedule',),
            'description': 'Optional schedule for when campaign can run'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_active_display(self, obj: Campaign) -> str:
        """Display active status with color coding."""
        color = 'green' if obj.is_active else 'red'
        text = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    is_active_display.short_description = 'Active'

    def daily_budget_display(self, obj: Campaign) -> str:
        """Display daily budget."""
        budget = obj.get_daily_budget_limit()
        return f"${budget:.2f}"
    daily_budget_display.short_description = 'Daily Budget'

    def monthly_budget_display(self, obj: Campaign) -> str:
        """Display monthly budget."""
        budget = obj.get_monthly_budget_limit()
        return f"${budget:.2f}"
    monthly_budget_display.short_description = 'Monthly Budget'

    def daily_spend_display(self, obj: Campaign) -> str:
        """Display daily spend with color coding."""
        spend = obj.get_daily_spend()
        budget = obj.get_daily_budget_limit()
        percentage = (spend / budget * 100) if budget > 0 else 0
        color = 'red' if percentage > 90 else 'orange' if percentage > 75 else 'green'
        return format_html(
            '<span style="color: {};">${:.2f} ({:.1f}%)</span>',
            color, spend, percentage
        )
    daily_spend_display.short_description = 'Daily Spend'

    def monthly_spend_display(self, obj: Campaign) -> str:
        """Display monthly spend with color coding."""
        spend = obj.get_monthly_spend()
        budget = obj.get_monthly_budget_limit()
        percentage = (spend / budget * 100) if budget > 0 else 0
        color = 'red' if percentage > 90 else 'orange' if percentage > 75 else 'green'
        return format_html(
            '<span style="color: {};">${:.2f} ({:.1f}%)</span>',
            color, spend, percentage
        )
    monthly_spend_display.short_description = 'Monthly Spend'

    def dayparting_status_display(self, obj: Campaign) -> str:
        """Display dayparting status."""
        if not obj.dayparting_schedule:
            return format_html('<span style="color: gray;">No Schedule</span>')
        
        is_within_schedule = obj.is_within_dayparting_schedule()
        color = 'green' if is_within_schedule else 'red'
        text = 'Within Schedule' if is_within_schedule else 'Outside Schedule'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    dayparting_status_display.short_description = 'Dayparting Status'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related('brand', 'dayparting_schedule') 