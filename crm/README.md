# CRM System Setup Guide

This guide provides step-by-step instructions for setting up the CRM system with Django, GraphQL, Celery, and Redis.

## Prerequisites

- Python 3.8+
- Redis server
- Virtual environment (recommended)

## Installation Steps

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install and Start Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Windows:
Download and install Redis from [https://redis.io/download](https://redis.io/download)

### 3. Database Setup

```bash
# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser
```

### 4. Start Django Development Server

```bash
# Start the Django server
python manage.py runserver
```

The GraphQL endpoint will be available at: `http://localhost:8000/graphql`

### 5. Start Celery Worker

Open a new terminal and run:

```bash
# Start Celery worker
celery -A crm worker -l info
```

### 6. Start Celery Beat (Task Scheduler)

Open another terminal and run:

```bash
# Start Celery Beat
celery -A crm beat -l info
```

### 7. Verify Setup

Check the following log files to verify everything is working:

```bash
# Check CRM heartbeat logs
tail -f /tmp/crm_heartbeat_log.txt

# Check low stock update logs
tail -f /tmp/low_stock_updates_log.txt

# Check CRM report logs
tail -f /tmp/crm_report_log.txt

# Check order reminder logs
tail -f /tmp/order_reminders_log.txt
```

## Scheduled Tasks

### Django-Crontab Tasks
- **CRM Heartbeat**: Every 5 minutes - `/tmp/crm_heartbeat_log.txt`
- **Low Stock Updates**: Every 12 hours - `/tmp/low_stock_updates_log.txt`

### Celery Beat Tasks
- **CRM Report Generation**: Every Monday at 6:00 AM - `/tmp/crm_report_log.txt`

## Manual Task Execution

### Run CRM Report Manually
```bash
# Using Django shell
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> result = generate_crm_report.delay()
>>> print(result.get())
```

### Run Low Stock Update Manually
```bash
# Using Django shell
python manage.py shell
>>> from crm.cron import update_low_stock
>>> update_low_stock()
```

## GraphQL Queries

### Test the GraphQL Endpoint
```bash
# Query all customers
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ allCustomers { id user { email } } }"}'

# Query all products
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ allProducts { id name stock price } }"}'

# Query all orders
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ allOrders { id totalAmount customer { user { email } } } }"}'
```

## Troubleshooting

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Check Redis status
sudo systemctl status redis-server
```

### Celery Issues
```bash
# Check Celery worker status
celery -A crm inspect active

# Check Celery Beat status
celery -A crm inspect scheduled
```

### Django Issues
```bash
# Check Django logs
python manage.py check

# Collect static files (if needed)
python manage.py collectstatic
```

## Development

### Adding New Tasks
1. Add task function to `crm/tasks.py`
2. Decorate with `@shared_task`
3. Add to `CELERY_BEAT_SCHEDULE` in settings if needed

### Adding New Cron Jobs
1. Add function to `crm/cron.py`
2. Add to `CRONJOBS` in settings
3. Run `python manage.py crontab add`

## Production Deployment

For production deployment, consider:
- Using a process manager like Supervisor
- Setting up Redis persistence
- Using a production database (PostgreSQL)
- Configuring proper logging
- Setting up monitoring and alerting

## File Structure

```
crm/
├── __init__.py          # Celery app initialization
├── celery.py           # Celery configuration
├── cron.py             # Django-crontab functions
├── models.py           # Django models
├── schema.py           # GraphQL schema
├── tasks.py            # Celery tasks
├── cron_jobs/          # Shell scripts
│   ├── clean_inactive_customers.sh
│   ├── send_order_reminders.py
│   └── README.md
└── README.md           # This file
```
