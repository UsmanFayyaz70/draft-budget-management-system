"""
Management command to reset monthly budgets and reactivate campaigns.
"""
from typing import Any
from django.core.management.base import BaseCommand
from core.services import BudgetResetService


class Command(BaseCommand):
    """Command to reset monthly budgets."""
    help = 'Reset monthly budgets and reactivate eligible campaigns'

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        self.stdout.write('Starting monthly budget reset...')
        
        result = BudgetResetService.reset_monthly_budgets()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Monthly budget reset completed. '
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