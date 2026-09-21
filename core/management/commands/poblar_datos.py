from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, time, timedelta
import random

from usuarios.models import Perfil
from jugadores.models import Jugador
from partidos.models import Partido
from asistencias.models import Asistencia
from alineaciones.models import Alineacion
from estadisticas.models import Estadistica
from comunicacion.models import Anuncio


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔄 Limpiando datos anteriores...'))

        # Limpiar datos (excepto superusuarios)
        Estadistica.objects.all().delete()
        Alineacion.objects.all().delete()
        Asistencia.objects.all().delete()
        Partido.objects.all().delete()
        Jugador.objects.all().delete()
        Anuncio.objects.all().delete()
        Perfil.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('✅ Datos anteriores eliminados'))

        # === CREAR USUARIOS ===
        self.stdout.write(self.style.WARNING('👥 Creando usuarios...'))

        # Director Técnico
        dt_user = User.objects.create_user(
            username='dt_diego',
            email='dt@lospibes.com',
            password='dt12345',
            first_name='Diego',
            last_name='Fernández'
        )
        dt_user.perfil.rol = 'DT'
        dt_user.perfil.telefono = '11-5555-0001'
        dt_user.perfil.save()

        # Ayudante
        ayudante_user = User.objects.create_user(
            username='ayudante_marce',
            email='ayudante@lospibes.com',
            password='ayudante123',
            first_name='Marcelo',
            last_name='Rodríguez'
        )
        ayudante_user.perfil.rol = 'AYUDANTE'
        ayudante_user.perfil.save()

        # Jugadores
        jugadores_data = [
            ('juan_perez', 'Juan', 'Pérez', 'DELANTERO', 9, '1995-05-15', '11-5555-1001'),
            ('carlos_gomez', 'Carlos', 'Gómez', 'MEDIOCAMPISTA', 8, '1993-08-20', '11-5555-1002'),
            ('luis_martinez', 'Luis', 'Martínez', 'DEFENSOR', 4, '1990-03-10', '11-5555-1003'),
            ('pedro_lopez', 'Pedro', 'López', 'ARQUERO', 1, '1992-11-25', '11-5555-1004'),
            ('matias_diaz', 'Matías', 'Díaz', 'DEFENSOR', 2, '1994-07-05', '11-5555-1005'),
            ('sebastian_ruiz', 'Sebastián', 'Ruiz', 'DEFENSOR', 3, '1996-01-30', '11-5555-1006'),
            ('nicolas_torres', 'Nicolás', 'Torres', 'MEDIOCAMPISTA', 5, '1995-09-12', '11-5555-1007'),
            ('federico_silva', 'Federico', 'Silva', 'MEDIOCAMPISTA', 6, '1997-04-18', '11-5555-1008'),
            ('martin_rojas', 'Martín', 'Rojas', 'MEDIOCAMPISTA', 7, '1994-12-03', '11-5555-1009'),
            ('gabriel_morales', 'Gabriel', 'Morales', 'DELANTERO', 10, '1993-06-22', '11-5555-1010'),
            ('alejandro_ortiz', 'Alejandro', 'Ortiz', 'DELANTERO', 11, '1996-02-14', '11-5555-1011'),
            ('diego_romero', 'Diego', 'Romero', 'DEFENSOR', 12, '1991-10-08', '11-5555-1012'),
            ('pablo_vargas', 'Pablo', 'Vargas', 'MEDIOCAMPISTA', 13, '1995-03-27', '11-5555-1013'),
            ('sergio_castro', 'Sergio', 'Castro', 'DELANTERO', 14, '1998-08-15', '11-5555-1014'),
            ('andres_flores', 'Andrés', 'Flores', 'DEFENSOR', 15, '1992-05-20', '11-5555-1015'),
            ('rodrigo_herrera', 'Rodrigo', 'Herrera', 'MEDIOCAMPISTA', 16, '1997-11-11', '11-5555-1016'),
            ('emiliano_nunez', 'Emiliano', 'Núñez', 'DELANTERO', 17, '1994-09-30', '11-5555-1017'),
            ('facundo_benitez', 'Facundo', 'Benítez', 'ARQUERO', 18, '1996-12-05', '11-5555-1018'),
        ]

        jugadores = []
        for username, nombre, apellido, posicion, dorsal, fecha_nac, telefono in jugadores_data:
            user = User.objects.create_user(
                username=username,
                email=f'{username}@lospibes.com',
                password='jugador123',
                first_name=nombre,
                last_name=apellido
            )
            user.perfil.rol = 'JUGADOR'
            user.perfil.telefono = telefono
            user.perfil.fecha_nacimiento = fecha_nac
            user.perfil.posicion = posicion
            user.perfil.save()

            jugador = Jugador.objects.create(
                usuario=user,
                nombre=nombre,
                apellido=apellido,
                email=f'{username}@lospibes.com',
                telefono=telefono,
                fecha_nacimiento=fecha_nac,
                posicion=posicion,
                dorsal=dorsal,
                activo=True
            )
            jugadores.append(jugador)

        self.stdout.write(self.style.SUCCESS(f'✅ {len(jugadores)} jugadores creados'))

        # === CREAR PARTIDOS ===
        self.stdout.write(self.style.WARNING('⚽ Creando partidos...'))

        hoy = date.today()
        rivales = [
            'Los Gallos', 'El Equipo FC', 'Los Leones', 'Deportivo Norte',
            'Atlético Sur', 'Villa Unida', 'Racing Club Amateur', 'Los Tigres',
            'Barrio Norte', 'Unión FC'
        ]
        lugares = [
            'Cancha Municipal', 'Estadio Central', 'Complejo Deportivo',
            'Club Atlético Local', 'Predio La Esperanza'
        ]

        partidos = []

        # 3 partidos finalizados (con estadísticas)
        for i in range(3):
            fecha = hoy - timedelta(days=7 * (i + 1))
            goles_local = random.randint(0, 5)
            goles_visitante = random.randint(0, 4)
            partido = Partido.objects.create(
                fecha=fecha,
                hora=time(15, 0),
                lugar=random.choice(lugares),
                rival=rivales[i],
                goles_local=goles_local,
                goles_visitante=goles_visitante,
                estado='FINALIZADO',
                creado_por=dt_user
            )
            partidos.append(partido)

        # 2 partidos próximos
        for i in range(2):
            fecha = hoy + timedelta(days=7 * (i + 1))
            partido = Partido.objects.create(
                fecha=fecha,
                hora=time(15, 0),
                lugar=random.choice(lugares),
                rival=rivales[i + 3],
                goles_local=0,
                goles_visitante=0,
                estado='PROGRAMADO',
                creado_por=dt_user
            )
            partidos.append(partido)

        self.stdout.write(self.style.SUCCESS(f'✅ {len(partidos)} partidos creados'))

        # === CREAR ASISTENCIAS PARA PRÓXIMOS PARTIDOS ===
        self.stdout.write(self.style.WARNING('📋 Creando asistencias...'))

        proximos = [p for p in partidos if p.estado == 'PROGRAMADO']
        for partido in proximos:
            for jugador in jugadores:
                estado = random.choice(['CONFIRMADO', 'CONFIRMADO', 'CONFIRMADO', 'DUDA', 'RECHAZADO'])
                Asistencia.objects.create(
                    partido=partido,
                    jugador=jugador,
                    estado=estado,
                    comentario='' if estado == 'CONFIRMADO' else random.choice(['Llego tarde', 'Tengo un compromiso', 'Puede que vaya', ''])
                )

        self.stdout.write(self.style.SUCCESS('✅ Asistencias creadas'))

        # === CREAR ALINEACIONES Y ESTADÍSTICAS ===
        self.stdout.write(self.style.WARNING('📊 Creando alineaciones y estadísticas...'))

        finalizados = [p for p in partidos if p.estado == 'FINALIZADO']
        for partido in finalizados:
            jugadores_disponibles = list(jugadores)
            random.shuffle(jugadores_disponibles)
            titulares = jugadores_disponibles[:11]
            suplentes = jugadores_disponibles[11:16]

            for i, jugador in enumerate(titulares):
                Alineacion.objects.create(
                    partido=partido,
                    jugador=jugador,
                    tipo='TITULAR',
                    orden=i
                )
            for i, jugador in enumerate(suplentes):
                Alineacion.objects.create(
                    partido=partido,
                    jugador=jugador,
                    tipo='SUPLENTE',
                    orden=i
                )

            for jugador in jugadores_disponibles[:15]:
                es_titular = jugador in titulares
                Estadistica.objects.create(
                    partido=partido,
                    jugador=jugador,
                    goles=random.choices([0, 0, 0, 1, 1, 2], k=1)[0],
                    asistencias=random.choices([0, 0, 0, 1, 1], k=1)[0],
                    tiempo_jugado=random.choice(['COMPLETO', 'COMPLETO', 'SALIO_2DO', 'ENTRO_2DO']),
                    tarjetas_amarillas=random.choices([0, 0, 0, 0, 1], k=1)[0],
                    tarjetas_rojas=0
                )

        self.stdout.write(self.style.SUCCESS('✅ Alineaciones y estadísticas creadas'))

        # === CREAR ANUNCIOS ===
        self.stdout.write(self.style.WARNING('📢 Creando anuncios...'))

        anuncios_data = [
            ('Bienvenidos a la nueva temporada',
             'Arrancamos un nuevo año con muchas expectativas. Vamos a entrenar los martes y jueves a las 20hs en la cancha de siempre. ¡A darle con todo!',
             'ALTA'),
            ('Recordatorio: Confirmar asistencia',
             'Chicos, por favor confirmen la asistencia al próximo partido antes del viernes. Así el DT puede armar la alineación con tiempo.',
             'MEDIA'),
            ('Cambio de horario del entrenamiento',
             'Esta semana el entrenamiento del jueves pasa a las 21hs por un evento en la cancha. Avisen si tienen problemas para asistir.',
             'URGENTE'),
            ('Felicitaciones por el triunfo',
             'Excelente partido el sábado. Gran actuación de todos. ¡Vamos por más!',
             'BAJA'),
            ('Lesiones y recuperación',
             'Recordamos que si están lesionados avisen al DT para no exigir de más. La salud es lo primero.',
             'MEDIA'),
        ]

        for titulo, contenido, prioridad in anuncios_data:
            Anuncio.objects.create(
                titulo=titulo,
                contenido=contenido,
                prioridad=prioridad,
                autor=dt_user,
                activo=True
            )

        self.stdout.write(self.style.SUCCESS(f'✅ {len(anuncios_data)} anuncios creados'))

        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Base de datos poblada exitosamente!'))
        self.stdout.write(self.style.WARNING('\n📝 Credenciales de acceso:'))
        self.stdout.write('  🔵 DT: dt_diego / dt12345')
        self.stdout.write('  🟢 Ayudante: ayudante_marce / ayudante123')
        self.stdout.write('  🟡 Jugador: juan_perez / jugador123')
