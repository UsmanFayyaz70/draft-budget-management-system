"""
Core models for the budget management system.
"""
from decimal import Decimal
from typing import Optional
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from campaigns.models import Campaign


class Spend(models.Model):
    """
    Tracks daily and monthly spend for campaigns.
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='spends'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField()
    description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spends'
        ordering = ['-date', '-created_at']
        unique_together = ['campaign', 'date']

    def __str__(self) -> str:
        return f"{self.campaign.name} - ${self.amount} on {self.date}"

    def get_daily_total(self) -> Decimal:
        """Get total spend for this campaign on this date."""
        return Spend.objects.filter(
            campaign=self.campaign,
            date=self.date
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_monthly_total(self) -> Decimal:
        """Get total spend for this campaign in this month."""
        return Spend.objects.filter(
            campaign=self.campaign,
            date__year=self.date.year,
            date__month=self.date.month
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_brand_daily_total(self) -> Decimal:
        """Get total spend for this campaign's brand on this date."""
        return Spend.objects.filter(
            campaign__brand=self.campaign.brand,
            date=self.date
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_brand_monthly_total(self) -> Decimal:
        """Get total spend for this campaign's brand in this month."""
        return Spend.objects.filter(
            campaign__brand=self.campaign.brand,
            date__year=self.date.year,
            date__month=self.date.month
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00') 