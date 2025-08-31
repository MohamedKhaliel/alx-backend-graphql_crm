#!/bin/bash

# Script to clean up inactive customers (no orders since a year ago)
# This script uses Django's manage.py shell to execute Python commands

# Set the Django project directory
DJANGO_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Function to log messages with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to log errors and exit
log_error() {
    log_message "ERROR: $1"
    echo "ERROR: $1" >&2
    exit 1
}

# Check if we're in the correct directory
if [ ! -f "$DJANGO_PROJECT_DIR/manage.py" ]; then
    log_error "manage.py not found in $DJANGO_PROJECT_DIR"
fi

# Change to the Django project directory
cd "$DJANGO_PROJECT_DIR" || log_error "Failed to change to Django project directory"

# Log script start
log_message "Starting customer cleanup script"

# Python script to delete inactive customers
# This script deletes customers with no orders since a year ago
PYTHON_SCRIPT="
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx-backend-graphql_crm.settings')
django.setup()

try:
    # Import the CRM models
    from crm.models import Customer, Order
    
    # Calculate the date one year ago
    one_year_ago = timezone.now() - timedelta(days=365)
    
    # Get all customers
    all_customers = Customer.objects.all()
    total_customers_before = all_customers.count()
    
    # Find customers with no orders since one year ago
    # This includes customers with no orders at all, and customers whose last order was more than a year ago
    inactive_customers = Customer.objects.filter(
        ~Q(orders__created_at__gte=one_year_ago)
    ).distinct()
    
    # Count how many will be deleted
    customers_to_delete = inactive_customers.count()
    
    # Delete the inactive customers
    # Note: This will also delete associated User records due to OneToOneField with CASCADE
    deleted_count = 0
    for customer in inactive_customers:
        try:
            # Delete the customer (this will also delete the associated User)
            customer.delete()
            deleted_count += 1
        except Exception as e:
            print(f'Error deleting customer {customer.id}: {str(e)}')
    
    # Log the results
    print(f'Total customers before cleanup: {total_customers_before}')
    print(f'Inactive customers found: {customers_to_delete}')
    print(f'Customers successfully deleted: {deleted_count}')
    print(f'Customers remaining: {total_customers_before - deleted_count}')
    
    # Return the count for the shell script
    sys.exit(deleted_count)
    
except Exception as e:
    print(f'Error during customer cleanup: {str(e)}')
    sys.exit(1)
"

# Execute the Python script using Django's shell
log_message "Executing Django shell command"
deleted_count=$(python manage.py shell -c "$PYTHON_SCRIPT" 2>&1)

# Check if the command was successful
if [ $? -eq 0 ]; then
    # Extract the deleted count from the output (assuming it's the last line with a number)
    deleted_count=$(echo "$deleted_count" | tail -n 1 | grep -o '[0-9]*' | head -n 1)
    if [ -z "$deleted_count" ]; then
        deleted_count=0
    fi
    log_message "Successfully completed customer cleanup. Deleted $deleted_count customers."
else
    log_error "Failed to execute Django shell command: $deleted_count"
fi

log_message "Customer cleanup script completed"
echo "Customer cleanup completed. Check $LOG_FILE for details."
