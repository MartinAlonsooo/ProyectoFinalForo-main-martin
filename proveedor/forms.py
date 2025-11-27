# proveedores/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Proveedor, SolicitudContacto, ProductoServicio, Promocion


class ProveedorForm(forms.ModelForm):
    """Formulario para registro y edición de proveedores"""
    
    # Campos de contraseña (no están en el modelo directamente como form fields)
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña'
    )
    
    password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar Contraseña'
        }),
        label='Confirmar Contraseña'
    )
    
    class Meta:
        model = Proveedor
        fields = [
            'nombre_empresa',
            'email',
            'cobertura',
            'whatsapp',
            'descripcion',
            'foto_empresa',
            'paises',
            'regiones',
            'comunas',
            'direccion',
            'categorias',
        ]
        
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Distribuidora El Sol'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
            'cobertura': forms.Select(attrs={
                'class': 'form-control'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56912345678'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu negocio y los productos que ofreces...'
            }),
            'foto_empresa': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'paises': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_paises'
            }),
            'regiones': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_regiones'
            }),
            'comunas': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_comunas'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle 123, Depto 456'
            }),
            'categorias': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
        labels = {
            'nombre_empresa': 'Nombre de la Empresa',
            'email': 'Correo Electrónico',
            'cobertura': 'Zona de Cobertura',
            'whatsapp': 'WhatsApp',
            'descripcion': 'Descripción del Negocio',
            'foto_empresa': 'Foto de la Empresa',
            'paises': 'País',
            'regiones': 'Región',
            'comunas': 'Comuna',
            'direccion': 'Dirección',
            'categorias': 'Categoría de Productos',
        }
        
        help_texts = {
            'email': 'Este será tu usuario para iniciar sesión',
            'whatsapp': 'Formato: +56912345678',
            'descripcion': 'Describe qué productos ofreces y qué te hace especial',
            'foto_empresa': 'Imagen JPG, PNG o GIF (máx. 5MB)',
            'categorias': 'Selecciona la categoría principal de tu negocio',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es un nuevo proveedor, hacer contraseñas requeridas
        if not self.instance.pk:
            self.fields['password'].required = True
            self.fields['password_confirm'].required = True
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        
        # Si es edición, excluir el email del proveedor actual
        if self.instance.pk:
            if Proveedor.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este correo ya está registrado.')
        else:
            if Proveedor.objects.filter(email=email).exists():
                raise ValidationError('Este correo ya está registrado.')
        
        return email
    
    def clean(self):
        """Validaciones generales"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        # Validar contraseñas solo si se están estableciendo
        if password or password_confirm:
            if password != password_confirm:
                raise ValidationError({
                    'password_confirm': 'Las contraseñas no coinciden.'
                })
            
            if len(password) < 6:
                raise ValidationError({
                    'password': 'La contraseña debe tener al menos 6 caracteres.'
                })
        
        return cleaned_data


class LoginProveedorForm(forms.Form):
    """Formulario simple de login"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        }),
        label='Correo Electrónico'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        }),
        label='Contraseña'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )


class ConfiguracionForm(forms.ModelForm):
    """Formulario para configuración del perfil del proveedor"""
    
    class Meta:
        model = Proveedor
        fields = [
            'modo_oscuro',
            'notif_email',
            'notif_mensajes',
            'notif_pedidos',
            'idioma',
            'zona_horaria',
            'perfil_publico',
            'mostrar_estadisticas',
        ]
        
        widgets = {
            'modo_oscuro': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notif_email': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notif_mensajes': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notif_pedidos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'idioma': forms.Select(attrs={
                'class': 'form-control'
            }),
            'zona_horaria': forms.Select(attrs={
                'class': 'form-control'
            }),
            'perfil_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_estadisticas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class SolicitudContactoForm(forms.ModelForm):
    class Meta:
        model = SolicitudContacto
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribe tu mensaje de presentación...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer el proveedor del kwargs
        self.proveedor = kwargs.pop('proveedor', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar el proveedor si está disponible
        if self.proveedor:
            instance.proveedor = self.proveedor
        
        if commit:
            instance.save()
        
        return instance


class ProductoServicioForm(forms.ModelForm):
    class Meta:
        model = ProductoServicio
        fields = [
            'nombre', 'descripcion', 'categorias', 
            'precio_referencia', 'imagen', 'activo', 'destacado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto o servicio'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe tu producto o servicio'
            }),
            'categorias': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio_referencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'destacado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer el proveedor del kwargs
        self.proveedor = kwargs.pop('proveedor', None)
        super().__init__(*args, **kwargs)
        
        # Hacer campos opcionales si es necesario
        self.fields['precio_referencia'].required = False
        self.fields['imagen'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar el proveedor si está disponible
        if self.proveedor:
            instance.proveedor = self.proveedor
        
        if commit:
            instance.save()
        
        return instance

class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = [
            'titulo', 'descripcion', 'imagen',
            'fecha_inicio', 'fecha_fin', 'activo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la promoción'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe la promoción'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extraer el proveedor del kwargs
        self.proveedor = kwargs.pop('proveedor', None)
        super().__init__(*args, **kwargs)
        
        # Hacer imagen opcional
        self.fields['imagen'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar el proveedor si está disponible
        if self.proveedor:
            instance.proveedor = self.proveedor
        
        if commit:
            instance.save()
        
        return instance
    
class BusquedaProveedorForm(forms.Form):
    """Formulario de búsqueda de proveedores"""
    
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o descripción...'
        }),
        label='Búsqueda'
    )
    
    categoria = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las categorías')] + list(Proveedor.CATEGORIAS_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Categoría'
    )
    
    region = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las regiones')] + list(Proveedor.REGION_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Región'
    )
    
    cobertura = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las coberturas')] + list(Proveedor.COBERTURA_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Cobertura'
    )