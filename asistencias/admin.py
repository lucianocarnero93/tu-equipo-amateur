from django.contrib import admin
from .models import Asistencia

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('partido', 'jugador', 'estado', 'fecha_respuesta')
    list_filter = ('estado', 'partido')
    search_fields = ('jugador__nombre', 'jugador__apellido', 'partido__rival')
    ordering = ('partido', 'jugador__apellido')
    readonly_fields = ('fecha_respuesta',)
