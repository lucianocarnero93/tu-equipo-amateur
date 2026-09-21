"""
Funciones de permisos reutilizables para Tu Equipo Amateur.

Este módulo centraliza la lógica de verificación de roles para evitar
duplicar código en cada app. Todas las apps importan desde acá.
"""


def es_dt(user):
    """
    Verifica si el usuario es Director Técnico.

    Args:
        user: instancia del modelo User de Django.

    Returns:
        bool: True si es DT, False en caso contrario.
    """
    return (
        user.is_authenticated
        and hasattr(user, 'perfil')
        and user.perfil.rol == 'DT'
    )


def es_ayudante(user):
    """
    Verifica si el usuario es Ayudante de Campo.
    """
    return (
        user.is_authenticated
        and hasattr(user, 'perfil')
        and user.perfil.rol == 'AYUDANTE'
    )


def es_dt_o_ayudante(user):
    """
    Verifica si el usuario es parte del cuerpo técnico (DT o Ayudante).
    Se usa para acciones que pueden hacer ambos.
    """
    return es_dt(user) or es_ayudante(user)


def es_jugador(user):
    """
    Verifica si el usuario es Jugador.
    """
    return (
        user.is_authenticated
        and hasattr(user, 'perfil')
        and user.perfil.rol == 'JUGADOR'
    )


def es_invitado(user):
    """
    Verifica si el usuario es Invitado.
    """
    return (
        user.is_authenticated
        and hasattr(user, 'perfil')
        and user.perfil.rol == 'INVITADO'
    )


def es_cuerpo_tecnico(user):
    """
    Alias de es_dt_o_ayudante, pero con nombre más descriptivo.
    """
    return es_dt_o_ayudante(user)
