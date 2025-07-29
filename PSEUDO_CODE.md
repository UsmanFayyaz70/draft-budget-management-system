# Budget Management System - Pseudo Code

## System Overview

This document provides a high-level, language-agnostic overview of the Django + Celery Budget Management System for advertising campaigns.

## Data Models

### Brand
```
Brand {
    id: unique_identifier
    name: string
    daily_budget: decimal
    monthly_budget: decimal
    is_active: boolean
    created_at: timestamp
    updated_at: timestamp
    
    methods:
        get_daily_spend(): decimal
        get_monthly_spend(): decimal
        get_daily_budget_remaining(): decimal
        get_monthly_budget_remaining(): decimal
        has_daily_budget_available(): boolean
        has_monthly_budget_available(): boolean
        get_active_campaigns(): list[Campaign]
        can_activate_campaigns(): boolean
}
```

### Campaign
```
Campaign {
    id: unique_identifier
    name: string
    brand: reference_to_brand
    status: enum['active', 'paused', 'completed', 'draft']
    is_active: boolean
    dayparting_schedule: optional_reference_to_dayparting_schedule
    daily_budget: optional_decimal
    monthly_budget: optional_decimal
    created_at: timestamp
    updated_at: timestamp
    
    methods:
        get_daily_spend(): decimal
        get_monthly_spend(): decimal
        get_daily_budget_limit(): decimal
        get_monthly_budget_limit(): decimal
        get_daily_budget_remaining(): decimal
        get_monthly_budget_remaining(): decimal
        has_daily_budget_available(): boolean
        has_monthly_budget_available(): boolean
        is_within_dayparting_schedule(): boolean
        can_be_activated(): boolean
        should_be_paused(): boolean
        activate(): boolean
        pause(): boolean
}
```

### DaypartingSchedule
```
DaypartingSchedule {
    id: unique_identifier
    name: string
    start_hour: integer (0-23)
    end_hour: integer (0-23)
    days_of_week: list[integer] (0=Monday, 6=Sunday)
    is_active: boolean
    created_at: timestamp
    updated_at: timestamp
    
    methods:
        is_currently_active(): boolean
        get_active_hours(): set[integer]
        get_days_display(): string
}
```

### Spend
```
Spend {
    id: unique_identifier
    campaign: reference_to_campaign
    amount: decimal
    date: date
    description: string
    created_at: timestamp
    updated_at: timestamp
    
    methods:
        get_daily_total(): decimal
        get_monthly_total(): decimal
        get_brand_daily_total(): decimal
        get_brand_monthly_total(): decimal
}
```

## Key Business Logic

### 1. Spend Tracking Logic
```
function update_spend(campaign_id, amount, date):
    campaign = get_campaign(campaign_id)
    spend_record = create_spend_record(campaign, amount, date)
    
    if campaign.should_be_paused():
        campaign.pause()
        log_campaign_paused(campaign, "Budget exceeded")
    
    return spend_record
```

### 2. Budget Enforcement Logic
```
function check_budget_limits():
    for each brand in active_brands:
        if not brand.has_daily_budget_available() or not brand.has_monthly_budget_available():
            deactivate_all_campaigns(brand)
            log_brand_budget_exceeded(brand)
    
    for each campaign in active_campaigns:
        if campaign.should_be_paused():
            campaign.pause()
            log_campaign_paused(campaign, "Budget exceeded")
```

### 3. Dayparting Enforcement Logic
```
function enforce_dayparting():
    for each campaign in active_campaigns_with_dayparting:
        if not campaign.is_within_dayparting_schedule():
            campaign.pause()
            log_campaign_paused(campaign, "Outside dayparting schedule")
```

### 4. Campaign Activation Logic
```
function activate_campaign(campaign):
    if campaign.can_be_activated():
        campaign.is_active = true
        campaign.save()
        log_campaign_activated(campaign)
        return true
    else:
        log_campaign_activation_failed(campaign, "Conditions not met")
        return false

function can_be_activated(campaign):
    return (
        campaign.status == 'active' and
        campaign.brand.is_active and
        campaign.brand.has_daily_budget_available() and
        campaign.brand.has_monthly_budget_available() and
        campaign.has_daily_budget_available() and
        campaign.has_monthly_budget_available() and
        campaign.is_within_dayparting_schedule()
    )
```

