from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo, get_equipo_activo_o_aviso
from partidos.models import Partido
from jugadores.models import Jugador
from .models import Estadistica
from .forms import EstadisticaForm


@login_required
def ver_estadisticas_partido(request, partido_id):
    """Los números de cada jugador en un partido puntual."""
    partido = get_object_or_404(Partido, pk=partido_id)

    # Verificar que el partido sea del equipo activo
    equipo = get_equipo_activo(request.user)
    if partido.equipo != equipo:
        messages.error(request, 'Ese partido no es de tu equipo.')
        return redirect('partidos:lista')

    estadisticas = Estadistica.objects.filter(partido=partido).select_related('jugador')
    es_cuerpo_tecnico = es_dt_o_ayudante(request.user)

    return render(request, 'estadisticas/partido.html', {
        'partido': partido,
        'estadisticas': estadisticas,
        'es_dt': es_cuerpo_tecnico,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def agregar_estadistica(request, partido_id):
    """El DT o ayudante cargan los números de un jugador."""
    partido = get_object_or_404(Partido, pk=partido_id)

    # Verificar que el partido sea del equipo activo
    equipo = get_equipo_activo_o_aviso(request)
    if equipo is None:
        return redirect('core:home')

    if partido.equipo != equipo:
        messages.error(request, 'Ese partido no es de tu equipo.')
        return redirect('partidos:lista')

    if request.method == 'POST':
        form = EstadisticaForm(request.POST)
        if form.is_valid():
            estadistica = form.save(commit=False)
            estadistica.partido = partido

            errores = []

            if Estadistica.objects.filter(partido=partido, jugador=estadistica.jugador).exists():
                errores.append(f'{estadistica.jugador.get_nombre_completo()} ya tiene números cargados en este partido.')

            goles_equipo = partido.goles_local
            if estadistica.goles > goles_equipo:
                errores.append(f'El equipo metió {goles_equipo} goles en total. No podés asignar {estadistica.goles} goles a un solo jugador.')

            if estadistica.asistencias > goles_equipo:
                errores.append(f'El equipo metió {goles_equipo} goles en total. No podés asignar {estadistica.asistencias} asistencias.')

            if estadistica.tarjetas_amarillas > 2:
                errores.append('Un jugador no puede tener más de 2 tarjetas amarillas.')
            if estadistica.tarjetas_rojas > 1:
                errores.append('Un jugador no puede tener más de 1 tarjeta roja.')

            if errores:
                for error in errores:
                    messages.error(request, error)
            else:
                estadistica.save()
                messages.success(request, f'Cargamos los números de {estadistica.jugador.get_nombre_completo()}.')
                return redirect('estadisticas:partido', partido_id=partido.pk)
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        jugadores_con_estadistica = Estadistica.objects.filter(partido=partido).values_list('jugador_id', flat=True)
        jugadores_disponibles = equipo.jugadores.filter(activo=True).exclude(id__in=jugadores_con_estadistica)
        form = EstadisticaForm()
        form.fields['jugador'].queryset = jugadores_disponibles

    return render(request, 'estadisticas/agregar.html', {
        'form': form,
        'partido': partido,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def editar_estadistica(request, pk):
    """El DT o ayudante pueden corregir los números."""
    estadistica = get_object_or_404(Estadistica, pk=pk)

    equipo = get_equipo_activo(request.user)
    if estadistica.partido.equipo != equipo:
        messages.error(request, 'No podés editar estadísticas de otro equipo.')
        return redirect('estadisticas:partido', partido_id=estadistica.partido.pk)

    if request.method == 'POST':
        form = EstadisticaForm(request.POST, instance=estadistica)
        if form.is_valid():
            datos = form.cleaned_data
            errores = []
            goles_equipo = estadistica.partido.goles_local

            if datos['goles'] > goles_equipo:
                errores.append(f'El equipo metió {goles_equipo} goles en total. No podés asignar {datos["goles"]} goles.')
            if datos['asistencias'] > goles_equipo:
                errores.append(f'El equipo metió {goles_equipo} goles en total. No podés asignar {datos["asistencias"]} asistencias.')
            if datos['tarjetas_amarillas'] > 2:
                errores.append('Un jugador no puede tener más de 2 tarjetas amarillas.')
            if datos['tarjetas_rojas'] > 1:
                errores.append('Un jugador no puede tener más de 1 tarjeta roja.')

            if errores:
                for error in errores:
                    messages.error(request, error)
            else:
                form.save()
                messages.success(request, f'Corregimos los números de {estadistica.nombre_jugador}.')
                return redirect('estadisticas:partido', partido_id=estadistica.partido.pk)
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = EstadisticaForm(instance=estadistica)

    return render(request, 'estadisticas/editar.html', {
        'form': form,
        'estadistica': estadistica,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def eliminar_estadistica(request, pk):
    """El DT o ayudante pueden borrar los números."""
    estadistica = get_object_or_404(Estadistica, pk=pk)

    equipo = get_equipo_activo(request.user)
    if estadistica.partido.equipo != equipo:
        messages.error(request, 'No podés borrar estadísticas de otro equipo.')
        return redirect('estadisticas:partido', partido_id=estadistica.partido.pk)

    partido_id = estadistica.partido.pk

    if request.method == 'POST':
        nombre = estadistica.nombre_jugador
        estadistica.delete()
        messages.success(request, f'Borramos los números de {nombre}.')
        return redirect('estadisticas:partido', partido_id=partido_id)

    return render(request, 'estadisticas/eliminar.html', {'estadistica': estadistica})


@login_required
def reportes(request):
    """Los rankings del equipo activo."""
    equipo = get_equipo_activo(request.user)

    if equipo is None:
        messages.warning(request, 'No tenés un equipo activo.')
        return redirect('core:home')

    # Los que más metieron (solo del equipo activo)
    goleadores = equipo.jugadores.annotate(
        total_goles=Sum('estadisticas__goles'),
        total_partidos=Count('estadisticas', distinct=True)
    ).filter(total_goles__gt=0).order_by('-total_goles')[:10]

    # Los que más asistieron
    asistidores = equipo.jugadores.annotate(
        total_asistencias=Sum('estadisticas__asistencias'),
        total_partidos=Count('estadisticas', distinct=True)
    ).filter(total_asistencias__gt=0).order_by('-total_asistencias')[:10]

    # Los que más veces estuvieron
    presencias = equipo.jugadores.annotate(
        total_partidos=Count('estadisticas', distinct=True),
        total_goles=Sum('estadisticas__goles')
    ).filter(total_partidos__gt=0).order_by('-total_partidos')[:10]

    # Los totales del equipo
    totales = Estadistica.objects.filter(partido__equipo=equipo).aggregate(
        total_goles=Sum('goles'),
        total_asistencias=Sum('asistencias'),
        total_partidos=Count('partido', distinct=True)
    )

    return render(request, 'estadisticas/reportes.html', {
        'goleadores': goleadores,
        'asistidores': asistidores,
        'presencias': presencias,
        'totales': totales,
        'equipo': equipo,
    })


@login_required
def mi_rendimiento(request):
    """Cada jugador puede ver sus propios números."""
    equipo = get_equipo_activo(request.user)

    if equipo is None:
        messages.warning(request, 'No tenés un equipo activo.')
        return redirect('core:home')

    try:
        jugador = Jugador.objects.get(usuario=request.user, equipo=equipo)
    except Jugador.DoesNotExist:
        messages.warning(request, 'No estás cargado como jugador en este equipo.')
        return redirect('core:home')

    estadisticas = Estadistica.objects.filter(jugador=jugador).select_related('partido')

    totales = estadisticas.aggregate(
        total_goles=Sum('goles'),
        total_asistencias=Sum('asistencias'),
        total_partidos=Count('id')
    )

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