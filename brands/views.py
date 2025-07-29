"""
API views for brands app.
"""
from typing import List
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Brand
from .services import BrandService
from .serializers import BrandSerializer, BrandSummarySerializer


class BrandViewSet(viewsets.ModelViewSet):
    """ViewSet for Brand model."""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    
    @action(detail=True, methods=['get'])
    def spend_summary(self, request, pk=None) -> Response:
        """Get spend summary for a specific brand."""
        try:
            brand = self.get_object()
            summary = BrandService.get_brand_spend_summary(brand)
            return Response(summary)
        except Brand.DoesNotExist:
            return Response(
                {'error': 'Brand not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reactivate_campaigns(self, request, pk=None) -> Response:
        """Reactivate campaigns for a brand."""
        try:
            brand = self.get_object()
            reactivated_campaigns = BrandService.reactivate_brand_campaigns(brand)
            
            return Response({
                'brand_id': brand.id,
                'brand_name': brand.name,
                'campaigns_reactivated': len(reactivated_campaigns),
                'reactivated_campaigns': [
                    {
                        'campaign_id': campaign.id,
                        'campaign_name': campaign.name
                    } for campaign in reactivated_campaigns
                ]
            })
        except Brand.DoesNotExist:
            return Response(
                {'error': 'Brand not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def deactivate_campaigns(self, request, pk=None) -> Response:
        """Deactivate all campaigns for a brand."""
        try:
            brand = self.get_object()
            deactivated_campaigns = BrandService.deactivate_brand_campaigns(brand)
            
            return Response({
                'brand_id': brand.id,
                'brand_name': brand.name,
                'campaigns_deactivated': len(deactivated_campaigns),
                'deactivated_campaigns': [
                    {
                        'campaign_id': campaign.id,
                        'campaign_name': campaign.name
                    } for campaign in deactivated_campaigns
                ]
            })
        except Brand.DoesNotExist:
            return Response(
                {'error': 'Brand not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request) -> Response:
        """Get summary for all brands."""
        summaries = BrandService.get_all_brands_summary()
        return Response(summaries)
    
    @action(detail=False, methods=['get'])
    def with_budget_issues(self, request) -> Response:
        """Get brands with budget issues."""
        brands_with_issues = BrandService.get_brands_with_budget_issues()
        
        return Response({
            'brands_with_issues': [
                {
                    'brand_id': brand.id,
                    'brand_name': brand.name,
                    'daily_spend': float(brand.get_daily_spend()),
                    'monthly_spend': float(brand.get_monthly_spend()),
                    'daily_budget': float(brand.daily_budget),
                    'monthly_budget': float(brand.monthly_budget),
                    'has_daily_budget': brand.has_daily_budget_available(),
                    'has_monthly_budget': brand.has_monthly_budget_available(),
                } for brand in brands_with_issues
            ]
        }) 