### 5. Budget Reset Logic
```
function reset_daily_budgets():
    for each brand in active_brands:
        for each campaign in brand.campaigns:
            if campaign.can_be_activated():
                campaign.activate()
                log_campaign_reactivated(campaign, "Daily budget reset")

function reset_monthly_budgets():
    for each brand in active_brands:
        for each campaign in brand.campaigns:
            if campaign.can_be_activated():
                campaign.activate()
                log_campaign_reactivated(campaign, "Monthly budget reset")
```

### 6. Dayparting Schedule Logic
```
function is_currently_active(schedule):
    current_time = get_current_time()
    current_day = current_time.weekday()
    current_hour = current_time.hour
    
    if current_day not in schedule.days_of_week:
        return false
    
    if schedule.start_hour <= schedule.end_hour:
        return schedule.start_hour <= current_hour < schedule.end_hour
    else:
        # Overnight schedule (e.g., 22:00-06:00)
        return current_hour >= schedule.start_hour or current_hour < schedule.end_hour
```

## Periodic Tasks

### 1. Spend Updates (Every 5 minutes)
```
task update_spend():
    for each active_campaign:
        # In real system, this would integrate with ad platforms
        spend_amount = get_spend_from_ad_platform(campaign)
        update_spend(campaign.id, spend_amount, current_date)
```

### 2. Dayparting Enforcement (Every minute)
```
task enforce_dayparting():
    enforce_dayparting()
```

### 3. Daily Budget Reset (Daily at midnight)
```
task reset_daily_budgets():
    reset_daily_budgets()
    log_daily_reset_completed()
```

### 4. Monthly Budget Reset (Monthly on 1st at midnight)
```
task reset_monthly_budgets():
    reset_monthly_budgets()
    log_monthly_reset_completed()
```

## System Workflow

### Daily Operations
1. **00:00** - Daily budget reset, reactivate eligible campaigns
2. **Every 5 minutes** - Update spend for all active campaigns
3. **Every minute** - Check dayparting schedules
4. **Throughout day** - Monitor budgets, pause campaigns when limits exceeded

### Monthly Operations
1. **1st of month 00:00** - Monthly budget reset, reactivate campaigns
2. **Throughout month** - Track monthly spend, enforce monthly limits

### Campaign Lifecycle
1. **Creation** - Campaign created with status 'draft'
2. **Activation** - Campaign status changed to 'active', system checks if can be activated
3. **Running** - Campaign is active and spending budget
4. **Paused** - Campaign paused due to budget limits or dayparting
5. **Reactivated** - Campaign reactivated when conditions allow

## Assumptions and Simplifications

1. **Time Zones** - All times handled in UTC
2. **Currency** - Single currency (USD) for simplicity
3. **Spend Updates** - Simulated spend tracking (would integrate with real ad platforms)
4. **Dayparting** - Basic hour-based scheduling (can be extended for complex patterns)
5. **Budget Types** - Daily and monthly budgets only
6. **Campaign Status** - Binary active/inactive (can be extended for more granular states)

## Error Handling

```
function handle_budget_exceeded(campaign):
    campaign.pause()
    send_alert("Budget exceeded", campaign)
    log_event("campaign_paused_budget", campaign)

function handle_dayparting_violation(campaign):
    campaign.pause()
    send_alert("Outside dayparting schedule", campaign)
    log_event("campaign_paused_dayparting", campaign)

function handle_system_error(error):
    log_error(error)
    send_alert("System error", error)
    # Continue processing other campaigns
```

## Performance Considerations

1. **Database Indexing** - Index on spend date, campaign_id, brand_id
2. **Caching** - Cache budget calculations for frequently accessed data
3. **Batch Processing** - Process campaigns in batches for large datasets
4. **Async Processing** - Use Celery for background tasks to avoid blocking
5. **Monitoring** - Track task execution times and system performance 