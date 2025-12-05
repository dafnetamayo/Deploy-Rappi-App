from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    # Mis pedidos (de la sesión actual)
    path('orders/', views.my_orders, name='order_list'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('activate/<int:user_id>/<str:token>/', views.activate_account, name='activate_account'),
    # Carrito por sesión
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/inc/<int:product_id>/', views.increment_cart, name='increment_cart'),
    path('cart/dec/<int:product_id>/', views.decrement_cart, name='decrement_cart'),
    path('cart/set/<int:product_id>/', views.set_cart_quantity, name='set_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/<int:order_id>/', views.checkout_success, name='checkout_success'),
]
