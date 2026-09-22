"""
Utilidades para trabajar con equipos.
"""
from django.contrib import messages


def get_equipo_activo(user):
    """
    Devuelve el equipo activo del usuario logueado.

    Args:
        user: Instancia del User de Django.

    Returns:
        Equipo: el equipo activo, o None si no tiene.
    """
    if not user.is_authenticated:
        return None

    try:
        return user.perfil.equipo_activo
    except AttributeError:
        return None


def get_equipo_activo_o_aviso(request):
    """
    Devuelve el equipo activo o muestra un mensaje de aviso.

    Args:
        request: La petición HTTP.

    Returns:
        Equipo o None. Si no tiene equipo, agrega un mensaje flash.
    """
    equipo = get_equipo_activo(request.user)

    if equipo is None:
        messages.warning(
            request,
            'No tenés un equipo activo. Elegí uno o creá tu equipo.'
        )

    return equipo

def sincronizar_rol_perfil(user):
    """
    Sincroniza el rol del Perfil con la Membresia del equipo activo.

    Se debe llamar cada vez que:
    - El usuario cambia de equipo activo.
    - El usuario se une a un equipo.
    - Cambia el rol del usuario en el equipo activo.
    """
    if not user.is_authenticated:
        return

    if not hasattr(user, 'perfil'):
        return

    if not user.perfil.equipo_activo:
        return

    membresia = user.membresias.filter(
        equipo=user.perfil.equipo_activo,
        activo=True
    ).first()

    if membresia:
        user.perfil.rol = membresia.rol
        user.perfil.save()
