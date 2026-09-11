from django.contrib import admin
from .models import Partido

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'rival', 'lugar', 'get_resultado', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('rival', 'lugar')
    ordering = ('-fecha', '-hora')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
