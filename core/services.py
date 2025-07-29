"""
Core services for spend management and budget operations.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from .models import Spend
from campaigns.models import Campaign
from brands.models import Brand


class SpendService:
    """Service class for spend-related operations."""

    @staticmethod
    def create_spend(
        campaign_id: int,
        amount: Decimal,
        date: Optional[date] = None,
        description: str = ""
    ) -> Spend:
        """Create a new spend record."""
        campaign = Campaign.objects.get(id=campaign_id)
        if date is None:
            date = timezone.now().date()
        
        return Spend.objects.create(
            campaign=campaign,
            amount=amount,
            date=date,
            description=description
        )

    @staticmethod
    def get_campaign_spend_summary(campaign: Campaign) -> Dict[str, Any]:
        """Get comprehensive spend summary for a campaign."""
        daily_spend = campaign.get_daily_spend()
        monthly_spend = campaign.get_monthly_spend()
        
        return {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'brand_name': campaign.brand.name,
            'daily_spend': float(daily_spend),
            'monthly_spend': float(monthly_spend),
            'daily_budget_limit': float(campaign.get_daily_budget_limit()),
            'monthly_budget_limit': float(campaign.get_monthly_budget_limit()),
            'daily_remaining': float(campaign.get_daily_budget_remaining()),
            'monthly_remaining': float(campaign.get_monthly_budget_remaining()),
            'daily_percentage': float((daily_spend / campaign.get_daily_budget_limit() * 100) if campaign.get_daily_budget_limit() > 0 else 0),
            'monthly_percentage': float((monthly_spend / campaign.get_monthly_budget_limit() * 100) if campaign.get_monthly_budget_limit() > 0 else 0),
        }

    @staticmethod
    def get_brand_spend_summary(brand: Brand) -> Dict[str, Any]:
        """Get comprehensive spend summary for a brand."""
        daily_spend = brand.get_daily_spend()
        monthly_spend = brand.get_monthly_spend()
        
        return {
            'brand_id': brand.id,
            'brand_name': brand.name,
            'daily_spend': float(daily_spend),
            'monthly_spend': float(monthly_spend),
            'daily_budget': float(brand.daily_budget),
            'monthly_budget': float(brand.monthly_budget),
            'daily_remaining': float(brand.get_daily_budget_remaining()),
            'monthly_remaining': float(brand.get_monthly_budget_remaining()),
            'daily_percentage': float((daily_spend / brand.daily_budget * 100) if brand.daily_budget > 0 else 0),
            'monthly_percentage': float((monthly_spend / brand.monthly_budget * 100) if brand.monthly_budget > 0 else 0),
        }

    @staticmethod
    def get_total_spend_summary() -> Dict[str, Any]:
        """Get total spend summary across all campaigns."""
        today = timezone.now().date()
        now = timezone.now()
        
        total_daily_spend = Spend.objects.filter(
            date=today
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        total_monthly_spend = Spend.objects.filter(
            date__year=now.year,
            date__month=now.month
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        return {
            'date': today.isoformat(),
            'total_daily_spend': float(total_daily_spend),
            'total_monthly_spend': float(total_monthly_spend),
            'total_campaigns': Campaign.objects.count(),
            'active_campaigns': Campaign.objects.filter(is_active=True).count(),
            'total_brands': Brand.objects.filter(is_active=True).count(),
        }

    @staticmethod
    def get_spend_by_date_range(
        start_date: date,
        end_date: date,
        campaign_id: Optional[int] = None,
        brand_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get spend records within a date range."""
        queryset = Spend.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('campaign', 'campaign__brand')
        
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        if brand_id:
            queryset = queryset.filter(campaign__brand_id=brand_id)
        
        spends = []
        for spend in queryset:
            spends.append({
                'id': spend.id,
                'campaign_id': spend.campaign.id,
                'campaign_name': spend.campaign.name,
                'brand_id': spend.campaign.brand.id,
                'brand_name': spend.campaign.brand.name,
                'amount': float(spend.amount),
                'date': spend.date.isoformat(),
                'description': spend.description,
                'created_at': spend.created_at.isoformat(),
            })
        
        return spends


class BudgetResetService:
    """Service class for budget reset operations."""

    @staticmethod
    def reset_daily_budgets() -> Dict[str, Any]:
        """Reset daily budgets and reactivate eligible campaigns."""
        reactivated_campaigns = []
        brands_checked = 0
        
        for brand in Brand.objects.filter(is_active=True):
            brands_checked += 1
            campaigns = brand.get_active_campaigns()
            
            for campaign in campaigns:
                if campaign.can_be_activated():
                    campaign.is_active = True
                    campaign.save()
                    reactivated_campaigns.append({
                        'campaign_id': campaign.id,
                        'campaign_name': campaign.name,
                        'brand_name': brand.name
                    })
        
        return {
            'timestamp': timezone.now().isoformat(),
            'brands_checked': brands_checked,
            'campaigns_reactivated': len(reactivated_campaigns),
            'reactivated_campaigns': reactivated_campaigns
        }

    @staticmethod
    def reset_monthly_budgets() -> Dict[str, Any]:
        """Reset monthly budgets and reactivate eligible campaigns."""
        reactivated_campaigns = []
        brands_checked = 0
        
        for brand in Brand.objects.filter(is_active=True):
            brands_checked += 1
            campaigns = brand.get_active_campaigns()
            
            for campaign in campaigns:
                if campaign.can_be_activated():
                    campaign.is_active = True
                    campaign.save()
                    reactivated_campaigns.append({
                        'campaign_id': campaign.id,
                        'campaign_name': campaign.name,
                        'brand_name': brand.name
                    })
        
        return {
            'timestamp': timezone.now().isoformat(),
            'brands_checked': brands_checked,
            'campaigns_reactivated': len(reactivated_campaigns),
            'reactivated_campaigns': reactivated_campaigns
        }

    @staticmethod
    def cleanup_old_spend_records(days_to_keep: int = 90) -> Dict[str, Any]:
        """Clean up old spend records to maintain database performance."""
        cutoff_date = timezone.now().date() - timedelta(days=days_to_keep)
        deleted_count = Spend.objects.filter(date__lt=cutoff_date).count()
        
        with transaction.atomic():
            Spend.objects.filter(date__lt=cutoff_date).delete()
        
        return {
            'timestamp': timezone.now().isoformat(),
            'cutoff_date': cutoff_date.isoformat(),
            'records_deleted': deleted_count
        } 