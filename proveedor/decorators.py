from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def proveedor_required(view_func):
    """
    Decorador para verificar que el usuario sea un proveedor autenticado
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar si hay sesión de proveedor
        if not request.session.get('proveedor_email'):
            messages.warning(request, 'Debes iniciar sesión como proveedor.')
            return redirect('proveedores:login_proveedor')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper