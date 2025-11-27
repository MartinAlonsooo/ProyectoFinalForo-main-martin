# usuarios/urls.py (CONTENIDO COMPLETO)

from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),

    # PLATFORM/FORUM
    path('plataforma/', views.plataforma_comerciante_view, name='plataforma_comerciante'),
    path('publicar/', views.publicar_post_view, name='crear_publicacion'),
    
    # PERFIL Y BENEFICIOS
    path('perfil/', views.perfil_view, name='perfil'),
    path('beneficios/', views.beneficios_view, name='beneficios'),
    
    # NUEVOS COMERCIOS (Muro/Blog)
    path('nuevos-comercios/', views.nuevos_comercios_view, name='comerciantes'), 
    
    # DIRECTORIO DE PROVEEDORES
    path('directorio/', views.directorio_view, name='directorio'),
    path('directorio/<int:pk>/', views.proveedor_perfil_view, name='proveedor_perfil'),
    
    # GESTIÓN DE ROLES (NUEVAS RUTAS AÑADIDAS)
    path('proveedores/dashboard/', views.proveedor_dashboard_view, name='proveedor_dashboard'),
    
    # POSTS (DETALLE, COMENTARIO, LIKE)
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('post/<int:post_id>/comentar/', views.add_comment_view, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post_view, name='like_post'),

    path('redes-sociales/', views.redes_sociales_view, name='redes_sociales'),
]