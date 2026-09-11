# Tu Equipo Amateur ⚽

Aplicación web para la gestión administrativa y deportiva del Club Atlético **"Los Pibes"**, los pibes sos vos, es tu equipo de fútbol amateur que juega los sábados en un torneo local.

**Trabajo práctico final de Programación II**
**Autor:** Luciano Carnero

---

## 📋 ¿Qué hace?

Esta aplicación reemplaza las planillas de papel, el grupo de WhatsApp y las hojas de cálculo por una plataforma web centralizada. Sirve tanto para el cuerpo técnico como para los jugadores.

### Para el cuerpo técnico (DT y ayudante):

- Agendar partidos con fecha, hora, lugar y rival
- Ver quién confirmó asistencia a cada partido en tiempo real
- Armar la formación con titulares y suplentes
- Cargar los números de cada jugador (goles, asistencias, minutos, tarjetas)
- Ver rankings del equipo: goleadores, asistidores, más presencias
- Publicar anuncios en un tablón digital

### Para los jugadores:

- Ver los partidos que vienen y confirmar asistencia (voy / no voy / duda)
- Consultar su propio historial y estadísticas personales
- Ver la formación del próximo partido
- Estar al tanto de las novedades del equipo

---

## 🛠️ Tecnologías usadas

- **Backend:** Django 6.1.1 (Python 3.12)
- **Base de datos:** SQLite (desarrollo)
- **Frontend:** HTML5, CSS3, Bootstrap 5, Font Awesome
- **Autenticación:** Django Authentication
- **Servidor de desarrollo:** Django Development Server

---

## 📁 Estructura del proyecto

El proyecto está dividido en 8 aplicaciones, cada una con una responsabilidad clara:

| Aplicación | ¿Para qué sirve? |

| `core` | Página de inicio y templates base |
| `usuarios` | Registro, login y perfiles con roles |
| `jugadores` | Gestión del plantel |
| `partidos` | Agenda de partidos y resultados |
| `asistencias` | Confirmación de asistencia a partidos |
| `alineaciones` | Titulares y suplentes por partido |
| `estadisticas` | Goles, asistencias, minutos y reportes |
| `comunicacion` | Tablón de anuncios del cuerpo técnico |

---

## 🚀 Cómo levantar el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/lucianocarnero93/tu-equipo-amateur.git
cd tu-equipo-amateur
