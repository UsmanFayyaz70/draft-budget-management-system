"""
Campaign models for the budget management system.
"""
from decimal import Decimal
from typing import List, Optional, Set
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from brands.models import Brand


class DaypartingSchedule(models.Model):
    """
    Defines when campaigns can run during specific hours and days.
    """
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    name = models.CharField(max_length=200)
    start_hour = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Hour in 24-hour format (0-23)"
    )
    end_hour = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Hour in 24-hour format (0-23)"
    )
    days_of_week = models.JSONField(
        default=list,
        help_text="List of day numbers (0=Monday, 6=Sunday)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dayparting_schedules'
        ordering = ['name']

    def __str__(self) -> str:
        return f"{self.name} ({self.start_hour:02d}:00-{self.end_hour:02d}:00)"

    def is_currently_active(self) -> bool:
        """Check if schedule is currently active based on time and day."""
        now = timezone.now()
        current_hour = now.hour
        current_day = now.weekday()
        
        # Check if current day is in allowed days
        if current_day not in self.days_of_week:
            return False
        
        # Check if current hour is within allowed range
        if self.start_hour <= self.end_hour:
            # Same day schedule (e.g., 9:00-17:00)
            return self.start_hour <= current_hour < self.end_hour
        else:
            # Overnight schedule (e.g., 22:00-06:00)
            return current_hour >= self.start_hour or current_hour < self.end_hour

    def get_active_hours(self) -> Set[int]:
        """Get set of active hours for this schedule."""
        if self.start_hour <= self.end_hour:
            return set(range(self.start_hour, self.end_hour))
        else:
            # Overnight schedule
            return set(range(self.start_hour, 24)) | set(range(0, self.end_hour))

    def get_days_display(self) -> str:
        """Get human-readable display of active days."""
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        active_days = [day_names[day] for day in sorted(self.days_of_week)]
        return ', '.join(active_days)


class Campaign(models.Model):
    """
    Represents an advertising campaign with budget tracking and dayparting.
    """
    CAMPAIGN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('draft', 'Draft'),
    ]

    name = models.CharField(max_length=200)
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE, 
        related_name='campaigns'
    )
    status = models.CharField(
        max_length=20, 
        choices=CAMPAIGN_STATUS_CHOICES, 
        default='draft'
    )
    is_active = models.BooleanField(default=False)
    dayparting_schedule = models.ForeignKey(
        DaypartingSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campaigns'
    )
    daily_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True
    )
    monthly_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['name']
        unique_together = ['brand', 'name']

    def __str__(self) -> str:
        return f"{self.name} ({self.brand.name})"

    def get_daily_spend(self) -> Decimal:
        """Get daily spend for this campaign."""
        from core.models import Spend
        today = timezone.now().date()
        return Spend.objects.filter(
            campaign=self,
            date=today
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_monthly_spend(self) -> Decimal:
        """Get monthly spend for this campaign."""
        from core.models import Spend
        now = timezone.now()
        return Spend.objects.filter(
            campaign=self,
            date__year=now.year,
            date__month=now.month
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def get_daily_budget_limit(self) -> Decimal:
        """Get effective daily budget limit (campaign or brand level)."""
        if self.daily_budget:
            return self.daily_budget
        return self.brand.daily_budget

    def get_monthly_budget_limit(self) -> Decimal:
        """Get effective monthly budget limit (campaign or brand level)."""
        if self.monthly_budget:
            return self.monthly_budget
        return self.brand.monthly_budget

    def get_daily_budget_remaining(self) -> Decimal:
        """Get remaining daily budget."""
        return self.get_daily_budget_limit() - self.get_daily_spend()

    def get_monthly_budget_remaining(self) -> Decimal:
        """Get remaining monthly budget."""
        return self.get_monthly_budget_limit() - self.get_monthly_spend()

    def has_daily_budget_available(self) -> bool:
        """Check if daily budget is available."""
        return self.get_daily_budget_remaining() > Decimal('0.00')

    def has_monthly_budget_available(self) -> bool:
        """Check if monthly budget is available."""
        return self.get_monthly_budget_remaining() > Decimal('0.00')

    def is_within_dayparting_schedule(self) -> bool:
        """Check if campaign is within its dayparting schedule."""
        if not self.dayparting_schedule:
            return True  # No dayparting restrictions
        return self.dayparting_schedule.is_currently_active()

    def can_be_activated(self) -> bool:
        """Check if campaign can be activated based on all criteria."""
        return (
            self.status == 'active' and
            self.brand.is_active and
            self.brand.has_daily_budget_available() and
            self.brand.has_monthly_budget_available() and
            self.has_daily_budget_available() and
            self.has_monthly_budget_available() and
            self.is_within_dayparting_schedule()
        )

    def should_be_paused(self) -> bool:
        """Check if campaign should be paused based on budget or dayparting."""
        return (
            not self.has_daily_budget_available() or
            not self.has_monthly_budget_available() or
            not self.brand.has_daily_budget_available() or
            not self.brand.has_monthly_budget_available() or
            not self.is_within_dayparting_schedule()
        )

    def activate(self) -> bool:
        """Activate the campaign if conditions are met."""
        if self.can_be_activated():
            self.is_active = True
            self.save()
            return True
        return False

    def pause(self) -> bool:
        """Pause the campaign."""
        if self.is_active:
            self.is_active = False
            self.save()
            return True
        return False 