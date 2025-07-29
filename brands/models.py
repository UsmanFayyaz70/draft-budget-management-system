"""
Brand models for the budget management system.
"""
from decimal import Decimal
from typing import List, Optional
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Brand(models.Model):
    """
    Represents an advertising brand/client with budget limits.
    """
    name = models.CharField(max_length=200, unique=True)
    daily_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    monthly_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def get_daily_spend(self) -> Decimal:
        """Get total daily spend across all campaigns."""
        from core.models import Spend
        today = timezone.now().date()
        return Spend.objects.filter(
            campaign__brand=self,
            date=today
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_monthly_spend(self) -> Decimal:
        """Get total monthly spend across all campaigns."""
        from core.models import Spend
        now = timezone.now()
        return Spend.objects.filter(
            campaign__brand=self,
            date__year=now.year,
            date__month=now.month
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_daily_budget_remaining(self) -> Decimal:
        """Get remaining daily budget."""
        return self.daily_budget - self.get_daily_spend()

    def get_monthly_budget_remaining(self) -> Decimal:
        """Get remaining monthly budget."""
        return self.monthly_budget - self.get_monthly_spend()

    def has_daily_budget_available(self) -> bool:
        """Check if daily budget is available."""
        return self.get_daily_budget_remaining() > Decimal('0.00')

    def has_monthly_budget_available(self) -> bool:
        """Check if monthly budget is available."""
        return self.get_monthly_budget_remaining() > Decimal('0.00')

    def get_active_campaigns(self) -> List['campaigns.Campaign']:
        """Get all active campaigns for this brand."""
        return list(self.campaigns.filter(is_active=True))

    def can_activate_campaigns(self) -> bool:
        """Check if brand can activate campaigns based on budget."""
        return (
            self.is_active and 
            self.has_daily_budget_available() and 
            self.has_monthly_budget_available()
        ) 