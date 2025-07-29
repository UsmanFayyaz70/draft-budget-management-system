"""
Management command to reset daily budgets and reactivate campaigns.
"""
from typing import Any
from django.core.management.base import BaseCommand
from core.services import BudgetResetService


class Command(BaseCommand):
    """Command to reset daily budgets."""
    help = 'Reset daily budgets and reactivate eligible campaigns'

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        self.stdout.write('Starting daily budget reset...')
        
        result = BudgetResetService.reset_daily_budgets()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Daily budget reset completed. '
                f'Brands checked: {result["brands_checked"]}, '
                f'Campaigns reactivated: {result["campaigns_reactivated"]}'
            )
        )
        
        if result['reactivated_campaigns']:
            self.stdout.write('Reactivated campaigns:')
            for campaign in result['reactivated_campaigns']:
                self.stdout.write(
                    f'  - {campaign["campaign_name"]} ({campaign["brand_name"]})'
                ) 