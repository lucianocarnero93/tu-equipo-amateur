from django.urls import path
from . import views

app_name = 'partidos'

urlpatterns = [
    path('', views.lista_partidos, name='lista'),
    path('crear/', views.crear_partido, name='crear'),
    path('editar/<int:pk>/', views.editar_partido, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_partido, name='eliminar'),
    path('detalle/<int:pk>/', views.detalle_partido, name='detalle'),
    path('resultado/<int:pk>/', views.actualizar_resultado, name='resultado'),
]
