#!/usr/bin/env python3
"""
Simple Celery Beat scheduler for the budget management system.
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

if __name__ == '__main__':
    from budget_system.celery import app
    
    print("⏰ Starting Celery Beat Scheduler for Budget Management System")
    print("=" * 70)
    print("Scheduled Tasks:")
    print("  - Update spend every 5 minutes")
    print("  - Enforce dayparting every minute")
    print("  - Reset daily budgets at midnight")
    print("  - Reset monthly budgets on 1st of month at midnight")
    print("=" * 70)
    
    # Start the beat scheduler with proper arguments
    argv = [
        'beat',
        '--loglevel=info',
        '--scheduler=django_celery_beat.schedulers:DatabaseScheduler'
    ]
    
    app.worker_main(argv) 