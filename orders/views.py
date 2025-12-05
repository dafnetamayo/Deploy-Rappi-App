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
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.html import strip_tags
import hashlib
from .forms import RegistroForm, CheckoutForm

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

def _generate_verification_token(user):
    """Generate a verification token for a user"""
    # Create a token based on user id, email, and secret key
    # This allows us to verify the token without storing it
    token_string = f"{user.id}{user.email}{settings.SECRET_KEY}"
    token = hashlib.sha256(token_string.encode()).hexdigest()
    return token

def _verify_token(user, token):
    """Verify if the provided token is valid for the user"""
    expected_token = _generate_verification_token(user)
    return token == expected_token

def send_order_confirmation_email(order, user):
    """Send order confirmation email to the user"""
    try:
        # Get order items with calculated subtotals
        order_items = []
        for item in order.items.select_related('product').all():
            order_items.append({
                'product': item.product,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.unit_price * item.quantity,
            })
        
        # Prepare context for email template
        context = {
            'order': order,
            'user': user,
            'order_items': order_items,
            'restaurant': order.restaurant,
            'delivery': order.delivery if hasattr(order, 'delivery') else None,
        }
        
        # Render HTML email template
        html_message = render_to_string('email/order_confirmation.html', context)
        
        # Create plain text version
        plain_message = f"""
Hola {user.get_full_name() or user.username},

Gracias por tu pedido en RAPPITESO.

Detalles del pedido:
Número de pedido: #{order.id}
Restaurante: {order.restaurant.name}
Fecha: {order.creation_date.strftime('%d/%m/%Y %H:%M')}
Estado: {order.get_status_display()}

Productos:
"""
        for item in order_items:
            plain_message += f"- {item['product'].name} x{item['quantity']} - ${item['subtotal']:.2f}\n"
        
        plain_message += f"""
Total: ${order.total:.2f}

Dirección de entrega: {order.delivery_address}
Método de pago: {order.get_payment_method_display()}
"""
        if order.comments:
            plain_message += f"Comentarios: {order.comments}\n"
        
        if context['delivery']:
            plain_message += f"\nConductor asignado: {context['delivery'].driver.name}\n"
        
        plain_message += """
Gracias por elegir RAPPITESO!

El equipo de RAPPITESO
        """
        
        # Send email
        subject = f'Confirmación de Pedido #{order.id} - RAPPITESO'
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        return True
    except Exception as e:
        # Log the error but don't break the order creation process
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error sending order confirmation email: {str(e)}')
        return False

