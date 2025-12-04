from rest_framework import serializers
from .models import Order, Product, Restaurant, Client, Driver, Review, Delivery

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'availability']

class OrderSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()  # Muestra el nombre del cliente
    restaurant = serializers.StringRelatedField()  # Muestra el nombre del restaurante
    products = ProductSerializer(many=True)  # Relaciona productos con el pedido

    class Meta:
        model = Order
        fields = ['id', 'client', 'restaurant', 'creation_date', 'status', 'total', 'delivery_date', 'delivery_address', 'payment_method', 'comments', 'products']

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone_number', 'opening_time', 'closing_time', 'rating']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'address', 'phone_number', 'registration_date']

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'name', 'email', 'phone_number', 'vehicle_type', 'availability']

class ReviewSerializer(serializers.ModelSerializer):
    client = ClientSerializer()  # Información del cliente
    restaurant = RestaurantSerializer()  # Información del restaurante

    class Meta:
        model = Review
        fields = ['id', 'client', 'restaurant', 'order', 'rating', 'comment']

class DeliverySerializer(serializers.ModelSerializer):
    order = OrderSerializer()  # Información del pedido
    driver = DriverSerializer()  # Información del conductor

    class Meta:
        model = Delivery
        fields = ['id', 'order', 'driver', 'delivery_date', 'delivery_time', 'delivery_status']


