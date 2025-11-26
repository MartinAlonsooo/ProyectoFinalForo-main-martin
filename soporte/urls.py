# soporte/urls.py
from django.urls import path
from .views import panel_soporte, ticket_detalle, cerrar_ticket

app_name = 'soporte'

urlpatterns = [
    path('panel/', panel_soporte, name='soporte_panel'),
    path('ticket/<int:ticket_id>/', ticket_detalle, name='soporte_ticket_detalle'),
    path('ticket/<int:ticket_id>/cerrar/', cerrar_ticket, name='soporte_cerrar_ticket'),
]
