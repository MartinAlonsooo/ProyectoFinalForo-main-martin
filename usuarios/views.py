# usuarios/views.py (COMPLETO Y FUNCIONAL)

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    Comerciante,
    Post,
    Like,
    Comentario,
    INTERESTS_CHOICES,
    Beneficio,
    NIVELES,
    CATEGORIAS,
    RUBROS_CHOICES,
)
from .forms import (
    RegistroComercianteForm,
    LoginForm,
    PostForm,
    ProfilePhotoForm,
    BusinessDataForm,
    ContactInfoForm,
    InterestsForm,
    ComentarioForm,
)

# --- Simulación de sesión global ---
current_logged_in_user = None

ROLES = {
    'COMERCIANTE': 'Comerciante Verificado',
    'PROVEEDOR': 'Proveedor',
    'ADMIN': 'Administrador',
    'INVITADO': 'Invitado',
}


# --- Decorador personalizado para reemplazar @login_required ---
def custom_login_required(view_func):
    """Decorador personalizado que verifica current_logged_in_user"""
    def wrapper(request, *args, **kwargs):
        global current_logged_in_user
        if not current_logged_in_user:
            messages.warning(request, 'Por favor, inicia sesión para acceder a esta página.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- Funciones helper ---

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
        proximo_nivel_display = dict(NIVELES).get(
            NIVELES_VALORES[nivel_index + 1],
            'N/A'
        )

    return {
        'nivel_codigo': nivel_actual_codigo,
        'puntos_restantes': puntos_restantes,
        'puntos_siguiente_nivel': puntos_siguiente_nivel,
        'progreso_porcentaje': progreso_porcentaje,
        'proximo_nivel': proximo_nivel_display,
    }


def is_online(last_login):
    if not last_login:
        return False
    return (timezone.now() - last_login) < timedelta(minutes=5)


# --- Autenticación y cuenta ---

def index(request):
    return redirect('login')


def registro_view(request):
    """
    Maneja el registro de nuevos comerciantes.
    Detecta el envío mediante el botón name="registro_submit".
    """
    global current_logged_in_user
    
    # Siempre pasamos ambos formularios
    login_form = LoginForm()

    if request.method == 'POST' and 'registro_submit' in request.POST:
        register_form = RegistroComercianteForm(request.POST)
        
        if register_form.is_valid():
            try:
                # Extraemos la contraseña antes de guardar
                raw_password = register_form.cleaned_data.get('password')
                
                # Guardamos el comerciante sin commit para modificarlo
                nuevo_comerciante = register_form.save(commit=False)
                
                # Hasheamos la contraseña
                nuevo_comerciante.password_hash = make_password(raw_password)
                
                # Asignamos la comuna desde comuna_select
                comuna_final = register_form.cleaned_data.get('comuna_select')
                if comuna_final:
                    nuevo_comerciante.comuna = comuna_final
                
                # Inicializamos puntos y nivel
                nuevo_comerciante.puntos = 0
                nuevo_comerciante.nivel_actual = 'BRONCE'
                
                # Aseguramos que NO sea proveedor
                nuevo_comerciante.es_proveedor = False
                
                # Asignamos rol por defecto
                if not nuevo_comerciante.rol:
                    nuevo_comerciante.rol = 'COMERCIANTE'
                
                # Convertimos el email a minúsculas para evitar duplicados
                nuevo_comerciante.email = nuevo_comerciante.email.lower()
                
                # Guardamos en la base de datos
                nuevo_comerciante.save()
                
                messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
                
                # Redirigimos a login con parámetro para mostrar pestaña de login
                return redirect('login')
                
            except IntegrityError as e:
                if 'email' in str(e).lower():
                    messages.error(
                        request,
                        'Este correo electrónico ya está registrado. Por favor, inicia sesión o usa otro correo.'
                    )
                else:
                    messages.error(
                        request,
                        'Ya existe un usuario con estos datos. Por favor, verifica tu información.'
                    )
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado al guardar: {e}')
        else:
            # Mostramos los errores específicos del formulario
            for field, errors in register_form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_label = register_form.fields[field].label or field
                        messages.error(request, f'{field_label}: {error}')
    else:
        register_form = RegistroComercianteForm()

    contexto = {
        'login_form': login_form,
        'register_form': register_form,
        'comerciante': current_logged_in_user,
    }
    return render(request, 'usuarios/cuenta.html', contexto)


def login_view(request):
    """
    Maneja el login de comerciantes existentes.
    Detecta el envío mediante el botón name="login_submit".
    """
    global current_logged_in_user

    # Siempre pasamos ambos formularios a la plantilla
    register_form = RegistroComercianteForm()

    # Solo procesamos el login si el POST proviene del formulario de login
    if request.method == 'POST' and 'login_submit' in request.POST:
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            email = login_form.cleaned_data['email'].lower()
            password = login_form.cleaned_data['password']

            try:
                comerciante = Comerciante.objects.get(email=email)

                if check_password(password, comerciante.password_hash):
                    # Actualizamos nivel y última conexión
                    progreso = calcular_nivel_y_progreso(comerciante.puntos)
                    comerciante.nivel_actual = progreso['nivel_codigo']
                    comerciante.ultima_conexion = timezone.now()
                    comerciante.save(update_fields=['ultima_conexion', 'nivel_actual'])

                    # Guardamos en "sesión" simulada
                    current_logged_in_user = comerciante

                    messages.success(request, f'¡Bienvenido {comerciante.nombre_apellido}!')

                    # Redirecciones según rol
                    if comerciante.rol == 'ADMIN':
                        return redirect('panel_admin')

                    return redirect('plataforma_comerciante')
                else:
                    messages.error(request, 'Contraseña incorrecta. Intenta nuevamente.')

            except Comerciante.DoesNotExist:
                messages.error(request, 'Este correo no está registrado. Por favor, regístrate primero.')
        else:
            messages.error(request, 'Por favor, completa todos los campos correctamente.')
    else:
        # GET o POST que no es del login -> mostramos el formulario vacío
        login_form = LoginForm()

    contexto = {
        'login_form': login_form,
        'register_form': register_form,
        'comerciante': current_logged_in_user,
    }
    return render(request, 'usuarios/cuenta.html', contexto)


def logout_view(request):
    global current_logged_in_user
    if current_logged_in_user:
        messages.info(
            request,
            f'Adiós, {current_logged_in_user.nombre_apellido}. Has cerrado sesión.'
        )
        current_logged_in_user = None
    return redirect('login')


# --- Perfil ---

@custom_login_required
def perfil_view(request):
    global current_logged_in_user

    comerciante = current_logged_in_user
    progreso = calcular_nivel_y_progreso(comerciante.puntos)

    if comerciante.nivel_actual != progreso['nivel_codigo']:
        comerciante.nivel_actual = progreso['nivel_codigo']
        comerciante.save(update_fields=['nivel_actual'])

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'edit_photo':
            photo_form = ProfilePhotoForm(
                request.POST,
                request.FILES,
                instance=comerciante
            )
            if photo_form.is_valid():
                photo_form.save()
                messages.success(request, '¡Foto de perfil actualizada con éxito!')
                return redirect('perfil')
            else:
                messages.error(
                    request,
                    'Error al subir la foto. Asegúrate de que sea un archivo válido.'
                )

        elif action == 'edit_contact':
            contact_form = ContactInfoForm(request.POST, instance=comerciante)
            if contact_form.is_valid():
                nuevo_email = contact_form.cleaned_data.get('email')

                if (
                    nuevo_email != comerciante.email and
                    Comerciante.objects.filter(email=nuevo_email).exists()
                ):
                    messages.error(request, 'Este correo ya está registrado por otro usuario.')
                else:
                    contact_form.save()
                    messages.success(request, 'Datos de contacto actualizados con éxito.')
                    current_logged_in_user.email = nuevo_email
                    current_logged_in_user.whatsapp = contact_form.cleaned_data.get('whatsapp')
                    return redirect('perfil')
            else:
                error_msgs = [
                    f"{field.label}: {', '.join(error for error in field.errors)}"
                    for field in contact_form if field.errors
                ]
                messages.error(
                    request,
                    f'Error en los datos de contacto. {"; ".join(error_msgs)}'
                )

        elif action == 'edit_business':
            business_form = BusinessDataForm(request.POST, instance=comerciante)
            if business_form.is_valid():
                business_form.save()
                messages.success(request, 'Datos del negocio actualizados con éxito.')
                current_logged_in_user.nombre_negocio = business_form.cleaned_data.get(
                    'nombre_negocio'
                )
                return redirect('perfil')
            else:
                error_msgs = [
                    f"{field.label}: {', '.join(error for error in field.errors)}"
                    for field in business_form if field.errors
                ]
                messages.error(
                    request,
                    f'Error en los datos del negocio. {"; ".join(error_msgs)}'
                )

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

    intereses_actuales_codigos = (
        comerciante.intereses.split(',') if comerciante.intereses else []
    )
    interests_form = InterestsForm(
        initial={'intereses': [c for c in intereses_actuales_codigos if c]}
    )

    intereses_choices_dict = dict(INTERESTS_CHOICES)

    context = {
        'comerciante': comerciante,
        'rol_usuario': ROLES.get(comerciante.rol, 'Usuario'),
        'nombre_negocio_display': comerciante.nombre_negocio,

        'puntos_actuales': comerciante.puntos,
        'nivel_actual': dict(NIVELES).get(comerciante.nivel_actual, 'Desconocido'),
        'puntos_restantes': progreso['puntos_restantes'],
        'progreso_porcentaje': progreso['progreso_porcentaje'],
        'es_proveedor': comerciante.es_proveedor,

        'photo_form': photo_form,
        'contact_form': contact_form,
        'business_form': business_form,
        'interests_form': interests_form,

        'intereses_actuales_codigos': [c for c in intereses_actuales_codigos if c],
        'intereses_choices_dict': intereses_choices_dict,
    }

    return render(request, 'usuarios/perfil.html', context)


# --- Plataforma / Foro ---

@custom_login_required
def plataforma_comerciante_view(request):
    global current_logged_in_user
    
    posts_query = (
        Post.objects
        .select_related('comerciante')
        .annotate(
            comentarios_count=Count('comentarios', distinct=True),
            likes_count=Count('likes', distinct=True),
            is_liked=Count(
                'likes',
                filter=Q(likes__comerciante=current_logged_in_user)
            )
        )
        .prefetch_related(
            'comentarios',
            'comentarios__comerciante'
        )
    )

    categoria_filtros = request.GET.getlist('categoria', [])

    if categoria_filtros and 'TODAS' not in categoria_filtros:
        posts = posts_query.filter(
            categoria__in=categoria_filtros
        ).order_by('-fecha_publicacion')
    else:
        posts = posts_query.all().order_by('-fecha_publicacion')
        if not categoria_filtros or 'TODAS' in categoria_filtros:
            categoria_filtros = ['TODOS']

    # Verificar si es admin
    is_admin = current_logged_in_user.rol == 'ADMIN'

    context = {
        'comerciante': current_logged_in_user,
        'rol_usuario': ROLES.get(current_logged_in_user.rol, 'Usuario'),
        'post_form': PostForm(),
        'posts': posts,
        'CATEGORIA_POST_CHOICES': Post._meta.get_field('categoria').choices,
        'categoria_seleccionada': categoria_filtros,
        'comentario_form': ComentarioForm(),
        'is_admin': is_admin,
        'notificaciones': [],  # Agregar notificaciones vacías por ahora
        'external_news': [],  # Agregar noticias vacías por ahora
        'message': (
            f'Bienvenido a la plataforma, '
            f'{current_logged_in_user.nombre_apellido.split()[0]}.'
        ),
    }

    return render(request, 'usuarios/plataforma_comerciante.html', context)


@custom_login_required
def publicar_post_view(request):
    global current_logged_in_user

    if request.method == 'POST':
        try:
            form = PostForm(request.POST, request.FILES)

            if form.is_valid():
                nuevo_post = form.save(commit=False)
                nuevo_post.comerciante = current_logged_in_user

                uploaded_file = form.cleaned_data.get('uploaded_file')

                if uploaded_file:
                    file_name = default_storage.save(
                        f'posts/{uploaded_file.name}',
                        uploaded_file
                    )
                    nuevo_post.imagen_url = default_storage.url(file_name)

                nuevo_post.save()
                messages.success(
                    request,
                    '¡Publicación creada con éxito! Se ha añadido al foro.'
                )
                return redirect('plataforma_comerciante')
            else:
                messages.error(
                    request,
                    f'Error al publicar. Corrige: {form.errors.as_text()}'
                )
                return redirect('plataforma_comerciante')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al publicar: {e}')

    return redirect('plataforma_comerciante')


@custom_login_required
def post_detail_view(request, post_id):
    global current_logged_in_user

    post = get_object_or_404(
        Post.objects
        .select_related('comerciante')
        .annotate(
            comentarios_count=Count('comentarios', distinct=True),
            likes_count=Count('likes', distinct=True),
            is_liked=Count(
                'likes',
                filter=Q(likes__comerciante=current_logged_in_user)
            )
        ),
        pk=post_id
    )

    comentarios = post.comentarios.select_related(
        'comerciante'
    ).all().order_by('fecha_creacion')

    context = {
        'comerciante': current_logged_in_user,
        'post': post,
        'comentarios': comentarios,
        'comentario_form': ComentarioForm(),
    }
    return render(request, 'usuarios/post_detail.html', context)


@custom_login_required
def add_comment_view(request, post_id):
    global current_logged_in_user

    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.post = post
            nuevo_comentario.comerciante = current_logged_in_user
            nuevo_comentario.save()
            messages.success(request, '¡Comentario publicado con éxito!')
        else:
            messages.error(
                request,
                'Error al publicar el comentario. El contenido no puede estar vacío.'
            )

    return redirect('plataforma_comerciante')


@custom_login_required
def like_post_view(request, post_id):
    global current_logged_in_user

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


# --- Beneficios ---

@custom_login_required
def beneficios_view(request):
    global current_logged_in_user

    comerciante = current_logged_in_user
    progreso = calcular_nivel_y_progreso(comerciante.puntos)

    category_filter = request.GET.get('category', 'TODOS')
    sort_by = request.GET.get('sort_by', '-fecha_creacion')

    beneficios_queryset = Beneficio.objects.all()

    if category_filter and category_filter != 'TODOS':
        beneficios_queryset = beneficios_queryset.filter(categoria=category_filter)

    valid_sort_fields = [
        'vence',
        '-vence',
        'puntos_requeridos',
        '-puntos_requeridos',
        '-fecha_creacion',
    ]
    if sort_by in valid_sort_fields:
        beneficios_queryset = beneficios_queryset.order_by(sort_by)
    else:
        sort_by = '-fecha_creacion'
        beneficios_queryset = beneficios_queryset.order_by(sort_by)

    no_beneficios_disponibles = not beneficios_queryset.exists()

    context = {
        'comerciante': comerciante,
        'rol_usuario': ROLES.get(comerciante.rol, 'Usuario'),

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


# --- Gestión de rol proveedor ---

@custom_login_required
def solicitar_rol_proveedor_view(request):
    global current_logged_in_user

    if request.method == 'POST':
        if current_logged_in_user.es_proveedor:
            messages.info(request, 'Ya tienes el rol de proveedor activo.')
            return redirect('proveedor_dashboard')

        current_logged_in_user.es_proveedor = True
        current_logged_in_user.save(update_fields=['es_proveedor'])
        messages.success(
            request,
            '¡Ahora tienes el rol de Proveedor activo en el sistema!'
        )
        return redirect('perfil')

    return redirect('perfil')