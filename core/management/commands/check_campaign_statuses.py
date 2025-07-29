"""
Management command to check and enforce campaign statuses.
"""
from typing import Any
from django.core.management.base import BaseCommand
from campaigns.services import CampaignService, DaypartingService


class Command(BaseCommand):
    """Command to check campaign statuses."""
    help = 'Check and enforce campaign statuses based on budgets and dayparting'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        parser.add_argument(
            '--enforce',
            action='store_true',
            help='Enforce status changes (pause/activate campaigns)',
        )
        parser.add_argument(
            '--dayparting-only',
            action='store_true',
            help='Only check dayparting schedules',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        enforce = options['enforce']
        dayparting_only = options['dayparting_only']
        
        self.stdout.write('Checking campaign statuses...')
        
        if dayparting_only:
            self._check_dayparting_only(enforce)
        else:
            self._check_all_statuses(enforce)

    def _check_dayparting_only(self, enforce: bool) -> None:
        """Check only dayparting schedules."""
        if enforce:
            result = DaypartingService.enforce_dayparting()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dayparting enforcement completed. '
                    f'Campaigns checked: {result["campaigns_checked"]}, '
                    f'Campaigns paused: {result["campaigns_paused"]}'
                )
            )
            
            if result['paused_campaigns']:
                self.stdout.write('Paused campaigns:')
                for campaign in result['paused_campaigns']:
                    self.stdout.write(
                        f'  - {campaign["campaign_name"]} ({campaign["brand_name"]}) - {campaign["schedule_name"]}'
                    )
        else:
            affected_campaigns = DaypartingService.get_campaigns_affected_by_dayparting()
            self.stdout.write(
                f'Found {len(affected_campaigns)} campaigns affected by dayparting:'
            )
            for campaign in affected_campaigns:
                self.stdout.write(
                    f'  - {campaign.name} ({campaign.brand.name})'
                )

    def _check_all_statuses(self, enforce: bool) -> None:
        """Check all campaign statuses."""
        if enforce:
            result = CampaignService.enforce_campaign_statuses()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Campaign status enforcement completed. '
                    f'Campaigns activated: {result["campaigns_activated"]}, '
                    f'Campaigns paused: {result["campaigns_paused"]}'
                )
            )
            
            if result['activated_campaigns']:
                self.stdout.write('Activated campaigns:')
                for campaign in result['activated_campaigns']:
                    self.stdout.write(
                        f'  - {campaign["campaign_name"]} ({campaign["brand_name"]})'
                    )
            
            if result['paused_campaigns']:
                self.stdout.write('Paused campaigns:')
                for campaign in result['paused_campaigns']:
                    self.stdout.write(
                        f'  - {campaign["campaign_name"]} ({campaign["brand_name"]})'
                    )
        else:
            campaigns_needing_activation = CampaignService.get_campaigns_needing_activation()
            campaigns_needing_pause = CampaignService.get_campaigns_needing_pause()
            
            self.stdout.write(
                f'Found {len(campaigns_needing_activation)} campaigns needing activation:'
            )
            for campaign in campaigns_needing_activation:
                self.stdout.write(
                    f'  - {campaign.name} ({campaign.brand.name})'
                )
            
            self.stdout.write(
                f'Found {len(campaigns_needing_pause)} campaigns needing pause:'
            )
            for campaign in campaigns_needing_pause:
                self.stdout.write(
                    f'  - {campaign.name} ({campaign.brand.name})'
                ) 