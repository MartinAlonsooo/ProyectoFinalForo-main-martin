from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Proveedor


class ProveedorBackend(BaseBackend):
    """
    Backend de autenticación personalizado para el modelo Proveedor
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Autentica un proveedor usando email y password
        """
        try:
            # Buscar proveedor por email
            proveedor = Proveedor.objects.get(email=email, activo=True)
            
            # Verificar contraseña
            if check_password(password, proveedor.password):
                return proveedor
            
        except Proveedor.DoesNotExist:
            # Ejecutar el hasher por defecto para evitar ataques de timing
            check_password(password, 'dummy')
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Obtiene un proveedor por su ID
        """
        try:
            return Proveedor.objects.get(pk=user_id)
        except Proveedor.DoesNotExist:
            return None