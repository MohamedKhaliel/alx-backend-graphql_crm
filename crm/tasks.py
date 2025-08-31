import os
import sys
from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests

@shared_task
def generate_crm_report():
    """
    Generate CRM report with total customers, orders, and revenue.
    Uses GraphQL queries to fetch data and logs the report.
    """
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Log file path
    log_file = '/tmp/crm_report_log.txt'
    
    try:
        # GraphQL endpoint
        graphql_endpoint = "http://localhost:8000/graphql"
        
        # Create GraphQL client
        transport = RequestsHTTPTransport(url=graphql_endpoint)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Query 1: Get total number of customers
        customers_query = gql("""
            query {
                allCustomers {
                    id
                }
            }
        """)
        
        # Query 2: Get total number of orders and revenue
        orders_query = gql("""
            query {
                allOrders {
                    id
                    totalAmount
                }
            }
        """)
        
        # Execute queries
        customers_result = client.execute(customers_query)
        orders_result = client.execute(orders_query)
        
        # Extract data
        total_customers = len(customers_result.get('allCustomers', []))
        orders = orders_result.get('allOrders', [])
        total_orders = len(orders)
        
        # Calculate total revenue
        total_revenue = sum(
            float(order.get('totalAmount', 0)) 
            for order in orders 
            if order.get('totalAmount') is not None
        )
        
        # Format revenue to 2 decimal places
        formatted_revenue = f"${total_revenue:.2f}"
        
        # Create report message
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {formatted_revenue} revenue"
        
        # Log the report
        try:
            with open(log_file, 'a') as f:
                f.write(report_message + '\n')
        except Exception as log_error:
            print(f"Error writing to log file: {log_error}", file=sys.stderr)
        
        # Return the report data for potential use
        return {
            'timestamp': timestamp,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'formatted_revenue': formatted_revenue
        }
        
    except Exception as e:
        error_message = f"{timestamp} - Error generating CRM report: {str(e)}"
        
        # Log error
        try:
            with open(log_file, 'a') as f:
                f.write(error_message + '\n')
        except:
            print(f"Error writing to log file: {e}", file=sys.stderr)
        
        print(f"Error generating CRM report: {str(e)}", file=sys.stderr)
        
        # Re-raise the exception so Celery knows the task failed
        raise
