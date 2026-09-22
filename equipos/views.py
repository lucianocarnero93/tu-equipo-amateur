from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo
from .models import Equipo, Membresia, Invitacion, SolicitudIngreso
from .forms import EquipoForm, InvitacionForm, SolicitudForm


# ============================================
# EQUIPOS
# ============================================

@login_required
def mis_equipos(request):
    """Lista los equipos a los que pertenece el usuario."""
    membresias = Membresia.objects.filter(
        usuario=request.user,
        activo=True
    ).select_related('equipo').order_by('-fecha_ingreso')

    return render(request, 'equipos/mis_equipos.html', {
        'membresias': membresias,
        'equipo_activo': request.user.perfil.equipo_activo,
    })


@login_required
def crear_equipo(request):
    """Crea un equipo nuevo. El usuario se vuelve DT."""
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save()

            Membresia.objects.create(
                usuario=request.user,
                equipo=equipo,
                rol='DT'
            )

            request.user.perfil.equipo_activo = equipo
            request.user.perfil.save()

            messages.success(request, f'¡Bienvenido a {equipo.nombre}! Ya podés empezar a gestionar tu equipo.')
            return redirect('equipos:detalle', slug=equipo.slug)
    else:
        form = EquipoForm()

    return render(request, 'equipos/formulario.html', {
        'form': form,
        'titulo': 'Inscribir nuevo equipo',
    })


@login_required
def detalle_equipo(request, slug):
    """Muestra la info de un equipo."""
    equipo = get_object_or_404(Equipo, slug=slug)

    membresia = Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).first()

    if not membresia:
        messages.error(request, 'No pertenecés a ese equipo.')
        return redirect('equipos:mis_equipos')

    return render(request, 'equipos/detalle.html', {
        'equipo': equipo,
        'membresia': membresia,
    })


@login_required
def cambiar_equipo(request, slug):
    """Cambia el equipo activo del usuario."""
    equipo = get_object_or_404(Equipo, slug=slug)

    membresia = Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).first()

    if not membresia:
        messages.error(request, 'No pertenecés a ese equipo.')
        return redirect('equipos:mis_equipos')

    request.user.perfil.equipo_activo = equipo
    request.user.perfil.save()

    messages.success(request, f'Ahora estás viendo "{equipo.nombre}".')
    return redirect('core:home')


# ============================================
# INVITACIONES
# ============================================

