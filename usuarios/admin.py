from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_rol_display', 'telefono', 'fecha_registro')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'usuario__email', 'telefono')
    raw_id_fields = ('usuario',)
