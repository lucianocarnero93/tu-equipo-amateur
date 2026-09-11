from django import forms
from .models import Estadistica


class EstadisticaForm(forms.ModelForm):
    """Formulario para cargar los números de un jugador en un partido"""

    class Meta:
        model = Estadistica
        fields = ['jugador', 'goles', 'asistencias', 'minutos_jugados',
                  'tarjetas_amarillas', 'tarjetas_rojas', 'observaciones']
        widgets = {
            'jugador': forms.Select(attrs={'class': 'form-control'}),
            'goles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'asistencias': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'minutos_jugados': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 120}),
            'tarjetas_amarillas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 2}),
            'tarjetas_rojas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 1}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alguna nota sobre cómo jugó'
            }),
        }
        labels = {
            'jugador': 'Jugador',
            'goles': 'Goles',
            'asistencias': 'Asistencias',
            'minutos_jugados': 'Minutos jugados',
            'tarjetas_amarillas': 'Amarillas',
            'tarjetas_rojas': 'Rojas',
            'observaciones': 'Observaciones',
        }
