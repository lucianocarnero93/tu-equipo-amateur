from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo, get_equipo_activo_o_aviso
from .models import Partido
from .forms import PartidoForm, ResultadoForm


@login_required
def lista_partidos(request):
    """Muestra los partidos del equipo activo."""
    equipo = get_equipo_activo(request.user)

    if equipo is None:
        partidos = Partido.objects.none()
    else:
        partidos = Partido.objects.filter(equipo=equipo)

    return render(request, 'partidos/lista.html', {
        'partidos': partidos,
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def crear_partido(request):
    """El DT o ayudante agendan un partido."""
    equipo = get_equipo_activo_o_aviso(request)
    if equipo is None:
        return redirect('core:home')

    if request.method == 'POST':
        form = PartidoForm(request.POST)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.creado_por = request.user
            partido.equipo = equipo  # ← ASIGNAR EQUIPO
            partido.save()
            messages.success(request, f'Quedó agendado el partido contra {partido.rival}.')
            return redirect('partidos:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = PartidoForm()

    return render(request, 'partidos/formulario.html', {
        'form': form,
        'titulo': 'Agendar un partido',
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def editar_partido(request, pk):
    """El DT o ayudante pueden corregir un partido."""
    partido = get_object_or_404(Partido, pk=pk)

    # Verificar que el partido pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if partido.equipo != equipo:
        messages.error(request, 'No podés editar partidos de otro equipo.')
        return redirect('partidos:lista')

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

    return render(request, 'partidos/formulario.html', {
        'form': form,
        'titulo': 'Editar partido',
        'partido': partido,
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def eliminar_partido(request, pk):
    """El DT o ayudante pueden borrar un partido."""
    partido = get_object_or_404(Partido, pk=pk)

    # Verificar que el partido pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if partido.equipo != equipo:
        messages.error(request, 'No podés borrar partidos de otro equipo.')
        return redirect('partidos:lista')

    if request.method == 'POST':
        rival = partido.rival
        partido.delete()
        messages.success(request, f'Borramos el partido contra {rival}.')
        return redirect('partidos:lista')

    return render(request, 'partidos/eliminar.html', {'partido': partido})


@login_required
def detalle_partido(request, pk):
    """Ficha completa del partido."""
    partido = get_object_or_404(Partido, pk=pk)
    es_dt_user = es_dt_o_ayudante(request.user)

    return render(request, 'partidos/detalle.html', {
        'partido': partido,
        'es_dt': es_dt_user,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def actualizar_resultado(request, pk):
    """El DT o ayudante cargan el resultado."""
    partido = get_object_or_404(Partido, pk=pk)

    # Verificar que el partido pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if partido.equipo != equipo:
        messages.error(request, 'No podés cargar el resultado de otro equipo.')
        return redirect('partidos:lista')

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

    return render(request, 'partidos/resultado.html', {
        'form': form,
        'partido': partido,
    })