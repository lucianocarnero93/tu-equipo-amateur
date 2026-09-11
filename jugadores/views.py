from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Jugador
from .forms import JugadorForm


def es_dt(user):
    """Chequea si el usuario es el técnico (DT)"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'DT'


@login_required
def lista_jugadores(request):
    """Muestra el plantel completo de Los Pibes"""
    jugadores = Jugador.objects.all()
    return render(request, 'jugadores/lista.html', {'jugadores': jugadores})


@login_required
@user_passes_test(es_dt, login_url='/')
def crear_jugador(request):
    """El DT carga un jugador nuevo al plantel"""
    if request.method == 'POST':
        form = JugadorForm(request.POST)
        if form.is_valid():
            jugador = form.save()
            messages.success(request, f'¡Listo! {jugador.get_nombre_completo()} ya está en el plantel.')
            return redirect('jugadores:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = JugadorForm()

    return render(request, 'jugadores/formulario.html', {'form': form, 'titulo': 'Sumar un pibe al plantel'})


@login_required
@user_passes_test(es_dt, login_url='/')
def editar_jugador(request, pk):
    """El DT puede corregir los datos de un jugador"""
    jugador = get_object_or_404(Jugador, pk=pk)

    if request.method == 'POST':
        form = JugadorForm(request.POST, instance=jugador)
        if form.is_valid():
            form.save()
            messages.success(request, f'Actualizamos los datos de {jugador.get_nombre_completo()}.')
            return redirect('jugadores:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = JugadorForm(instance=jugador)

    return render(request, 'jugadores/formulario.html', {'form': form, 'titulo': 'Editar datos del jugador', 'jugador': jugador})


@login_required
@user_passes_test(es_dt, login_url='/')
def eliminar_jugador(request, pk):
    """El DT puede dar de baja a un jugador"""
    jugador = get_object_or_404(Jugador, pk=pk)

    if request.method == 'POST':
        nombre = jugador.get_nombre_completo()
        jugador.delete()
        messages.success(request, f'{nombre} fue dado de baja del plantel.')
        return redirect('jugadores:lista')

    return render(request, 'jugadores/eliminar.html', {'jugador': jugador})


@login_required
def detalle_jugador(request, pk):
    """Ficha completa de un jugador"""
    jugador = get_object_or_404(Jugador, pk=pk)
    return render(request, 'jugadores/detalle.html', {'jugador': jugador})
