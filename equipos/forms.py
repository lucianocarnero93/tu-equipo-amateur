from django import forms
from .models import Equipo


class EquipoForm(forms.ModelForm):
    """Formulario para crear o editar un equipo."""

    class Meta:
        model = Equipo
        fields = ['nombre', 'escudo', 'color_primario', 'color_secundario', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Los Pibes FC'
            }),
            'escudo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'color_primario': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'color_secundario': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Contanos algo del equipo (opcional)'
            }),
        }
        labels = {
            'nombre': 'Nombre del equipo',
            'escudo': 'Escudo (opcional)',
            'color_primario': 'Color primario',
            'color_secundario': 'Color secundario',
            'descripcion': 'Descripción (opcional)',
        }

    def clean_nombre(self):
        """Valida que no exista otro equipo con el mismo nombre."""
        nombre = self.cleaned_data.get('nombre')
        if nombre and Equipo.objects.filter(nombre__iexact=nombre).exists():
            if self.instance and self.instance.pk:
                if Equipo.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un equipo con ese nombre.')
            else:
                raise forms.ValidationError('Ya existe un equipo con ese nombre.')
        return nombre


class InvitacionForm(forms.Form):
    """Formulario para crear una invitación."""

    ROLES = [
        ('JUGADOR', 'Jugador'),
        ('AYUDANTE', 'Ayudante de Campo'),
        ('DT', 'Director Técnico'),
    ]

    rol_asignado = forms.ChoiceField(
        choices=ROLES,
        initial='JUGADOR',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rol a asignar'
    )

    usos_maximos = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0 = ilimitado'
        }),
        label='Usos máximos',
        help_text='0 significa ilimitado'
    )


class SolicitudForm(forms.Form):
    """Formulario para solicitar ingreso a un equipo."""

    mensaje = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Contale al DT por qué querés unirte (opcional)'
        }),
        label='Mensaje para el DT'
    )
