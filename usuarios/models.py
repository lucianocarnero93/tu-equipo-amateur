from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    """Modelo para extender el usuario de Django"""
    
    # Roles disponibles
    ROLES = [
        ('DT', 'Director Técnico'),
        ('AYUDANTE', 'Ayudante de Campo'),
        ('JUGADOR', 'Jugador'),
        ('INVITADO', 'Invitado'),
    ]
    
    # Posiciones para jugadores
    POSICIONES = [
        ('ARQUERO', 'Arquero'),
        ('DEFENSOR', 'Defensor'),
        ('MEDIOCAMPISTA', 'Mediocampista'),
        ('DELANTERO', 'Delantero'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='JUGADOR')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    posicion = models.CharField(max_length=20, choices=POSICIONES, blank=True, null=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

# Señal para crear automáticamente el perfil cuando se crea un usuario
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()
