"""
CRM Cron Jobs
This module contains functions that can be executed by django-crontab.
"""

import os
import sys
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a heartbeat message to indicate CRM is alive.
    Optionally queries GraphQL hello field to verify endpoint responsiveness.
    """
    
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Log file path
    log_file = '/tmp/crm_heartbeat_log.txt'
    
    # Create heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"
    
    try:
        # Append to log file (does not overwrite)
        with open(log_file, 'a') as f:
            f.write(heartbeat_message + '\n')
        
        # Optionally query GraphQL hello field to verify endpoint is responsive
        try:
            # GraphQL endpoint
            graphql_endpoint = "http://localhost:8000/graphql"
            
            # GraphQL query for hello field
            query = gql("""
                query {
                    name
                }
            """)
            
            # Create GraphQL client
            transport = RequestsHTTPTransport(url=graphql_endpoint)
            client = Client(transport=transport, fetch_schema_from_transport=True)
            
            # Execute the query
            result = client.execute(query)
            
            # Log successful GraphQL query
            graphql_status = f"{timestamp} GraphQL endpoint responsive: {result.get('name', 'No response')}"
            with open(log_file, 'a') as f:
                f.write(graphql_status + '\n')
                
        except Exception as graphql_error:
            # Log GraphQL error but don't fail the heartbeat
            graphql_error_msg = f"{timestamp} GraphQL endpoint error: {str(graphql_error)}"
            with open(log_file, 'a') as f:
                f.write(graphql_error_msg + '\n')
    
    except Exception as e:
        # If we can't write to log file, print to stderr
        print(f"Error writing heartbeat log: {str(e)}", file=sys.stderr)
        sys.exit(1)

def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation via GraphQL endpoint.
    Logs updated product names and new stock levels.
    """
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Log file path
    log_file = '/tmp/low_stock_updates_log.txt'
    
    try:
        # GraphQL endpoint
        graphql_endpoint = "http://localhost:8000/graphql"
        
        # GraphQL mutation for updating low stock products
        mutation = gql("""
            mutation UpdateLowStockProducts($threshold: Int, $increment: Int) {
                updateLowStockProducts(threshold: $threshold, increment: $increment) {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                        price
                    }
                }
            }
        """)
        
        # Create GraphQL client
        transport = RequestsHTTPTransport(url=graphql_endpoint)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Execute the mutation
        variables = {
            "threshold": 10,
            "increment": 10
        }
        
        result = client.execute(mutation, variable_values=variables)
        
        # Extract results
        mutation_result = result.get('updateLowStockProducts', {})
        success = mutation_result.get('success', False)
        message = mutation_result.get('message', 'No message')
        updated_products = mutation_result.get('updatedProducts', [])
        
        # Log the results
        log_message = f"{timestamp} Low stock update initiated"
        with open(log_file, 'a') as f:
            f.write(log_message + '\n')
        
        if success:
            log_message = f"{timestamp} {message}"
            with open(log_file, 'a') as f:
                f.write(log_message + '\n')
            
            # Log each updated product
            for product in updated_products:
                product_name = product.get('name', 'Unknown Product')
                new_stock = product.get('stock', 0)
                product_id = product.get('id', 'Unknown ID')
                
                product_log = f"{timestamp} Updated Product ID: {product_id}, Name: {product_name}, New Stock: {new_stock}"
                with open(log_file, 'a') as f:
                    f.write(product_log + '\n')
        else:
            error_log = f"{timestamp} Low stock update failed: {message}"
            with open(log_file, 'a') as f:
                f.write(error_log + '\n')
    
    except Exception as e:
        # Log error
        error_message = f"{timestamp} Error in low stock update: {str(e)}"
        try:
            with open(log_file, 'a') as f:
                f.write(error_message + '\n')
        except:
            print(f"Error writing to log file: {e}", file=sys.stderr)
        print(f"Error in low stock update: {str(e)}", file=sys.stderr)
        sys.exit(1)
