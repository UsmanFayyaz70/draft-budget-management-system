"""
Celery tasks for campaign operations and dayparting enforcement.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from celery import shared_task
from django.utils import timezone
from .models import Campaign, DaypartingSchedule
from .services import CampaignService, DaypartingService


@shared_task
def enforce_dayparting_task() -> Dict[str, Any]:
    """Enforce dayparting schedules by pausing campaigns outside their schedules."""
    return DaypartingService.enforce_dayparting()


@shared_task
def enforce_campaign_statuses_task() -> Dict[str, Any]:
    """Enforce campaign statuses based on budgets and dayparting."""
    return CampaignService.enforce_campaign_statuses()


@shared_task
def check_campaign_budgets_task() -> Dict[str, Any]:
    """Check all campaign budgets and pause campaigns if needed."""
    campaigns_to_pause = []
    
    for campaign in Campaign.objects.filter(is_active=True):
        if campaign.should_be_paused():
            if CampaignService.pause_campaign(campaign):
                campaigns_to_pause.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'brand_name': campaign.brand.name,
                    'reason': 'Budget exceeded'
                })
    
    return {
        'timestamp': timezone.now().isoformat(),
        'campaigns_checked': Campaign.objects.filter(is_active=True).count(),
        'campaigns_paused': len(campaigns_to_pause),
        'paused_campaigns': campaigns_to_pause
    }


@shared_task
def reactivate_campaigns_task() -> Dict[str, Any]:
    """Reactivate campaigns that can be activated."""
    campaigns_to_activate = CampaignService.get_campaigns_needing_activation()
    activated_campaigns = []
    
    for campaign in campaigns_to_activate:
        if CampaignService.activate_campaign(campaign):
            activated_campaigns.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'brand_name': campaign.brand.name
            })
    
    return {
        'timestamp': timezone.now().isoformat(),
        'campaigns_checked': Campaign.objects.filter(status='active', is_active=False).count(),
        'campaigns_activated': len(activated_campaigns),
        'activated_campaigns': activated_campaigns
    }


@shared_task
def update_campaign_spend_task(
    campaign_id: int, 
    amount: Decimal
) -> Dict[str, Any]:
    """Update spend for a specific campaign."""
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        from core.models import Spend
        
        # Create spend record
        spend = Spend.objects.create(
            campaign=campaign,
            amount=amount,
            date=timezone.now().date()
        )
        
        # Check if campaign should be paused after spend update
        should_pause = campaign.should_be_paused()
        if should_pause and campaign.is_active:
            CampaignService.pause_campaign(campaign)
        
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
def generate_campaign_summary_task() -> Dict[str, Any]:
    """Generate comprehensive summary of all campaigns."""
    campaigns_summary = []
    total_active_campaigns = 0
    total_paused_campaigns = 0
    total_daily_spend = Decimal('0.00')
    total_monthly_spend = Decimal('0.00')
    
    for campaign in Campaign.objects.select_related('brand', 'dayparting_schedule'):
        status = CampaignService.check_campaign_status(campaign)
        campaigns_summary.append(status)
        
        if campaign.is_active:
            total_active_campaigns += 1
        else:
            total_paused_campaigns += 1
        
        total_daily_spend += campaign.get_daily_spend()
        total_monthly_spend += campaign.get_monthly_spend()
    
    return {
        'timestamp': timezone.now().isoformat(),
        'total_campaigns': len(campaigns_summary),
        'total_active_campaigns': total_active_campaigns,
        'total_paused_campaigns': total_paused_campaigns,
        'total_daily_spend': float(total_daily_spend),
        'total_monthly_spend': float(total_monthly_spend),
        'campaigns_summary': campaigns_summary
    }


@shared_task
def update_campaign_status_task(campaign_id: int) -> Dict[str, Any]:
    """Update status of a specific campaign based on current conditions."""
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        status = CampaignService.check_campaign_status(campaign)
        
        # Determine if campaign should be activated or paused
        if campaign.can_be_activated() and not campaign.is_active:
            CampaignService.activate_campaign(campaign)
            action = 'activated'
        elif campaign.should_be_paused() and campaign.is_active:
            CampaignService.pause_campaign(campaign)
            action = 'paused'
        else:
            action = 'no_change'
        
        return {
            'timestamp': timezone.now().isoformat(),
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'action': action,
            'status': status,
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