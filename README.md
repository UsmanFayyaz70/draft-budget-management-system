# Budget Management System

A Django + Celery backend system for managing advertising budgets, campaigns, and dayparting schedules.

## Features

- **Budget Tracking**: Daily and monthly ad spend tracking
- **Campaign Management**: Automatic campaign activation/deactivation based on budgets
- **Dayparting**: Campaign scheduling with specific time windows
- **Automated Resets**: Daily and monthly budget resets with campaign reactivation
- **Type Safety**: Full static typing with MyPy support

## Tech Stack

- **Django**: Web framework, ORM, admin interface
- **Celery**: Background task processing
- **SQLite**: Database (can be easily switched to PostgreSQL)
- **Redis**: Message broker for Celery
- **MyPy**: Static type checking

## Project Structure

```
budget-management-system/
├── README.md
├── requirements.txt
├── mypy.ini
├── manage.py
├── budget_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── brands/
│   ├── __init__.py
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   └── tasks.py
├── campaigns/
│   ├── __init__.py
│   ├── models.py
│   ├── admin.py
│   ├── services.py
│   └── tasks.py
└── core/
    ├── __init__.py
    ├── models.py
    ├── services.py
    └── tasks.py
```

## Data Models

### Brand
- Represents an advertising brand/client
- Has daily and monthly budget limits
- Contains multiple campaigns

### Campaign
- Belongs to a brand
- Has status (active/inactive)
- Contains dayparting schedule
- Tracks spend

### Spend
- Tracks daily and monthly spend for campaigns
- Automatically updated by system

### DaypartingSchedule
- Defines when campaigns can run
- Specifies allowed hours and days

## System Workflow

### Daily Operations
1. **Budget Reset** (00:00 daily): Reset daily budgets, reactivate eligible campaigns
2. **Spend Tracking**: Monitor and update campaign spend throughout the day
3. **Budget Enforcement**: Automatically pause campaigns when budgets are exceeded
4. **Dayparting**: Enable/disable campaigns based on current time

### Monthly Operations
1. **Monthly Reset** (1st of month): Reset monthly budgets, reactivate campaigns
2. **Monthly Reporting**: Generate spend reports

### Periodic Tasks
- **Spend Updates**: Every 5 minutes - update spend and check budgets
- **Dayparting Enforcement**: Every minute - check dayparting schedules
- **Budget Resets**: Daily and monthly at specified times

## Setup Instructions

### Prerequisites
- Python 3.8+
- Redis server
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd budget-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file with:
   DEBUG=True
   SECRET_KEY=your-secret-key
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis server**
   ```bash
   # Install Redis if not already installed
   # Start Redis server
   redis-server
   ```

8. **Start Celery worker**
   ```bash
   celery -A budget_system worker -l info
   ```

9. **Start Celery beat (scheduler)**
   ```bash
   celery -A budget_system beat -l info
   ```

10. **Run development server**
    ```bash
    python manage.py runserver
    ```

### Type Checking

Run MyPy to check for type errors:
```bash
mypy .
```

## Usage

### Admin Interface
- Access Django admin at `http://localhost:8000/admin/`
- Manage brands, campaigns, and schedules through the admin interface

### API Endpoints
- `/api/brands/` - Brand management
- `/api/campaigns/` - Campaign management
- `/api/spend/` - Spend tracking

### Management Commands
```bash
# Reset daily budgets
python manage.py reset_daily_budgets

# Reset monthly budgets
python manage.py reset_monthly_budgets

# Check campaign statuses
python manage.py check_campaign_statuses
```

## Assumptions and Simplifications

1. **Time Zones**: All times are handled in UTC for simplicity
2. **Currency**: Single currency (USD) - can be extended
3. **Spend Updates**: Simplified spend tracking - in production would integrate with actual ad platforms
4. **Dayparting**: Basic hour-based scheduling - can be extended for more complex patterns
5. **Budget Types**: Daily and monthly budgets only - can be extended for weekly, yearly, etc.
6. **Campaign Status**: Binary active/inactive - can be extended for more granular states

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type hints
4. Run type checking: `mypy .`
5. Submit a pull request

## License

MIT License 