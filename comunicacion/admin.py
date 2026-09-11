from django.contrib import admin
from .models import Anuncio

@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridad', 'autor', 'fecha_publicacion', 'activo')
    list_filter = ('prioridad', 'activo', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido', 'autor__username')
    ordering = ('-fecha_publicacion',)
    readonly_fields = ('fecha_publicacion', 'fecha_actualizacion')
    list_editable = ('activo',)
