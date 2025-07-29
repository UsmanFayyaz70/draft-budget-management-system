"""
Celery tasks for brand operations.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from celery import shared_task
from django.utils import timezone
from .models import Brand
from .services import BrandService


@shared_task
def check_brand_budgets_task() -> Dict[str, Any]:
    """Check all brand budgets and deactivate campaigns if needed."""
    brands_with_issues = BrandService.get_brands_with_budget_issues()
    deactivated_campaigns = []
    
    for brand in brands_with_issues:
        campaigns = BrandService.deactivate_brand_campaigns(brand)
        deactivated_campaigns.extend([{
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'brand_id': brand.id,
            'brand_name': brand.name
        } for campaign in campaigns])
    
    return {
        'timestamp': timezone.now().isoformat(),
        'brands_checked': Brand.objects.filter(is_active=True).count(),
        'brands_with_issues': len(brands_with_issues),
        'campaigns_deactivated': len(deactivated_campaigns),
        'deactivated_campaigns': deactivated_campaigns
    }


@shared_task
def reactivate_brand_campaigns_task() -> Dict[str, Any]:
    """Reactivate campaigns for brands that have budget available."""
    reactivated_campaigns = []
    
    for brand in Brand.objects.filter(is_active=True):
        campaigns = BrandService.reactivate_brand_campaigns(brand)
        reactivated_campaigns.extend([{
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'brand_id': brand.id,
            'brand_name': brand.name
        } for campaign in campaigns])
    
    return {
        'timestamp': timezone.now().isoformat(),
        'brands_checked': Brand.objects.filter(is_active=True).count(),
        'campaigns_reactivated': len(reactivated_campaigns),
        'reactivated_campaigns': reactivated_campaigns
    }


@shared_task
def generate_brand_summary_task() -> Dict[str, Any]:
    """Generate spend summary for all brands."""
    summaries = BrandService.get_all_brands_summary()
    
    total_daily_spend = sum(s['daily_spend'] for s in summaries)
    total_monthly_spend = sum(s['monthly_spend'] for s in summaries)
    total_daily_budget = sum(s['daily_budget'] for s in summaries)
    total_monthly_budget = sum(s['monthly_budget'] for s in summaries)
    
    return {
        'timestamp': timezone.now().isoformat(),
        'total_brands': len(summaries),
        'total_daily_spend': total_daily_spend,
        'total_monthly_spend': total_monthly_spend,
        'total_daily_budget': total_daily_budget,
        'total_monthly_budget': total_monthly_budget,
        'brand_summaries': summaries
    }


@shared_task
def update_brand_budgets_task(
    brand_id: int, 
    daily_budget: Optional[Decimal] = None, 
    monthly_budget: Optional[Decimal] = None
) -> Dict[str, Any]:
    """Update brand budget limits."""
    try:
        brand = Brand.objects.get(id=brand_id)
        updated_brand = BrandService.update_brand_budgets(
            brand, daily_budget, monthly_budget
        )
        
        return {
            'timestamp': timezone.now().isoformat(),
            'brand_id': brand_id,
            'brand_name': updated_brand.name,
            'daily_budget': float(updated_brand.daily_budget),
            'monthly_budget': float(updated_brand.monthly_budget),
            'success': True
        }
    except Brand.DoesNotExist:
        return {
            'timestamp': timezone.now().isoformat(),
            'brand_id': brand_id,
            'success': False,
            'error': 'Brand not found'
        }
    except Exception as e:
        return {
            'timestamp': timezone.now().isoformat(),
            'brand_id': brand_id,
            'success': False,
            'error': str(e)
        } 