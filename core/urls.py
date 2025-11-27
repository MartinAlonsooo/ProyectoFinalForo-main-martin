# usuarios/urls.py
from django.urls import path
from . import views
app_name = 'core' 
urlpatterns = [
    

path('', views.index, name='index_principal'),
path('registro/', views.register_view, name='registro'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),

#Administrador
path('admin/dashboard/', views.admin_login_view, name='admin_dashboard'),
path('comerciante/dashboard/', views.dashboard_comerciante, name='comerciante_dashboard'),
path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
path('contacto/', views.contacto, name='contacto'),
path('beneficios/', views.beneficios, name='beneficios'),
]
