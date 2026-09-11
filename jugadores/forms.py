from django import forms
from .models import Jugador

class JugadorForm(forms.ModelForm):
    """Formulario para crear y editar jugadores"""
    
    class Meta:
        model = Jugador
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'posicion', 'dorsal', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'posicion': forms.Select(attrs={'class': 'form-control'}),
            'dorsal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de camiseta'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'posicion': 'Posición',
            'dorsal': 'Número de Camiseta',
            'activo': 'Jugador Activo',
        }
