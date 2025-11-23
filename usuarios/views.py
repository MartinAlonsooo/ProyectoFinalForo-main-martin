# usuarios/views.py (CÓDIGO COMPLETO Y FINAL)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password 
from django.core.files.storage import default_storage 
from django.utils import timezone
from django.db.models import Count, Q 
from django.db import IntegrityError 
from datetime import timedelta, date 
from django.contrib.auth.decorators import login_required 
from django.templatetags.static import static 
from django.urls import reverse # Necesario para redireccionar a la nueva app proveedores

# Importamos todos los modelos y opciones
from .models import (
    Comerciante, Post, Like, Comentario, INTERESTS_CHOICES, Beneficio,
    NIVELES, CATEGORIAS, RUBROS_CHOICES, ROLES_CHOICES 
    # Los modelos Proveedor y Propuesta fueron eliminados de este archivo
) 
# Si tu app proveedores tiene un modelo Proveedor, puedes referenciarlo para tipado
# from proveedores.models import Proveedor as NewProveedor 

# Importamos todos los formularios necesarios
from .forms import (
    RegistroComercianteForm,
    LoginForm,
    PostForm,
    ProfilePhotoForm,
    BusinessDataForm,
    ContactInfoForm,
    InterestsForm,
    ComentarioForm 
)

# --- SIMULACIÓN DE ESTADO DE SESIÓN GLOBAL ---
current_logged_in_user = None 
ROLES_DISPLAY = dict(ROLES_CHOICES)

# --- DATOS DE NOTICIAS EXTERNAS (DATASET COMPLETO Y REALISTA) ---
ALL_EXTERNAL_NEWS = [
    {
        'title': "El desafío del comercio local en Chile",
        'snippet': "Una ciudad con comercio local vivo es una ciudad más segura, más diversa y con mejor convivencia.",
        'url': "https://www.nuevopoder.cl/basta-con-guardias-el-desafio-del-comercio-local-en-chile/",
        'source': "La Tercera",
        'theme': "Economía y Ciudad",
        'image_url': static('img/logos/latercera.png')
    },
    {
        'title': "Día de la Madre: 5 tips para que las pymes no colapsen",
        'snippet': "Según cifras de 2023 de la Cámara de Comercio de Santiago, las ventas llegan a su peak el día sábado.",
        'url': "https://comerciante.lacuarta.com/categoria/noticias",
        'source': "Revista Comerciante",
        'theme': "Marketing y Ventas",
        'image_url': static('img/logos/comerciante.png')
    },
    {
        'title': "Fondo Mujeres Por la Equidad 2024 abre sus postulaciones",
        'snippet': "Organizaciones de todo Chile podrán postular proyectos cuyas temáticas aborden el acceso de mujeres a la tecnología.",
        'url': "https://comerciante.lacuarta.com/categoria/noticias",
        'source': "Revista Comerciante",
        'theme': "Ayudas y Subsidios",
        'image_url': static('img/logos/comerciante.png')
    },
    {
        'title': "Utilidades de Ripley caen 40% en el tercer trimestre",
        'snippet': "Análisis de Barclays y Morgan Stanley sobre la caída de utilidades de las grandes tiendas en el sector retail.",
        'url': "https://www.emol.com/movil/economia/index.aspx",
        'source': "Emol",
        'theme': "Retail y Tendencias",
        'image_url': static('img/logos/emol.png')
    },
    {
        'title': "El descontrolado comercio ambulante en Santiago",
        'snippet': "Tras este desorden los asaltos y robos tienen a los locatarios entre la espada y la pared.",
        'url': "https://www.youtube.com/watch?v=80a7qy5SkjA",
        'source': "Canal 13",
        'theme': "Seguridad",
        'image_url': static('img/logos/canal13.png')
    },
    {
        'title': "Dólar se dispara $14 y anota su mayor salto diario",
        'snippet': "El billete verde cerró la semana por sobre los $940, impactando la importación de productos.",
        'url': "https://www.emol.com/movil/economia/index.aspx",
        'source': "Emol",
        'theme': "Economía y Finanzas",
        'image_url': static('img/logos/emol.png')
    },
    {
        'title': "Comerciantes en alerta por alza de patentes en La Estrella",
        'snippet': "Vecinos y dueños de minimarket critican el nuevo plan regulador municipal que eleva costos de permisos.",
        'url': "#",
        'source': "La Estrella",
        'theme': "Normativa y Ciudad",
        'image_url': static('img/logos/laestrella.png')
    },
    {
        'title': "TVN reporta baja en ventas de pequeños locales",
        'snippet': "Reportaje especial sobre los hábitos de consumo post-pandemia y el impacto en las ventas del comercio minorista.",
        'url': "#",
        'source': "TVN",
        'theme': "Retail y Tendencias",
        'image_url': static('img/logos/tvn.png')
    },
]

