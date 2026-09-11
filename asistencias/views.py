from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from partidos.models import Partido
from jugadores.models import Jugador
from .models import Asistencia
from .forms import AsistenciaForm


def es_dt(user):
    """Chequea si el usuario es el técnico (DT)"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'DT'


@login_required
def mis_partidos(request):
    """El jugador ve los partidos que se vienen y confirma si va o no"""
    # Buscamos el jugador asociado al usuario actual
    try:
        jugador = Jugador.objects.get(usuario=request.user)
    except Jugador.DoesNotExist:
        messages.warning(request, 'No estás cargado como jugador. Hablá con el técnico.')
        return redirect('core:home')

    # Traemos los partidos programados (los que todavía no se jugaron)
    partidos = Partido.objects.filter(estado='PROGRAMADO').order_by('fecha', 'hora')

    # Armamos un diccionario con las respuestas que ya dio este jugador
    asistencias = {a.partido_id: a for a in Asistencia.objects.filter(jugador=jugador)}

    # Combinamos la info de cada partido con la respuesta del jugador
    partidos_con_asistencia = []
    for partido in partidos:
        partidos_con_asistencia.append({
            'partido': partido,
            'asistencia': asistencias.get(partido.id)
        })

    return render(request, 'asistencias/mis_partidos.html', {
        'partidos_con_asistencia': partidos_con_asistencia,
        'jugador': jugador
    })


@login_required
def confirmar_asistencia(request, partido_id):
    """El jugador confirma si va, no va o está en duda"""
    partido = get_object_or_404(Partido, pk=partido_id)

    try:
        jugador = Jugador.objects.get(usuario=request.user)
    except Jugador.DoesNotExist:
        messages.error(request, 'No estás cargado como jugador en el sistema.')
        return redirect('core:home')

    # Buscamos si ya respondió algo, sino creamos una respuesta por defecto
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
        'asistencia': asistencia
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def resumen_asistencias(request, partido_id):
    """El DT ve quién confirmó, quién no va y quién todavía no contestó"""
    partido = get_object_or_404(Partido, pk=partido_id)

    # Traemos todas las respuestas de este partido
    asistencias = Asistencia.objects.filter(partido=partido).select_related('jugador')

    # Separamos por estado
    confirmados = asistencias.filter(estado='CONFIRMADO')
    rechazados = asistencias.filter(estado='RECHAZADO')
    dudas = asistencias.filter(estado='DUDA')

    # Vemos quiénes todavía no dijeron nada
    jugadores_activos = Jugador.objects.filter(activo=True)
    jugadores_con_respuesta = asistencias.values_list('jugador_id', flat=True)
    sin_respuesta = jugadores_activos.exclude(id__in=jugadores_con_respuesta)

    return render(request, 'asistencias/resumen.html', {
        'partido': partido,
        'confirmados': confirmados,
        'rechazados': rechazados,
        'dudas': dudas,
        'sin_respuesta': sin_respuesta,
        'total_confirmados': confirmados.count(),
        'total_jugadores': jugadores_activos.count()
    })
