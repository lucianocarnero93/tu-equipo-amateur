from django.db import models
from partidos.models import Partido
from jugadores.models import Jugador


class Estadistica(models.Model):
    """Modelo para registrar las estadísticas individuales de cada jugador en un partido"""

    # Opciones de tiempo jugado (en amateur no se calculan minutos exactos)
    TIEMPO = [
        ('COMPLETO', 'Partido completo'),
        ('SALIO_2DO', 'Salió en el segundo tiempo'),
        ('ENTRO_2DO', 'Entró en el segundo tiempo'),
        ('POCO', 'Jugó pocos minutos'),
        ('NO_JUGO', 'No ingresó'),
    ]

    # Relaciones
    partido = models.ForeignKey(
        Partido,
        on_delete=models.CASCADE,
        related_name='estadisticas'
    )
    jugador = models.ForeignKey(
        Jugador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estadisticas'
    )

    # Guardamos el nombre por si se borra el jugador (para preservar el historial)
    nombre_jugador = models.CharField(
        max_length=200,
        blank=True,
        help_text='Se completa automáticamente. Sirve para conservar el historial si se borra el jugador.'
    )

    # Estadísticas principales
    goles = models.PositiveIntegerField(default=0)
    asistencias = models.PositiveIntegerField(default=0)

    # Tiempo jugado
    tiempo_jugado = models.CharField(
        max_length=20,
        choices=TIEMPO,
        default='COMPLETO'
    )

    # Tarjetas
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    tarjetas_rojas = models.PositiveIntegerField(default=0)

    # Observaciones
    observaciones = models.TextField(blank=True, null=True)

    # Fecha de registro
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_jugador or 'Jugador'} - {self.partido.rival} ({self.goles} goles)"

    def save(self, *args, **kwargs):
        """Guarda el nombre del jugador automáticamente antes de persistir."""
        if self.jugador:
            self.nombre_jugador = self.jugador.get_nombre_completo()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Estadística'
        verbose_name_plural = 'Estadísticas'
        unique_together = ('partido', 'jugador')
        ordering = ['partido', 'nombre_jugador']
