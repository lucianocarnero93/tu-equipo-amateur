from django.contrib import admin
from .models import Estadistica


@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('partido', 'nombre_jugador', 'goles', 'asistencias',
                    'tiempo_jugado', 'tarjetas_amarillas', 'tarjetas_rojas')
    list_filter = ('tiempo_jugado', 'partido')
    search_fields = ('nombre_jugador', 'partido__rival')
    ordering = ('partido', 'nombre_jugador')
    readonly_fields = ('fecha_registro', 'nombre_jugador')