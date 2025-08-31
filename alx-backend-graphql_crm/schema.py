import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User

class Query(graphene.ObjectType):
    # Define your queries here
    name = graphene.String(default_value="Hello, GraphQL!")
    
schema = graphene.Schema(query=Query)




class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True , unique=True)
        phone = graphene.String(required=False)
        

    success = graphene.Boolean()
    customer = graphene.Field(lambda: User)

    def mutate(self, info, name, email):
        customer = User(name=name, email=email)
        customer.save()
        return CreateCustomer(success=True, customer=customer)
    
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(CreateCustomer)

    success = graphene.Boolean()
    customers = graphene.List(lambda: User)

    def mutate(self, info, customers):
        created_customers = []
        for customer_data in customers:
            customer = User(name=customer_data.name, email=customer_data.email)
            customer.save()
            created_customers.append(customer)
        return BulkCreateCustomers(success=True, customers=created_customers)
    
    
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)

    success = graphene.Boolean()
    product = graphene.Field(lambda: User)  # Assuming Product is a Django model

    def mutate(self, info, name, price):
        product = User(name=name, email=price)  # Replace with actual Product model
        product.save()
        return CreateProduct(success=True, product=product)
    

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    success = graphene.Boolean()
    order = graphene.Field(lambda: User)  # Assuming Order is a Django model

    def mutate(self, info, customer_id, product_id, quantity):
        order = User(name=customer_id, email=product_id)  # Replace with actual Order model
        order.save()
        return CreateOrder(success=True, order=order)



class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()