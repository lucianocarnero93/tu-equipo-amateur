from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import random
import string


def generar_codigo_invitacion():
    """Genera un código aleatorio de 8 caracteres para invitar al equipo."""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=8))


class Equipo(models.Model):
    """Un equipo de fútbol amateur."""

    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    escudo = models.ImageField(upload_to='escudos/', blank=True, null=True)
    color_primario = models.CharField(max_length=7, default='#1a73e8')
    color_secundario = models.CharField(max_length=7, default='#34a853')
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        """Genera un slug único a partir del nombre."""
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            contador = 1
            while Equipo.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{contador}'
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_iniciales(self):
        """Devuelve las iniciales del nombre para mostrar si no hay escudo."""
        palabras = self.nombre.split()
        if len(palabras) >= 2:
            return (palabras[0][0] + palabras[1][0]).upper()
        return self.nombre[:2].upper()

    def cantidad_jugadores_activos(self):
        """Cuenta cuántos jugadores activos tiene el equipo."""
        return self.jugadores.filter(activo=True).count()

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['nombre']


class Membresia(models.Model):
    """Relación entre un User y un Equipo, con un rol específico."""

    ROLES = [
        ('DT', 'Director Técnico'),
        ('AYUDANTE', 'Ayudante de Campo'),
        ('JUGADOR', 'Jugador'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membresias')
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='membresias')
    rol = models.CharField(max_length=20, choices=ROLES)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.equipo.nombre} ({self.get_rol_display()})'

    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'
        unique_together = ('usuario', 'equipo')
        ordering = ['equipo', 'rol', 'usuario__username']


class Invitacion(models.Model):
    """Código de invitación para que los jugadores se sumen al equipo."""

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='invitaciones')
    codigo = models.CharField(max_length=10, unique=True, default=generar_codigo_invitacion)
    creada_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitaciones_creadas')
    rol_asignado = models.CharField(max_length=20, choices=Membresia.ROLES, default='JUGADOR')
    usos_maximos = models.PositiveIntegerField(default=0, help_text='0 = ilimitado')
    usos_actuales = models.PositiveIntegerField(default=0)
    expira = models.DateTimeField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invitación a {self.equipo.nombre} ({self.codigo})'

    def es_valida(self):
        """Devuelve True si la invitación todavía se puede usar."""
        if not self.activa:
            return False
        if self.usos_maximos > 0 and self.usos_actuales >= self.usos_maximos:
            return False
        if self.expira and self.expira < timezone.now():
            return False
        return True

    class Meta:
        verbose_name = 'Invitación'
        verbose_name_plural = 'Invitaciones'
        ordering = ['-fecha_creacion']


class SolicitudIngreso(models.Model):
    """Solicitud de un usuario para unirse a un equipo."""

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='solicitudes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_ingreso')
    mensaje = models.TextField(blank=True, null=True, help_text='Mensaje opcional para el DT')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.usuario.username} → {self.equipo.nombre} ({self.get_estado_display()})'

    class Meta:
        verbose_name = 'Solicitud de ingreso'
        verbose_name_plural = 'Solicitudes de ingreso'
        unique_together = ('equipo', 'usuario')
        ordering = ['-fecha_solicitud']
