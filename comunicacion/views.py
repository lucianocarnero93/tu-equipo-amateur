from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Anuncio
from .forms import AnuncioForm


def es_dt(user):
    """Chequea si el usuario es el técnico (DT)"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'DT'


def lista_anuncios(request):
    """Muestra todos los anuncios activos (público)"""
    anuncios = Anuncio.objects.filter(activo=True)

    # Filtramos por prioridad si eligen una
    prioridad = request.GET.get('prioridad')
    if prioridad:
        anuncios = anuncios.filter(prioridad=prioridad)

    es_dt_user = es_dt(request.user) if request.user.is_authenticated else False

    return render(request, 'comunicacion/lista.html', {
        'anuncios': anuncios,
        'es_dt': es_dt_user,
        'prioridad_actual': prioridad,
    })


@login_required
def detalle_anuncio(request, pk):
    """Muestra el anuncio completo"""
    anuncio = get_object_or_404(Anuncio, pk=pk)
    es_dt_user = es_dt(request.user)

    return render(request, 'comunicacion/detalle.html', {
        'anuncio': anuncio,
        'es_dt': es_dt_user,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def crear_anuncio(request):
    """El DT publica un anuncio nuevo"""
    if request.method == 'POST':
        form = AnuncioForm(request.POST)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.autor = request.user
            anuncio.save()
            messages.success(request, f'Quedó publicado el anuncio "{anuncio.titulo}".')
            return redirect('comunicacion:lista')
        else:
            messages.error(request, 'Uhh, revisá los datos porque algo no cierra.')
    else:
        form = AnuncioForm()

    return render(request, 'comunicacion/formulario.html', {
        'form': form,
        'titulo': 'Publicar un anuncio'
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def editar_anuncio(request, pk):
    """El DT puede corregir un anuncio ya publicado"""
    anuncio = get_object_or_404(Anuncio, pk=pk)

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
        'anuncio': anuncio
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def eliminar_anuncio(request, pk):
    """El DT puede borrar un anuncio"""
    anuncio = get_object_or_404(Anuncio, pk=pk)

    if request.method == 'POST':
        titulo = anuncio.titulo
        anuncio.delete()
        messages.success(request, f'Borramos el anuncio "{titulo}".')
        return redirect('comunicacion:lista')

    return render(request, 'comunicacion/eliminar.html', {'anuncio': anuncio})
