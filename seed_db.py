#!/usr/bin/env python3
"""
Database seeding script for ALX Backend GraphQL CRM
Run this script to populate the database with sample data
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order, OrderItem


def seed_customers():
    """Seed sample customers"""
    print("🌱 Seeding customers...")
    
    customers_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice.johnson@example.com',
            'phone': '+1234567890'
        },
        {
            'name': 'Bob Smith',
            'email': 'bob.smith@example.com',
            'phone': '1234567890'
        },
        {
            'name': 'Carol Davis',
            'email': 'carol.davis@example.com',
            'phone': '+442079460958'
        },
        {
            'name': 'David Wilson',
            'email': 'david.wilson@example.com',
            'phone': '5551234567'
        },
        {
            'name': 'Eva Brown',
            'email': 'eva.brown@example.com',
            'phone': '+15559876543'
        }
    ]
    
    created_customers = []
    for customer_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults=customer_data
        )
        if created:
            created_customers.append(customer)
            print(f"✅ Created customer: {customer.name}")
        else:
            print(f"ℹ️  Customer already exists: {customer.name}")
    
    print(f"📊 Total customers: {Customer.objects.count()}")
    return created_customers


def seed_products():
    """Seed sample products"""
    print("\n🌱 Seeding products...")
    
    products_data = [
        {
            'name': 'Laptop Pro',
            'price': Decimal('1299.99'),
            'stock': 15
        },
        {
            'name': 'Smartphone X',
            'price': Decimal('799.99'),
            'stock': 25
        },
        {
            'name': 'Wireless Headphones',
            'price': Decimal('199.99'),
            'stock': 30
        },
        {
            'name': 'Tablet Air',
            'price': Decimal('599.99'),
            'stock': 20
        },
        {
            'name': 'Smart Watch',
            'price': Decimal('299.99'),
            'stock': 18
        },
        {
            'name': 'Gaming Console',
            'price': Decimal('499.99'),
            'stock': 12
        },
        {
            'name': 'Bluetooth Speaker',
            'price': Decimal('89.99'),
            'stock': 35
        },
        {
            'name': 'USB-C Cable',
            'price': Decimal('19.99'),
            'stock': 100
        }
    ]
    
    created_products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            created_products.append(product)
            print(f"✅ Created product: {product.name} - ${product.price}")
        else:
            print(f"ℹ️  Product already exists: {product.name}")
    
    print(f"📊 Total products: {Product.objects.count()}")
    return created_products


def seed_orders(customers, products):
    """Seed sample orders"""
    print("\n🌱 Seeding orders...")
    
    # Create some sample orders
    orders_data = [
        {
            'customer': customers[0],  # Alice
            'products': [products[0], products[2]],  # Laptop + Headphones
            'description': 'Work setup order'
        },
        {
            'customer': customers[1],  # Bob
            'products': [products[1], products[4]],  # Smartphone + Smart Watch
            'description': 'Mobile accessories'
        },
        {
            'customer': customers[2],  # Carol
            'products': [products[3], products[6]],  # Tablet + Speaker
            'description': 'Entertainment bundle'
        },
        {
            'customer': customers[0],  # Alice again
            'products': [products[7]],  # USB-C Cable
            'description': 'Additional accessory'
        },
        {
            'customer': customers[3],  # David
            'products': [products[5], products[2]],  # Gaming Console + Headphones
            'description': 'Gaming setup'
        }
    ]
    
    created_orders = []
    for order_data in orders_data:
        # Calculate total amount
        total_amount = sum(product.price for product in order_data['products'])
        
        # Create order
        order = Order.objects.create(
            customer=order_data['customer'],
            total_amount=total_amount
        )
        
        # Create order items
        for product in order_data['products']:
            OrderItem.objects.create(
                order=order,
                product=product,
                price_at_time=product.price
            )
        
        created_orders.append(order)
        print(f"✅ Created order #{order.id}: {order.customer.name} - ${order.total_amount}")
    
    print(f"📊 Total orders: {Order.objects.count()}")
    return created_orders


def main():
    """Main seeding function"""
    print("🚀 Starting database seeding for ALX Backend GraphQL CRM...")
    print("=" * 60)
    
    try:
        # Seed customers
        customers = seed_customers()
        
        # Seed products
        products = seed_products()
        
        # Seed orders (only if we have both customers and products)
        if customers and products:
            orders = seed_orders(customers, products)
        else:
            print("⚠️  Skipping orders - need both customers and products")
        
        print("\n" + "=" * 60)
        print("🎉 Database seeding completed successfully!")
        print(f"📊 Final counts:")
        print(f"   - Customers: {Customer.objects.count()}")
        print(f"   - Products: {Product.objects.count()}")
        print(f"   - Orders: {Order.objects.count()}")
        print(f"   - Order Items: {OrderItem.objects.count()}")
        print("\n✨ You can now test the GraphQL mutations!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
