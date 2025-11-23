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
            'rol',
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        password = self.cleaned_data.get('raw_password')
        if password:
            instance.password_hash = make_password(password)

        if commit:
            instance.save()

        return instance