@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def lista_invitaciones(request):
    """Muestra las invitaciones del equipo activo."""
    equipo = get_equipo_activo(request.user)
    if equipo is None:
        messages.warning(request, 'No tenés un equipo activo.')
        return redirect('core:home')

    membresia = Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).first()
    if not membresia or membresia.rol not in ['DT', 'AYUDANTE']:
        messages.error(request, 'Solo el cuerpo técnico puede ver las invitaciones.')
        return redirect('core:home')

    invitaciones = Invitacion.objects.filter(equipo=equipo).order_by('-fecha_creacion')

    return render(request, 'equipos/invitaciones.html', {
        'equipo': equipo,
        'invitaciones': invitaciones,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def crear_invitacion(request):
    """El DT o ayudante generan una invitación."""
    equipo = get_equipo_activo(request.user)
    if equipo is None:
        messages.warning(request, 'No tenés un equipo activo.')
        return redirect('core:home')

    membresia = Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).first()
    if not membresia or membresia.rol not in ['DT', 'AYUDANTE']:
        messages.error(request, 'Solo el cuerpo técnico puede crear invitaciones.')
        return redirect('core:home')

    if request.method == 'POST':
        form = InvitacionForm(request.POST)
        if form.is_valid():
            invitacion = Invitacion.objects.create(
                equipo=equipo,
                creada_por=request.user,
                rol_asignado=form.cleaned_data['rol_asignado'],
                usos_maximos=form.cleaned_data.get('usos_maximos') or 0,
            )
            messages.success(request, f'¡Invitación creada! El código es: {invitacion.codigo}')
            return redirect('equipos:lista_invitaciones')
    else:
        form = InvitacionForm()

    return render(request, 'equipos/crear_invitacion.html', {
        'form': form,
        'equipo': equipo,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def desactivar_invitacion(request, pk):
    """Desactiva una invitación existente."""
    invitacion = get_object_or_404(Invitacion, pk=pk)

    membresia = Membresia.objects.filter(
        usuario=request.user,
        equipo=invitacion.equipo,
        activo=True
    ).first()

    if not membresia or membresia.rol not in ['DT', 'AYUDANTE']:
        messages.error(request, 'No tenés permiso.')
        return redirect('core:home')

    if request.method == 'POST':
        invitacion.activa = False
        invitacion.save()
        messages.success(request, 'Invitación desactivada.')
        return redirect('equipos:lista_invitaciones')

    return render(request, 'equipos/desactivar_invitacion.html', {'invitacion': invitacion})


@login_required
def unirse_con_codigo(request):
    """Un jugador se une a un equipo usando un código."""
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()

        if not codigo:
            messages.error(request, 'Ingresá un código.')
            return render(request, 'equipos/unirse.html')

        try:
            invitacion = Invitacion.objects.get(codigo=codigo)
        except Invitacion.DoesNotExist:
            messages.error(request, 'El código no existe.')
            return render(request, 'equipos/unirse.html')

        if not invitacion.es_valida():
            messages.error(request, 'La invitación ya no es válida.')
            return render(request, 'equipos/unirse.html')

        if Membresia.objects.filter(usuario=request.user, equipo=invitacion.equipo, activo=True).exists():
            messages.warning(request, f'Ya sos miembro de {invitacion.equipo.nombre}.')
            return redirect('equipos:mis_equipos')

        Membresia.objects.create(
            usuario=request.user,
            equipo=invitacion.equipo,
            rol=invitacion.rol_asignado,
        )

        invitacion.usos_actuales += 1
        invitacion.save()

        if not request.user.perfil.equipo_activo:
            request.user.perfil.equipo_activo = invitacion.equipo
            request.user.perfil.save()

        messages.success(request, f'¡Te uniste a {invitacion.equipo.nombre} como {invitacion.get_rol_asignado_display()}!')
        return redirect('equipos:mis_equipos')

    return render(request, 'equipos/unirse.html')


# ============================================
# SOLICITUDES DE INGRESO
# ============================================

@login_required
def buscar_equipos(request):
    """El jugador busca equipos por nombre."""
    query = request.GET.get('q', '').strip()

    if query:
        equipos = Equipo.objects.filter(nombre__icontains=query, activo=True)
    else:
        equipos = Equipo.objects.filter(activo=True)

    # Marcamos los que ya es miembro
    equipos_miembro = set(
        Membresia.objects.filter(
            usuario=request.user,
            activo=True
        ).values_list('equipo_id', flat=True)
    )

    # Marcamos los que ya tiene solicitud pendiente
    solicitudes_pendientes = set(
        SolicitudIngreso.objects.filter(
            usuario=request.user,
            estado='PENDIENTE'
        ).values_list('equipo_id', flat=True)
    )

    return render(request, 'equipos/buscar.html', {
        'equipos': equipos,
        'query': query,
        'equipos_miembro': equipos_miembro,
        'solicitudes_pendientes': solicitudes_pendientes,
    })


@login_required
def solicitar_ingreso(request, slug):
    """El jugador pide unirse a un equipo."""
    equipo = get_object_or_404(Equipo, slug=slug)

    # No puede solicitar si ya es miembro
    if Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).exists():
        messages.info(request, f'Ya sos miembro de {equipo.nombre}.')
        return redirect('equipos:buscar')

    # No puede solicitar dos veces
    if SolicitudIngreso.objects.filter(usuario=request.user, equipo=equipo, estado='PENDIENTE').exists():
        messages.info(request, f'Ya pediste unirte a {equipo.nombre}. Esperá la respuesta.')
        return redirect('equipos:buscar')

    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            SolicitudIngreso.objects.create(
                equipo=equipo,
                usuario=request.user,
                mensaje=form.cleaned_data.get('mensaje', '')
            )
            messages.success(request, f'¡Pedido enviado! El DT de {equipo.nombre} va a revisarlo.')
            return redirect('equipos:buscar')
    else:
        form = SolicitudForm()

    return render(request, 'equipos/solicitar.html', {
        'equipo': equipo,
        'form': form,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def lista_solicitudes(request):
    """El DT ve las solicitudes pendientes del equipo activo."""
    equipo = get_equipo_activo(request.user)
    if equipo is None:
        messages.warning(request, 'No tenés un equipo activo.')
        return redirect('core:home')

    membresia = Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).first()
    if not membresia or membresia.rol not in ['DT', 'AYUDANTE']:
        messages.error(request, 'Solo el cuerpo técnico puede ver las solicitudes.')
        return redirect('core:home')

    pendientes = SolicitudIngreso.objects.filter(equipo=equipo, estado='PENDIENTE').order_by('-fecha_solicitud')
    historial = SolicitudIngreso.objects.filter(equipo=equipo).exclude(estado='PENDIENTE').order_by('-fecha_respuesta')[:10]

    return render(request, 'equipos/solicitudes.html', {
        'equipo': equipo,
        'pendientes': pendientes,
        'historial': historial,
    })


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def aceptar_solicitud(request, pk):
    """El DT acepta una solicitud."""
    solicitud = get_object_or_404(SolicitudIngreso, pk=pk)

    membresia = Membresia.objects.filter(
        usuario=request.user,
        equipo=solicitud.equipo,
        activo=True
    ).first()

    if not membresia or membresia.rol not in ['DT', 'AYUDANTE']:
        messages.error(request, 'No tenés permiso.')
        return redirect('core:home')

    if request.method == 'POST':
        # Crear la membresía
        Membresia.objects.get_or_create(
            usuario=solicitud.usuario,
            equipo=solicitud.equipo,
            defaults={'rol': 'JUGADOR'}
        )

        # Actualizar la solicitud
        solicitud.estado = 'ACEPTADA'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()

        # Si el usuario no tiene equipo activo, asignar este
        if not solicitud.usuario.perfil.equipo_activo:
            solicitud.usuario.perfil.equipo_activo = solicitud.equipo
            solicitud.usuario.perfil.save()

        messages.success(request, f'¡{solicitud.usuario.username} fue aceptado en el equipo!')
        return redirect('equipos:lista_solicitudes')

    return render(request, 'equipos/aceptar_solicitud.html', {'solicitud': solicitud})


@login_required
@user_passes_test(es_dt_o_ayudante, login_url='/')
def rechazar_solicitud(request, pk):
    """El DT rechaza una solicitud."""
    solicitud = get_object_or_404(SolicitudIngreso, pk=pk)

    membresia = Membresia.objects.filter(
        usuario=request.user,
        equipo=solicitud.equipo,
        activo=True
    ).first()

    if not membresia or membresia.rol not in ['DT', 'AYUDANTE']:
        messages.error(request, 'No tenés permiso.')
        return redirect('core:home')

    if request.method == 'POST':
        solicitud.estado = 'RECHAZADA'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()

        messages.success(request, f'Rechazaste la solicitud de {solicitud.usuario.username}.')
        return redirect('equipos:lista_solicitudes')

    return render(request, 'equipos/rechazar_solicitud.html', {'solicitud': solicitud})
