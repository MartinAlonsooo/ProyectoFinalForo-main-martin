from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Proveedor(models.Model):
    """Modelo principal de Proveedor"""
    
    # Información básica
    nombre_empresa = models.CharField(max_length=200, verbose_name='Nombre de la Empresa')
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    password = models.CharField(max_length=128, verbose_name='Contraseña')
    
    # Zona de cobertura
    COBERTURA_CHOICES = [
        ('local', 'Local'),
        ('comunal', 'Comunal'),
        ('regional', 'Regional'),
        ('internacional', 'Internacional'),
    ]

    PAISES_CHOICES = [
        ('CL', 'Chile'),
        ('AR', 'Argentina'),
        ('PE', 'Perú'),
        ('CO', 'Colombia'),
        ('MX', 'México'),
    ]

    REGION_CHOICES = [
        ('RM', 'Región Metropolitana'),
        ('VA', 'Valparaíso'),
        ('BI', 'Biobío'),
        ('AR', 'La Araucanía'),
        ('MA', 'Magallanes'),
    ]

    COMUNAS_CHOICES = [
        ('STG', 'Santiago'),
        ('LCN', 'Las Condes'),
        ('VMA', 'Viña del Mar'),
        ('CON', 'Concepción'),
        ('TEM', 'Temuco'),
    ]

    CATEGORIAS_CHOICES = [
        ('COM', 'Comidas'),
        ('BEB', 'Bebestibles'),
        ('SAL', 'Salud y Bienestar'),
        ('FER', 'Ferretería'),
        ('ABA', 'Abarrotes'),
    ]
    
    cobertura = models.CharField(
        max_length=40, 
        choices=COBERTURA_CHOICES, 
        default='local',
        verbose_name='Zona de Cobertura'
    )
    
    # Contacto
    telefono_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Formato: '+56912345678'. Hasta 15 dígitos."
    )
    whatsapp = models.CharField(
        validators=[telefono_regex],
        max_length=17,
        verbose_name='WhatsApp'
    )

    # Descripción
    descripcion = models.TextField(verbose_name='Descripción del Negocio')
    
    # Foto de la empresa
    foto_empresa = models.ImageField(
        upload_to='proveedores/fotos/',
        blank=True,
        null=True,
        verbose_name='Foto de la Empresa'
    )
    
    
    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección'
    )

    paises = models.CharField(
        max_length=40, 
        choices=PAISES_CHOICES, 
        default='MX',
        verbose_name='Paises'
    )

    regiones = models.CharField(
        max_length=40, 
        choices=REGION_CHOICES, 
        default='RM',
        verbose_name='Regiones'
    )

    comunas = models.CharField(
        max_length=40, 
        choices=COMUNAS_CHOICES, 
        default='STG',
        verbose_name='Comunas'
    )

    categorias = models.CharField(
        max_length=40, 
        choices=CATEGORIAS_CHOICES, 
        default='COM',
        verbose_name='Categorias'
    )
    
    # ===== NUEVOS CAMPOS DE CONFIGURACIÓN =====
    
    # Preferencias de interfaz
    modo_oscuro = models.BooleanField(
        default=False,
        verbose_name='Modo Oscuro'
    )
    
    # Notificaciones
    notif_email = models.BooleanField(
        default=True,
        verbose_name='Notificaciones por Email'
    )
    notif_mensajes = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de Mensajes'
    )
    notif_pedidos = models.BooleanField(
        default=True,
        verbose_name='Notificaciones de Pedidos'
    )
    
    # Idioma y zona horaria
    IDIOMA_CHOICES = [
        ('es', 'Español'),
        ('en', 'English'),
        ('pt', 'Português'),
    ]
    idioma = models.CharField(
        max_length=10,
        choices=IDIOMA_CHOICES,
        default='es',
        verbose_name='Idioma'
    )
    
    ZONA_HORARIA_CHOICES = [
        ('America/Santiago', 'Santiago (Chile)'),
        ('America/Argentina/Buenos_Aires', 'Buenos Aires (Argentina)'),
        ('America/Sao_Paulo', 'São Paulo (Brasil)'),
        ('America/Lima', 'Lima (Perú)'),
        ('America/Bogota', 'Bogotá (Colombia)'),
        ('America/Mexico_City', 'Ciudad de México (México)'),
    ]
    zona_horaria = models.CharField(
        max_length=50,
        choices=ZONA_HORARIA_CHOICES,
        default='America/Santiago',
        verbose_name='Zona Horaria'
    )
    
    # Privacidad
    perfil_publico = models.BooleanField(
        default=True,
        verbose_name='Perfil Público',
        help_text='Si está desactivado, tu perfil no aparecerá en búsquedas públicas'
    )
    mostrar_estadisticas = models.BooleanField(
        default=False,
        verbose_name='Mostrar Estadísticas Públicas',
        help_text='Mostrar número de visitas y contactos en tu perfil público'
    )
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return self.nombre_empresa


class SolicitudContacto(models.Model):
    """Modelo para solicitudes de contacto a proveedores"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='solicitudes_contacto',
        verbose_name='Proveedor'
    )
    mensaje = models.TextField(
        verbose_name='Mensaje',
        help_text='Mensaje de presentación'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado'
    )
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Solicitud'
    )
    fecha_respuesta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Respuesta'
    )
    
    class Meta:
        db_table = 'solicitud_contacto'
        verbose_name = 'Solicitud de Contacto'
        verbose_name_plural = 'Solicitudes de Contacto'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Solicitud a {self.proveedor.nombre_empresa} - {self.estado}"
    
    def aceptar(self):
        """Marcar solicitud como aceptada"""
        self.estado = 'aceptada'
        self.fecha_respuesta = timezone.now()
        self.save()
    
    def rechazar(self):
        """Marcar solicitud como rechazada"""
        self.estado = 'rechazada'
        self.fecha_respuesta = timezone.now()
        self.save()


class ProductoServicio(models.Model):
    """Modelo para productos y servicios ofrecidos por proveedores"""
    
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='productos_servicios',
        verbose_name='Proveedor'
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Producto/Servicio'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    
    categorias = models.CharField(
        max_length=40, 
        choices=Proveedor.CATEGORIAS_CHOICES, 
        default='COM',
        verbose_name='Categorias'
    )

    precio_referencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio de Referencia',
        help_text='Precio aproximado o de referencia'
    )
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name='Imagen del Producto'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    destacado = models.BooleanField(
        default=False,
        verbose_name='Destacado',
        help_text='Destacar este producto en el perfil'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        db_table = 'producto_servicio'
        verbose_name = 'Producto/Servicio'
        verbose_name_plural = 'Productos/Servicios'
        ordering = ['-destacado', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.proveedor.nombre_empresa}"


class Promocion(models.Model):
    """Modelo para promociones de proveedores"""
    
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='promociones',
        verbose_name='Proveedor'
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título de la Promoción'
    )
    descripcion = models.TextField(
        verbose_name='Descripción'
    )
    imagen = models.ImageField(
        upload_to='promociones/',
        blank=True,
        null=True,
        verbose_name='Imagen de la Promoción'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        db_table = 'promocion'
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.titulo} - {self.proveedor.nombre_empresa}"
    
    def esta_vigente(self):
        """Verificar si la promoción está vigente"""
        from django.utils import timezone
        hoy = timezone.now().date()
        return self.activo and self.fecha_inicio <= hoy <= self.fecha_fin