"""
Celery tasks for core operations including spend updates and budget resets.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta
from .models import Spend
from .services import SpendService, BudgetResetService
from campaigns.models import Campaign
from brands.models import Brand


@shared_task
def update_spend_task() -> Dict[str, Any]:
    """Update spend for all active campaigns (simulated)."""
    # In a real system, this would integrate with actual ad platforms
    # For now, we'll simulate spend updates
    updated_campaigns = []
    total_spend = Decimal('0.00')
    
    for campaign in Campaign.objects.filter(is_active=True):
        # Simulate random spend between $1 and $10
        import random
        spend_amount = Decimal(str(random.uniform(1.0, 10.0))).quantize(Decimal('0.01'))
        
        try:
            spend = SpendService.create_spend(
                campaign_id=campaign.id,
                amount=spend_amount,
                description="Simulated spend update"
            )
            
            updated_campaigns.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'brand_name': campaign.brand.name,
                'amount': float(spend_amount),
                'spend_id': spend.id
            })
            
            total_spend += spend_amount
            
        except Exception as e:
            # Log error but continue with other campaigns
            continue
    
    return {
        'timestamp': timezone.now().isoformat(),
        'campaigns_updated': len(updated_campaigns),
        'total_spend': float(total_spend),
        'updated_campaigns': updated_campaigns
    }


@shared_task
def reset_daily_budgets_task() -> Dict[str, Any]:
    """Reset daily budgets and reactivate eligible campaigns."""
    return BudgetResetService.reset_daily_budgets()


@shared_task
def reset_monthly_budgets_task() -> Dict[str, Any]:
    """Reset monthly budgets and reactivate eligible campaigns."""
    return BudgetResetService.reset_monthly_budgets()


@shared_task
def cleanup_old_spend_records_task(days_to_keep: int = 90) -> Dict[str, Any]:
    """Clean up old spend records to maintain database performance."""
    return BudgetResetService.cleanup_old_spend_records(days_to_keep)


@shared_task
def generate_spend_report_task(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    campaign_id: Optional[int] = None,
    brand_id: Optional[int] = None
) -> Dict[str, Any]:
    """Generate comprehensive spend report."""
    if start_date is None:
        start_date = (timezone.now().date() - timedelta(days=30)).isoformat()
    if end_date is None:
        end_date = timezone.now().date().isoformat()
    
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    
    spends = SpendService.get_spend_by_date_range(
        start_date=start,
        end_date=end,
        campaign_id=campaign_id,
        brand_id=brand_id
    )
    
    total_amount = sum(spend['amount'] for spend in spends)
    
    return {
        'timestamp': timezone.now().isoformat(),
        'start_date': start_date,
        'end_date': end_date,
        'campaign_id': campaign_id,
        'brand_id': brand_id,
        'total_records': len(spends),
        'total_amount': total_amount,
        'spends': spends
    }


@shared_task
def update_campaign_spend_task(
    campaign_id: int,
    amount: Decimal,
    description: str = ""
) -> Dict[str, Any]:
    """Update spend for a specific campaign."""
    try:
        spend = SpendService.create_spend(
            campaign_id=campaign_id,
            amount=amount,
            description=description
        )
        
        # Check if campaign should be paused after spend update
        campaign = Campaign.objects.get(id=campaign_id)
        should_pause = campaign.should_be_paused()
        
        if should_pause and campaign.is_active:
            campaign.is_active = False
            campaign.save()
        
        return {
            'timestamp': timezone.now().isoformat(),
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'amount': float(amount),
            'spend_id': spend.id,
            'should_pause': should_pause,
            'was_paused': should_pause and campaign.is_active,
            'success': True
        }
    except Campaign.DoesNotExist:
        return {
            'timestamp': timezone.now().isoformat(),
            'campaign_id': campaign_id,
            'success': False,
            'error': 'Campaign not found'
        }
    except Exception as e:
        return {
            'timestamp': timezone.now().isoformat(),
            'campaign_id': campaign_id,
            'success': False,
            'error': str(e)
        }


@shared_task
def generate_total_summary_task() -> Dict[str, Any]:
    """Generate total spend summary across all campaigns."""
    return SpendService.get_total_spend_summary()


@shared_task
def check_budget_limits_task() -> Dict[str, Any]:
    """Check all budget limits and generate alerts."""
    alerts = []
    
    # Check brand budgets
    for brand in Brand.objects.filter(is_active=True):
        daily_percentage = (brand.get_daily_spend() / brand.daily_budget * 100) if brand.daily_budget > 0 else 0
        monthly_percentage = (brand.get_monthly_spend() / brand.monthly_budget * 100) if brand.monthly_budget > 0 else 0
        
        if daily_percentage >= 90:
            alerts.append({
                'type': 'brand_daily_budget',
                'brand_id': brand.id,
                'brand_name': brand.name,
                'percentage': daily_percentage,
                'severity': 'high' if daily_percentage >= 100 else 'medium'
            })
        
        if monthly_percentage >= 90:
            alerts.append({
                'type': 'brand_monthly_budget',
                'brand_id': brand.id,
                'brand_name': brand.name,
                'percentage': monthly_percentage,
                'severity': 'high' if monthly_percentage >= 100 else 'medium'
            })
    
    # Check campaign budgets
    for campaign in Campaign.objects.filter(is_active=True):
        daily_percentage = (campaign.get_daily_spend() / campaign.get_daily_budget_limit() * 100) if campaign.get_daily_budget_limit() > 0 else 0
        monthly_percentage = (campaign.get_monthly_spend() / campaign.get_monthly_budget_limit() * 100) if campaign.get_monthly_budget_limit() > 0 else 0
        
        if daily_percentage >= 90:
            alerts.append({
                'type': 'campaign_daily_budget',
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'brand_name': campaign.brand.name,
                'percentage': daily_percentage,
                'severity': 'high' if daily_percentage >= 100 else 'medium'
            })
        
        if monthly_percentage >= 90:
            alerts.append({
                'type': 'campaign_monthly_budget',
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'brand_name': campaign.brand.name,
                'percentage': monthly_percentage,
                'severity': 'high' if monthly_percentage >= 100 else 'medium'
            })
    
    return {
        'timestamp': timezone.now().isoformat(),
        'total_alerts': len(alerts),
        'high_severity_alerts': len([a for a in alerts if a['severity'] == 'high']),
        'medium_severity_alerts': len([a for a in alerts if a['severity'] == 'medium']),
        'alerts': alerts
    } 