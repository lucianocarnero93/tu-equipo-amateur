from django import forms
from .models import Asistencia

class AsistenciaForm(forms.ModelForm):
    """Formulario para confirmar asistencia a un partido"""
    
    class Meta:
        model = Asistencia
        fields = ['estado', 'comentario']
        widgets = {
            'estado': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'comentario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comentario opcional (ej: llego tarde)'
            }),
        }
        labels = {
            'estado': '¿Vas al partido?',
            'comentario': 'Comentario',
        }
