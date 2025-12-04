from django.db import models

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=20)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    rating = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"

class Product(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=20)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('cash', 'Cash'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_date = models.DateTimeField()
    delivery_address = models.CharField(max_length=300)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES)
    comments = models.TextField()
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')

    def __str__(self):
        return f"Order {self.id} - {self.client.name}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

class Driver(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

class Delivery(models.Model):

    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    delivery_date = models.DateTimeField()
    delivery_time = models.TimeField()
    delivery_status = models.CharField(max_length=30, choices=DELIVERY_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Delivery {self.id} - {self.order.id}"

    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"

class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=1, decimal_places=0)
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} - {self.restaurant.name}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"


