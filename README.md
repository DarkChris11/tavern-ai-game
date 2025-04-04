# Pygame AI RPG - Documentación

![Pygame AI RPG](assets/images/game_banner.png)

## Descripción
Pygame AI RPG es un juego de rol por turnos donde controlas a un Brujo y una Curandera aliada que deben enfrentarse a diversos enemigos. El juego integra inteligencia artificial para controlar el comportamiento de los enemigos, creando una experiencia de combate dinámica y estratégica.

## Características principales
- Sistema de combate por turnos
- Múltiples habilidades y ataques con efectos visuales
- Efectos de estado (veneno, sangrado, congelación, etc.)
- IA para controlar enemigos y aliados
- Integración con ChatGPT para decisiones estratégicas
- Interfaz visual con animaciones de ataque
- Sistema de mensajes de combate

## Requisitos
- Python 3.7 o superior
- Pygame 2.0.0 o superior
- OpenAI Python (opcional, para integración con IA)
- Dotenv (para manejo de variables de entorno)

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/DarkChris11/tavern-ai-game
cd pygame-ai-game
```

2. Crea y activa un entorno virtual:
```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configuración de la API de OpenAI (opcional):
   - Crea un archivo .env en la raíz del proyecto
   - Añade tu clave de API: `OPENAI_API_KEY=tu_clave_aqui`

## Cómo jugar

### Iniciar el juego
```bash
python main.py
```

### Controles
- **Números 1-5**: Usar ataques/habilidades
- **Tab**: Cambiar entre objetivos enemigos
- **P**: Usar poción
- **D**: Defender
- **C**: Borrar historial de mensajes

### Mecánicas de juego
- **Combate por turnos**: Tú atacas primero, luego los enemigos
- **Efectos de estado**: Algunos ataques aplican efectos que duran varios turnos
- **Aliado**: La Curandera te ayudará usando su IA para decidir entre atacar o curarte
- **Pociones**: Usa pociones para recuperar salud en momentos críticos

## Estructura del proyecto

```
pygame-ai-game/
├── assets/
│   └── images/       # Imágenes del juego
├── config/
│   └── openai_config.json   # Configuración de la API
├── src/
│   ├── abilities.py         # Sistema de ataques y efectos
│   ├── characters.py        # Clases de personajes
│   ├── enemies.py           # Generación de enemigos
│   ├── engine.py            # Motor principal del juego
│   ├── scenarios.py         # Escenarios y progresión
│   ├── ui.py                # Interfaz de usuario
│   └── ai/                  # Módulos de IA
│       ├── chatgpt_client.py  # Cliente para OpenAI
│       └── decision_engine.py # Lógica de decisiones
├── main.py                  # Punto de entrada
└── requirements.txt         # Dependencias
```

## Integración con ChatGPT

El juego utiliza la API de OpenAI para mejorar el comportamiento de los enemigos. Los enemigos evaluarán la situación de combate y tomarán decisiones estratégicas basadas en:

- Salud actual del jugador y aliados
- Ataques disponibles y sus efectos
- Presencia de efectos de estado
- Priorización de objetivos

Para habilitar esta función, asegúrate de:
1. Tener una clave API válida de OpenAI
2. Configurar correctamente el archivo .env
3. Verificar la configuración en openai_config.json

## Personalización

### Añadir nuevos ataques
Edita characters.py para añadir nuevos ataques a personajes:

```python
"Nuevo Ataque": {
    "dice": 2,        # Número de dados
    "sides": 8,       # Caras por dado
    "type": "magic",  # Tipo (physical, magic, holy)
    "effect": "veneno" # Efecto opcional
},
```

### Crear nuevos enemigos
Modifica enemies.py para añadir nuevos tipos de enemigos con sus propios ataques y estadísticas.

## Créditos
- Desarrollado con Pygame
- Integración con la API de ChatGPT de OpenAI

## Licencia
Este proyecto está bajo la licencia MIT.

---

¡Disfruta del juego y que tus decisiones estratégicas te lleven a la victoria!
