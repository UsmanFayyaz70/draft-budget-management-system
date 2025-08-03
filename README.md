# 🚀 Budget Management System for Ad Agencies

Hey there! 👋 This is a super cool system that helps ad agencies manage their advertising budgets automatically. Think of it like a smart assistant that watches your money and makes sure you don't spend too much!

## 🌟 What This System Does

Imagine you're running ads for different brands (like Nike, Coca-Cola, etc.). Each brand has a budget:
- **Daily Budget**: How much they can spend each day (like $1000/day)
- **Monthly Budget**: How much they can spend each month (like $25,000/month)

This system automatically:
- ✅ **Tracks spending** - Records every penny spent on ads
- ✅ **Stops overspending** - Pauses campaigns when budgets are exceeded
- ✅ **Resets daily** - Gives fresh budgets every day at midnight
- ✅ **Resets monthly** - Gives fresh budgets every month
- ✅ **Respects schedules** - Only runs ads during allowed hours

## 🎯 Quick Start Guide

### Step 1: Check if everything is working
```bash
python status.py
```
This will tell you if everything is set up correctly!

### Step 2: Start the web server
```bash
python manage.py runserver
```
Now you can visit http://localhost:8000 in your web browser!

### Step 3: Test the system
```bash
python celery_scripts/test_tasks.py
```
This makes sure all the background tasks are working properly.

## 🛠️ How to Use the System

### 🌐 Web Interface
- **Main Site**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`

### 📱 API Endpoints (for developers)
You can also control the system using these web addresses:

#### Brands
- `GET /api/brands/` - See all brands
- `POST /api/brands/` - Create a new brand
- `GET /api/brands/1/spend_summary/` - See spending for brand #1

#### Campaigns
- `GET /api/campaigns/` - See all campaigns
- `POST /api/campaigns/` - Create a new campaign

#### Spending
- `GET /api/spends/` - See all spending records
- `POST /api/spends/create_spend/` - Add a new spending record

## 🔧 Advanced Features

### Background Tasks (Celery)
The system runs background tasks to keep everything working:

```bash
# Start the background worker
python celery_scripts/worker.py

# Start the scheduler (runs tasks on schedule)
python celery_scripts/beat.py
```

### What the Background Tasks Do:
1. **Every 5 minutes**: Update spending tracking
2. **Every minute**: Check if campaigns should be running
3. **Daily at midnight**: Reset daily budgets
4. **Monthly on 1st**: Reset monthly budgets

## 📊 Example: How It Works

Let's say Nike has:
- Daily budget: $1,000
- Monthly budget: $25,000

**Scenario 1**: Nike spends $1,200 in one day
- ✅ System detects overspending
- ✅ Automatically pauses Nike's campaigns
- ✅ Prevents further spending

**Scenario 2**: It's midnight
- ✅ System resets daily budget
- ✅ Reactivates Nike's campaigns (if monthly budget allows)

**Scenario 3**: It's the 1st of the month
- ✅ System resets monthly budget
- ✅ All campaigns get fresh budgets

## 🎮 Testing the System

### Create a Test Brand
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Test Brand", "daily_budget": 500, "monthly_budget": 15000}' \
  http://localhost:8000/api/brands/
```

### Create a Test Campaign
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "Test Campaign", "brand": 1, "daily_budget": 100, "monthly_budget": 3000}' \
  http://localhost:8000/api/campaigns/
```

### Add Some Spending
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"campaign_id": 1, "amount": 50.00, "description": "Ad spend"}' \
  http://localhost:8000/api/spends/create_spend/
```

## 🏗️ Project Structure

```
budget-management-system/
├── 📁 brands/           # Brand management
├── 📁 campaigns/        # Campaign management  
├── 📁 core/            # Core features (spending, etc.)
├── 📁 budget_system/   # Main Django project
├── 📁 celery_scripts/  # Background task scripts
├── 📄 manage.py        # Django management
├── 📄 status.py        # System status checker
└── 📄 README.md        # This file!
```

## 🚨 Troubleshooting

### "Module not found" errors?
Make sure you have all the required packages:
```bash
pip install -r requirements.txt
```

### "Database errors"?
Run the database setup:
```bash
python manage.py migrate
```

### "Celery not working"?
The system is designed to work even without Celery running. The tasks will execute synchronously in development mode.

## 🎉 You're All Set!

Your Budget Management System is ready to:
- ✅ Track ad spending automatically
- ✅ Enforce daily and monthly budgets
- ✅ Reset budgets on schedule
- ✅ Provide a web interface
- ✅ Handle background processing

Start with `python status.py` to check everything is working, then `python manage.py runserver` to start the web server!

Happy budgeting! 🎯💰 