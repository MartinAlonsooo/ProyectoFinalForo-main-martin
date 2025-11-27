from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('perfil/', views.perfil_view, name='perfil'),
    path('plataforma/', views.plataforma_comerciante_view, name='plataforma_comerciante'),
    path('publicar/', views.publicar_post_view, name='crear_publicacion'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),
    
    path('post/<int:post_id>/comentar/', views.add_comment_view, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post_view, name='like_post'),
    path('beneficios/', views.beneficios_view, name='beneficios'),
    path('solicitar-proveedor/', views.solicitar_rol_proveedor_view, name='solicitar_rol_proveedor'),
]