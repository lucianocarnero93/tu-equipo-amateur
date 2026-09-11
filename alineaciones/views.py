from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from partidos.models import Partido
from jugadores.models import Jugador
from .models import Alineacion
from .forms import AlineacionForm


def es_dt(user):
    """Chequea si el usuario es el técnico (DT)"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'DT'


@login_required
def ver_alineacion(request, partido_id):
    """Muestra la formación del partido: titulares y suplentes"""
    partido = get_object_or_404(Partido, pk=partido_id)
    titulares = Alineacion.objects.filter(partido=partido, tipo='TITULAR').select_related('jugador')
    suplentes = Alineacion.objects.filter(partido=partido, tipo='SUPLENTE').select_related('jugador')

    es_dt_user = es_dt(request.user)

    return render(request, 'alineaciones/ver.html', {
        'partido': partido,
        'titulares': titulares,
        'suplentes': suplentes,
        'es_dt': es_dt_user,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def agregar_jugador(request, partido_id):
    """El DT suma un jugador a la formación"""
    partido = get_object_or_404(Partido, pk=partido_id)

    if request.method == 'POST':
        form = AlineacionForm(request.POST)
        if form.is_valid():
            alineacion = form.save(commit=False)
            alineacion.partido = partido

            # Chequeamos que no esté repetido
            if Alineacion.objects.filter(partido=partido, jugador=alineacion.jugador).exists():
                messages.error(request, f'{alineacion.jugador.get_nombre_completo()} ya está en la formación.')
            else:
                alineacion.save()
                messages.success(request, f'{alineacion.jugador.get_nombre_completo()} entró a la formación.')
                return redirect('alineaciones:ver', partido_id=partido.pk)
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        # Solo mostramos los jugadores que todavía no están en la formación
        jugadores_en_alineacion = Alineacion.objects.filter(partido=partido).values_list('jugador_id', flat=True)
        jugadores_disponibles = Jugador.objects.filter(activo=True).exclude(id__in=jugadores_en_alineacion)
        form = AlineacionForm()
        form.fields['jugador'].queryset = jugadores_disponibles

    return render(request, 'alineaciones/agregar.html', {
        'form': form,
        'partido': partido,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def eliminar_jugador(request, alineacion_id):
    """El DT saca un jugador de la formación"""
    alineacion = get_object_or_404(Alineacion, pk=alineacion_id)
    partido_id = alineacion.partido.pk

    if request.method == 'POST':
        nombre = alineacion.jugador.get_nombre_completo()
        alineacion.delete()
        messages.success(request, f'{nombre} salió de la formación.')
        return redirect('alineaciones:ver', partido_id=partido_id)

    return render(request, 'alineaciones/eliminar.html', {'alineacion': alineacion})


@login_required
@user_passes_test(es_dt, login_url='/')
def cambiar_tipo(request, alineacion_id):
    """El DT cambia a un jugador entre titular y suplente"""
    alineacion = get_object_or_404(Alineacion, pk=alineacion_id)

    if alineacion.tipo == 'TITULAR':
        alineacion.tipo = 'SUPLENTE'
    else:
        alineacion.tipo = 'TITULAR'
    alineacion.save()

    messages.success(request, f'{alineacion.jugador.get_nombre_completo()} ahora es {alineacion.get_tipo_display().lower()}.')
    return redirect('alineaciones:ver', partido_id=alineacion.partido.pk)
