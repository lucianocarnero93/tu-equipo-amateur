"""
Funciones de permisos reutilizables para Tu Equipo Amateur.

Los roles viven en la Membresia (User ↔ Equipo).
Un usuario puede ser DT en un equipo y jugador en otro.
"""


def get_rol_en_equipo_activo(user):
    """
    Devuelve el rol del usuario en su equipo activo.

    Args:
        user: Instancia del User.

    Returns:
        str con el rol ('DT', 'AYUDANTE', 'JUGADOR') o None si no tiene equipo activo.
    """
    if not user.is_authenticated:
        return None

    try:
        equipo_activo = user.perfil.equipo_activo
        if not equipo_activo:
            return None

        membresia = user.membresias.filter(
            equipo=equipo_activo,
            activo=True
        ).first()

        if not membresia:
            return None

        return membresia.rol

    except AttributeError:
        return None


def es_dt(user):
    """Verifica si el usuario es DT en su equipo activo."""
    return get_rol_en_equipo_activo(user) == 'DT'


def es_ayudante(user):
    """Verifica si el usuario es Ayudante en su equipo activo."""
    return get_rol_en_equipo_activo(user) == 'AYUDANTE'


def es_dt_o_ayudante(user):
    """Verifica si el usuario es DT o Ayudante en su equipo activo."""
    return get_rol_en_equipo_activo(user) in ('DT', 'AYUDANTE')


def es_jugador(user):
    """Verifica si el usuario es Jugador en su equipo activo."""
    return get_rol_en_equipo_activo(user) == 'JUGADOR'


def es_cuerpo_tecnico(user):
    """Alias de es_dt_o_ayudante."""
    return es_dt_o_ayudante(user)
