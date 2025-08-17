import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    email = django_filters.CharFilter(lookup_expr='icontains', label='Email contains')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte', label='Created after')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte', label='Created before')
    
    # Custom filter for phone number pattern (e.g., starts with +1)
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern', label='Phone pattern')
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at__gte', 'created_at__lte', 'phone_pattern']
    
    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter for phone number patterns"""
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Price greater than or equal to')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Price less than or equal to')
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte', label='Stock greater than or equal to')
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte', label='Stock less than or equal to')
    
    # Custom filter for low stock (e.g., stock < 10)
    low_stock = django_filters.BooleanFilter(method='filter_low_stock', label='Low stock')
    
    class Meta:
        model = Product
        fields = ['name', 'price__gte', 'price__lte', 'stock__gte', 'stock__lte', 'low_stock']
    
    def filter_low_stock(self, queryset, name, value):
        """Custom filter for low stock products"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte', label='Total amount greater than or equal to')
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte', label='Total amount less than or equal to')
    order_date__gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte', label='Order date after')
    order_date__lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte', label='Order date before')
    
    # Filter by customer name (case-insensitive partial match)
    customer_name = django_filters.CharFilter(method='filter_customer_name', label='Customer name contains')
    
    # Filter by product name (case-insensitive partial match)
    product_name = django_filters.CharFilter(method='filter_product_name', label='Product name contains')
    
    # Filter orders that include a specific product ID
    product_id = django_filters.NumberFilter(method='filter_product_id', label='Contains product ID')
    
    class Meta:
        model = Order
        fields = [
            'total_amount__gte', 'total_amount__lte',
            'order_date__gte', 'order_date__lte',
            'customer_name', 'product_name', 'product_id'
        ]
    
    def filter_customer_name(self, queryset, name, value):
        """Filter orders by customer name"""
        if value:
            return queryset.filter(customer__name__icontains=value)
        return queryset
    
    def filter_product_name(self, queryset, name, value):
        """Filter orders by product name"""
        if value:
            return queryset.filter(products__name__icontains=value)
        return queryset
    
    def filter_product_id(self, queryset, name, value):
        """Filter orders that contain a specific product ID"""
        if value:
            return queryset.filter(products__id=value)
        return queryset