# Recopilar fuentes y temas únicos para los filtros del front-end
UNIQUE_SOURCES = sorted(list(set(news['source'] for news in ALL_EXTERNAL_NEWS)))
UNIQUE_THEMES = sorted(list(set(news['theme'] for news in ALL_EXTERNAL_NEWS)))


# --- FUNCIÓN HELPER: Genera Notificaciones Simuladas ---
def generar_notificaciones_simuladas(comerciante):
    notificaciones = []
    hoy = timezone.now().date()
    puntos_actuales = comerciante.puntos
    
    # 1. Notificaciones de Beneficios
    # Usando Comerciante como proxy temporal para Beneficios, ya que ese modelo no está en este archivo
    nuevos_beneficios = Comerciante.objects.filter(fecha_registro__date__gte=hoy - timedelta(days=7)).order_by('-fecha_registro')
    if nuevos_beneficios.exists():
        notificaciones.append({'tipo': '🔔 Beneficio', 'mensaje': f'¡Hay {nuevos_beneficios.count()} nuevos descuentos y promociones disponibles!', 'url': '/beneficios/', 'tiempo': 'Hace poco', 'color': 'text-secondary',})
    if puntos_actuales >= 100:
        notificaciones.append({'tipo': '🔔 Puntos', 'mensaje': f'Acumulaste {puntos_actuales} puntos. ¡Ya puedes canjear!', 'url': '/beneficios/', 'tiempo': 'Ahora', 'color': 'text-green-500',})
    
    # 2. Invitaciones
    fecha_evento_simulado = hoy + timedelta(days=2)
    notificaciones.append({'tipo': '📨 Invitación', 'mensaje': f'Recordatorio: Taller de Marketing para Almacenes este {fecha_evento_simulado.strftime("%d/%m")}.', 'url': '#', 'tiempo': 'Hace 1 día', 'color': 'text-primary',})
    
    # 4. Redes Sociales integradas
    notificaciones.append({'tipo': '📱 Contenido', 'mensaje': '¡Nuevo video! 5 Claves para Optimizar tu Inventario de Minimarket.', 'url': 'https://www.youtube.com/user/ClubAlmacen', 'tiempo': 'Hace 3 horas', 'color': 'text-red-600',})
    
    # 6. Reuniones
    notificaciones.append({'tipo': '💬 Reunión', 'mensaje': 'Invitación a Reunión de Socios de Santiago Centro (Google Meet).', 'url': '#', 'tiempo': 'Hoy', 'color': 'text-purple-600',})

    return notificaciones 

