from django.db import models
from django.contrib.auth.models import User

class Partido(models.Model):
    """Modelo para gestionar los partidos del equipo"""
    
    # Estados del partido
    ESTADOS = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    # Datos del partido
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=200)
    rival = models.CharField(max_length=100)
    
    # Resultado
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PROGRAMADO')
    
    # Datos de registro
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='partidos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.rival} - {self.fecha} {self.hora}"
    
    def get_resultado(self):
        if self.estado == 'FINALIZADO':
            return f"{self.goles_local} - {self.goles_visitante}"
        return "Sin disputar"
    
    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'
        ordering = ['-fecha', '-hora']
