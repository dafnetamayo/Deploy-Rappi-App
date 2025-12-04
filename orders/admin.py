from django.contrib import admin

from .models import Product, Order, Restaurant, Client, Driver, Review, Delivery, OrderItem


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone_number', 'rating', 'opening_time', 'closing_time']
    search_fields = ['name', 'address']
    list_filter = ['rating']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'price', 'availability']
    list_filter = ['restaurant', 'availability']
    search_fields = ['name', 'description']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'registration_date']
    search_fields = ['name', 'email']
    list_filter = ['registration_date']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'vehicle_type', 'availability']
    list_filter = ['availability', 'vehicle_type']
    search_fields = ['name', 'email']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'restaurant', 'status', 'total', 'creation_date', 'payment_method']
    list_filter = ['status', 'payment_method', 'creation_date']
    search_fields = ['client__name', 'restaurant__name']
    date_hierarchy = 'creation_date'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price']
    list_filter = ['product']
    search_fields = ['order__id', 'product__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'restaurant', 'rating', 'review_date']
    list_filter = ['rating', 'review_date']
    search_fields = ['comment', 'client__name', 'restaurant__name']
    date_hierarchy = 'review_date'


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'driver', 'delivery_status', 'delivery_date', 'delivery_time']
    list_filter = ['delivery_status', 'delivery_date']
    search_fields = ['order__id', 'driver__name']
    date_hierarchy = 'delivery_date'

