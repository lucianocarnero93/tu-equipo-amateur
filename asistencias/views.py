from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo, get_equipo_activo_o_aviso
from partidos.models import Partido
from jugadores.models import Jugador
from .models import Asistencia
from .forms import AsistenciaForm


@login_required
def mis_partidos(request):
    """El jugador ve los partidos programados de su equipo."""
    # Buscar el jugador del usuario en el equipo activo
    equipo = get_equipo_activo(request.user)

    if equipo is None:
        messages.warning(request, 'No tenés un equipo activo.')
        return redirect('core:home')

    try:
        jugador = Jugador.objects.get(usuario=request.user, equipo=equipo)
    except Jugador.DoesNotExist:
        messages.warning(request, 'No estás cargado como jugador en este equipo.')
        return redirect('core:home')

    # Traemos los partidos programados del equipo
    partidos = Partido.objects.filter(equipo=equipo, estado='PROGRAMADO').order_by('fecha', 'hora')

    # Armamos un diccionario con las respuestas del jugador
    asistencias = {a.partido_id: a for a in Asistencia.objects.filter(jugador=jugador)}

    # Combinamos la info
    partidos_con_asistencia = []
    for partido in partidos:
        partidos_con_asistencia.append({
            'partido': partido,
            'asistencia': asistencias.get(partido.id)
        })

    return render(request, 'asistencias/mis_partidos.html', {
        'partidos_con_asistencia': partidos_con_asistencia,
        'jugador': jugador,
        'equipo': equipo,
    })


@login_required
def confirmar_asistencia(request, partido_id):
    """El jugador confirma su asistencia a un partido."""
    partido = get_object_or_404(Partido, pk=partido_id)

    # Verificar que el partido sea del equipo activo
    equipo = get_equipo_activo(request.user)
    if partido.equipo != equipo:
        messages.error(request, 'Ese partido no es de tu equipo.')
        return redirect('asistencias:mis_partidos')

    try:
        jugador = Jugador.objects.get(usuario=request.user, equipo=equipo)
    except Jugador.DoesNotExist:
        messages.error(request, 'No estás cargado como jugador en este equipo.')
        return redirect('core:home')

    # Obtener o crear la asistencia
    asistencia, created = Asistencia.objects.get_or_create(
        partido=partido,
        jugador=jugador,
        defaults={'estado': 'DUDA'}
    )

    if request.method == 'POST':
        form = AsistenciaForm(request.POST, instance=asistencia)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Listo! Ya tenemos tu respuesta para el partido contra {partido.rival}.')
            return redirect('asistencias:mis_partidos')
    else:
        form = AsistenciaForm(instance=asistencia)

    return render(request, 'asistencias/confirmar.html', {
        'form': form,
        'partido': partido,
        'asistencia': asistencia,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def resumen_asistencias(request, partido_id):
    """El DT o ayudante ven el resumen de asistencias."""
    partido = get_object_or_404(Partido, pk=partido_id)

    # Verificar que el partido sea del equipo activo
    equipo = get_equipo_activo(request.user)
    if partido.equipo != equipo:
        messages.error(request, 'Ese partido no es de tu equipo.')
        return redirect('partidos:lista')

    asistencias = Asistencia.objects.filter(partido=partido).select_related('jugador')

    confirmados = asistencias.filter(estado='CONFIRMADO')
    rechazados = asistencias.filter(estado='RECHAZADO')
    dudas = asistencias.filter(estado='DUDA')

    jugadores_activos = equipo.jugadores.filter(activo=True)
    jugadores_con_respuesta = asistencias.values_list('jugador_id', flat=True)
    sin_respuesta = jugadores_activos.exclude(id__in=jugadores_con_respuesta)

    return render(request, 'asistencias/resumen.html', {
        'partido': partido,
        'confirmados': confirmados,
        'rechazados': rechazados,
        'dudas': dudas,
        'sin_respuesta': sin_respuesta,
        'total_confirmados': confirmados.count(),
        'total_jugadores': jugadores_activos.count(),
    })