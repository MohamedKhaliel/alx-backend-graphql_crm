# CRM Cron Jobs

This directory contains automated scripts for maintaining the CRM system.

## Django-Crontab Setup

The project uses `django-crontab` for managing cron jobs within Django. This provides better integration and management of cron jobs.

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add cron jobs to system crontab:**
   ```bash
   python manage.py crontab add
   ```

3. **Remove cron jobs from system crontab:**
   ```bash
   python manage.py crontab remove
   ```

4. **Show current cron jobs:**
   ```bash
   python manage.py crontab show
   ```

## clean_inactive_customers.sh

This script automatically removes customers who have not placed any orders in the last year.

### Features

- Uses Django's `manage.py shell` to execute Python commands
- Deletes customers with no orders since a year ago
- Logs all activities with timestamps to `/tmp/customer_cleanup_log.txt`
- Includes error handling and validation
- Automatically handles the Django project directory detection

### Usage

1. **Manual execution:**
   ```bash
   ./crm/cron_jobs/clean_inactive_customers.sh
   ```

2. **Set up as a cron job:**
   ```bash
   # Edit crontab
   crontab -e
   
   # Add this line to run daily at 2 AM
   0 2 * * * /path/to/your/project/crm/cron_jobs/clean_inactive_customers.sh
   ```

### Requirements

- Django project with Customer and Order models
- Proper database migrations applied
- Script must be executable (`chmod +x`)

### Log File

The script logs all activities to `/tmp/customer_cleanup_log.txt` with timestamps:
```
2024-01-15 14:30:00 - Starting customer cleanup script
2024-01-15 14:30:01 - Executing Django shell command
2024-01-15 14:30:02 - Successfully completed customer cleanup. Deleted 5 customers.
2024-01-15 14:30:02 - Customer cleanup script completed
```

### Model Requirements

The script expects the following Django models:

- **Customer**: Linked to Django User model with OneToOneField
- **Order**: Linked to Customer with ForeignKey and includes `created_at` field

### Safety Features

- Validates Django project directory before execution
- Logs all operations with timestamps
- Handles errors gracefully
- Provides detailed output of operations performed

### Customization

You can modify the script to:
- Change the inactivity period (currently 365 days)
- Add additional filtering criteria
- Modify the log file location
- Add email notifications for cleanup results

## CRM Heartbeat (Django-Crontab)

The CRM heartbeat is managed through `django-crontab` and runs every 5 minutes.

### Configuration

- **Function**: `crm.cron.log_crm_heartbeat`
- **Schedule**: Every 5 minutes (`*/5 * * * *`)
- **Log File**: `/tmp/crm_heartbeat_log.txt`
- **Format**: `DD/MM/YYYY-HH:MM:SS CRM is alive`

### Features

- Logs heartbeat messages with timestamps
- Optionally queries GraphQL endpoint to verify responsiveness
- Appends to log file (does not overwrite)
- Error handling for both logging and GraphQL queries

### Log Output Example

```
15/01/2024-14:30:00 CRM is alive
15/01/2024-14:30:00 GraphQL endpoint responsive: Hello, GraphQL!
15/01/2024-14:35:00 CRM is alive
15/01/2024-14:35:00 GraphQL endpoint responsive: Hello, GraphQL!
```

## Low Stock Updates (Django-Crontab)

The low stock update is managed through `django-crontab` and runs every 12 hours.

### Configuration

- **Function**: `crm.cron.update_low_stock`
- **Schedule**: Every 12 hours (`0 */12 * * *`)
- **Log File**: `/tmp/low_stock_updates_log.txt`
- **GraphQL Mutation**: `UpdateLowStockProducts`

### Features

- Queries products with stock < 10
- Increments their stock by 10 (simulating restocking)
- Logs updated product names and new stock levels
- Uses GraphQL mutation for data consistency
- Comprehensive error handling and logging

### GraphQL Mutation

The `UpdateLowStockProducts` mutation:
- Finds products with stock below threshold (default: 10)
- Increments stock by specified amount (default: 10)
- Returns list of updated products and success message

### Log Output Example

```
15/01/2024-08:00:00 Low stock update initiated
15/01/2024-08:00:00 Successfully updated 3 products with low stock
15/01/2024-08:00:00 Updated Product ID: 1, Name: Laptop, New Stock: 15
15/01/2024-08:00:00 Updated Product ID: 2, Name: Mouse, New Stock: 12
15/01/2024-08:00:00 Updated Product ID: 3, Name: Keyboard, New Stock: 18
```
