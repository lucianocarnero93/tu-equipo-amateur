from django import forms
from .models import Estadistica


class EstadisticaForm(forms.ModelForm):
    """Formulario para cargar los números de un jugador en un partido"""

    class Meta:
        model = Estadistica
        fields = [
            'jugador',
            'goles',
            'asistencias',
            'tiempo_jugado',
            'tarjetas_amarillas',
            'tarjetas_rojas',
            'observaciones',
        ]
        widgets = {
            'jugador': forms.Select(attrs={'class': 'form-control'}),
            'goles': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'asistencias': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'tiempo_jugado': forms.Select(attrs={'class': 'form-control'}),
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
            'tiempo_jugado': 'Tiempo jugado',
            'tarjetas_amarillas': 'Amarillas',
            'tarjetas_rojas': 'Rojas',
            'observaciones': 'Observaciones',
        }

    def clean(self):
        """Validaciones generales que no dependen del partido."""
        cleaned_data = super().clean()

        tarjetas_amarillas = cleaned_data.get('tarjetas_amarillas', 0) or 0
        tarjetas_rojas = cleaned_data.get('tarjetas_rojas', 0) or 0

        if tarjetas_amarillas > 2:
            raise forms.ValidationError(
                'Un jugador no puede tener más de 2 tarjetas amarillas en un partido.'
            )

        if tarjetas_rojas > 1:
            raise forms.ValidationError(
                'Un jugador no puede tener más de 1 tarjeta roja en un partido.'
            )

        return cleaned_data