from django.shortcuts import render

def home(request):
    """Vista para la página de inicio"""
    context = {
        'titulo': 'Muchachooos, bienvenidos al vestuario virtual!!',
        'descripcion': 'Acá vas a poder organizar todo lo del equipo: los partidos, la asistencia, las estadísticas y mucho más. Nada de andar perdiendo info en el grupo de WhatsApp.',
        'features': [
            {
                'icon': 'fa-users',
                'title': 'Los Pibes',
                'desc': 'Mira el plantel completo',
                'url_name': 'jugadores:lista'
            },
            {
                'icon': 'fa-calendar-alt',
                'title': 'Partidos',
                'desc': 'Enterate de todo, cuando y donde se juega',
                'url_name': 'partidos:lista'
            },
            {
                'icon': 'fa-chart-line',
                'title': 'Estadísticas',
                'desc': 'Seguimiento de rendimiento',
                'url_name': 'estadisticas:reportes'
            },
            {
                'icon': 'fa-bullhorn',
                'title': 'Anuncios',
                'desc': 'Novedades del tecnico y del  equipo',
                'url_name': 'comunicacion:lista'
            }
        ]
    }
    return render(request, 'core/home.html', context)
