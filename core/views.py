# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError


def index(request):
    """
    Vista principal - Landing page de Club Almacén
    """
    # Si el usuario ya está autenticado, redirigir según su tipo
    if request.user.is_authenticated:
        # Si es staff/admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('core:admin_dashboard')
        
        # Si es proveedor
        try:
            if hasattr(request.user, 'proveedor_perfil'):
                return redirect('proveedores:dashboard_proveedor')
        except:
            pass
        
        # Si es comerciante (usuario regular)
        return redirect('core:comerciante_dashboard')
    
    return render(request, 'core/index.html')


def register_view(request):
    """
    Vista de registro para nuevos comerciantes
    """
    if request.user.is_authenticated:
        return redirect('core:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validaciones
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'core/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'core/register.html')
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'core/register.html')
        
        try:
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('core:login')
            
        except IntegrityError:
            messages.error(request, 'El nombre de usuario o email ya está en uso.')
            return render(request, 'core/register.html')
    
    return render(request, 'core/register.html')


def login_view(request):
    """
    Vista de inicio de sesión
    """
    if request.user.is_authenticated:
        return redirect('usuarios:plataforma_comerciante')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor completa todos los campos.')
            return render(request, 'core/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name or user.username}!')
            
            # Redirigir según el tipo de usuario
            if user.is_staff or user.is_superuser:
                return redirect('core:admin_dashboard')
            
            try:
                if hasattr(user, 'proveedor_perfil'):
                    return redirect('proveedores:dashboard_proveedor')
            except:
                pass
            
            return redirect('core:comerciante_dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'core/login.html')
    
    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:index')


def admin_login_view(request):
    """
    Vista de login específica para administradores
    Redirige al admin de Django
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('/admin/')
    
    # Redirigir al admin de Django que tiene su propio sistema de login
    return redirect('/admin/')


@login_required
def dashboard_comerciante(request):
    """
    Dashboard principal para comerciantes
    """
    context = {
        'user': request.user,
    }
    return render(request, 'usuarios/plataforma_comerciante.html', context)


@login_required
def admin_dashboard(request):
    """
    Dashboard para administradores
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')
    
    context = {
        'total_usuarios': User.objects.count(),
        'usuarios_activos': User.objects.filter(is_active=True).count(),
    }
    return render(request, 'core/admin_dashboard.html', context)


# Vistas de información estática
def quienes_somos(request):
    """Vista de Quiénes Somos"""
    return render(request, 'core/quienes_somos.html')


def beneficios(request):
    """Vista de Beneficios"""
    return render(request, 'core/beneficios.html')


def contacto(request):
    """Vista de Contacto"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        
        # Aquí podrías enviar un email o guardar en base de datos
        messages.success(request, '¡Mensaje enviado! Te contactaremos pronto.')
        return redirect('core:contacto')
    
    return render(request, 'core/contacto.html')
