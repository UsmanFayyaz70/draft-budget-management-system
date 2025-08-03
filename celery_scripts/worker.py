#!/usr/bin/env python3
"""
Simple Celery worker for the budget management system.
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
    
    print("🚀 Starting Celery Worker for Budget Management System")
    print("=" * 60)
    print("Configuration:")
    print(f"  - Broker: {app.conf.broker_url}")
    print(f"  - Result Backend: {app.conf.result_backend}")
    print(f"  - Task Always Eager: {app.conf.task_always_eager}")
    print("=" * 60)
    
    # Start the worker with proper arguments
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=1',
        '--pool=solo'  # Use solo pool to avoid multiprocessing issues on Windows
    ]
    
    app.worker_main(argv) 