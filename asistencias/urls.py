from django.urls import path
from . import views

app_name = 'asistencias'

urlpatterns = [
    path('mis-partidos/', views.mis_partidos, name='mis_partidos'),
    path('confirmar/<int:partido_id>/', views.confirmar_asistencia, name='confirmar'),
    path('resumen/<int:partido_id>/', views.resumen_asistencias, name='resumen'),
]
