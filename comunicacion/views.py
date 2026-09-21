from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo, get_equipo_activo_o_aviso
from .models import Anuncio
from .forms import AnuncioForm


def lista_anuncios(request):
    """Muestra los anuncios activos del equipo activo."""
    equipo = get_equipo_activo(request.user)

    # Si no tiene equipo activo, mostramos lista vacía con aviso
    if equipo is None:
        anuncios = Anuncio.objects.none()
    else:
        anuncios = Anuncio.objects.filter(equipo=equipo, activo=True)

    # Filtramos por prioridad si eligen una
    prioridad = request.GET.get('prioridad')
    if prioridad:
        anuncios = anuncios.filter(prioridad=prioridad)

    es_dt_user = es_dt_o_ayudante(request.user) if request.user.is_authenticated else False

    return render(request, 'comunicacion/lista.html', {
        'anuncios': anuncios,
        'es_dt': es_dt_user,
        'prioridad_actual': prioridad,
        'equipo': equipo,
    })


@login_required
def detalle_anuncio(request, pk):
    """Muestra el anuncio completo."""
    anuncio = get_object_or_404(Anuncio, pk=pk)
    es_dt_user = es_dt_o_ayudante(request.user)

    return render(request, 'comunicacion/detalle.html', {
        'anuncio': anuncio,
        'es_dt': es_dt_user,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def crear_anuncio(request):
    """El DT o ayudante publican un anuncio en su equipo."""
    equipo = get_equipo_activo_o_aviso(request)
    if equipo is None:
        return redirect('core:home')

    if request.method == 'POST':
        form = AnuncioForm(request.POST)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.autor = request.user
            anuncio.equipo = equipo  # ← ASIGNAR EQUIPO
            anuncio.save()
            messages.success(request, f'Quedó publicado el anuncio "{anuncio.titulo}".')
            return redirect('comunicacion:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = AnuncioForm()

    return render(request, 'comunicacion/formulario.html', {
        'form': form,
        'titulo': 'Publicar un anuncio',
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def editar_anuncio(request, pk):
    """El DT o ayudante pueden corregir un anuncio."""
    anuncio = get_object_or_404(Anuncio, pk=pk)

    # Verificar que el anuncio pertenezca al equipo activo del usuario
    equipo = get_equipo_activo(request.user)
    if anuncio.equipo != equipo:
        messages.error(request, 'No podés editar anuncios de otro equipo.')
        return redirect('comunicacion:lista')

    if request.method == 'POST':
        form = AnuncioForm(request.POST, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, f'Actualizamos el anuncio "{anuncio.titulo}".')
            return redirect('comunicacion:detalle', pk=anuncio.pk)
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = AnuncioForm(instance=anuncio)

    return render(request, 'comunicacion/formulario.html', {
        'form': form,
        'titulo': 'Editar anuncio',
        'anuncio': anuncio,
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def eliminar_anuncio(request, pk):
    """El DT o ayudante pueden borrar un anuncio."""
    anuncio = get_object_or_404(Anuncio, pk=pk)

    # Verificar que el anuncio pertenezca al equipo activo
    equipo = get_equipo_activo(request.user)
    if anuncio.equipo != equipo:
        messages.error(request, 'No podés borrar anuncios de otro equipo.')
        return redirect('comunicacion:lista')

    if request.method == 'POST':
        titulo = anuncio.titulo
        anuncio.delete()
        messages.success(request, f'Borramos el anuncio "{titulo}".')
        return redirect('comunicacion:lista')

    return render(request, 'comunicacion/eliminar.html', {'anuncio': anuncio})