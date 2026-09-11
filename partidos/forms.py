from django import forms
from .models import Partido

class PartidoForm(forms.ModelForm):
    """Formulario para crear y editar partidos"""
    
    class Meta:
        model = Partido
        fields = ['fecha', 'hora', 'lugar', 'rival', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estadio, cancha, etc.'}),
            'rival': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del equipo rival'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'fecha': 'Fecha del Partido',
            'hora': 'Hora del Partido',
            'lugar': 'Lugar',
            'rival': 'Rival',
            'estado': 'Estado',
        }

class ResultadoForm(forms.ModelForm):
    """Formulario para actualizar el resultado de un partido"""
    
    class Meta:
        model = Partido
        fields = ['goles_local', 'goles_visitante', 'estado']
        widgets = {
            'goles_local': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'goles_visitante': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'goles_local': 'Goles de Tu Equipo',
            'goles_visitante': 'Goles del Rival',
            'estado': 'Estado',
        }
