from django.db import models
from partidos.models import Partido
from jugadores.models import Jugador

class Estadistica(models.Model):
    """Modelo para registrar las estadísticas individuales de cada jugador en un partido"""
    
    # Relaciones
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='estadisticas')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='estadisticas')
    
    # Estadísticas
    goles = models.PositiveIntegerField(default=0)
    asistencias = models.PositiveIntegerField(default=0)
    minutos_jugados = models.PositiveIntegerField(default=0)
    
    # Tarjetas
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    tarjetas_rojas = models.PositiveIntegerField(default=0)
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    # Fecha de registro
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.jugador.get_nombre_completo()} - {self.partido.rival} ({self.goles} goles)"
    
    class Meta:
        verbose_name = 'Estadística'
        verbose_name_plural = 'Estadísticas'
        unique_together = ('partido', 'jugador')  # Un jugador solo puede tener una estadística por partido
        ordering = ['partido', 'jugador__apellido']
