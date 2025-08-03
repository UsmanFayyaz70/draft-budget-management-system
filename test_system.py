#!/usr/bin/env python
"""
Test script for the Budget Management System.
This script demonstrates the core functionality of the system.
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_system.settings')
django.setup()

from brands.models import Brand
from campaigns.models import Campaign, DaypartingSchedule
from core.models import Spend
from brands.services import BrandService
from campaigns.services import CampaignService, DaypartingService
from core.services import SpendService


def test_basic_functionality():
    """Test basic system functionality."""
    print("=== Testing Budget Management System ===\n")
    
    # Create test data
    print("1. Creating test brands...")
    brand1 = BrandService.create_brand(
        name="Test Brand 3",
        daily_budget=Decimal('100.00'),
        monthly_budget=Decimal('2000.00')
    )
    brand2 = BrandService.create_brand(
        name="Test Brand 2", 
        daily_budget=Decimal('50.00'),
        monthly_budget=Decimal('1000.00')
    )
    print(f"   Created brands: {brand1.name}, {brand2.name}")
    
    # Create dayparting schedule
    print("\n2. Creating dayparting schedule...")
    schedule = DaypartingService.create_dayparting_schedule(
        name="Business Hours",
        start_hour=9,
        end_hour=17,
        days_of_week=[0, 1, 2, 3, 4]  # Monday to Friday
    )
    print(f"   Created schedule: {schedule.name} ({schedule.start_hour}:00-{schedule.end_hour}:00)")
    
    # Create campaigns
    print("\n3. Creating campaigns...")
    campaign1 = CampaignService.create_campaign(
        name="Test Campaign 1",
        brand_id=brand1.id,
        status='active',
        daily_budget=Decimal('25.00'),
        dayparting_schedule_id=schedule.id
    )
    campaign2 = CampaignService.create_campaign(
        name="Test Campaign 2",
        brand_id=brand2.id,
        status='active'
    )
    print(f"   Created campaigns: {campaign1.name}, {campaign2.name}")
    
    # Test campaign activation
    print("\n4. Testing campaign activation...")
    if campaign1.can_be_activated():
        campaign1.activate()
        print(f"   ✓ {campaign1.name} activated successfully")
    else:
        print(f"   ✗ {campaign1.name} cannot be activated")
    
    if campaign2.can_be_activated():
        campaign2.activate()
        print(f"   ✓ {campaign2.name} activated successfully")
    else:
        print(f"   ✗ {campaign2.name} cannot be activated")
    
    # Test spend tracking
    print("\n5. Testing spend tracking...")
    spend1 = SpendService.create_spend(
        campaign_id=campaign1.id,
        amount=Decimal('10.00'),
        description="Test spend 1"
    )
    spend2 = SpendService.create_spend(
        campaign_id=campaign1.id,
        amount=Decimal('15.00'),
        description="Test spend 2"
    )
    print(f"   Created spend records: ${spend1.amount}, ${spend2.amount}")
    
    # Check budget status
    print("\n6. Checking budget status...")
    brand1_summary = BrandService.get_brand_spend_summary(brand1)
    print(f"   {brand1.name} - Daily spend: ${brand1_summary['daily_spend']:.2f}")
    print(f"   {brand1.name} - Daily remaining: ${brand1_summary['daily_remaining']:.2f}")
    
    campaign1_summary = SpendService.get_campaign_spend_summary(campaign1)
    print(f"   {campaign1.name} - Daily spend: ${campaign1_summary['daily_spend']:.2f}")
    print(f"   {campaign1.name} - Daily remaining: ${campaign1_summary['daily_remaining']:.2f}")
    
    # Test dayparting
    print("\n7. Testing dayparting...")
    is_active = schedule.is_currently_active()
    print(f"   Schedule '{schedule.name}' is currently active: {is_active}")
    print(f"   Active hours: {schedule.get_active_hours()}")
    print(f"   Active days: {schedule.get_days_display()}")
    
    # Test budget enforcement
    print("\n8. Testing budget enforcement...")
    # Add more spend to exceed budget
    SpendService.create_spend(
        campaign_id=campaign1.id,
        amount=Decimal('100.00'),  # This will exceed the daily budget
        description="Large spend to test budget enforcement"
    )
    
    campaign1.refresh_from_db()
    if campaign1.should_be_paused():
        print(f"   ✓ {campaign1.name} should be paused (budget exceeded)")
        CampaignService.pause_campaign(campaign1)
        print(f"   ✓ {campaign1.name} paused successfully")
    else:
        print(f"   ✗ {campaign1.name} should not be paused")
    
    # Test reactivation
    print("\n9. Testing campaign reactivation...")
    reactivated = BrandService.reactivate_brand_campaigns(brand1)
    print(f"   Reactivated {len(reactivated)} campaigns for {brand1.name}")
    
    # Generate summary
    print("\n10. Generating system summary...")
    total_summary = SpendService.get_total_spend_summary()
    print(f"   Total daily spend: ${total_summary['total_daily_spend']:.2f}")
    print(f"   Total monthly spend: ${total_summary['total_monthly_spend']:.2f}")
    print(f"   Active campaigns: {total_summary['active_campaigns']}")
    print(f"   Total brands: {total_summary['total_brands']}")
    
    print("\n=== Test completed successfully! ===")


def test_api_endpoints():
    """Test API endpoints (if running)."""
    print("\n=== Testing API Endpoints ===")
    print("Note: This requires the Django server to be running")
    print("You can test the following endpoints:")
    print("  - GET /api/brands/")
    print("  - GET /api/brands/{id}/spend_summary/")
    print("  - GET /api/campaigns/")
    print("  - GET /api/campaigns/{id}/status_check/")
    print("  - GET /api/spend/total_summary/")
    print("  - POST /api/spend/create_spend/")


if __name__ == '__main__':
    try:
        test_basic_functionality()
        test_api_endpoints()
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1) 