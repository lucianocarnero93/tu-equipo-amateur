from django.db import models
from django.contrib.auth.models import User

class Anuncio(models.Model):
    """Modelo para gestionar anuncios del cuerpo técnico"""
    
    # Prioridad del anuncio
    PRIORIDADES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    # Datos del anuncio
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='MEDIA')
    
    # Autor
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anuncios')
    
    # Fechas
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo
    
    def get_prioridad_color(self):
        colores = {
            'BAJA': 'secondary',
            'MEDIA': 'info',
            'ALTA': 'warning',
            'URGENTE': 'danger',
        }
        return colores.get(self.prioridad, 'secondary')
    
    class Meta:
        verbose_name = 'Anuncio'
        verbose_name_plural = 'Anuncios'
        ordering = ['-fecha_publicacion']
