from django.urls import path
from . import views

app_name = 'estadisticas'

urlpatterns = [
    path('partido/<int:partido_id>/', views.ver_estadisticas_partido, name='partido'),
    path('partido/<int:partido_id>/agregar/', views.agregar_estadistica, name='agregar'),
    path('editar/<int:pk>/', views.editar_estadistica, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_estadistica, name='eliminar'),
    path('reportes/', views.reportes, name='reportes'),
    path('mi-rendimiento/', views.mi_rendimiento, name='mi_rendimiento'),
]
