from django.db import models
from django.contrib.auth.models import User


class Jugador(models.Model):
    """Modelo para gestionar los jugadores del equipo"""

    POSICIONES = [
        ('ARQUERO', 'Arquero'),
        ('DEFENSOR', 'Defensor'),
        ('MEDIOCAMPISTA', 'Mediocampista'),
        ('DELANTERO', 'Delantero'),
    ]

    # FK al equipo
    equipo = models.ForeignKey(
        'equipos.Equipo',
        on_delete=models.CASCADE,
        related_name='jugadores',
        null=True,
        blank=True
    )

    # Perfil del usuario
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='jugador'
    )

    # Datos personales
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    # Datos deportivos
    posicion = models.CharField(max_length=20, choices=POSICIONES, blank=True, null=True)
    dorsal = models.PositiveIntegerField(blank=True, null=True)

    # Estado
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.dorsal})"

    def get_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = 'Jugador'
        verbose_name_plural = 'Jugadores'
        ordering = ['dorsal', 'apellido', 'nombre']
