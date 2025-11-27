from .models import Proveedor


class ProveedorMiddleware:
    """
    Middleware que agrega el proveedor autenticado al objeto request
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Obtener el ID del proveedor de la sesión
        proveedor_id = request.session.get('proveedor_id')
        
        if proveedor_id:
            try:
                # Cargar el proveedor y agregarlo al request
                request.proveedor = Proveedor.objects.get(id=proveedor_id, activo=True)
            except Proveedor.DoesNotExist:
                # Si el proveedor no existe o está inactivo, limpiar la sesión
                request.session.flush()
                request.proveedor = None
        else:
            request.proveedor = None
        
        response = self.get_response(request)
        return response