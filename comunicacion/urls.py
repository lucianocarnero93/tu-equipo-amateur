from django.urls import path
from . import views

app_name = 'comunicacion'

urlpatterns = [
    path('', views.lista_anuncios, name='lista'),
    path('detalle/<int:pk>/', views.detalle_anuncio, name='detalle'),
    path('crear/', views.crear_anuncio, name='crear'),
    path('editar/<int:pk>/', views.editar_anuncio, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_anuncio, name='eliminar'),
]
