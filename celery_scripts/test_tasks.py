#!/usr/bin/env python3
"""
Test script to verify Celery tasks are working.
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_system.settings')

# Setup Django
django.setup()

def test_celery_tasks():
    """Test various Celery tasks."""
    print("🧪 Testing Celery Tasks")
    print("=" * 50)
    
    try:
        # Import tasks
        from brands.tasks import check_brand_budgets_task
        from campaigns.tasks import enforce_dayparting_task
        from core.tasks import update_spend_task
        
        print("✅ Successfully imported Celery tasks")
        
        # Test a simple task
        print("\n📋 Testing debug task...")
        from budget_system.celery import debug_task
        result = debug_task.delay()
        print(f"   Task ID: {result.id}")
        print(f"   Status: {result.status}")
        
        # Test brand budget check task
        print("\n📋 Testing brand budget check task...")
        brand_result = check_brand_budgets_task.delay()
        print(f"   Task ID: {brand_result.id}")
        print(f"   Status: {brand_result.status}")
        
        # Test dayparting enforcement task
        print("\n📋 Testing dayparting enforcement task...")
        dayparting_result = enforce_dayparting_task.delay()
        print(f"   Task ID: {dayparting_result.id}")
        print(f"   Status: {dayparting_result.status}")
        
        # Test spend update task
        print("\n📋 Testing spend update task...")
        spend_result = update_spend_task.delay()
        print(f"   Task ID: {spend_result.id}")
        print(f"   Status: {spend_result.status}")
        
        print("\n✅ All tasks submitted successfully!")
        print("   Tasks will execute synchronously in development mode.")
        
    except Exception as e:
        print(f"❌ Error testing Celery tasks: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_celery_tasks() 