from django.db import models
from django.contrib.auth.models import User
from partidos.models import Partido
from jugadores.models import Jugador

class Asistencia(models.Model):
    """Modelo para gestionar la asistencia de jugadores a partidos"""
    
    # Estados de asistencia
    ESTADOS = [
        ('CONFIRMADO', 'Confirmado'),
        ('RECHAZADO', 'No voy'),
        ('DUDA', 'Duda'),
    ]
    
    # Relaciones
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='asistencias')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='asistencias')
    
    # Estado de la asistencia
    estado = models.CharField(max_length=20, choices=ESTADOS, default='DUDA')
    
    # Comentario opcional (motivo de ausencia, etc.)
    comentario = models.CharField(max_length=200, blank=True, null=True)
    
    # Fecha de confirmación
    fecha_respuesta = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.jugador.get_nombre_completo()} - {self.partido.rival} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ('partido', 'jugador')  # Un jugador solo puede tener una asistencia por partido
        ordering = ['partido', 'jugador__apellido']
