from django.urls import path
from . import views

app_name = 'jugadores'

urlpatterns = [
    path('', views.lista_jugadores, name='lista'),
    path('crear/', views.crear_jugador, name='crear'),
    path('editar/<int:pk>/', views.editar_jugador, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_jugador, name='eliminar'),
    path('reactivar/<int:pk>/', views.reactivar_jugador, name='reactivar'),
    path('detalle/<int:pk>/', views.detalle_jugador, name='detalle'),
]