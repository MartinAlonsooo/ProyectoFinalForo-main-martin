from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator



from .models import (
    Proveedor, SolicitudContacto, ProductoServicio, 
    Promocion
)
from .forms import (
    ProveedorForm, LoginProveedorForm, 
   SolicitudContactoForm, ProductoServicioForm,
    PromocionForm, ConfiguracionForm, BusquedaProveedorForm
)


# ============================================================================
# DECORADOR PARA REQUERIR LOGIN
# ============================================================================

def proveedor_login_required(view_func):
    """Decorador para requerir login de proveedor"""
    def wrapper(request, *args, **kwargs):
        proveedor_id = request.session.get('proveedor_id')
        if not proveedor_id:
            messages.warning(request, 'Debes iniciar sesión primero.')
            return redirect('proveedores:login')
        
        try:
            proveedor = Proveedor.objects.get(id=proveedor_id, activo=True)
            request.proveedor = proveedor
        except Proveedor.DoesNotExist:
            messages.error(request, 'Proveedor no encontrado.')
            return redirect('proveedores:login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# AUTENTICACIÓN
# ============================================================================

def registro_proveedor(request):
    """Registro de nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                proveedor = form.save(commit=False)
                # Hashear la contraseña
                proveedor.password = make_password(form.cleaned_data['password'])
                proveedor.save()
                form.save_m2m()  # Guardar relaciones many-to-many (categorías)
                
                messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
                return redirect('proveedores:login')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
                print(f"Error al guardar proveedor: {e}")
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            print("Errores del formulario:", form.errors)
    else:
        form = ProveedorForm()
    
    return render(request, 'proveedores/registro.html', {'form': form})


def login_proveedor(request):
    """Login de proveedores"""
    if request.method == 'POST':
        form = LoginProveedorForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember_me', False)
            
            try:
                proveedor = Proveedor.objects.get(email=email, activo=True)
                if check_password(password, proveedor.password):
                    # Guardar proveedor en sesión
                    request.session['proveedor_id'] = proveedor.id
                    request.session['proveedor_email'] = proveedor.email
                    request.session['proveedor_nombre'] = proveedor.nombre_empresa
                    
                    # Configurar duración de sesión
                    if not remember:
                        request.session.set_expiry(0)  # Cerrar al cerrar navegador
                    else:
                        request.session.set_expiry(1209600)  # 2 semanas
                    
                    messages.success(request, f'¡Bienvenido {proveedor.nombre_empresa}!')
                    return redirect('proveedores:perfil')
                else:
                    messages.error(request, 'Email o contraseña incorrectos.')
            except Proveedor.DoesNotExist:
                messages.error(request, 'Email o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = LoginProveedorForm()
    
    return render(request, 'proveedores/login.html', {'form': form})


def logout_proveedor(request):
    """Cerrar sesión del proveedor"""
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('proveedores:login')


# ============================================================================
# PERFIL Y CONFIGURACIÓN
# ============================================================================

@proveedor_login_required
def perfil_proveedor(request):
    """Perfil del proveedor logueado"""
    proveedor = request.proveedor

    # Obtener productos, promociones y solicitudes (limitados para mostrar)
    productos = ProductoServicio.objects.filter(proveedor=proveedor, activo=True)[:6]
    promociones = Promocion.objects.filter(proveedor=proveedor, activo=True)[:3]
    solicitudes_pendientes = SolicitudContacto.objects.filter(
        proveedor=proveedor, 
        estado='pendiente'
    ).count()
    
    # Contar totales
    total_productos = ProductoServicio.objects.filter(proveedor=proveedor, activo=True).count()
    total_promociones = Promocion.objects.filter(proveedor=proveedor, activo=True).count()
    total_solicitudes = SolicitudContacto.objects.filter(proveedor=proveedor).count()
    
    context = {
        'proveedor': proveedor,
        'productos': productos,
        'promociones': promociones,
        'solicitudes_pendientes': solicitudes_pendientes,
        'total_productos': total_productos,
        'total_promociones': total_promociones,
        'total_solicitudes': total_solicitudes,
    }
    
    return render(request, 'proveedores/perfil.html', context)


@proveedor_login_required
def editar_perfil(request):
    """Editar información del perfil"""
    proveedor = request.proveedor
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, request.FILES, instance=proveedor)
        
        if form.is_valid():
            proveedor_updated = form.save(commit=False)
            
            # Si se cambió la contraseña, hashearla
            if form.cleaned_data.get('password'):
                proveedor_updated.password = make_password(form.cleaned_data['password'])
            
            proveedor_updated.save()
            form.save_m2m()
            
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('proveedores:perfil')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ProveedorForm(instance=proveedor)
        # No requerir contraseña en edición
        form.fields['password'].required = False
        form.fields['password_confirm'].required = False
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/editar_perfil.html', context)


@proveedor_login_required
def configuracion_proveedor(request):
    """Configuración de cuenta del proveedor"""
    proveedor = request.proveedor
    
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=proveedor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente.')
            return redirect('proveedores:configuracion')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ConfiguracionForm(instance=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/configuracion.html', context)


@proveedor_login_required
def cambiar_password(request):
    """Cambiar contraseña del proveedor"""
    proveedor = request.proveedor
    
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, proveedor=proveedor)
        
        if form.is_valid():
            nueva_password = form.cleaned_data['password_nueva']
            proveedor.password = make_password(nueva_password)
            proveedor.save(update_fields=['password'])
            
            messages.success(request, '¡Contraseña actualizada correctamente!')
            return redirect('proveedores:configuracion')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ConfiguracionForm(proveedor=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/cambiar_password.html', context)


# ============================================================================
# PRODUCTOS Y SERVICIOS
# ============================================================================

@proveedor_login_required
def lista_productos(request):
    """Lista de productos del proveedor con filtros"""
    proveedor = request.proveedor
    productos = ProductoServicio.objects.filter(proveedor=proveedor)
    
    # Aplicar filtros
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categorias=categoria)
    
    estado = request.GET.get('estado')
    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)
    
    buscar = request.GET.get('buscar')
    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) | 
            Q(descripcion__icontains=buscar)
        )
    
    # Ordenar por fecha de creación descendente
    productos = productos.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(productos, 12)
    page = request.GET.get('page')
    productos_paginados = paginator.get_page(page)
    
    context = {
        'proveedor': proveedor,
        'productos': productos_paginados,
        # Mantener valores de filtros en el formulario
        'categoria_actual': categoria,
        'estado_actual': estado,
        'buscar_actual': buscar,
    }
    
    return render(request, 'proveedores/productos/lista.html', context)


@proveedor_login_required
def crear_producto(request):
    """Crear nuevo producto/servicio"""
    proveedor = request.proveedor
    
    if request.method == 'POST':
        form = ProductoServicioForm(request.POST, request.FILES, proveedor=proveedor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('proveedores:lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ProductoServicioForm(proveedor=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/productos/crear.html', context)


@proveedor_login_required
def editar_producto(request, pk):
    """Editar producto/servicio"""
    proveedor = request.proveedor
    producto = get_object_or_404(ProductoServicio, pk=pk, proveedor=proveedor)
    
    if request.method == 'POST':
        form = ProductoServicioForm(request.POST, request.FILES, instance=producto, proveedor=proveedor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('proveedores:lista_productos')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ProductoServicioForm(instance=producto, proveedor=proveedor)
    
    context = {
        'form': form,
        'producto': producto,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/productos/editar.html', context)


@proveedor_login_required
def eliminar_producto(request, pk):
    """Eliminar producto/servicio"""
    proveedor = request.proveedor
    producto = get_object_or_404(ProductoServicio, pk=pk, proveedor=proveedor)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('proveedores:lista_productos')
    
    context = {
        'producto': producto,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/productos/eliminar.html', context)


# ============================================================================
# PROMOCIONES
# ============================================================================

@proveedor_login_required
def lista_promociones(request):
    """Lista de promociones del proveedor con filtros y paginación"""
    proveedor = request.proveedor
    promociones_qs = Promocion.objects.filter(proveedor=proveedor)

    # Obtener filtros desde GET
    estado = request.GET.get('estado', '').strip()        # 'activas' | 'inactivas' | ''
    vigencia = request.GET.get('vigencia', '').strip()    # 'vigentes' | 'programadas' | 'vencidas' | ''
    buscar = request.GET.get('buscar', '').strip()
    fecha_desde = request.GET.get('fecha_desde', '').strip()  # formato 'YYYY-MM-DD'
    fecha_hasta = request.GET.get('fecha_hasta', '').strip()  # formato 'YYYY-MM-DD'

    # Filtrar por estado (activo / inactivo)
    if estado == 'activas':
        promociones_qs = promociones_qs.filter(activo=True)
    elif estado == 'inactivas':
        promociones_qs = promociones_qs.filter(activo=False)

    # Filtrar por vigencia respecto a la fecha actual
    hoy = timezone.now().date()
    if vigencia == 'vigentes':
        promociones_qs = promociones_qs.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy, activo=True)
    elif vigencia == 'programadas':
        promociones_qs = promociones_qs.filter(fecha_inicio__gt=hoy)
    elif vigencia == 'vencidas':
        promociones_qs = promociones_qs.filter(fecha_fin__lt=hoy)

    # Filtrar por texto en título o descripción
    if buscar:
        promociones_qs = promociones_qs.filter(
            Q(titulo__icontains=buscar) | Q(descripcion__icontains=buscar)
        )

    # Filtrar por rango de fechas (si se proporcionan)
    if fecha_desde:
        try:
            fd = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            promociones_qs = promociones_qs.filter(fecha_inicio__gte=fd)
        except ValueError:
            # fecha inválida: ignorar o podrías agregar un mensaje de error
            pass

    if fecha_hasta:
        try:
            fh = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            promociones_qs = promociones_qs.filter(fecha_fin__lte=fh)
        except ValueError:
            pass

    # Ordenar (más reciente primero)
    promociones_qs = promociones_qs.order_by('-fecha_inicio')

    # Paginación (12 por página, ajustar si quieres)
    paginator = Paginator(promociones_qs, 12)
    page = request.GET.get('page')
    promociones = paginator.get_page(page)

    context = {
        'proveedor': proveedor,
        'promociones': promociones,
        # Mantener valores de filtros en el template
        'estado_actual': estado,
        'vigencia_actual': vigencia,
        'buscar_actual': buscar,
        'fecha_desde_actual': fecha_desde,
        'fecha_hasta_actual': fecha_hasta,
    }

    return render(request, 'proveedores/promociones/lista.html', context)

@proveedor_login_required
def crear_promocion(request):
    """Crear nueva promoción"""
    proveedor = request.proveedor
    
    if request.method == 'POST':
        form = PromocionForm(request.POST, request.FILES, proveedor=proveedor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Promoción creada exitosamente.')
            return redirect('proveedores:lista_promociones')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PromocionForm(proveedor=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/promociones/crear.html', context)


@proveedor_login_required
def editar_promocion(request, pk):
    """Editar promoción"""
    proveedor = request.proveedor
    promocion = get_object_or_404(Promocion, pk=pk, proveedor=proveedor)
    
    if request.method == 'POST':
        form = PromocionForm(request.POST, request.FILES, instance=promocion, proveedor=proveedor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Promoción actualizada exitosamente.')
            return redirect('proveedores:lista_promociones')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PromocionForm(instance=promocion, proveedor=proveedor)
    
    context = {
        'form': form,
        'promocion': promocion,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/promociones/editar.html', context)


@proveedor_login_required
def eliminar_promocion(request, pk):
    """Eliminar promoción"""
    proveedor = request.proveedor
    promocion = get_object_or_404(Promocion, pk=pk, proveedor=proveedor)
    
    if request.method == 'POST':
        promocion.delete()
        messages.success(request, 'Promoción eliminada exitosamente.')
        return redirect('proveedores:lista_promociones')
    
    context = {
        'promocion': promocion,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/promociones/eliminar.html', context)


# ============================================================================
# SOLICITUDES DE CONTACTO
# ============================================================================

@proveedor_login_required
def lista_solicitudes(request):
    """Lista de solicitudes de contacto recibidas"""
    proveedor = request.proveedor
    
    # Filtrar por estado si se proporciona
    estado = request.GET.get('estado', 'todas')
    
    if estado == 'todas':
        solicitudes = SolicitudContacto.objects.filter(proveedor=proveedor)
    else:
        solicitudes = SolicitudContacto.objects.filter(proveedor=proveedor, estado=estado)
    
    solicitudes = solicitudes.order_by('-fecha_solicitud')
    
    # Paginación
    paginator = Paginator(solicitudes, 10)
    page = request.GET.get('page')
    solicitudes_paginadas = paginator.get_page(page)
    
    context = {
        'proveedor': proveedor,
        'solicitudes': solicitudes_paginadas,
        'estado_actual': estado
    }
    
    return render(request, 'proveedores/solicitudes/mis_solicitudes.html', context)


@proveedor_login_required
def responder_solicitud(request, pk, accion):
    """Aceptar o rechazar una solicitud de contacto"""
    proveedor = request.proveedor
    solicitud = get_object_or_404(SolicitudContacto, pk=pk, proveedor=proveedor)
    
    if accion == 'aceptar':
        solicitud.aceptar()
        messages.success(request, 'Solicitud aceptada.')
    elif accion == 'rechazar':
        solicitud.rechazar()
        messages.success(request, 'Solicitud rechazada.')
    else:
        messages.error(request, 'Acción no válida.')
    
    return redirect('proveedores:lista_solicitudes')


# ============================================================================
# BÚSQUEDA Y LISTADO PÚBLICO
# ============================================================================

def buscar_proveedores(request):
    """Búsqueda pública de proveedores"""
    form = BusquedaProveedorForm(request.GET)
    proveedores = Proveedor.objects.filter(activo=True, perfil_publico=True)
    
    if form.is_valid():
        # Búsqueda por texto
        busqueda = form.cleaned_data.get('busqueda')
        if busqueda:
            proveedores = proveedores.filter(
                Q(nombre_empresa__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )
        
        # Filtro por categoría
        categoria = form.cleaned_data.get('categoria')
        if categoria:
            proveedores = proveedores.filter(categorias=categoria)
        
        # Filtro por región
        region = form.cleaned_data.get('region')
        if region:
            proveedores = proveedores.filter(region=region)
        
        # Filtro por cobertura
        cobertura = form.cleaned_data.get('cobertura')
        if cobertura:
            proveedores = proveedores.filter(cobertura=cobertura)
    
    # Paginación
    paginator = Paginator(proveedores, 12)
    page = request.GET.get('page')
    proveedores_paginados = paginator.get_page(page)
    
    context = {
        'form': form,
        'proveedores': proveedores_paginados
    }
    
    return render(request, 'proveedores/buscar.html', context)


def detalle_proveedor_publico(request, pk):
    """Detalle público de un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk, activo=True, perfil_publico=True)
    
    # Obtener productos y promociones activas
    productos = ProductoServicio.objects.filter(proveedor=proveedor, activo=True)[:12]
    promociones_vigentes = Promocion.objects.filter(
        proveedor=proveedor,
        activo=True,
        fecha_inicio__lte=timezone.now().date(),
        fecha_fin__gte=timezone.now().date()
    )
    
    context = {
        'proveedor': proveedor,
        'productos': productos,
        'promociones': promociones_vigentes
    }
    
    return render(request, 'proveedores/detalle.html', context)


def enviar_solicitud_contacto(request, pk):
    """Enviar solicitud de contacto a un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk, activo=True)
    
    if request.method == 'POST':
        form = SolicitudContactoForm(request.POST, proveedor=proveedor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitud enviada exitosamente.')
            return redirect('proveedores:detalle_publico', pk=pk)
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = SolicitudContactoForm(proveedor=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor
    }
    
    return render(request, 'proveedores/solicitudes/enviar.html', context)


