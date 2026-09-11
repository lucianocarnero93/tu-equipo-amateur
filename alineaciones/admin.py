from django.contrib import admin
from .models import Alineacion

@admin.register(Alineacion)
class AlineacionAdmin(admin.ModelAdmin):
    list_display = ('partido', 'jugador', 'tipo', 'posicion_cancha', 'orden')
    list_filter = ('tipo', 'partido')
    search_fields = ('jugador__nombre', 'jugador__apellido', 'partido__rival')
    ordering = ('partido', 'tipo', 'orden')
