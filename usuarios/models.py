# usuarios/models.py (CONTENIDO COMPLETO Y FINAL)

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
from django.templatetags.static import static 
from django.contrib.auth.models import User 
from datetime import timedelta 

# --- Opciones de Selección Múltiple ---

RELACION_NEGOCIO_CHOICES = [
    ('DUEÑO', 'Dueño/a'),
    ('ADMIN', 'Administrador/a'),
    ('EMPLEADO', 'Empleado/a clave'),
    ('FAMILIAR', 'Familiar a cargo'),
]

TIPO_NEGOCIO_CHOICES = [
    ('ALMACEN', 'Almacén de Barrio'),
    ('MINIMARKET', 'Minimarket'),
    ('BOTILLERIA', 'Botillería'),
    ('PANADERIA', 'Panadería/Pastelería'),
    ('FERIA', 'Feria Libre'),
    ('KIOSCO', 'Kiosco'),
    ('FOODTRUCK', 'Food Truck/Carro de Comida'),
]

# Categorías para publicaciones del foro (MANTENIDO)
CATEGORIA_POST_CHOICES = [
    ('DUDA', 'Duda / Pregunta'),
    ('OPINION', 'Opinión / Debate'),
    ('RECOMENDACION', 'Recomendación'),
    ('NOTICIA', 'Noticia del Sector'),
    ('GENERAL', 'General'),
]

# Definición de CATEGORIAS para Beneficio (Mantenido)
CATEGORIAS = [
    ('DESCUENTO', 'Descuento y Ofertas'),
    ('SORTEO', 'Sorteos y Rifas'),
    ('CAPACITACION', 'Capacitación y Cursos'),
    ('ACCESO', 'Acceso Exclusivo'),
    ('EVENTO', 'Eventos Especiales'),
]

ESTADO_BENEFICIO = [
    ('ACTIVO', 'Activo'),
    ('TERMINADO', 'Terminado'),
    ('BENEFICIO_ACTIVO', 'Beneficio Reclamado'), 
]

# Definición de Niveles (Sistema de 100 puntos)
NIVELES = [
    ('BRONCE', 'Bronce'),
    ('PLATA', 'Plata'),
    ('ORO', 'Oro'),
    ('PLATINO', 'Platino'),
    ('DIAMANTE', 'Diamante'),
]

RUBROS_CHOICES = [
    ('ABARROTES', 'Abarrotes'),
    ('CARNES', 'Carnes'),
    ('LACTEOS', 'Lácteos'),
    ('FRUTAS', 'Frutas y Verduras'),
    ('LIMPIEZA', 'Limpieza'),
    ('PANADERIA', 'Panadería'),
    ('VARIOS', 'Varios'),
]

# --- MODELO PRINCIPAL DE COMERCIANTE ---

class Comerciante(models.Model):
    nombre_apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128) 
    
    whatsapp_validator = RegexValidator(
        regex=r'^\+569\d{8}$', 
        message="El formato debe ser '+569XXXXXXXX'."
    )
    whatsapp = models.CharField(
        validators=[whatsapp_validator], 
        max_length=12, 
        blank=True, 
        null=True,
        help_text="Formato: +569XXXXXXXX"
    )

    relacion_negocio = models.CharField(max_length=10, choices=RELACION_NEGOCIO_CHOICES)
    tipo_negocio = models.CharField(max_length=20, choices=TIPO_NEGOCIO_CHOICES)
    comuna = models.CharField(max_length=50) 
    nombre_negocio = models.CharField(max_length=100, default='Mi Negocio Local', blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField(default=timezone.now)

    foto_perfil = models.ImageField( 
        upload_to='perfiles/', 
        default='usuarios/img/default_profile.png', 
        blank=True, 
        null=True
    )
    
    # --- CAMPOS DE PUNTOS Y ROLES ---
    puntos = models.IntegerField(default=0, verbose_name='Puntos Acumulados')
    nivel_actual = models.CharField(max_length=50, choices=NIVELES, default='BRONCE', verbose_name='Nivel de Beneficios')
    
    ROL_CHOICES = [
        ('COMERCIANTE', 'Comerciante'),
        ('ADMIN', 'Administrador'),
    ]
    rol = models.CharField(max_length=15, choices=ROL_CHOICES, default='COMERCIANTE', verbose_name='Rol de Usuario')
    
    es_proveedor = models.BooleanField(default=False, verbose_name='Es Proveedor')

    class Meta:
        verbose_name = 'Comerciante'
        verbose_name_plural = 'Comerciantes'

    def __str__(self):
        return f"{self.nombre_apellido} ({self.email})"

    def get_profile_picture_url(self):
        if self.foto_perfil and self.foto_perfil.name and 'default' not in self.foto_perfil.name:
            return self.foto_perfil.url
        return static('img/default_profile.png')


# --- MODELOS DE FORO (Post, Comentario, Like) ---

class Post(models.Model):
    """Modelo que representa una publicación en el foro."""
    comerciante = models.ForeignKey(
        Comerciante,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Comerciante'
    )
    titulo = models.CharField(max_length=200, verbose_name='Título de la Publicación')
    contenido = models.TextField(verbose_name='Contenido del Post')
    categoria = models.CharField(max_length=50, choices=CATEGORIA_POST_CHOICES, default='GENERAL', verbose_name='Categoría')
    imagen_url = models.URLField(max_length=200, blank=True, null=True, verbose_name='URL de Imagen/Link de Archivo Subido')
    etiquetas = models.CharField(max_length=255, blank=True, verbose_name='Etiquetas (@usuarios, hashtags)')
    fecha_publicacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Publicación')
    
    class Meta:
        verbose_name = 'Publicación de Foro'
        verbose_name_plural = 'Publicaciones de Foro'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo} por {self.comerciante.nombre_apellido}"

