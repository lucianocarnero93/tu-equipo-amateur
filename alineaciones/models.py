from django.db import models
from partidos.models import Partido
from jugadores.models import Jugador

class Alineacion(models.Model):
    """Modelo para gestionar la alineación de jugadores en un partido"""
    
    # Tipos de jugador en la alineación
    TIPOS = [
        ('TITULAR', 'Titular'),
        ('SUPLENTE', 'Suplente'),
    ]
    
    # Relaciones
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='alineaciones')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='alineaciones')
    
    # Tipo de jugador
    tipo = models.CharField(max_length=20, choices=TIPOS, default='TITULAR')
    
    # Posición en la cancha (opcional)
    posicion_cancha = models.CharField(max_length=50, blank=True, null=True,
        help_text="Ej: Lateral derecho, Mediocampista ofensivo, etc.")
    
    # Orden dentro de la alineación (para mostrar en orden)
    orden = models.PositiveIntegerField(default=0)
    
    # Fecha de creación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.jugador.get_nombre_completo()} - {self.partido.rival} ({self.get_tipo_display()})"
    
    class Meta:
        verbose_name = 'Alineación'
        verbose_name_plural = 'Alineaciones'
        unique_together = ('partido', 'jugador')  # Un jugador solo puede estar una vez por partido
        ordering = ['partido', 'tipo', 'orden']
