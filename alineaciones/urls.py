from django.urls import path
from . import views

app_name = 'alineaciones'

urlpatterns = [
    path('partido/<int:partido_id>/', views.ver_alineacion, name='ver'),
    path('partido/<int:partido_id>/agregar/', views.agregar_jugador, name='agregar'),
    path('eliminar/<int:alineacion_id>/', views.eliminar_jugador, name='eliminar'),
    path('cambiar-tipo/<int:alineacion_id>/', views.cambiar_tipo, name='cambiar_tipo'),
]
