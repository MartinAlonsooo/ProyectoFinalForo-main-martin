# administrador/forms.py

from django import forms
from django.contrib.auth.hashers import make_password
from usuarios.models import Comerciante

class ComercianteAdminForm(forms.ModelForm):

    raw_password = forms.CharField(
        required=False,
        label="Contraseña nueva",
        widget=forms.PasswordInput
    )

    class Meta:
        model = Comerciante
        fields = [
            'nombre_apellido',
            'email',
            'whatsapp',
            'relacion_negocio',
            'tipo_negocio',
            'comuna',
            'nombre_negocio',
            'rol',           # 👈 aquí aparecerá COMERCIANTE / PROVEEDOR / ADMIN
            # ya NO necesitamos mostrar es_proveedor al admin
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Si el admin escribe contraseña nueva → actualizar password_hash
        password = self.cleaned_data.get('raw_password')
        if password:
            instance.password_hash = make_password(password)

        # Sincronizar campo es_proveedor con el rol
        if instance.rol == 'PROVEEDOR':
            instance.es_proveedor = True
        else:
            instance.es_proveedor = False

        if commit:
            instance.save()

        return instance
