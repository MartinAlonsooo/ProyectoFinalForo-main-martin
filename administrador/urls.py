# administrador/urls.py

from django.urls import path
from .views import (
    panel_admin_view,
    crear_comerciante_view,
    editar_comerciante_view,
    eliminar_comerciante_view
)

urlpatterns = [
    path('', panel_admin_view, name='panel_admin'),
    path('comerciantes/crear/', crear_comerciante_view, name='crear_comerciante'),
    path('comerciantes/<int:comerciante_id>/editar/', editar_comerciante_view, name='editar_comerciante'),
    path('comerciantes/<int:comerciante_id>/eliminar/', eliminar_comerciante_view, name='eliminar_comerciante'),
]
