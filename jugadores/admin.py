from django.contrib import admin
from .models import Jugador

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('dorsal', 'nombre', 'apellido', 'posicion', 'telefono', 'activo')
    list_filter = ('posicion', 'activo')
    search_fields = ('nombre', 'apellido', 'email', 'telefono')
    list_editable = ('activo',)
    ordering = ('dorsal', 'apellido')