# --- FUNCIÓN DE CÁLCULO DE NIVEL (se mantiene) ---
def calcular_nivel_y_progreso(puntos):
    NIVELES_VALORES = [nivel[0] for nivel in NIVELES] 
    UMBRAL_PUNTOS = 100 
    MAX_NIVEL_INDEX = len(NIVELES_VALORES) - 1 
    
    nivel_index = min(MAX_NIVEL_INDEX, puntos // UMBRAL_PUNTOS)
    nivel_actual_codigo = NIVELES_VALORES[nivel_index]
    current_threshold = nivel_index * UMBRAL_PUNTOS
    
    if nivel_actual_codigo == 'DIAMANTE':
        progreso_porcentaje = 100
        puntos_restantes = 0
        puntos_siguiente_nivel = puntos 
        proximo_nivel_display = 'Máximo'
    else:
        next_threshold = (nivel_index + 1) * UMBRAL_PUNTOS
        puntos_en_nivel = puntos - current_threshold
        puntos_a_avanzar = UMBRAL_PUNTOS 
        
        puntos_restantes = next_threshold - puntos
        progreso_porcentaje = int((puntos_en_nivel / puntos_a_avanzar) * 100)
        puntos_siguiente_nivel = next_threshold
        proximo_nivel_display = dict(NIVELES).get(NIVELES_VALORES[nivel_index + 1], 'N/A')

    return {
        'nivel_codigo': nivel_actual_codigo,
        'puntos_restantes': puntos_restantes,
        'puntos_siguiente_nivel': puntos_siguiente_nivel,
        'progreso_porcentaje': progreso_porcentaje,
        'proximo_nivel': proximo_nivel_display,
    }

# --- Helper Function for Online Status (se mantiene) ---
def is_online(last_login):
    """Determina si un usuario/proveedor está en línea (última conexión en los últimos 5 minutos)."""
    if not last_login:
        return False
    return (timezone.now() - last_login) < timedelta(minutes=5)


# --- VISTAS DE AUTENTICACIÓN Y PERFIL (se mantienen) ---

def index(request):
    return redirect('registro') 

def registro_view(request):
    if request.method == 'POST':
        form = RegistroComercianteForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.pop('password')
            hashed_password = make_password(raw_password)

            nuevo_comerciante = form.save(commit=False)
            nuevo_comerciante.password_hash = hashed_password
            
            comuna_final = form.cleaned_data.get('comuna') 
            if comuna_final:
                nuevo_comerciante.comuna = comuna_final
            
            # Asegurar que los nuevos registros son COMERCIANTE por defecto
            nuevo_comerciante.puntos = 0
            nuevo_comerciante.nivel_actual = 'BRONCE'
            nuevo_comerciante.rol = 'COMERCIANTE' 
            
            try:
                nuevo_comerciante.save()
                messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
                return redirect('login') 
            except IntegrityError:
                messages.error(request, 'Este correo electrónico ya está registrado. Por favor, inicia sesión o usa otro correo.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado al guardar: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = RegistroComercianteForm()
    
    context = {
        'form': form
    }
    return render(request, 'usuarios/cuenta.html', context)


def login_view(request):
    global current_logged_in_user
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                comerciante = Comerciante.objects.get(email=email)

                if check_password(password, comerciante.password_hash):
                    progreso = calcular_nivel_y_progreso(comerciante.puntos)
                    comerciante.nivel_actual = progreso['nivel_codigo']
                    
                    comerciante.ultima_conexion = timezone.now()
                    comerciante.save(update_fields=['ultima_conexion', 'nivel_actual']) 
                    
                    current_logged_in_user = comerciante
                    
                    messages.success(request, f'¡Bienvenido {comerciante.nombre_apellido}!')
                    
                    if comerciante.rol == 'ADMIN':
                        return redirect('panel_admin') 
                    
                    # Redirección a la nueva app proveedores (si existe el perfil)
                    if hasattr(comerciante, 'proveedor'):
                         return redirect(reverse('proveedores:perfil_proveedor'))
                        
                    return redirect('plataforma_comerciante')
                else:
                    messages.error(request, 'Contraseña incorrecta. Intenta nuevamente.')

            except Comerciante.DoesNotExist:
                messages.error(request, 'Este correo no está registrado. Por favor, regístrate primero.')
        else:
            messages.error(request, 'Por favor, completa todos los campos correctamente.')
    else:
        form = LoginForm()
        current_logged_in_user = None 

    context = {
        'form': form
    }
    return render(request, 'usuarios/cuenta.html', context)


def logout_view(request):
    global current_logged_in_user
    if current_logged_in_user:
        messages.info(request, f'Adiós, {current_logged_in_user.nombre_apellido}. Has cerrado sesión.')
        current_logged_in_user = None
    return redirect('login')


def perfil_view(request):
    global current_logged_in_user
    
    if not current_logged_in_user:
        messages.warning(request, 'Por favor, inicia sesión para acceder a tu perfil.')
        return redirect('login') 
        
    comerciante = current_logged_in_user 
    progreso = calcular_nivel_y_progreso(comerciante.puntos)
    
    if comerciante.nivel_actual != progreso['nivel_codigo']:
        comerciante.nivel_actual = progreso['nivel_codigo']
        comerciante.save(update_fields=['nivel_actual'])
    
    if request.method == 'POST':
        action = request.POST.get('action') 
        
        if action == 'edit_photo':
            photo_form = ProfilePhotoForm(request.POST, request.FILES, instance=comerciante)
            if photo_form.is_valid():
                photo_form.save()
                messages.success(request, '¡Foto de perfil actualizada con éxito!')
                return redirect('perfil')
            else:
                messages.error(request, 'Error al subir la foto. Asegúrate de que sea un archivo válido.')

        elif action == 'edit_contact':
            contact_form = ContactInfoForm(request.POST, instance=comerciante) 
            if contact_form.is_valid():
                nuevo_email = contact_form.cleaned_data.get('email')
                
                if nuevo_email != comerciante.email and Comerciante.objects.filter(email=nuevo_email).exists():
                    messages.error(request, 'Este correo ya está registrado por otro usuario.')
                else:
                    contact_form.save()
                    messages.success(request, 'Datos de contacto actualizados con éxito.')
                    current_logged_in_user.email = nuevo_email 
                    current_logged_in_user.whatsapp = contact_form.cleaned_data.get('whatsapp')
                    return redirect('perfil')
            else:
                error_msgs = [f"{field.label}: {', '.join(error for error in field.errors)}" for field in contact_form if field.errors]
                messages.error(request, f'Error en los datos de contacto. {"; ".join(error_msgs)}')

        elif action == 'edit_business':
            business_form = BusinessDataForm(request.POST, instance=comerciante)
            if business_form.is_valid():
                business_form.save()
                messages.success(request, 'Datos del negocio actualizados con éxito.')
                current_logged_in_user.nombre_negocio = business_form.cleaned_data.get('nombre_negocio')
                return redirect('perfil')
            else:
                error_msgs = [f"{field.label}: {', '.join(error for error in field.errors)}" for field in business_form if field.errors]
                messages.error(request, f'Error en los datos del negocio. {"; ".join(error_msgs)}')

        elif action == 'edit_interests':
            interests_form = InterestsForm(request.POST)
            if interests_form.is_valid():
                intereses_seleccionados = interests_form.cleaned_data['intereses']
                intereses_csv = ','.join(intereses_seleccionados)
                
                comerciante.intereses = intereses_csv
                comerciante.save(update_fields=['intereses']) 
                
                messages.success(request, 'Intereses actualizados con éxito.')
                return redirect('perfil')
            else:
                messages.error(request, 'Error al actualizar los intereses.')

    photo_form = ProfilePhotoForm()
    contact_form = ContactInfoForm(instance=comerciante) 
    business_form = BusinessDataForm(instance=comerciante) 

    intereses_actuales_codigos = comerciante.intereses.split(',') if comerciante.intereses else []
    interests_form = InterestsForm(initial={'intereses': [c for c in intereses_actuales_codigos if c]})

    intereses_choices_dict = dict(INTERESTS_CHOICES)
    
    # Generar notificaciones
    notificaciones = generar_notificaciones_simuladas(comerciante)

    context = {
        'comerciante': comerciante,
        'rol_usuario': ROLES_DISPLAY.get(comerciante.rol, 'Usuario'), 
        'nombre_negocio_display': comerciante.nombre_negocio,
        
        'puntos_actuales': comerciante.puntos,
        'nivel_actual': dict(NIVELES).get(comerciante.nivel_actual, 'Desconocido'),
        'puntos_restantes': calcular_nivel_y_progreso(comerciante.puntos)['puntos_restantes'],
        'progreso_porcentaje': calcular_nivel_y_progreso(comerciante.puntos)['progreso_porcentaje'],
        'es_proveedor': comerciante.es_proveedor, 
        
        'photo_form': photo_form,
        'contact_form': contact_form,
        'business_form': business_form,
        'interests_form': interests_form,
        
        'intereses_actuales_codigos': [c for c in intereses_actuales_codigos if c],
        'intereses_choices_dict': intereses_choices_dict,
        
        'notificaciones': notificaciones, 
    }
    
    return render(request, 'usuarios/perfil.html', context)


# --- VISTA PRINCIPAL DE LA PLATAFORMA (Foro y Noticias) ---

def plataforma_comerciante_view(request):
    global current_logged_in_user

    if not current_logged_in_user:
        messages.warning(request, 'Por favor, inicia sesión para acceder a la plataforma.')
        return redirect('login') 
        
    # Restricción: Solo posts de Admin (se mantiene)
    posts_query = Post.objects.select_related('comerciante').filter(
        comerciante__rol='ADMIN'
    ).annotate(
        comentarios_count=Count('comentarios', distinct=True), 
        likes_count=Count('likes', distinct=True),
        is_liked=Count('likes', filter=Q(likes__comerciante=current_logged_in_user)) 
    ).prefetch_related(
        'comentarios', 
        'comentarios__comerciante' 
    )
    
    categoria_filtros = request.GET.getlist('categoria', [])
    
    if categoria_filtros and 'TODAS' not in categoria_filtros:
        posts = posts_query.filter(categoria__in=categoria_filtros).order_by('-fecha_publicacion')
    else:
        posts = posts_query.all().order_by('-fecha_publicacion')
        if not categoria_filtros or 'TODAS' in categoria_filtros:
            categoria_filtros = ['TODAS']
            
    # Generar notificaciones
    notificaciones = generar_notificaciones_simuladas(current_logged_in_user)
    
    # --- SIMULACIÓN DE NOTICIAS EXTERNAS (FUNCIONALIDAD 12.3) ---
    # Mostramos las primeras 4 noticias para el sidebar.
    external_news_sidebar = ALL_EXTERNAL_NEWS[:4]
        
    context = {
        'comerciante': current_logged_in_user,
        'rol_usuario': ROLES_DISPLAY.get(current_logged_in_user.rol, 'Usuario'),
        'post_form': PostForm(),
        'posts': posts,
        'CATEGORIA_POST_CHOICES': Post._meta.get_field('categoria').choices, 
        'categoria_seleccionada': categoria_filtros, 
        'comentario_form': ComentarioForm(), 
        'message': f'Bienvenido a la plataforma, {current_logged_in_user.nombre_apellido.split()[0]}.',
        'is_admin': current_logged_in_user.rol == 'ADMIN',
        
        'notificaciones': notificaciones, 
        'external_news': external_news_sidebar, # <-- PASAMOS LAS PRIMERAS 4 CON IMAGEN
    }
    
    return render(request, 'usuarios/plataforma_comerciante.html', context)


# --- NUEVA VISTA PARA LA CUADRÍCULA DE NOTICIAS CON FILTROS (NUEVO) ---
def noticias_view(request):
    
    # 1. Obtener filtros
    source_filter = request.GET.get('fuente', 'TODOS')
    theme_filter = request.GET.get('tematica', 'TODOS')
    
    # 2. Aplicar filtros
    filtered_news = ALL_EXTERNAL_NEWS
    
    if source_filter != 'TODOS':
        filtered_news = [news for news in filtered_news if news['source'] == source_filter]
        
    if theme_filter != 'TODOS':
        filtered_news = [news for news in filtered_news if news['theme'] == theme_filter]

    context = {
        'noticias': filtered_news,
        'fuentes': UNIQUE_SOURCES,
        'tematicas': UNIQUE_THEMES,
        'source_seleccionada': source_filter,
        'theme_seleccionada': theme_filter,
        'comerciante': current_logged_in_user,
        # Necesario para el header
        'current_user_name': current_logged_in_user.nombre_apellido if current_logged_in_user else 'Usuario', 
        'current_user_img': current_logged_in_user.get_profile_picture_url() if current_logged_in_user else '',
    }
    
    return render(request, 'usuarios/noticias.html', context)


def publicar_post_view(request):
    global current_logged_in_user
    
    # Restricción: Solo Admins pueden publicar
    if not current_logged_in_user or current_logged_in_user.rol != 'ADMIN': 
        messages.error(request, 'No tienes permiso para crear publicaciones en el foro.')
        return redirect('plataforma_comerciante') 
            
    if request.method == 'POST':
        if not current_logged_in_user:
            messages.error(request, 'Debes iniciar sesión para publicar.')
            return redirect('login') 
            
        try:
            form = PostForm(request.POST, request.FILES) 
            
            if form.is_valid():
                nuevo_post = form.save(commit=False)
                nuevo_post.comerciante = current_logged_in_user
                
                uploaded_file = form.cleaned_data.get('uploaded_file')
                
                if uploaded_file:
                    file_name = default_storage.save(f'posts/{uploaded_file.name}', uploaded_file)
                    nuevo_post.imagen_url = default_storage.url(file_name) 
                
                nuevo_post.save()
                messages.success(request, '¡Publicación creada con éxito! Se ha añadido al foro.')
                return redirect('plataforma_comerciante')
            else:
                messages.error(request, f'Error al publicar. Por favor, corrige los errores: {form.errors.as_text()}')
                return redirect('plataforma_comerciante') 
        
        except Exception as e:
            messages.error(request, f'Ocurrió un error al publicar: {e}')
            
    return redirect('plataforma_comerciante')


def post_detail_view(request, post_id):
    global current_logged_in_user
    
    if not current_logged_in_user:
        messages.warning(request, 'Debes iniciar sesión para ver los detalles.')
        return redirect('login') 
        
    post = get_object_or_404(Post.objects.select_related('comerciante').annotate(
        comentarios_count=Count('comentarios', distinct=True),
        likes_count=Count('likes', distinct=True),
        is_liked=Count('likes', filter=Q(likes__comerciante=current_logged_in_user))
    ), pk=post_id)
        
    comentarios = post.comentarios.select_related('comerciante').all().order_by('fecha_creacion')
    
    context = {
        'comerciante': current_logged_in_user,
        'post': post,
        'comentarios': comentarios,
        'comentario_form': ComentarioForm(),
    }
    
    return render(request, 'usuarios/post_detail.html', context)


def add_comment_view(request, post_id):
    global current_logged_in_user
    
    if not current_logged_in_user:
        messages.error(request, 'No autorizado para comentar. Inicia sesión.')
        return redirect('login')
        
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.post = post
            nuevo_comentario.comerciante = current_logged_in_user
            nuevo_comentario.save()
            messages.success(request, '¡Comentario publicado con éxito!')
            return redirect('plataforma_comerciante') 
        else:
            messages.error(request, 'Error al publicar el comentario. Asegúrate de que el contenido no esté vacío.')
            return redirect('plataforma_comerciante') 
            
    return redirect('plataforma_comerciante')


def like_post_view(request, post_id):
    global current_logged_in_user

    if not current_logged_in_user:
        messages.error(request, 'Debes iniciar sesión para dar like.')
        return redirect('login')

    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(
            post=post,
            comerciante=current_logged_in_user
        )
        
        if not created:
            like.delete()
            messages.success(request, 'Dislike registrado.')
        else:
            messages.success(request, '¡Like registrado!')

    return redirect('plataforma_comerciante')


def beneficios_view(request):
    global current_logged_in_user

    if not current_logged_in_user:
        messages.warning(request, 'Por favor, inicia sesión para acceder a los beneficios.')
        return redirect('login') 
        
    comerciante = current_logged_in_user
    progreso = calcular_nivel_y_progreso(comerciante.puntos)
    
    category_filter = request.GET.get('category', 'TODOS')
    sort_by = request.GET.get('sort_by', '-fecha_creacion') 
    
    beneficios_queryset = Comerciante.objects.all() # Usado como placeholder
    

    no_beneficios_disponibles = not beneficios_queryset.exists()
    
    context = {
        'comerciante': comerciante,
        'rol_usuario': ROLES_DISPLAY.get(comerciante.rol, 'Usuario'),
        
        'puntos_actuales': comerciante.puntos,
        'nivel_actual': dict(NIVELES).get(progreso['nivel_codigo'], 'Bronce'),
        'puntos_restantes': progreso['puntos_restantes'],
        'puntos_siguiente_nivel': progreso['puntos_siguiente_nivel'],
        'progreso_porcentaje': progreso['progreso_porcentaje'],
        'proximo_nivel': progreso['proximo_nivel'],
        
        'beneficios': beneficios_queryset,
        'no_beneficios_disponibles': no_beneficios_disponibles,
        'CATEGORIAS': CATEGORIAS, 
        'current_category': category_filter, 
        'current_sort': sort_by, 
    }
    
    return render(request, 'usuarios/beneficios.html', context)


def solicitar_rol_proveedor_view(request):
    global current_logged_in_user

    if not current_logged_in_user:
        messages.warning(request, 'Debes iniciar sesión para realizar esta solicitud.')
        return redirect('login') 

    if request.method == 'POST':
        if current_logged_in_user.es_proveedor:
            messages.info(request, 'Ya tienes el rol de proveedor activo.')
            # 🚨 REDIRECCIÓN A LA NUEVA APP PROVEEDORES
            return redirect(reverse('proveedores:perfil_proveedor')) 
        
        messages.success(request, '¡Solicitud de rol de Proveedor enviada! Un administrador revisará tu solicitud.')
        
        return redirect('perfil') 
    
    return redirect('perfil')


def proveedor_dashboard_view(request):
    global current_logged_in_user

    if not current_logged_in_user or not current_logged_in_user.es_proveedor:
        messages.warning(request, 'Acceso denegado. Esta interfaz es solo para Proveedores activos.')
        return redirect('perfil')
    
    # 🚨 REDIRECCIÓN A LA NUEVA APP PROVEEDORES
    return redirect(reverse('proveedores:perfil_proveedor'))


def directorio_view(request):
    global current_logged_in_user
    
    # 🚨 REDIRECCIÓN A LA NUEVA APP PROVEEDORES
    return redirect(reverse('proveedores:directorio_proveedores'))


def proveedor_perfil_view(request, pk):
    global current_logged_in_user
    
    # 🚨 REDIRECCIÓN A LA NUEVA APP PROVEEDORES
    return redirect(reverse('proveedores:detalle_proveedor', kwargs={'proveedor_id': pk}))