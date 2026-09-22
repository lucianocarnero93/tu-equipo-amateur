from django.urls import path
from . import views

app_name = 'equipos'

urlpatterns = [
    # Equipos
    path('', views.mis_equipos, name='mis_equipos'),
    path('crear/', views.crear_equipo, name='crear'),
    
    # Invitaciones
    path('invitaciones/', views.lista_invitaciones, name='lista_invitaciones'),
    path('invitaciones/crear/', views.crear_invitacion, name='crear_invitacion'),
    path('invitaciones/<int:pk>/desactivar/', views.desactivar_invitacion, name='desactivar_invitacion'),
    path('unirse/', views.unirse_con_codigo, name='unirse'),
    
    # Solicitudes
    path('buscar/', views.buscar_equipos, name='buscar'),
    path('solicitar/<slug:slug>/', views.solicitar_ingreso, name='solicitar'),
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/<int:pk>/aceptar/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('solicitudes/<int:pk>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    
    # Miembros y transferencia (usar rutas específicas ANTES del slug genérico)
    path('<slug:slug>/miembros/', views.lista_miembros, name='lista_miembros'),
    path('<slug:slug>/transferir-dt/', views.transferir_dt, name='transferir_dt'),
    path('<slug:slug>/transferir-ayudante/', views.transferir_ayudante, name='transferir_ayudante'),
    path('<slug:slug>/salir/', views.salir_equipo, name='salir_equipo'),
    path('<slug:slug>/expulsar/<int:membresia_id>/', views.expulsar_miembro, name='expulsar_miembro'),
    
    # Detalle y cambio (SIEMPRE al final)
    path('<slug:slug>/', views.detalle_equipo, name='detalle'),
    path('<slug:slug>/cambiar/', views.cambiar_equipo, name='cambiar'),
]