"""
API views for core app.
"""
from typing import List
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Spend
from .services import SpendService
from .serializers import SpendSerializer, SpendCreateSerializer


class SpendViewSet(viewsets.ModelViewSet):
    """ViewSet for Spend model."""
    queryset = Spend.objects.select_related('campaign', 'campaign__brand')
    serializer_class = SpendSerializer
    
    @action(detail=False, methods=['get'])
    def total_summary(self, request) -> Response:
        """Get total spend summary across all campaigns."""
        summary = SpendService.get_total_spend_summary()
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request) -> Response:
        """Get spend records by date range."""
        from datetime import date
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        campaign_id = request.query_params.get('campaign_id')
        brand_id = request.query_params.get('brand_id')
        
        if not start_date_str or not end_date_str:
            return Response(
                {'error': 'start_date and end_date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign_id_int = None
        if campaign_id:
            try:
                campaign_id_int = int(campaign_id)
            except ValueError:
                return Response(
                    {'error': 'Invalid campaign_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        brand_id_int = None
        if brand_id:
            try:
                brand_id_int = int(brand_id)
            except ValueError:
                return Response(
                    {'error': 'Invalid brand_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        spends = SpendService.get_spend_by_date_range(
            start_date=start_date,
            end_date=end_date,
            campaign_id=campaign_id_int,
            brand_id=brand_id_int
        )
        
        return Response({
            'start_date': start_date_str,
            'end_date': end_date_str,
            'campaign_id': campaign_id_int,
            'brand_id': brand_id_int,
            'total_records': len(spends),
            'total_amount': sum(spend['amount'] for spend in spends),
            'spends': spends
        })
    
    @action(detail=False, methods=['post'])
    def create_spend(self, request) -> Response:
        """Create a new spend record."""
        campaign_id = request.data.get('campaign_id')
        amount = request.data.get('amount')
        description = request.data.get('description', '')
        date_str = request.data.get('date')
        
        if not campaign_id or not amount:
            return Response(
                {'error': 'campaign_id and amount are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            campaign_id_int = int(campaign_id)
            amount_decimal = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid campaign_id or amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        date_obj = None
        if date_str:
            try:
                from datetime import date
                date_obj = date.fromisoformat(date_str)
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            spend = SpendService.create_spend(
                campaign_id=campaign_id_int,
                amount=amount_decimal,
                date=date_obj,
                description=description
            )
            
            return Response({
                'spend_id': spend.id,
                'campaign_id': spend.campaign.id,
                'campaign_name': spend.campaign.name,
                'amount': float(spend.amount),
                'date': spend.date.isoformat(),
                'description': spend.description,
                'created_at': spend.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 