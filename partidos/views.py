from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Partido
from .forms import PartidoForm, ResultadoForm


def es_dt(user):
    """Chequea si el usuario es el técnico (DT)"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'DT'


@login_required
def lista_partidos(request):
    """Muestra todos los partidos, los jugados y los que vienen"""
    partidos = Partido.objects.all()
    return render(request, 'partidos/lista.html', {'partidos': partidos})


@login_required
@user_passes_test(es_dt, login_url='/')
def crear_partido(request):
    """El DT carga un partido nuevo en la agenda"""
    if request.method == 'POST':
        form = PartidoForm(request.POST)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.creado_por = request.user
            partido.save()
            messages.success(request, f'Quedó agendado el partido contra {partido.rival}.')
            return redirect('partidos:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = PartidoForm()

    return render(request, 'partidos/formulario.html', {'form': form, 'titulo': 'Agendar un partido'})


@login_required
@user_passes_test(es_dt, login_url='/')
def editar_partido(request, pk):
    """El DT puede corregir los datos de un partido"""
    partido = get_object_or_404(Partido, pk=pk)

    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Actualizamos los datos del partido contra {partido.rival}.')
            return redirect('partidos:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = PartidoForm(instance=partido)

    return render(request, 'partidos/formulario.html', {'form': form, 'titulo': 'Editar partido', 'partido': partido})


@login_required
@user_passes_test(es_dt, login_url='/')
def eliminar_partido(request, pk):
    """El DT puede borrar un partido de la agenda"""
    partido = get_object_or_404(Partido, pk=pk)

    if request.method == 'POST':
        rival = partido.rival
        partido.delete()
        messages.success(request, f'Borramos el partido contra {rival}.')
        return redirect('partidos:lista')

    return render(request, 'partidos/eliminar.html', {'partido': partido})


@login_required
def detalle_partido(request, pk):
    """Ficha completa del partido"""
    partido = get_object_or_404(Partido, pk=pk)
    es_dt_user = es_dt(request.user)

    return render(request, 'partidos/detalle.html', {
        'partido': partido,
        'es_dt': es_dt_user
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def actualizar_resultado(request, pk):
    """El DT carga el resultado final del partido"""
    partido = get_object_or_404(Partido, pk=pk)

    if request.method == 'POST':
        form = ResultadoForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cargamos el resultado del partido contra {partido.rival}.')
            return redirect('partidos:detalle', pk=partido.pk)
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = ResultadoForm(instance=partido)

    return render(request, 'partidos/resultado.html', {'form': form, 'partido': partido})
