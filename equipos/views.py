from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from core.utils.permisos import es_dt, es_dt_o_ayudante
from core.utils.equipos import get_equipo_activo, sincronizar_rol_perfil
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

            # Crear la membresía del creador como DT
            Membresia.objects.create(
                usuario=request.user,
                equipo=equipo,
                rol='DT'
            )

            # Asignar como equipo activo y sincronizar rol del perfil
            request.user.perfil.equipo_activo = equipo
            request.user.perfil.save()
            sincronizar_rol_perfil(request.user)

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

    # Cambiar el equipo activo y sincronizar rol del perfil
    request.user.perfil.equipo_activo = equipo
    request.user.perfil.save()
    sincronizar_rol_perfil(request.user)

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

        sincronizar_rol_perfil(request.user)

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

    equipos_miembro = set(
        Membresia.objects.filter(
            usuario=request.user,
            activo=True
        ).values_list('equipo_id', flat=True)
    )

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

    if Membresia.objects.filter(usuario=request.user, equipo=equipo, activo=True).exists():
        messages.info(request, f'Ya sos miembro de {equipo.nombre}.')
        return redirect('equipos:buscar')

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
        Membresia.objects.get_or_create(
            usuario=solicitud.usuario,
            equipo=solicitud.equipo,
            defaults={'rol': 'JUGADOR'}
        )

        solicitud.estado = 'ACEPTADA'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()

        if not solicitud.usuario.perfil.equipo_activo:
            solicitud.usuario.perfil.equipo_activo = solicitud.equipo
            solicitud.usuario.perfil.save()

        sincronizar_rol_perfil(solicitud.usuario)

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


# ============================================
# MIEMBROS Y TRANSFERENCIA DE MANDO
# ============================================

