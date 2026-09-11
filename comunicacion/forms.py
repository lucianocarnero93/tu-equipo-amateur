from django import forms
from .models import Anuncio

class AnuncioForm(forms.ModelForm):
    """Formulario para crear y editar anuncios"""
    
    class Meta:
        model = Anuncio
        fields = ['titulo', 'contenido', 'prioridad', 'activo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del anuncio'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribí el contenido del anuncio...'
            }),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titulo': 'Título',
            'contenido': 'Contenido',
            'prioridad': 'Prioridad',
            'activo': 'Anuncio Activo',
        }
