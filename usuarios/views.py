from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm


def registro(request):
    """Alta de un usuario nuevo en el sistema"""
    # Si ya está logueado, lo mandamos al home
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Ya sos parte de Los Pibes! Bienvenido al equipo.')
            return redirect('core:home')
        else:
            messages.error(request, 'Uhh, algo salió mal. Revisá los datos que cargaste.')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """Login de un usuario existente"""
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Volviste, {user.username}! Dale que arrancamos.')
                return redirect('core:home')
        else:
            messages.error(request, 'Usuario o contraseña mal. Probá de nuevo.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


@login_required
def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.info(request, 'Cerraste sesión. Nos vemos en la cancha.')
    return redirect('core:home')


@login_required
def perfil(request):
    """Mostrar los datos del usuario logueado"""
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})
