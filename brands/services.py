"""
Brand services for budget management and business logic.
"""
from decimal import Decimal
from typing import List, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from .models import Brand
from campaigns.models import Campaign


class BrandService:
    """Service class for brand-related operations."""

    @staticmethod
    def create_brand(
        name: str, 
        daily_budget: Decimal, 
        monthly_budget: Decimal
    ) -> Brand:
        """Create a new brand with budget limits."""
        return Brand.objects.create(
            name=name,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget
        )

    @staticmethod
    def update_brand_budgets(
        brand: Brand, 
        daily_budget: Optional[Decimal] = None, 
        monthly_budget: Optional[Decimal] = None
    ) -> Brand:
        """Update brand budget limits."""
        if daily_budget is not None:
            brand.daily_budget = daily_budget
        if monthly_budget is not None:
            brand.monthly_budget = monthly_budget
        brand.save()
        return brand

    @staticmethod
    def check_brand_budget_status(brand: Brand) -> Tuple[bool, bool]:
        """Check if brand has daily and monthly budget available."""
        has_daily = brand.has_daily_budget_available()
        has_monthly = brand.has_monthly_budget_available()
        return has_daily, has_monthly

    @staticmethod
    def get_brands_with_budget_issues() -> List[Brand]:
        """Get brands that have exceeded their budgets."""
        brands_with_issues = []
        for brand in Brand.objects.filter(is_active=True):
            if not brand.has_daily_budget_available() or not brand.has_monthly_budget_available():
                brands_with_issues.append(brand)
        return brands_with_issues

    @staticmethod
    def reactivate_brand_campaigns(brand: Brand) -> List[Campaign]:
        """Reactivate campaigns for a brand if budget allows."""
        if not brand.can_activate_campaigns():
            return []

        reactivated_campaigns = []
        for campaign in brand.campaigns.filter(is_active=False):
            if campaign.can_be_activated():
                campaign.is_active = True
                campaign.save()
                reactivated_campaigns.append(campaign)

        return reactivated_campaigns

    @staticmethod
    def deactivate_brand_campaigns(brand: Brand) -> List[Campaign]:
        """Deactivate all campaigns for a brand."""
        campaigns_to_deactivate = list(brand.campaigns.filter(is_active=True))
        
        with transaction.atomic():
            for campaign in campaigns_to_deactivate:
                campaign.is_active = False
                campaign.save()

        return campaigns_to_deactivate

    @staticmethod
    def get_brand_spend_summary(brand: Brand) -> dict:
        """Get comprehensive spend summary for a brand."""
        daily_spend = brand.get_daily_spend()
        monthly_spend = brand.get_monthly_spend()
        daily_remaining = brand.get_daily_budget_remaining()
        monthly_remaining = brand.get_monthly_budget_remaining()

        return {
            'brand_id': brand.id,
            'brand_name': brand.name,
            'daily_budget': float(brand.daily_budget),
            'monthly_budget': float(brand.monthly_budget),
            'daily_spend': float(daily_spend),
            'monthly_spend': float(monthly_spend),
            'daily_remaining': float(daily_remaining),
            'monthly_remaining': float(monthly_remaining),
            'daily_percentage': float((daily_spend / brand.daily_budget * 100) if brand.daily_budget > 0 else 0),
            'monthly_percentage': float((monthly_spend / brand.monthly_budget * 100) if brand.monthly_budget > 0 else 0),
            'has_daily_budget': brand.has_daily_budget_available(),
            'has_monthly_budget': brand.has_monthly_budget_available(),
            'active_campaigns_count': brand.campaigns.filter(is_active=True).count(),
            'total_campaigns_count': brand.campaigns.count(),
        }

    @staticmethod
    def get_all_brands_summary() -> List[dict]:
        """Get spend summary for all brands."""
        summaries = []
        for brand in Brand.objects.filter(is_active=True):
            summaries.append(BrandService.get_brand_spend_summary(brand))
        return summaries 