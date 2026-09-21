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
