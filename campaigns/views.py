"""
API views for campaigns app.
"""
from typing import List
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Campaign, DaypartingSchedule
from .services import CampaignService, DaypartingService
from .serializers import CampaignSerializer, CampaignCreateSerializer, DaypartingScheduleSerializer


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for Campaign model."""
    queryset = Campaign.objects.select_related('brand', 'dayparting_schedule')
    serializer_class = CampaignSerializer
    
    @action(detail=True, methods=['get'])
    def status_check(self, request, pk=None) -> Response:
        """Get comprehensive status check for a campaign."""
        try:
            campaign = self.get_object()
            status = CampaignService.check_campaign_status(campaign)
            return Response(status)
        except Campaign.DoesNotExist:
            return Response(
                {'error': 'Campaign not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None) -> Response:
        """Activate a campaign."""
        try:
            campaign = self.get_object()
            success = CampaignService.activate_campaign(campaign)
            
            return Response({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'success': success,
                'is_active': campaign.is_active
            })
        except Campaign.DoesNotExist:
            return Response(
                {'error': 'Campaign not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None) -> Response:
        """Pause a campaign."""
        try:
            campaign = self.get_object()
            success = CampaignService.pause_campaign(campaign)
            
            return Response({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'success': success,
                'is_active': campaign.is_active
            })
        except Campaign.DoesNotExist:
            return Response(
                {'error': 'Campaign not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def needing_activation(self, request) -> Response:
        """Get campaigns that need to be activated."""
        campaigns = CampaignService.get_campaigns_needing_activation()
        
        return Response({
            'campaigns': [
                {
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'brand_name': campaign.brand.name,
                    'status': campaign.status,
                    'is_active': campaign.is_active
                } for campaign in campaigns
            ]
        })
    
    @action(detail=False, methods=['get'])
    def needing_pause(self, request) -> Response:
        """Get campaigns that need to be paused."""
        campaigns = CampaignService.get_campaigns_needing_pause()
        
        return Response({
            'campaigns': [
                {
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'brand_name': campaign.brand.name,
                    'status': campaign.status,
                    'is_active': campaign.is_active
                } for campaign in campaigns
            ]
        })
    
    @action(detail=False, methods=['post'])
    def enforce_statuses(self, request) -> Response:
        """Enforce campaign statuses based on budgets and dayparting."""
        result = CampaignService.enforce_campaign_statuses()
        return Response(result)


class DaypartingScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for DaypartingSchedule model."""
    queryset = DaypartingSchedule.objects.all()
    serializer_class = DaypartingScheduleSerializer
    
    @action(detail=True, methods=['get'])
    def is_active(self, request, pk=None) -> Response:
        """Check if a dayparting schedule is currently active."""
        try:
            schedule = self.get_object()
            is_active = schedule.is_currently_active()
            
            return Response({
                'schedule_id': schedule.id,
                'schedule_name': schedule.name,
                'is_active': is_active,
                'active_hours': list(schedule.get_active_hours()),
                'active_days': schedule.get_days_display()
            })
        except DaypartingSchedule.DoesNotExist:
            return Response(
                {'error': 'Schedule not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def active_schedules(self, request) -> Response:
        """Get all currently active dayparting schedules."""
        active_schedules = DaypartingService.get_active_schedules()
        
        return Response({
            'active_schedules': [
                {
                    'schedule_id': schedule.id,
                    'schedule_name': schedule.name,
                    'start_hour': schedule.start_hour,
                    'end_hour': schedule.end_hour,
                    'active_days': schedule.get_days_display(),
                    'active_hours': list(schedule.get_active_hours())
                } for schedule in active_schedules
            ]
        })
    
    @action(detail=False, methods=['post'])
    def enforce_dayparting(self, request) -> Response:
        """Enforce dayparting schedules."""
        result = DaypartingService.enforce_dayparting()
        return Response(result) 