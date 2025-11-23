# administrador/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from usuarios.models import Comerciante
from usuarios import views as usuarios_views 
from .forms import ComercianteAdminForm

def require_admin():
    """
    Revisa si el usuario global actual es admin.
    Leemos siempre desde usuarios_views.current_logged_in_user
    para que vea el valor actualizado que se setea en login_view.
    """
    user = usuarios_views.current_logged_in_user
    if not user:
        return False
    return user.rol == 'ADMIN'



def panel_admin_view(request):
    if not require_admin():
        return redirect('login')

    admin_user = usuarios_views.current_logged_in_user  # 👈 aquí
    comerciantes = Comerciante.objects.all().order_by('-fecha_registro')

    return render(request, 'administrador/panel_admin.html', {
        'comerciantes': comerciantes,
        'admin': admin_user,
    })


def crear_comerciante_view(request):
    if not require_admin():
        return redirect('login')

    if request.method == 'POST':
        form = ComercianteAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Comerciante creado")
            return redirect('panel_admin')
    else:
        form = ComercianteAdminForm()

    return render(request, "administrador/crear_comerciante.html", {"form": form})


def editar_comerciante_view(request, comerciante_id):
    if not require_admin():
        return redirect('login')

    comerciante = get_object_or_404(Comerciante, id=comerciante_id)

    if request.method == 'POST':
        form = ComercianteAdminForm(request.POST, instance=comerciante)
        if form.is_valid():
            form.save()
            messages.success(request, "Comerciante actualizado")
            return redirect('panel_admin')
    else:
        form = ComercianteAdminForm(instance=comerciante)

    return render(request, "administrador/editar_comerciante.html", {
        "form": form,
        "comerciante": comerciante
    })


def eliminar_comerciante_view(request, comerciante_id):
    if not require_admin():
        return redirect('login')

    comerciante = get_object_or_404(Comerciante, id=comerciante_id)

    if request.method == 'POST':
        comerciante.delete()
        messages.success(request, "Eliminado correctamente")
        return redirect('panel_admin')

    return render(request, "administrador/confirmar_eliminar.html", {
        "comerciante": comerciante
    })
