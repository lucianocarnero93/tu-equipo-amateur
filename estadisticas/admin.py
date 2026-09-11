from django.contrib import admin
from .models import Estadistica

@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('partido', 'jugador', 'goles', 'asistencias', 'minutos_jugados', 
                    'tarjetas_amarillas', 'tarjetas_rojas')
    list_filter = ('partido', 'jugador__posicion')
    search_fields = ('jugador__nombre', 'jugador__apellido', 'partido__rival')
    ordering = ('partido', 'jugador__apellido')
    readonly_fields = ('fecha_registro',)