def registro(request):
    if request.user.is_authenticated:
        return redirect('perfil')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set user as inactive until email is verified
            user.is_active = False
            user.save()
            
            # Generate verification token
            verification_token = _generate_verification_token(user)
            
            # Create verification link
            verification_url = request.build_absolute_uri(
                f'/activate/{user.id}/{verification_token}/'
            )
            
            # Send verification email
            try:
                send_mail(
                    subject='Verifica tu cuenta en RAPPITESO',
                    message=f'''
Hola {user.get_full_name() or user.username},

Gracias por registrarte en RAPPITESO.

Por favor, verifica tu cuenta haciendo clic en el siguiente enlace:
{verification_url}

Si no creaste esta cuenta, puedes ignorar este mensaje.

Saludos,
El equipo de RAPPITESO
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(
                    request, 
                    '¡Cuenta creada exitosamente! Por favor revisa tu correo electrónico para verificar tu cuenta antes de iniciar sesión.'
                )
            except Exception as e:
                # If email fails, still create the account but warn the user
                messages.warning(
                    request,
                    f'Cuenta creada, pero hubo un problema al enviar el email de verificación: {str(e)}. '
                    'Por favor contacta al administrador.'
                )
                # In development, you might want to activate the user anyway
                if settings.DEBUG:
                    user.is_active = True
                    user.save()
                    messages.info(request, 'En modo DEBUG: cuenta activada automáticamente.')
            
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
    # Inicializar estadísticas
    total_orders = 0
    pending_orders = 0
    total_spent = 0
    
    # Buscar clientes por email (asumiendo que el email del usuario es único)
    client_email = request.user.email
    
    # Obtener todos los clientes con este email (puede haber múltiples)
    clients = Client.objects.filter(email=client_email)
    
    if clients.exists():
        # Si hay múltiples clientes con el mismo email, tomamos el primero
        # En una implementación real, podrías querer fusionar estos registros
        client = clients.first()
        
        # Obtener todos los pedidos de los clientes con este email
        orders = Order.objects.filter(client__in=clients)
        total_orders = orders.count()
        
        # Contar pedidos pendientes
        pending_orders = orders.filter(status__in=['pending', 'in_progress']).count()
        
        # Calcular el total gastado
        total_spent = sum(order.total for order in orders if order.total)
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_spent': total_spent,
        'client': client if 'client' in locals() else None,
    }
    
    return render(request, 'user/perfil.html', context)


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

def activate_account(request, user_id, token):
    user = get_object_or_404(User, pk=user_id)
    
    # Verify the token
    if not _verify_token(user, token):
        messages.error(request, 'El enlace de verificación no es válido o ha expirado.')
        return redirect('login')
    
    # Activate the user if not already active
    if not user.is_active:
        user.is_active = True
        user.save()
        messages.success(request, '¡Tu cuenta ha sido verificada exitosamente! Ahora puedes iniciar sesión.')
    else:
        messages.info(request, 'Tu cuenta ya está verificada.')
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
    total = sum(p.price * qty for p, qty in products)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Get or create Client for this user
            user = request.user
            client, _ = Client.objects.get_or_create(
                name=user.get_full_name() or user.username,
                defaults={
                    'email': user.email or 'no-email@example.com',
                    'address': form.cleaned_data['delivery_address'],
                    'phone_number': '',
                }
            )
            
            # Update client address if it's different
            if client.address != form.cleaned_data['delivery_address']:
                client.address = form.cleaned_data['delivery_address']
                client.save()

            # Create the order
            order = Order.objects.create(
                client=client,
                restaurant=restaurant,
                status='pending',
                total=total,
                delivery_date=timezone.now(),
                delivery_address=form.cleaned_data['delivery_address'],
                payment_method=form.cleaned_data['payment_method'],
                comments=form.cleaned_data['comments'],
            )
            
            # Create OrderItems
            for p, qty in products:
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=qty,
                    unit_price=p.price,
                )
            
            # Asignar conductor automáticamente
            try:
                # Buscar el conductor con menos entregas pendientes
                driver = Driver.objects.filter(availability=True)
                if not driver.exists():
                    # Si no hay conductores disponibles, buscar cualquier conductor
                    driver = Driver.objects.first()
                    if driver is None:
                        # Si no hay conductores en el sistema, crear uno de emergencia
                        driver = Driver.objects.create(
                            name='Conductor de Emergencia',
                            email='emergencia@example.com',
                            phone_number='555-0000',
                            vehicle_type='Moto',
                            availability=True
                        )
                        messages.warning(request, 'Se ha creado un conductor de emergencia para tu pedido.')
                else:
                    # Seleccionar el conductor con menos entregas pendientes
                    driver = min(
                        driver,
                        key=lambda d: Delivery.objects.filter(
                            driver=d, 
                            delivery_status__in=['pending', 'in_transit']
                        ).count()
                    )
                
                # Crear la entrega
                delivery = Delivery.objects.create(
                    order=order,
                    driver=driver,
                    delivery_date=timezone.now(),
                    delivery_time=timezone.now().time(),
                    delivery_status='pending',
                )
                
                # Send order confirmation email
                if user.email:
                    email_sent = send_order_confirmation_email(order, user)
                    if not email_sent:
                        # Log warning but don't break the flow
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f'Could not send order confirmation email for order #{order.id}')
                
                messages.success(request, f'Pedido #{order.id} creado exitosamente. Conductor asignado: {driver.name}.')
                if user.email:
                    messages.info(request, 'Se ha enviado un correo de confirmación a tu email.')
                
                # Clear cart
                request.session['cart'] = {}
                return redirect('checkout_success', order_id=order.id)
                
            except Exception as e:
                # En caso de error, registrar y notificar
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error asignando conductor al pedido {order.id}: {str(e)}')
                messages.error(request, 'Hubo un error al procesar tu pedido. Por favor intenta de nuevo.')
                order.delete()  # Eliminar el pedido si hay un error
                return redirect('view_cart')
    else:
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'client'):
            initial_data['delivery_address'] = request.user.client.address
            initial_data['payment_method'] = 'cash'
        form = CheckoutForm(initial=initial_data)
    
    # Preparar la lista de productos con sus cantidades
    product_list = [(p, qty) for p, qty in products]
    
    context = {
        'form': form,
        'products': [p for p, _ in products],
        'product_list': product_list,  # Lista de tuplas (producto, cantidad)
        'total': total,
        'restaurant': restaurant,
    }
    return render(request, 'checkout_form.html', context)

    # Create OrderItems
    for p, qty in products:
        OrderItem.objects.create(
            order=order,
            product=p,
            quantity=qty,
            unit_price=p.price,
        )

    # Asignar conductor automáticamente
    try:
        # Buscar el conductor con menos entregas pendientes
        driver = Driver.objects.filter(availability=True)
        if not driver.exists():
            # Si no hay conductores disponibles, buscar cualquier conductor
            driver = Driver.objects.first()
            if driver is None:
                # Si no hay conductores en el sistema, crear uno de emergencia
                driver = Driver.objects.create(
                    name='Conductor de Emergencia',
                    email='emergencia@example.com',
                    phone_number='555-0000',
                    vehicle_type='Moto',
                    availability=True
                )
                messages.warning(request, 'Se ha creado un conductor de emergencia para tu pedido.')
        else:
            # Seleccionar el conductor con menos entregas pendientes
            driver = min(
                driver,
                key=lambda d: Delivery.objects.filter(
                    driver=d, 
                    delivery_status__in=['pending', 'in_transit']
                ).count()
            )
        
        # Crear la entrega
        delivery = Delivery.objects.create(
            order=order,
            driver=driver,
            delivery_date=timezone.now(),
            delivery_time=timezone.now().time(),
            delivery_status='pending',  # Cambiado a 'pending' en lugar de 'in_transit'
        )
        
        # Actualizar el estado del pedido
        order.status = 'in_progress'
        order.save()
        
        messages.success(request, f'Pedido #{order.id} creado exitosamente. Conductor asignado: {driver.name}.')
        
    except Exception as e:
        # En caso de error, registrar y notificar
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error asignando conductor al pedido {order.id}: {str(e)}')
        messages.error(request, 'Hubo un error al asignar un conductor. Por favor contacta al soporte.')

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