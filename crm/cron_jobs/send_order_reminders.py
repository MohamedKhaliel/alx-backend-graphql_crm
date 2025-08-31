#!/usr/bin/env python3
"""
Order Reminders Script
Queries GraphQL endpoint for orders within the last 7 days and logs them.
"""

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GraphQL endpoint
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

def log_message(message):
    """Log message with timestamp to the log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}\n"
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}", file=sys.stderr)

def get_recent_orders():
    """Query GraphQL for orders within the last 7 days."""
    
    # GraphQL query to get orders with customer information
    query = gql("""
        query GetRecentOrders {
            orders {
                id
                customer {
                    user {
                        email
                    }
                }
                created_at
                status
                total_amount
            }
        }
    """)
    
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute the query
        result = client.execute(query)
        
        return result.get('orders', [])
        
    except Exception as e:
        log_message(f"Error querying GraphQL: {str(e)}")
        return []

def filter_recent_orders(orders):
    """Filter orders to only include those from the last 7 days."""
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_orders = []
    
    for order in orders:
        try:
            # Parse the created_at date
            order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
            
            # Check if order is within last 7 days
            if order_date >= seven_days_ago:
                recent_orders.append(order)
                
        except Exception as e:
            log_message(f"Error parsing date for order {order.get('id', 'unknown')}: {str(e)}")
    
    return recent_orders

def main():
    """Main function to process order reminders."""
    
    log_message("Starting order reminders processing")
    
    try:
        # Get all orders from GraphQL
        all_orders = get_recent_orders()
        
        if not all_orders:
            log_message("No orders found or error occurred while fetching orders")
            return
        
        # Filter for recent orders (last 7 days)
        recent_orders = filter_recent_orders(all_orders)
        
        log_message(f"Found {len(recent_orders)} orders within the last 7 days")
        
        # Log each order's details
        for order in recent_orders:
            order_id = order.get('id', 'unknown')
            customer_email = order.get('customer', {}).get('user', {}).get('email', 'no-email')
            order_date = order.get('created_at', 'unknown-date')
            status = order.get('status', 'unknown-status')
            total_amount = order.get('total_amount', 'unknown-amount')
            
            log_message(f"Order ID: {order_id}, Customer Email: {customer_email}, Date: {order_date}, Status: {status}, Amount: {total_amount}")
        
        log_message("Order reminders processing completed successfully")
        
    except Exception as e:
        log_message(f"Unexpected error in main function: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
    print("Order reminders processed!")
