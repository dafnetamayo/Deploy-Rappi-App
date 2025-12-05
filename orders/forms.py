from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Order


class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        min_length=8,
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
        help_text='Ingresa la misma contraseña para verificación.'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_',
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')
        return password_confirm
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CheckoutForm(forms.Form):
    delivery_address = forms.CharField(
        label='Dirección de entrega',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#004270]',
            'rows': 3,
            'placeholder': 'Ingresa la dirección completa de entrega',
            'required': True
        }),
        help_text='Por favor ingresa la dirección completa incluyendo calles, número, colonia, código postal y referencias.'
    )
    
    payment_method = forms.ChoiceField(
        label='Método de pago',
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'mt-1',
        }),
        initial='cash'
    )
    
    comments = forms.CharField(
        label='Instrucciones adicionales (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#004270]',
            'rows': 2,
            'placeholder': 'Ej: Llamar antes de llegar, timbre azul, etc.'
        })
    )

