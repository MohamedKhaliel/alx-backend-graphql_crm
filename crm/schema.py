import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from crm.models import Customer, Product, Order
from crm.models import Product

# GraphQL Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'

# Queries
class Query(graphene.ObjectType):
    # Hello query for testing
    name = graphene.String(default_value="Hello, GraphQL!")
    
    # Customer queries
    all_customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    
    # Product queries
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    low_stock_products = graphene.List(ProductType, threshold=graphene.Int(default_value=10))
    
    # Order queries
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    
    def resolve_all_customers(self, info):
        return Customer.objects.all()
    
    def resolve_customer(self, info, id):
        return Customer.objects.get(pk=id)
    
    def resolve_all_products(self, info):
        return Product.objects.all()
    
    def resolve_product(self, info, id):
        return Product.objects.get(pk=id)
    
    def resolve_low_stock_products(self, info, threshold=10):
        return Product.objects.filter(stock__lt=threshold)
    
    def resolve_all_orders(self, info):
        return Order.objects.all()
    
    def resolve_order(self, info, id):
        return Order.objects.get(pk=id)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        phone = graphene.String()
        address = graphene.String()

    success = graphene.Boolean()
    customer = graphene.Field(CustomerType)

    def mutate(self, info, username, email, first_name=None, last_name=None, phone=None, address=None):
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name or '',
                last_name=last_name or ''
            )
            
            # Create customer profile
            customer = Customer.objects.create(
                user=user,
                phone=phone,
                address=address
            )
            
            return CreateCustomer(success=True, customer=customer)
        except Exception as e:
            return CreateCustomer(success=False, customer=None)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    success = graphene.Boolean()
    product = graphene.Field(ProductType)

    def mutate(self, info, name, description=None, price=0.0, stock=0):
        try:
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=stock
            )
            return CreateProduct(success=True, product=product)
        except Exception as e:
            return CreateProduct(success=False, product=None)

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        threshold = graphene.Int(default_value=10)
        increment = graphene.Int(default_value=10)

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info, threshold=10, increment=10):
        try:
            # Find products with stock below threshold
            low_stock_products = Product.objects.filter(stock__lt=threshold)
            
            updated_products = []
            for product in low_stock_products:
                # Increment stock
                product.stock += increment
                product.save()
                updated_products.append(product)
            
            if updated_products:
                message = f"Successfully updated {len(updated_products)} products with low stock"
            else:
                message = "No products found with low stock"
            
            return UpdateLowStockProducts(
                success=True,
                message=message,
                updated_products=updated_products
            )
        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating low stock products: {str(e)}",
                updated_products=[]
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    success = graphene.Boolean()
    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_id, quantity):
        try:
            customer = Customer.objects.get(pk=customer_id)
            product = Product.objects.get(pk=product_id)
            
            # Calculate total amount
            total_amount = product.price * quantity
            
            # Check if enough stock is available
            if product.stock < quantity:
                return CreateOrder(success=False, order=None)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                total_amount=total_amount
            )
            
            # Update product stock
            product.stock -= quantity
            product.save()
            
            return CreateOrder(success=True, order=order)
        except Exception as e:
            return CreateOrder(success=False, order=None)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
    create_order = CreateOrder.Field()

# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
