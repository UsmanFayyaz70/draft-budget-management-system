"""
Campaign services for campaign management and dayparting enforcement.
"""
from decimal import Decimal
from typing import List, Optional, Dict, Any
from django.db import transaction
from django.utils import timezone
from .models import Campaign, DaypartingSchedule


class CampaignService:
    """Service class for campaign-related operations."""

    @staticmethod
    def create_campaign(
        name: str,
        brand_id: int,
        status: str = 'draft',
        daily_budget: Optional[Decimal] = None,
        monthly_budget: Optional[Decimal] = None,
        dayparting_schedule_id: Optional[int] = None
    ) -> Campaign:
        """Create a new campaign."""
        from brands.models import Brand
        
        brand = Brand.objects.get(id=brand_id)
        dayparting_schedule = None
        if dayparting_schedule_id:
            dayparting_schedule = DaypartingSchedule.objects.get(id=dayparting_schedule_id)
        
        return Campaign.objects.create(
            name=name,
            brand=brand,
            status=status,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            dayparting_schedule=dayparting_schedule
        )

    @staticmethod
    def activate_campaign(campaign: Campaign) -> bool:
        """Activate a campaign if all conditions are met."""
        if campaign.can_be_activated():
            campaign.is_active = True
            campaign.save()
            return True
        return False

    @staticmethod
    def pause_campaign(campaign: Campaign) -> bool:
        """Pause a campaign."""
        if campaign.is_active:
            campaign.is_active = False
            campaign.save()
            return True
        return False

    @staticmethod
    def check_campaign_status(campaign: Campaign) -> Dict[str, Any]:
        """Check comprehensive status of a campaign."""
        return {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'brand_name': campaign.brand.name,
            'status': campaign.status,
            'is_active': campaign.is_active,
            'has_daily_budget': campaign.has_daily_budget_available(),
            'has_monthly_budget': campaign.has_monthly_budget_available(),
            'brand_has_daily_budget': campaign.brand.has_daily_budget_available(),
            'brand_has_monthly_budget': campaign.brand.has_monthly_budget_available(),
            'is_within_dayparting': campaign.is_within_dayparting_schedule(),
            'can_be_activated': campaign.can_be_activated(),
            'should_be_paused': campaign.should_be_paused(),
            'daily_spend': float(campaign.get_daily_spend()),
            'monthly_spend': float(campaign.get_monthly_spend()),
            'daily_budget_limit': float(campaign.get_daily_budget_limit()),
            'monthly_budget_limit': float(campaign.get_monthly_budget_limit()),
            'daily_remaining': float(campaign.get_daily_budget_remaining()),
            'monthly_remaining': float(campaign.get_monthly_budget_remaining()),
        }

    @staticmethod
    def get_campaigns_needing_activation() -> List[Campaign]:
        """Get campaigns that should be activated."""
        campaigns_to_activate = []
        for campaign in Campaign.objects.filter(status='active', is_active=False):
            if campaign.can_be_activated():
                campaigns_to_activate.append(campaign)
        return campaigns_to_activate

    @staticmethod
    def get_campaigns_needing_pause() -> List[Campaign]:
        """Get campaigns that should be paused."""
        campaigns_to_pause = []
        for campaign in Campaign.objects.filter(is_active=True):
            if campaign.should_be_paused():
                campaigns_to_pause.append(campaign)
        return campaigns_to_pause

    @staticmethod
    def enforce_campaign_statuses() -> Dict[str, Any]:
        """Enforce campaign statuses based on budgets and dayparting."""
        activated_campaigns = []
        paused_campaigns = []
        
        # Activate campaigns that can be activated
        for campaign in CampaignService.get_campaigns_needing_activation():
            if CampaignService.activate_campaign(campaign):
                activated_campaigns.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'brand_name': campaign.brand.name
                })
        
        # Pause campaigns that should be paused
        for campaign in CampaignService.get_campaigns_needing_pause():
            if CampaignService.pause_campaign(campaign):
                paused_campaigns.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'brand_name': campaign.brand.name
                })
        
        return {
            'timestamp': timezone.now().isoformat(),
            'campaigns_activated': len(activated_campaigns),
            'campaigns_paused': len(paused_campaigns),
            'activated_campaigns': activated_campaigns,
            'paused_campaigns': paused_campaigns
        }


class DaypartingService:
    """Service class for dayparting-related operations."""

    @staticmethod
    def create_dayparting_schedule(
        name: str,
        start_hour: int,
        end_hour: int,
        days_of_week: List[int]
    ) -> DaypartingSchedule:
        """Create a new dayparting schedule."""
        return DaypartingSchedule.objects.create(
            name=name,
            start_hour=start_hour,
            end_hour=end_hour,
            days_of_week=days_of_week
        )

    @staticmethod
    def get_active_schedules() -> List[DaypartingSchedule]:
        """Get all currently active dayparting schedules."""
        active_schedules = []
        for schedule in DaypartingSchedule.objects.filter(is_active=True):
            if schedule.is_currently_active():
                active_schedules.append(schedule)
        return active_schedules

    @staticmethod
    def get_campaigns_affected_by_dayparting() -> List[Campaign]:
        """Get campaigns that are affected by dayparting schedules."""
        affected_campaigns = []
        for campaign in Campaign.objects.filter(
            is_active=True,
            dayparting_schedule__isnull=False
        ):
            if not campaign.is_within_dayparting_schedule():
                affected_campaigns.append(campaign)
        return affected_campaigns

    @staticmethod
    def enforce_dayparting() -> Dict[str, Any]:
        """Enforce dayparting schedules by pausing campaigns outside their schedules."""
        campaigns_to_pause = DaypartingService.get_campaigns_affected_by_dayparting()
        paused_campaigns = []
        
        for campaign in campaigns_to_pause:
            if CampaignService.pause_campaign(campaign):
                paused_campaigns.append({
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'brand_name': campaign.brand.name,
                    'schedule_name': campaign.dayparting_schedule.name if campaign.dayparting_schedule else 'None'
                })
        
        return {
            'timestamp': timezone.now().isoformat(),
            'campaigns_checked': Campaign.objects.filter(
                dayparting_schedule__isnull=False
            ).count(),
            'campaigns_paused': len(paused_campaigns),
            'paused_campaigns': paused_campaigns
        } 