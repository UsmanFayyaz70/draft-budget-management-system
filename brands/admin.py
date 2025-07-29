"""
Admin configuration for brands app.
"""
from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin interface for Brand model."""
    list_display = [
        'name', 
        'daily_budget', 
        'monthly_budget', 
        'daily_spend_display',
        'monthly_spend_display',
        'daily_remaining_display',
        'monthly_remaining_display',
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
        ('Budget Settings', {
            'fields': ('daily_budget', 'monthly_budget')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def daily_spend_display(self, obj: Brand) -> str:
        """Display daily spend with color coding."""
        spend = obj.get_daily_spend()
        percentage = (spend / obj.daily_budget * 100) if obj.daily_budget > 0 else 0
        color = 'red' if percentage > 90 else 'orange' if percentage > 75 else 'green'
        return format_html(
            '<span style="color: {};">${:.2f} ({:.1f}%)</span>',
            color, spend, percentage
        )
    daily_spend_display.short_description = 'Daily Spend'

    def monthly_spend_display(self, obj: Brand) -> str:
        """Display monthly spend with color coding."""
        spend = obj.get_monthly_spend()
        percentage = (spend / obj.monthly_budget * 100) if obj.monthly_budget > 0 else 0
        color = 'red' if percentage > 90 else 'orange' if percentage > 75 else 'green'
        return format_html(
            '<span style="color: {};">${:.2f} ({:.1f}%)</span>',
            color, spend, percentage
        )
    monthly_spend_display.short_description = 'Monthly Spend'

    def daily_remaining_display(self, obj: Brand) -> str:
        """Display remaining daily budget."""
        remaining = obj.get_daily_budget_remaining()
        color = 'red' if remaining <= 0 else 'green'
        return format_html(
            '<span style="color: {};">${:.2f}</span>',
            color, remaining
        )
    daily_remaining_display.short_description = 'Daily Remaining'

    def monthly_remaining_display(self, obj: Brand) -> str:
        """Display remaining monthly budget."""
        remaining = obj.get_monthly_budget_remaining()
        color = 'red' if remaining <= 0 else 'green'
        return format_html(
            '<span style="color: {};">${:.2f}</span>',
            color, remaining
        )
    monthly_remaining_display.short_description = 'Monthly Remaining'

    def get_queryset(self, request):
        """Optimize queryset with related data."""
        return super().get_queryset(request).select_related() 