from django.db import migrations


def crear_equipo_y_asignar(apps, schema_editor):
    """
    Crea el equipo 'Los Pibes' y asigna todos los datos actuales:
    - Todos los jugadores
    - Todos los partidos
    - Todos los anuncios
    - Crea membresías para todos los usuarios según su rol en el perfil
    """
    Equipo = apps.get_model('equipos', 'Equipo')
    Membresia = apps.get_model('equipos', 'Membresia')
    Perfil = apps.get_model('usuarios', 'Perfil')
    Jugador = apps.get_model('jugadores', 'Jugador')
    Partido = apps.get_model('partidos', 'Partido')
    Anuncio = apps.get_model('comunicacion', 'Anuncio')

    # 1. Crear el equipo "Los Pibes"
    equipo, created = Equipo.objects.get_or_create(
        slug='los-pibes',
        defaults={
            'nombre': 'Los Pibes',
            'color_primario': '#1a73e8',
            'color_secundario': '#34a853',
            'descripcion': 'Club Atlético Los Pibes - Equipo amateur de fútbol',
            'activo': True,
        }
    )

    # 2. Crear membresías para todos los usuarios con perfil
    for perfil in Perfil.objects.all():
        if perfil.usuario:
            # Traducir el rol del perfil al rol de la membresía
            rol_membresia = 'JUGADOR'
            if perfil.rol == 'DT':
                rol_membresia = 'DT'
            elif perfil.rol == 'AYUDANTE':
                rol_membresia = 'AYUDANTE'
            elif perfil.rol == 'JUGADOR':
                rol_membresia = 'JUGADOR'

            Membresia.objects.get_or_create(
                usuario=perfil.usuario,
                equipo=equipo,
                defaults={'rol': rol_membresia}
            )

            # Asignar el equipo activo al perfil
            perfil.equipo_activo = equipo
            perfil.save()

    # 3. Asignar el equipo a todos los jugadores
    Jugador.objects.all().update(equipo=equipo)

    # 4. Asignar el equipo a todos los partidos
    Partido.objects.all().update(equipo=equipo)

    # 5. Asignar el equipo a todos los anuncios
    Anuncio.objects.all().update(equipo=equipo)


def revertir(apps, schema_editor):
    """Revierte la migración."""
    Equipo = apps.get_model('equipos', 'Equipo')
    Membresia = apps.get_model('equipos', 'Membresia')
    Perfil = apps.get_model('usuarios', 'Perfil')
    Jugador = apps.get_model('jugadores', 'Jugador')
    Partido = apps.get_model('partidos', 'Partido')
    Anuncio = apps.get_model('comunicacion', 'Anuncio')

    # Desasignar todo
    Jugador.objects.all().update(equipo=None)
    Partido.objects.all().update(equipo=None)
    Anuncio.objects.all().update(equipo=None)
    Perfil.objects.all().update(equipo_activo=None)

    # Borrar las membresías y el equipo
    Membresia.objects.all().delete()
    Equipo.objects.filter(slug='los-pibes').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('equipos', '0001_initial'),
        ('usuarios', '0002_perfil_equipo_activo'),
        ('jugadores', '0002_jugador_equipo_alter_jugador_dorsal'),
        ('partidos', '0002_partido_equipo'),
        ('comunicacion', '0002_anuncio_equipo'),
    ]

    operations = [
        migrations.RunPython(crear_equipo_y_asignar, revertir),
    ]
