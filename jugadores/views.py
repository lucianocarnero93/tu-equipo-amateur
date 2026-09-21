from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo, get_equipo_activo_o_aviso
from .models import Jugador
from .forms import JugadorForm


@login_required
def lista_jugadores(request):
    """Muestra el plantel del equipo activo."""
    equipo = get_equipo_activo(request.user)

    if equipo is None:
        jugadores = Jugador.objects.none()
    else:
        filtro = request.GET.get('filtro', 'activos')

        if filtro == 'inactivos':
            jugadores = equipo.jugadores.filter(activo=False)
        elif filtro == 'todos':
            jugadores = equipo.jugadores.all()
        else:  # 'activos' por defecto
            jugadores = equipo.jugadores.filter(activo=True)

    return render(request, 'jugadores/lista.html', {
        'jugadores': jugadores,
        'filtro_actual': request.GET.get('filtro', 'activos'),
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def crear_jugador(request):
    """El DT o ayudante suman un jugador al plantel."""
    equipo = get_equipo_activo_o_aviso(request)
    if equipo is None:
        return redirect('core:home')

    if request.method == 'POST':
        form = JugadorForm(request.POST)
        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.equipo = equipo  # ← ASIGNAR EQUIPO
            jugador.save()
            messages.success(request, f'¡Listo! {jugador.get_nombre_completo()} ya está en el plantel.')
            return redirect('jugadores:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = JugadorForm()

    return render(request, 'jugadores/formulario.html', {
        'form': form,
        'titulo': 'Sumar un pibe al plantel',
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def editar_jugador(request, pk):
    """El DT o ayudante pueden corregir los datos de un jugador."""
    jugador = get_object_or_404(Jugador, pk=pk)

    # Verificar que el jugador pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if jugador.equipo != equipo:
        messages.error(request, 'No podés editar jugadores de otro equipo.')
        return redirect('jugadores:lista')

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

    return render(request, 'jugadores/formulario.html', {
        'form': form,
        'titulo': 'Editar datos del jugador',
        'jugador': jugador,
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def eliminar_jugador(request, pk):
    """El DT o ayudante dan de baja a un jugador."""
    jugador = get_object_or_404(Jugador, pk=pk)

    # Verificar que el jugador pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if jugador.equipo != equipo:
        messages.error(request, 'No podés dar de baja jugadores de otro equipo.')
        return redirect('jugadores:lista')

    if request.method == 'POST':
        jugador.activo = False
        jugador.save()
        messages.success(request, f'{jugador.get_nombre_completo()} fue dado de baja del plantel.')
        return redirect('jugadores:lista')

    return render(request, 'jugadores/eliminar.html', {'jugador': jugador})


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def reactivar_jugador(request, pk):
    """El DT o ayudante reactivan a un jugador dado de baja."""
    jugador = get_object_or_404(Jugador, pk=pk)

    # Verificar que el jugador pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if jugador.equipo != equipo:
        messages.error(request, 'No podés reactivar jugadores de otro equipo.')
        return redirect('jugadores:lista')

    if request.method == 'POST':
        jugador.activo = True
        jugador.save()
        messages.success(request, f'{jugador.get_nombre_completo()} volvió al plantel.')
        return redirect('jugadores:lista')

    return render(request, 'jugadores/reactivar.html', {'jugador': jugador})


@login_required
def detalle_jugador(request, pk):
    """Ficha completa de un jugador."""
    jugador = get_object_or_404(Jugador, pk=pk)
    return render(request, 'jugadores/detalle.html', {'jugador': jugador})