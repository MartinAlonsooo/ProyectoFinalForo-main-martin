from django.contrib import admin
from .models import (
    Comerciante,
    Post,
    Comentario,
    Like,
    Beneficio,
)


@admin.register(Comerciante)
class ComercianteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_apellido',
        'email',
        'rol',
        'comuna',
        'nombre_negocio',
        'puntos',
        'nivel_actual',
        'es_proveedor',
        'fecha_registro',
        'ultima_conexion',
    )
    list_filter = (
        'rol',
        'comuna',
        'nivel_actual',
        'es_proveedor',
        'relacion_negocio',
        'tipo_negocio',
    )
    search_fields = ('nombre_apellido', 'email', 'nombre_negocio', 'comuna')
    readonly_fields = ('fecha_registro', 'ultima_conexion', 'puntos', 'nivel_actual')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'comerciante', 'categoria', 'fecha_publicacion')
    list_filter = ('categoria', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido', 'comerciante__nombre_apellido')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('post', 'comerciante', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('contenido', 'comerciante__nombre_apellido', 'post__titulo')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'comerciante')
    search_fields = ('post__titulo', 'comerciante__nombre_apellido')


@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'categoria',
        'puntos_requeridos',
        'estado',
        'vence',
        'fecha_creacion',
    )
    list_filter = ('categoria', 'estado')
    search_fields = ('titulo', 'descripcion')



