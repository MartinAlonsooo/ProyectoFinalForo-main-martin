# usuarios/urls.py (CÓDIGO COMPLETO MODIFICADO)

from django.urls import path
from . import views
from django.views.generic import RedirectView # <-- Importamos para redireccionar

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
    
    # NOTICIAS
    path('noticias/', views.noticias_view, name='noticias'),
    
    # POSTS
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('post/<int:post_id>/comentar/', views.add_comment_view, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post_view, name='like_post'),
    
    # --- REDIRECCIONES A LA NUEVA APP 'PROVEEDORES' ---
    # Esto asegura que los enlaces viejos sigan funcionando:
    path('directorio/', RedirectView.as_view(url='/proveedores/', permanent=True), name='directorio'),
    path('directorio/<int:pk>/', RedirectView.as_view(url='/proveedores/%(pk)s/', permanent=True), name='proveedor_perfil'),
    path('proveedor/solicitar/', RedirectView.as_view(url='/proveedores/panel/crear/', permanent=True), name='solicitar_proveedor'),
    path('proveedores/dashboard/', RedirectView.as_view(url='/proveedores/panel/', permanent=True), name='proveedor_dashboard'),
]