@login_required
def lista_miembros(request, slug):
    """Muestra todos los miembros del equipo."""
    equipo = get_object_or_404(Equipo, slug=slug)

    membresia = Membresia.objects.filter(
        usuario=request.user,
        equipo=equipo,
        activo=True
    ).first()

    if not membresia:
        messages.error(request, 'No pertenecés a ese equipo.')
        return redirect('equipos:mis_equipos')

    miembros = Membresia.objects.filter(
        equipo=equipo,
        activo=True
    ).select_related('usuario').order_by('rol', 'usuario__username')

    return render(request, 'equipos/miembros.html', {
        'equipo': equipo,
        'membresia': membresia,
        'miembros': miembros,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def transferir_dt(request, slug):
    """El DT transfiere su rol a otro miembro."""
    equipo = get_object_or_404(Equipo, slug=slug)

    membresia_dt = Membresia.objects.filter(
        usuario=request.user,
        equipo=equipo,
        rol='DT',
        activo=True
    ).first()

    if not membresia_dt:
        messages.error(request, 'Solo el DT puede transferir el mando.')
        return redirect('equipos:lista_miembros', slug=slug)

    candidatos = Membresia.objects.filter(
        equipo=equipo,
        activo=True
    ).exclude(usuario=request.user).select_related('usuario')

    if not candidatos.exists():
        messages.warning(request, 'No hay otros miembros para transferir el mando.')
        return redirect('equipos:lista_miembros', slug=slug)

    if request.method == 'POST':
        nuevo_dt_id = request.POST.get('nuevo_dt')

        try:
            nuevo_dt_membresia = Membresia.objects.get(
                pk=nuevo_dt_id,
                equipo=equipo,
                activo=True
            )
        except Membresia.DoesNotExist:
            messages.error(request, 'El miembro seleccionado no existe.')
            return redirect('equipos:transferir_dt', slug=slug)

        rol_anterior_nuevo = nuevo_dt_membresia.rol

        membresia_dt.rol = rol_anterior_nuevo
        membresia_dt.save()

        nuevo_dt_membresia.rol = 'DT'
        nuevo_dt_membresia.save()

        # Sincronizar roles en los perfiles
        sincronizar_rol_perfil(membresia_dt.usuario)
        sincronizar_rol_perfil(nuevo_dt_membresia.usuario)

        messages.success(
            request,
            f'¡Ahora {nuevo_dt_membresia.usuario.username} es el DT de {equipo.nombre}! '
            f'Tu nuevo rol es {membresia_dt.get_rol_display()}.'
        )
        return redirect('equipos:lista_miembros', slug=slug)

    return render(request, 'equipos/transferir_dt.html', {
        'equipo': equipo,
        'candidatos': candidatos,
        'mi_membresia': membresia_dt,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def transferir_ayudante(request, slug):
    """El DT asigna el rol de ayudante a otro miembro."""
    equipo = get_object_or_404(Equipo, slug=slug)

    membresia_dt = Membresia.objects.filter(
        usuario=request.user,
        equipo=equipo,
        rol='DT',
        activo=True
    ).first()

    if not membresia_dt:
        messages.error(request, 'Solo el DT puede asignar al ayudante.')
        return redirect('equipos:lista_miembros', slug=slug)

    candidatos = Membresia.objects.filter(
        equipo=equipo,
        activo=True
    ).exclude(usuario=request.user).select_related('usuario')

    if request.method == 'POST':
        nuevo_ayudante_id = request.POST.get('nuevo_ayudante')

        if nuevo_ayudante_id == 'ninguno':
            # Quitar el rol de ayudante a quien lo tenga
            Membresia.objects.filter(
                equipo=equipo,
                rol='AYUDANTE'
            ).update(rol='JUGADOR')

            # Sincronizar los perfiles afectados
            for m in Membresia.objects.filter(equipo=equipo, activo=True):
                sincronizar_rol_perfil(m.usuario)

            messages.success(request, 'Ya no hay ayudante en el equipo.')
            return redirect('equipos:lista_miembros', slug=slug)

        try:
            nuevo_ayudante = Membresia.objects.get(
                pk=nuevo_ayudante_id,
                equipo=equipo,
                activo=True
            )
        except Membresia.DoesNotExist:
            messages.error(request, 'El miembro seleccionado no existe.')
            return redirect('equipos:transferir_ayudante', slug=slug)

        # Quitar el rol de ayudante al actual
        Membresia.objects.filter(
            equipo=equipo,
            rol='AYUDANTE'
        ).update(rol='JUGADOR')

        # Asignar el nuevo
        nuevo_ayudante.rol = 'AYUDANTE'
        nuevo_ayudante.save()

        # Sincronizar los perfiles afectados
        for m in Membresia.objects.filter(equipo=equipo, activo=True):
            sincronizar_rol_perfil(m.usuario)

        messages.success(
            request,
            f'¡{nuevo_ayudante.usuario.username} es el nuevo ayudante de {equipo.nombre}!'
        )
        return redirect('equipos:lista_miembros', slug=slug)

    ayudante_actual = Membresia.objects.filter(
        equipo=equipo,
        rol='AYUDANTE',
        activo=True
    ).first()

    return render(request, 'equipos/transferir_ayudante.html', {
        'equipo': equipo,
        'candidatos': candidatos,
        'ayudante_actual': ayudante_actual,
    })


@login_required
def salir_equipo(request, slug):
    """Un miembro sale del equipo."""
    equipo = get_object_or_404(Equipo, slug=slug)

    membresia = Membresia.objects.filter(
        usuario=request.user,
        equipo=equipo,
        activo=True
    ).first()

    if not membresia:
        messages.error(request, 'No sos miembro de ese equipo.')
        return redirect('equipos:mis_equipos')

    if membresia.rol == 'DT':
        otros_miembros = Membresia.objects.filter(
            equipo=equipo,
            activo=True
        ).exclude(usuario=request.user).count()

        if otros_miembros > 0:
            messages.warning(
                request,
                'Antes de salir, transferí el mando a otro miembro o asigná un nuevo DT.'
            )
            return redirect('equipos:transferir_dt', slug=slug)

    if request.method == 'POST':
        membresia.activo = False
        membresia.save()

        if request.user.perfil.equipo_activo == equipo:
            siguiente = Membresia.objects.filter(
                usuario=request.user,
                activo=True
            ).first()

            if siguiente:
                request.user.perfil.equipo_activo = siguiente.equipo
            else:
                request.user.perfil.equipo_activo = None

            request.user.perfil.save()
            sincronizar_rol_perfil(request.user)

        messages.success(request, f'Saliste de {equipo.nombre}.')
        return redirect('equipos:mis_equipos')

    return render(request, 'equipos/salir_equipo.html', {
        'equipo': equipo,
        'membresia': membresia,
    })


@login_required
@user_passes_test(es_dt, login_url='/')
def expulsar_miembro(request, slug, membresia_id):
    """El DT expulsa a un miembro."""
    equipo = get_object_or_404(Equipo, slug=slug)

    if not Membresia.objects.filter(
        usuario=request.user,
        equipo=equipo,
        rol='DT',
        activo=True
    ).exists():
        messages.error(request, 'Solo el DT puede expulsar miembros.')
        return redirect('equipos:lista_miembros', slug=slug)

    membresia = get_object_or_404(Membresia, pk=membresia_id, equipo=equipo)

    if membresia.usuario == request.user:
        messages.error(request, 'No podés expulsarte a vos mismo. Usá "Salir del equipo".')
        return redirect('equipos:lista_miembros', slug=slug)

    if request.method == 'POST':
        membresia.activo = False
        membresia.save()

        if membresia.usuario.perfil.equipo_activo == equipo:
            siguiente = Membresia.objects.filter(
                usuario=membresia.usuario,
                activo=True
            ).first()

            if siguiente:
                membresia.usuario.perfil.equipo_activo = siguiente.equipo
            else:
                membresia.usuario.perfil.equipo_activo = None

            membresia.usuario.perfil.save()
            sincronizar_rol_perfil(membresia.usuario)

        messages.success(request, f'{membresia.usuario.username} fue expulsado del equipo.')
        return redirect('equipos:lista_miembros', slug=slug)

    return render(request, 'equipos/expulsar_miembro.html', {
        'equipo': equipo,
        'membresia': membresia,
    })
