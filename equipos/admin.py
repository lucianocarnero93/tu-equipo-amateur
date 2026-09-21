from django.contrib import admin
from .models import Equipo, Membresia, Invitacion, SolicitudIngreso


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'color_primario', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion',)


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'rol', 'activo', 'fecha_ingreso')
    list_filter = ('rol', 'activo', 'equipo')
    search_fields = ('usuario__username', 'equipo__nombre')
    raw_id_fields = ('usuario',)


@admin.register(Invitacion)
class InvitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'equipo', 'rol_asignado', 'usos_actuales', 'usos_maximos', 'activa')
    list_filter = ('activa', 'equipo', 'rol_asignado')
    search_fields = ('codigo', 'equipo__nombre')
    readonly_fields = ('usos_actuales', 'fecha_creacion')


@admin.register(SolicitudIngreso)
class SolicitudIngresoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'equipo')
    search_fields = ('usuario__username', 'equipo__nombre')
    readonly_fields = ('fecha_solicitud',)
