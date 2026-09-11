from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from partidos.models import Partido
from jugadores.models import Jugador
from .models import Estadistica
from .forms import EstadisticaForm


def es_dt(user):
    """Chequea si el usuario es el técnico (DT)"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'DT'


@login_required
def ver_estadisticas_partido(request, partido_id):
    """Los números de cada jugador en un partido puntual"""
    partido = get_object_or_404(Partido, pk=partido_id)
    estadisticas = Estadistica.objects.filter(partido=partido).select_related('jugador')

    es_dt_user = es_dt(request.user)

    return render(request, 'estadisticas/partido.html', {
        'partido': partido,
        'estadisticas': estadisticas,
        'es_dt': es_dt_user,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def agregar_estadistica(request, partido_id):
    """El DT carga los números de un jugador en un partido"""
    partido = get_object_or_404(Partido, pk=partido_id)

    if request.method == 'POST':
        form = EstadisticaForm(request.POST)
        if form.is_valid():
            estadistica = form.save(commit=False)
            estadistica.partido = partido

            # Chequeamos que no esté repetido
            if Estadistica.objects.filter(partido=partido, jugador=estadistica.jugador).exists():
                messages.error(request, f'{estadistica.jugador.get_nombre_completo()} ya tiene números cargados en este partido.')
            else:
                estadistica.save()
                messages.success(request, f'Cargamos los números de {estadistica.jugador.get_nombre_completo()}.')
                return redirect('estadisticas:partido', partido_id=partido.pk)
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        # Solo mostramos los jugadores que todavía no tienen números en este partido
        jugadores_con_estadistica = Estadistica.objects.filter(partido=partido).values_list('jugador_id', flat=True)
        jugadores_disponibles = Jugador.objects.filter(activo=True).exclude(id__in=jugadores_con_estadistica)
        form = EstadisticaForm()
        form.fields['jugador'].queryset = jugadores_disponibles

    return render(request, 'estadisticas/agregar.html', {
        'form': form,
        'partido': partido,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def editar_estadistica(request, pk):
    """El DT puede corregir los números de un jugador"""
    estadistica = get_object_or_404(Estadistica, pk=pk)

    if request.method == 'POST':
        form = EstadisticaForm(request.POST, instance=estadistica)
        if form.is_valid():
            form.save()
            messages.success(request, f'Corregimos los números de {estadistica.jugador.get_nombre_completo()}.')
            return redirect('estadisticas:partido', partido_id=estadistica.partido.pk)
    else:
        form = EstadisticaForm(instance=estadistica)

    return render(request, 'estadisticas/editar.html', {
        'form': form,
        'estadistica': estadistica,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def eliminar_estadistica(request, pk):
    """El DT puede borrar los números de un jugador"""
    estadistica = get_object_or_404(Estadistica, pk=pk)
    partido_id = estadistica.partido.pk

    if request.method == 'POST':
        nombre = estadistica.jugador.get_nombre_completo()
        estadistica.delete()
        messages.success(request, f'Borramos los números de {nombre}.')
        return redirect('estadisticas:partido', partido_id=partido_id)

    return render(request, 'estadisticas/eliminar.html', {'estadistica': estadistica})


@login_required
def reportes(request):
    """Los rankings del equipo: goleadores, asistidores y los que más jugaron"""
    # Los que más metieron
    goleadores = Jugador.objects.annotate(
        total_goles=Sum('estadisticas__goles'),
        total_partidos=Count('estadisticas', distinct=True)
    ).filter(total_goles__gt=0).order_by('-total_goles')[:10]

    # Los que más asistieron
    asistidores = Jugador.objects.annotate(
        total_asistencias=Sum('estadisticas__asistencias'),
        total_partidos=Count('estadisticas', distinct=True)
    ).filter(total_asistencias__gt=0).order_by('-total_asistencias')[:10]

    # Los que más veces estuvieron
    presencias = Jugador.objects.annotate(
        total_partidos=Count('estadisticas', distinct=True),
        total_minutos=Sum('estadisticas__minutos_jugados'),
        total_goles=Sum('estadisticas__goles')
    ).filter(total_partidos__gt=0).order_by('-total_partidos')[:10]

    # Los totales del equipo
    totales = Estadistica.objects.aggregate(
        total_goles=Sum('goles'),
        total_asistencias=Sum('asistencias'),
        total_minutos=Sum('minutos_jugados'),
        total_partidos=Count('partido', distinct=True)
    )

    return render(request, 'estadisticas/reportes.html', {
        'goleadores': goleadores,
        'asistidores': asistidores,
        'presencias': presencias,
        'totales': totales,
    })


@login_required
def mi_rendimiento(request):
    """Cada jugador puede ver sus propios números"""
    try:
        jugador = Jugador.objects.get(usuario=request.user)
    except Jugador.DoesNotExist:
        messages.warning(request, 'No estás cargado como jugador. Hablá con el técnico.')
        return redirect('core:home')

    estadisticas = Estadistica.objects.filter(jugador=jugador).select_related('partido')

    # Totales del jugador
    totales = estadisticas.aggregate(
        total_goles=Sum('goles'),
        total_asistencias=Sum('asistencias'),
        total_minutos=Sum('minutos_jugados'),
        total_partidos=Count('id')
    )

    # Promedios por partido
    if totales['total_partidos'] and totales['total_partidos'] > 0:
        totales['promedio_goles'] = round(totales['total_goles'] / totales['total_partidos'], 2) if totales['total_goles'] else 0
        totales['promedio_asistencias'] = round(totales['total_asistencias'] / totales['total_partidos'], 2) if totales['total_asistencias'] else 0
    else:
        totales['promedio_goles'] = 0
        totales['promedio_asistencias'] = 0

    return render(request, 'estadisticas/mi_rendimiento.html', {
        'jugador': jugador,
        'estadisticas': estadisticas,
        'totales': totales,
    })