class Comentario(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comentarios', 
        verbose_name='Publicación'
    )
    comerciante = models.ForeignKey(
        'Comerciante', 
        on_delete=models.CASCADE, 
        related_name='comentarios_dados', 
        verbose_name='Autor'
    )
    contenido = models.TextField(verbose_name='Comentario')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion'] 

    def __str__(self):
        return f"Comentario de {self.comerciante.nombre_apellido} en {self.post.titulo[:20]}"


class Like(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='likes', 
        verbose_name='Publicación'
    )
    comerciante = models.ForeignKey(
        'Comerciante', 
        on_delete=models.CASCADE, 
        related_name='likes_dados', 
        verbose_name='Comerciante'
    )
    
    class Meta:
        unique_together = ('post', 'comerciante')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

    def __str__(self):
        return f"Like de {self.comerciante.nombre_apellido} a {self.post.titulo[:20]}"


# --- MODELO BENEFICIO ---
class Beneficio(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título del Beneficio")
    descripcion = models.TextField(verbose_name="Descripción")
    foto = models.ImageField(upload_to='beneficios_fotos/', null=True, blank=True, verbose_name="Imagen") 
    vence = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento") 
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='DESCUENTO', verbose_name="Categoría") 
    puntos_requeridos = models.IntegerField(default=0, verbose_name="Puntos Requeridos")
    estado = models.CharField(max_length=30, choices=ESTADO_BENEFICIO, default='ACTIVO')
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name='Subido por'
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Beneficio y Promoción'
        verbose_name_plural = 'Beneficios y Promociones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"


# --- MODELOS PARA EL DIRECTORIO DE PROVEEDORES ---

class Proveedor(models.Model):
    # Ficha base
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500, blank=True)
    foto_perfil = models.ImageField(upload_to='proveedores/fotos/', null=True, blank=True)
    
    # Datos de Contacto Externo (Requerimiento de la Ficha)
    email_contacto = models.EmailField(blank=True, null=True)
    whatsapp_contacto = models.CharField(max_length=12, blank=True, null=True, help_text="Formato: +569XXXXXXXX")
    
    # Gestión de estado en línea
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField(default=timezone.now) # Usado para el estado 'en línea'

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre
    
    def get_profile_picture_url(self):
        if self.foto_perfil and self.foto_perfil.name and 'default' not in self.foto_perfil.name:
            return self.foto_perfil.url
        return static('img/default_profile.png')


class Propuesta(models.Model):
    # La propuesta o "post" del proveedor (Simula el post que sube el proveedor)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='propuestas')
    titulo = models.CharField(max_length=100)
    rubros_ofertados = models.CharField(max_length=255, verbose_name='Rubros Ofertados', help_text='Separados por coma')
    zona_geografica = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Propuesta de Proveedor"
        verbose_name_plural = "Propuestas de Proveedores"
        
    def __str__(self):
        return f"{self.titulo} - {self.proveedor.nombre}"   


# --- MODELO DE TICKETS DE SOPORTE ---
TICKET_CATEGORIES = [
    ('TECNICO', 'Fallo Técnico/Error'),
    ('PAGO', 'Consulta de Pago/Facturación'),
    ('SUGERENCIA', 'Sugerencia de Mejora'),
    ('OTRO', 'Otro/General'),
]

class Ticket(models.Model):
    """Modelo para solicitudes de soporte o tickets."""
    # Asume que Comerciante y User están definidos
    comerciante = models.ForeignKey('Comerciante', on_delete=models.CASCADE, verbose_name="Comerciante")
    titulo = models.CharField(max_length=150, verbose_name="Asunto del Ticket")
    categoria = models.CharField(max_length=20, choices=TICKET_CATEGORIES, verbose_name="Categoría")
    comentario = models.TextField(verbose_name="Comentario y Detalles")
    adjunto = models.FileField(upload_to='tickets/', blank=True, null=True, verbose_name="Foto/Archivo Adjunto")
    
    contacto_opcional = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Contacto (Correo o Teléfono)",
        help_text="Opcional, para respuesta rápida fuera de la plataforma."
    )
    
    estado = models.CharField(max_length=20, default='ABIERTO', choices=[('ABIERTO', 'Abierto'), ('CERRADO', 'Cerrado'), ('EN_PROCESO', 'En Proceso')])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ticket de Soporte'
        verbose_name_plural = 'Tickets de Soporte'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Ticket #{self.id}: {self.titulo} ({self.get_categoria_display()})"