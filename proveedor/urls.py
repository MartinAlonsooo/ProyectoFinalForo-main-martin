from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    # ============================================================================
    # AUTENTICACIÓN
    # ============================================================================
    path('registro/', views.registro_proveedor, name='registro'),
    path('login/', views.login_proveedor, name='login'),
    path('logout/', views.logout_proveedor, name='logout'),
    
    # ============================================================================
    # PERFIL Y CONFIGURACIÓN
    # ============================================================================
    path('perfil/', views.perfil_proveedor, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('configuracion/', views.configuracion_proveedor, name='configuracion'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # ============================================================================
    # PRODUCTOS Y SERVICIOS
    # ============================================================================
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    
    # ============================================================================
    # PROMOCIONES
    # ============================================================================
    path('promociones/', views.lista_promociones, name='lista_promociones'),
    path('promociones/crear/', views.crear_promocion, name='crear_promocion'),
    path('promociones/<int:pk>/editar/', views.editar_promocion, name='editar_promocion'),
    path('promociones/<int:pk>/eliminar/', views.eliminar_promocion, name='eliminar_promocion'),
    
    # ============================================================================
    # SOLICITUDES DE CONTACTO
    # ============================================================================
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/<int:pk>/<str:accion>/', views.responder_solicitud, name='responder_solicitud'),
    
    # ============================================================================
    # BÚSQUEDA Y PERFIL PÚBLICO
    # ============================================================================
    path('buscar/', views.buscar_proveedores, name='buscar'),
    path('<int:pk>/', views.detalle_proveedor_publico, name='detalle_publico'),
    path('<int:pk>/contactar/', views.enviar_solicitud_contacto, name='enviar_solicitud'),
    
]