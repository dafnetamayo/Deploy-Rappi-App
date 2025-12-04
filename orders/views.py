from django.shortcuts import get_object_or_404, redirect
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm
from django.utils import timezone

from .models import (
    Product,
    Order,
    Restaurant,
    Client,
    Driver,
    Review,
    Delivery,
    OrderItem,
)
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    RestaurantSerializer,
    ClientSerializer,
    DriverSerializer,
    ReviewSerializer,
    DeliverySerializer,
)

def registro(request):
    if request.user.is_authenticated:
        return redirect('perfil')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True  # Changed to True so users can login immediately
            user.save()
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'user/registro_page.html', {'form': form})


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('perfil')
    
    # Check if Google login is available (allauth not configured, so always False)
    google_provider_enabled = False

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                welcome_name = user.get_full_name() if user.get_full_name() else user.username
                messages.success(request, f'¡Bienvenido, {welcome_name}!')
                return redirect('perfil')
            else:
                messages.error(request, 'Tu cuenta está inactiva. Por favor contacta al administrador.')
        else:
            messages.error(request, 'Credenciales incorrectas')
        return render(request, 'user/login_page.html', {'google_provider_enabled': google_provider_enabled})
    
    return render(request, 'user/login_page.html', {'google_provider_enabled': google_provider_enabled})


@login_required
def perfil(request):
    return render(request, 'user/perfil.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('home')


def index(request):
    # Show up to 20 restaurants on the home page
    restaurants = Restaurant.objects.all().order_by('-rating')[:20]
    return render(request, 'index.html', {'restaurants': restaurants})


def restaurant_list(request):
    """Display a list of all restaurants"""
    restaurants = Restaurant.objects.all().order_by('-rating')
    return render(request, 'restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, restaurant_id):
    """Display a restaurant menu (products)"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    products = Product.objects.filter(restaurant=restaurant, availability=True).order_by('name')
    return render(request, 'restaurant_detail.html', {
        'restaurant': restaurant,
        'products': products,
    })


def order_list(request):
    """Display a list of all orders"""
    orders = Order.objects.all().order_by('-creation_date')
    return render(request, 'order_list.html', {'orders': orders})


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'restaurant', 'status', 'total']
    search_fields = ['client__name', 'restaurant__name']
    ordering_fields = ['creation_date', 'status', 'total']
    ordering = ['-creation_date']

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['restaurant', 'availability']
    search_fields = ['name']
    ordering_fields = ['price', 'availability']
    ordering = ['-price']
    
class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for Restaurant model"""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'opening_time', 'closing_time']
    search_fields = ['name']
    ordering_fields = ['rating', 'opening_time', 'closing_time']
    ordering = ['-rating']

class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet for Client model"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'email', 'registration_date']
    search_fields = ['name', 'email']
    ordering_fields = ['registration_date']
    ordering = ['-registration_date']
    

class DriverViewSet(viewsets.ModelViewSet):
    """ViewSet for Driver model"""
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'email', 'availability']
    search_fields = ['name', 'email']
    ordering_fields = ['availability']
    ordering = ['-availability']
    
class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'restaurant', 'order', 'rating']
    search_fields = ['comment']
    ordering_fields = ['creation_date', 'rating']
    ordering = ['-creation_date']
    
class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for Delivery model"""
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order', 'driver', 'delivery_date', 'delivery_time', 'delivery_status']
    search_fields = ['order__client__name', 'driver__name']
    ordering_fields = ['delivery_date', 'delivery_time', 'delivery_status']
    ordering = ['-delivery_date']

def activate_account(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    return redirect('login')

def _get_cart(request):
    cart = request.session.get('cart', {})
    return cart


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = _get_cart(request)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"Agregado al carrito: {product.name}")
    return redirect('view_cart')


def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session['cart'] = cart
        messages.info(request, "Producto removido del carrito")
    return redirect('view_cart')


def view_cart(request):
    cart = _get_cart(request)
    items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        subtotal = product.price * qty
        total += subtotal
        items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal,
        })
    return render(request, 'cart.html', {'items': items, 'total': total})


def increment_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = _get_cart(request)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"Se aumentó la cantidad de {product.name}")
    return redirect('view_cart')


def decrement_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        cart[pid] = max(0, cart[pid] - 1)
        if cart[pid] == 0:
            del cart[pid]
            messages.info(request, f"{product.name} removido del carrito")
        else:
            messages.success(request, f"Se redujo la cantidad de {product.name}")
        request.session['cart'] = cart
    return redirect('view_cart')


def set_cart_quantity(request, product_id):
    if request.method != 'POST':
        return redirect('view_cart')
    product = get_object_or_404(Product, pk=product_id)
    try:
        qty = int(request.POST.get('quantity', '1'))
    except ValueError:
        qty = 1
    qty = max(0, qty)
    cart = _get_cart(request)
    pid = str(product_id)
    if qty == 0:
        cart.pop(pid, None)
        messages.info(request, f"{product.name} removido del carrito")
    else:
        cart[pid] = qty
        messages.success(request, f"Cantidad de {product.name} actualizada a {qty}")
    request.session['cart'] = cart
    return redirect('view_cart')


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('view_cart')

    # Build order data
    products = []
    for pid, qty in cart.items():
        product = get_object_or_404(Product, pk=int(pid))
        products.append((product, qty))

    # Choose restaurant from first product
    restaurant = products[0][0].restaurant

    # Get or create Client for this user
    user = request.user
    client, _ = Client.objects.get_or_create(
        name=user.get_full_name() or user.username,
        defaults={
            'email': user.email or 'no-email@example.com',
            'address': '',
            'phone_number': '',
        }
    )

    # Compute total
    total = sum(p.price * qty for p, qty in products)

    order = Order.objects.create(
        client=client,
        restaurant=restaurant,
        status='in_progress',
        total=total,
        delivery_date=timezone.now(),
        delivery_address='No especificada',
        payment_method='cash',
        comments='',
    )

    # Create OrderItems
    for p, qty in products:
        OrderItem.objects.create(
            order=order,
            product=p,
            quantity=qty,
            unit_price=p.price,
        )

    # Assign available driver and create delivery
    driver = Driver.objects.filter(availability=True).first()
    if driver is None:
        # fallback: create a placeholder driver
        driver = Driver.objects.create(name='Conductor Asignado', email='driver@example.com', phone_number='', vehicle_type='Moto', availability=True)
    Delivery.objects.create(
        order=order,
        driver=driver,
        delivery_date=timezone.now(),
        delivery_time=timezone.now().time(),
        delivery_status='in_transit',
    )

    # Clear cart
    request.session['cart'] = {}
    messages.success(request, f'Pago realizado con éxito. Pedido #{order.id} creado y conductor asignado.')
    return redirect('checkout_success', order_id=order.id)


@login_required
def my_orders(request):
    # Retrieve orders for the implicit Client created for this user
    name_key = request.user.get_full_name() or request.user.username
    orders = Order.objects.filter(client__name=name_key).order_by('-creation_date')
    return render(request, 'order_list.html', {'orders': orders})


@login_required
def checkout_success(request, order_id: int):
    order = get_object_or_404(Order, pk=order_id)
    items = order.items.select_related('product').all()
    delivery = Delivery.objects.filter(order=order).select_related('driver').first()
    return render(request, 'checkout.html', {
        'order': order,
        'items': items,
        'delivery': delivery,
    })