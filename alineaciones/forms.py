from django import forms
from .models import Alineacion

class AlineacionForm(forms.ModelForm):
    """Formulario para agregar/editar un jugador en la alineación"""
    
    class Meta:
        model = Alineacion
        fields = ['jugador', 'tipo', 'posicion_cancha', 'orden']
        widgets = {
            'jugador': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'posicion_cancha': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Lateral derecho'
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'jugador': 'Jugador',
            'tipo': 'Tipo',
            'posicion_cancha': 'Posición en la cancha',
            'orden': 'Orden',
        }
