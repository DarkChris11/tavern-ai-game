import pygame
import sys
import os
import json
import math
import random
import threading
from src.ui import COLORS, font_large, font_medium, font_small

# Intentar importar los modelos, con fallback si no están disponibles
try:
    from src.ai.list_models import MODEL_NAMES, get_model_index, get_model_id
    from src.ai.chatgpt_client import ChatGPTClient
except ImportError:
    print("Módulos de IA no encontrados. Usando valores por defecto.")
    MODEL_NAMES = ["GPT-3.5", "GPT-4", "Local"]

    def get_model_index(model_id):
        if model_id == "gpt-4":
            return 1
        if model_id == "local":
            return 2
        return 0  # gpt-3.5-turbo por defecto

    def get_model_id(model_name):
        if model_name == "GPT-4":
            return "gpt-4"
        if model_name == "Local":
            return "local"
        return "gpt-3.5-turbo"


# Variable global para almacenar configuración
_CONFIG = {
    "difficulty": "Normal",
    "music": True,
    "sound_effects": True,
    "ai_model": "gpt-3.5-turbo",
}


# Generador de consejos y frases épicas por IA
class WisdomGenerator:
    def __init__(self, model_id="gpt-3.5-turbo"):
        self.model_id = model_id
        self.client = None
        self.current_phrase = "Cargando sabiduría ancestral..."
        self.phrases = [
            "Los héroes se forjan en la adversidad y se definen por sus decisiones.",
            "La estrategia supera a la fuerza bruta; planifica tu victoria.",
            "Incluso el guerrero más experimentado fue una vez un aprendiz.",
            "El conocimiento es tan poderoso como cualquier arma encantada.",
            "La verdadera victoria no solo está en derrotar a tus enemigos, sino en superar tus propios límites.",
            "Recuerda revisar tu inventario antes de cada batalla importante.",
            "Siempre ten pociones de reserva para momentos críticos.",
            "La paciencia es una virtud, especialmente contra jefes difíciles.",
        ]
        self.initialized = False
        threading.Thread(target=self._initialize_client, daemon=True).start()

    def _initialize_client(self):
        try:
            self.client = ChatGPTClient(model_id=self.model_id)
            self.initialized = True
        except Exception as e:
            print(
                f"No se pudo inicializar el cliente de IA para el generador de frases: {e}"
            )

    def get_random_phrase(self):
        """Devuelve una frase aleatoria del conjunto predefinido"""
        return random.choice(self.phrases)

    def generate_new_phrase(self):
        """Intenta generar una nueva frase usando la IA"""
        if not self.initialized or not self.client or not self.client.is_initialized():
            self.current_phrase = self.get_random_phrase()
            return self.current_phrase

        try:
            prompts = [
                "Genera un consejo corto y útil para un jugador de RPG táctico con combate por turnos.",
                "Crea una frase épica y motivadora para un héroe que se embarca en una aventura.",
                "Ofrece una perla de sabiduría sobre estrategia de combate en un juego RPG.",
                "Comparte un secreto que todo aventurero debería conocer en una frase corta.",
                "Da un consejo místico sobre el poder de la magia y la estrategia en batalla.",
            ]

            response = self.client.get_completion(random.choice(prompts))

            if response and len(response) > 10:
                # Truncar si es demasiado largo
                if len(response) > 120:
                    response = response[:120] + "..."
                self.current_phrase = response
                # Añadir a la colección para futuras referencias
                self.phrases.append(response)
            else:
                self.current_phrase = self.get_random_phrase()
        except Exception as e:
            print(f"Error generando frase: {e}")
            self.current_phrase = self.get_random_phrase()

        return self.current_phrase


# Clase para efectos visuales
class VisualEffects:
    @staticmethod
    def draw_particle_background(screen, time, num_particles=50):
        """Dibuja un fondo con partículas mágicas flotantes"""
        width, height = screen.get_size()
        for i in range(num_particles):
            # Reducir velocidad de movimiento
            x = width * 0.1 + (width * 0.8) * (
                0.5 + 0.5 * math.sin(time * 0.0003 + i * 0.2)
            )
            y = height * 0.1 + (height * 0.8) * (
                0.5 + 0.5 * math.cos(time * 0.0004 + i * 0.3)
            )

            # Reducir velocidad de cambio de tamaño y color
            size = max(2, 2 + 3 * math.sin(time * 0.0008 + i))
            alpha = max(
                30, min(255, 100 + 155 * abs(math.sin(time * 0.0003 + i * 0.2)))
            )

            # Reducir velocidad de cambio de color y DEFINIR r, g, b
            hue = (time * 0.003 + i * 10) % 360
            r, g, b = VisualEffects.hsv_to_rgb(hue, 0.7, 0.9)  # Esta línea faltaba

            # Crear superficie solo si el tamaño es válido
            if size > 0:
                surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(
                    surf, (r, g, b, alpha), (int(size), int(size)), int(size)
                )
                screen.blit(surf, (int(x - size), int(y - size)))

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convierte HSV a RGB para generar colores dinámicos"""
        h = h % 360
        h_i = int(h / 60)
        f = h / 60 - h_i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if h_i == 0:
            r, g, b = v, t, p
        elif h_i == 1:
            r, g, b = q, v, p
        elif h_i == 2:
            r, g, b = p, v, t
        elif h_i == 3:
            r, g, b = p, q, v
        elif h_i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return int(r * 255), int(g * 255), int(b * 255)

    @staticmethod
    def draw_magical_border(screen, rect, color, time, thickness=3):
        """Dibuja un borde mágico pulsante alrededor de un elemento"""
        # Asegurar valores positivos para todos los parámetros
        if rect.width <= 0 or rect.height <= 0:
            return  # No dibujar si el rectángulo tiene dimensiones inválidas

        # Reducir velocidad de pulsación
        pulse = 0.5 + 0.5 * math.sin(time * 0.0015)  # 0.005 → 0.0015
        alpha = int(155 + 100 * pulse)

        # Garantizar tamaño de brillo positivo
        glow_size = max(1, thickness + int(thickness * 2 * pulse))

        # Verificar tamaño final
        if rect.width + glow_size * 2 <= 0 or rect.height + glow_size * 2 <= 0:
            return

        # Crear superficie con dimensiones seguras
        glow_surf = pygame.Surface(
            (max(1, rect.width + glow_size * 2), max(1, rect.height + glow_size * 2)),
            pygame.SRCALPHA,
        )

        # Color base con transparencia
        r, g, b = color
        pygame.draw.rect(
            glow_surf,
            (r, g, b, alpha),
            (0, 0, glow_surf.get_width(), glow_surf.get_height()),
            border_radius=10,
        )

        # Dibujar el borde interior más brillante
        inner_rect = pygame.Rect(
            glow_size // 2,
            glow_size // 2,
            rect.width + glow_size,
            rect.height + glow_size,
        )
        pygame.draw.rect(
            glow_surf,
            (min(r + 50, 255), min(g + 50, 255), min(b + 50, 255), alpha),
            inner_rect,
            glow_size // 2,
            border_radius=8,
        )

        # Posicionar y dibujar
        glow_rect = glow_surf.get_rect(center=rect.center)
        screen.blit(glow_surf, (glow_rect.x - glow_size, glow_rect.y - glow_size))


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.options = ["Jugar", "Tutorial", "Opciones", "Salir"]
        self.selected = 0
        self.clock = pygame.time.Clock()
        self.time = 0  # Contador para animaciones

        # Cargar imagen de fondo (si existe)
        self.background = None
        bg_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "images",
            "background.jpg",
        )
        try:
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(
                    self.background, (self.width, self.height)
                )
        except Exception as e:
            print(f"Error cargando imagen de fondo: {e}")

        # Generador de frases sabias
        config = get_config()
        self.wisdom = WisdomGenerator(model_id=config["ai_model"])
        self.current_wisdom = self.wisdom.get_random_phrase()
        self.wisdom_opacity = 0
        self.wisdom_visible = False
        self.wisdom_timer = 0
        self.show_wisdom = True

        # Sonidos (si se implementan)
        self.select_sound = None
        self.confirm_sound = None

        # Decoraciones
        self.decoration_images = []
        # Intentar cargar decoraciones (espadas, escudos, etc.)
        try:
            deco_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets",
                "images",
                "decorations",
            )
            if os.path.exists(deco_path):
                for file in os.listdir(deco_path):
                    if file.endswith(".png") or file.endswith(".jpg"):
                        img = pygame.image.load(os.path.join(deco_path, file))
                        self.decoration_images.append(img)
        except Exception as e:
            print(f"No se pudieron cargar decoraciones: {e}")

    def reset(self):
        """Reinicia elementos del menú para una nueva sesión"""
        # NO generar nueva frase, solo resetear visibilidad
        # ELIMINADO: self.current_wisdom = self.wisdom.generate_new_phrase()
        self.wisdom_timer = 0
        self.wisdom_opacity = 0
        self.wisdom_visible = True

    def draw(self):
        # Actualizar contador de tiempo para animaciones
        self.time += self.clock.get_time()

        # Dibujar fondo
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # Fondo gradiente dinámico
            for y in range(self.height):
                color_value = int(y / self.height * 100)
                pulse = 10 * math.sin(self.time * 0.0005)
                pygame.draw.line(
                    self.screen,
                    (20, 20 + pulse, 50 + color_value + pulse),
                    (0, y),
                    (self.width, y),
                )

        # Dibujar partículas mágicas
        VisualEffects.draw_particle_background(self.screen, self.time, 30)

        # Título del juego
        title_size = font_large.size("Pygame AI RPG")
        title_height = title_size[1]
        title_y = self.height // 4

        # Efecto de título con sombra y brillo
        shadow_offset = int(1 + math.sin(self.time * 0.001))  # Velocidad reducida
        shadow = font_large.render("Pygame AI RPG", True, (30, 30, 50))
        title = font_large.render("Pygame AI RPG", True, COLORS["GOLD"])

        # Sombra
        self.screen.blit(
            shadow,
            (
                self.width // 2 - title_size[0] // 2 + shadow_offset,
                title_y + shadow_offset,
            ),
        )

        # Brillo dinámico detrás del título
        title_rect = pygame.Rect(
            self.width // 2 - title_size[0] // 2 - 20,
            title_y - 10,
            title_size[0] + 40,
            title_height + 20,
        )
        VisualEffects.draw_magical_border(
            self.screen, title_rect, (255, 215, 0), self.time
        )

        # Título
        self.screen.blit(title, (self.width // 2 - title_size[0] // 2, title_y))

        # Subtítulo
        subtitle = font_medium.render(
            "Una aventura táctica con Inteligencia Artificial", True, COLORS["WHITE"]
        )
        self.screen.blit(
            subtitle,
            (self.width // 2 - subtitle.get_width() // 2, title_y + title_height + 10),
        )

        # Decoración horizontal
        line_width = min(self.width - 200, 600)
        pygame.draw.line(
            self.screen,
            COLORS["GOLD"],
            (self.width // 2 - line_width // 2, title_y + title_height + 45),
            (self.width // 2 + line_width // 2, title_y + title_height + 45),
            2,
        )

        # Opciones del menú
        menu_y = self.height // 2 + 20
        for i, option in enumerate(self.options):
            color = COLORS["GOLD"] if i == self.selected else COLORS["WHITE"]
            text = font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.width // 2, menu_y))

            # Resaltar opción seleccionada
            if i == self.selected:
                # Dibujar rectángulo redondeado detrás de la opción seleccionada
                rect = pygame.Rect(
                    self.width // 2 - text.get_width() // 2 - 20,
                    menu_y - 5,
                    text.get_width() + 40,
                    text.get_height() + 10,
                )

                # Fondo del botón seleccionado
                pygame.draw.rect(self.screen, (60, 60, 90), rect, border_radius=5)

                # Borde mágico
                VisualEffects.draw_magical_border(
                    self.screen, rect, COLORS["GOLD"], self.time
                )

                # Indicador de selección (flechas)
                arrow_pulse = abs(math.sin(self.time * 0.003))  # Velocidad reducida
                arrow_x = (
                    self.width // 2 - text.get_width() // 2 - 30 - 10 * arrow_pulse
                )

                pygame.draw.polygon(
                    self.screen,
                    COLORS["GOLD"],
                    [
                        (arrow_x, menu_y + text.get_height() // 2),
                        (arrow_x + 15, menu_y),
                        (arrow_x + 15, menu_y + text.get_height()),
                    ],
                )

                # Flecha derecha
                arrow_x = (
                    self.width // 2 + text.get_width() // 2 + 15 + 10 * arrow_pulse
                )
                pygame.draw.polygon(
                    self.screen,
                    COLORS["GOLD"],
                    [
                        (arrow_x, menu_y + text.get_height() // 2),
                        (arrow_x - 15, menu_y),
                        (arrow_x - 15, menu_y + text.get_height()),
                    ],
                )

            # Dibujar texto de opción
            self.screen.blit(text, text_rect)
            menu_y += 60

        # Mostrar frase de sabiduría
        self._update_wisdom_display()

        # Información en la parte inferior
        info_text = font_small.render(
            "© 2025 - Desarrollado por DarkChris Studio", True, COLORS["GRAY"]
        )
        self.screen.blit(
            info_text, (self.width // 2 - info_text.get_width() // 2, self.height - 40)
        )

        # Mostar versión
        version_text = font_small.render("v1.0", True, COLORS["GRAY"])
        self.screen.blit(version_text, (self.width - version_text.get_width() - 15, 15))

        # Actualizar pantalla
        pygame.display.flip()

    def _update_wisdom_display(self):
        """Actualiza y muestra el mensaje de sabiduría"""
        # Control de visibilidad y temporizador
        self.wisdom_timer += self.clock.get_time()

        if not self.current_wisdom or not self.current_wisdom.strip():
            self.current_wisdom = "La sabiduría aguarda ser descubierta..."

        # ELIMINADO: Cambiar frase cada 10 segundos
        # if self.wisdom_timer > 10000:
        #     self.wisdom_timer = 0
        #     self.current_wisdom = self.wisdom.generate_new_phrase()
        #     self.wisdom_opacity = 0
        #     self.wisdom_visible = True

        # Fade in/out (mantener esta parte)
        if self.wisdom_visible and self.wisdom_opacity < 255:
            self.wisdom_opacity = min(255, self.wisdom_opacity + 5)
        elif not self.wisdom_visible and self.wisdom_opacity > 0:
            self.wisdom_opacity = max(0, self.wisdom_opacity - 5)

        # MODIFICADO: No cambiar la frase, solo la visibilidad
        if not self.wisdom_visible and self.wisdom_opacity == 0:
            self.wisdom_visible = True
            # self.current_wisdom = self.wisdom.generate_new_phrase()

        if self.show_wisdom and self.wisdom_opacity > 0:
            # Determinar tamaño y posición
            max_width = self.width - 80
            lines = []
            words = self.current_wisdom.split()
            if not words:
                words = ["..."]
            current_line = words[0]

            for word in words[1:]:
                test_line = current_line + " " + word
                if font_small.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            # Calcular altura total
            line_height = font_small.get_height()
            total_height = line_height * len(lines) + 20  # Padding

            # Dibujar fondo
            wisdom_box = pygame.Rect(
                40, self.height - total_height - 50, self.width - 80, total_height
            )

            # Superficie con transparencia
            wisdom_surf = pygame.Surface(
                (wisdom_box.width, wisdom_box.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                wisdom_surf,
                (20, 20, 50, min(180, self.wisdom_opacity)),
                (0, 0, wisdom_box.width, wisdom_box.height),
                border_radius=10,
            )

            # Borde
            pygame.draw.rect(
                wisdom_surf,
                (255, 215, 0, min(100, self.wisdom_opacity)),
                (0, 0, wisdom_box.width, wisdom_box.height),
                3,
                border_radius=10,
            )

            # Icono de sabiduría
            pygame.draw.polygon(
                wisdom_surf,
                (255, 215, 0, min(200, self.wisdom_opacity)),
                [(20, 15), (35, 15), (30, 30), (25, 30)],
            )

            # Renderizar texto
            for i, line in enumerate(lines):
                line_surf = font_small.render(line, True, (255, 255, 255))
                line_surf.set_alpha(min(255, self.wisdom_opacity))
                wisdom_surf.blit(line_surf, (40, 10 + i * line_height))

            # Mostrar en pantalla
            self.screen.blit(wisdom_surf, wisdom_box)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                    # Hacer visible la frase sin generar una nueva
                    self.wisdom_timer = 0
                    self.wisdom_visible = True
                    # ELIMINADO: self.current_wisdom = self.wisdom.generate_new_phrase()

                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                    # Hacer visible la frase sin generar una nueva
                    self.wisdom_timer = 0
                    self.wisdom_visible = True
                    # self.current_wisdom = self.wisdom.generate_new_phrase()

                elif event.key == pygame.K_RETURN:
                    # Reproducir sonido si está implementado
                    return self.options[self.selected]

                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "QUIT"

                elif event.key == pygame.K_SPACE:
                    # Mostrar/ocultar sabiduría
                    self.show_wisdom = not self.show_wisdom

        return None

    def run(self):
        # Generar nueva frase al iniciar
        self.reset()

        while self.running:
            self.clock.tick(60)  # 60 FPS

            # Manejar eventos
            result = self.handle_events()
            if result == "QUIT":
                return "QUIT"
            elif result == "Jugar":
                return "PLAY"
            elif result == "Tutorial":
                return "TUTORIAL"
            elif result == "Opciones":
                return "OPTIONS"
            elif result == "Salir":
                return "QUIT"
            elif result == "MENU":  # Manejar retorno desde submenús
                return "MENU"

            # Dibujar el menú
            self.draw()

        return "QUIT"


class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.clock = pygame.time.Clock()
        self.time = 0  # Contador para animaciones

        # Obtener config actual
        config = get_config()

        # Mapear valores a índices
        difficulty_idx = 1  # Normal por defecto
        if config["difficulty"] == "Easy":
            difficulty_idx = 0
        elif config["difficulty"] == "Hard":
            difficulty_idx = 2

        music_idx = 0 if config["music"] else 1
        effects_idx = 0 if config["sound_effects"] else 1

        # Obtener índice del modelo actual
        model_idx = get_model_index(config["ai_model"])

        # Opciones
        self.options = [
            {
                "name": "Dificultad",
                "values": ["Fácil", "Normal", "Difícil"],
                "selected": difficulty_idx,
                "description": "Ajusta el nivel de desafío y la inteligencia de los enemigos",
            },
            {
                "name": "Música",
                "values": ["On", "Off"],
                "selected": music_idx,
                "description": "Activa o desactiva la música de fondo",
            },
            {
                "name": "Efectos",
                "values": ["On", "Off"],
                "selected": effects_idx,
                "description": "Activa o desactiva los efectos de sonido",
            },
            {
                "name": "Modelo IA",
                "values": MODEL_NAMES,
                "selected": model_idx,
                "description": "Selecciona el modelo de IA que controla a los enemigos y genera contenido",
            },
            {
                "name": "Volver",
                "values": None,
                "selected": 0,
                "description": "Regresar al menú principal",
            },
        ]
        self.selected_option = 0

        # Descripción actual con efecto de transición
        self.current_description = ""
        self.target_description = self.options[0]["description"]
        self.description_timer = 0

    def draw(self):
        # Actualizar contador para animaciones
        self.time += self.clock.get_time()

        # Dibujar fondo
        # Fondo gradiente dinámico
        for y in range(self.height):
            color_value = int(y / self.height * 100)
            pulse = 10 * math.sin(self.time * 0.0005)
            pygame.draw.line(
                self.screen,
                (20, 20 + pulse, 50 + color_value + pulse),
                (0, y),
                (self.width, y),
            )

        # Dibujar partículas sutiles
        VisualEffects.draw_particle_background(self.screen, self.time, 20)

        # Título
        title = font_large.render("Opciones", True, COLORS["GOLD"])
        title_rect = title.get_rect(center=(self.width // 2, 60))

        # Efecto de brillo para el título
        VisualEffects.draw_magical_border(
            self.screen, title_rect, COLORS["GOLD"], self.time
        )
        self.screen.blit(title, title_rect)

        # Panel de opciones
        panel_rect = pygame.Rect(
            self.width // 2 - 300,
            120,
            max(1, 600),  # Asegurar ancho mínimo
            max(1, self.height - 200),  # Asegurar alto mínimo
        )

        # Comprobar dimensiones antes de crear superficie
        if panel_rect.width <= 0 or panel_rect.height <= 0:
            panel_rect.width = max(1, panel_rect.width)
            panel_rect.height = max(1, panel_rect.height)

        # Fondo del panel
        panel_surf = pygame.Surface(
            (panel_rect.width, panel_rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            panel_surf,
            (20, 20, 40, 200),
            (0, 0, panel_rect.width, panel_rect.height),
            border_radius=10,
        )

        # Borde del panel
        pygame.draw.rect(
            panel_surf,
            (100, 100, 150, 100),
            (0, 0, panel_rect.width, panel_rect.height),
            2,
            border_radius=10,
        )

        self.screen.blit(panel_surf, panel_rect)

        # Opciones
        option_y = 150
        for i, option in enumerate(self.options):
            # Resaltado para opción seleccionada
            if i == self.selected_option:
                highlight_rect = pygame.Rect(
                    self.width // 2 - 280, option_y - 5, 560, 40
                )

                # Fondo del botón seleccionado con animación
                pulse = abs(math.sin(self.time * 0.002))  # Velocidad reducida
                highlight_alpha = 100 + int(pulse * 50)
                highlight_surf = pygame.Surface(
                    (highlight_rect.width, highlight_rect.height), pygame.SRCALPHA
                )
                pygame.draw.rect(
                    highlight_surf,
                    (60, 60, 120, highlight_alpha),
                    (0, 0, highlight_rect.width, highlight_rect.height),
                    border_radius=5,
                )
                self.screen.blit(highlight_surf, highlight_rect)

                # Actualizar descripción objetivo con suavizado
                self.target_description = option["description"]
                if self.description_timer < 10:
                    self.description_timer += 1

                # Transición de descripción
                if self.current_description != self.target_description:
                    if self.description_timer >= 10:  # Después de un breve retraso
                        chars_to_copy = max(1, len(self.target_description) // 10)
                        current_len = len(self.current_description)
                        target_len = len(self.target_description)

                        if current_len < target_len:
                            # Añadir caracteres
                            self.current_description = self.target_description[
                                : current_len + chars_to_copy
                            ]
                        else:
                            # Eliminar caracteres
                            self.current_description = self.current_description[
                                : current_len - chars_to_copy
                            ]
                            if len(self.current_description) <= 0:
                                self.current_description = self.target_description[
                                    :chars_to_copy
                                ]

            # Color según selección
            color = COLORS["GOLD"] if i == self.selected_option else COLORS["WHITE"]

            # Nombre
            text = font_medium.render(option["name"], True, color)
            self.screen.blit(text, (self.width // 2 - 250, option_y))

            # Valor si existe
            if option["values"]:
                # Obtener valor seleccionado
                selected_value = option["values"][option["selected"]]

                # Color del valor
                value_color = (
                    COLORS["GREEN"] if i == self.selected_option else COLORS["GRAY"]
                )

                # Renderizar texto del valor
                value_text = font_medium.render(selected_value, True, value_color)

                # Posición del valor
                value_x = self.width // 2 + 150
                value_rect = value_text.get_rect(
                    center=(value_x, option_y + text.get_height() // 2)
                )
                self.screen.blit(value_text, value_rect)

                # Flechas para cambiar valor si está seleccionado
                if i == self.selected_option:
                    # Flecha izquierda
                    arrow_pulse = abs(math.sin(self.time * 0.003))  # Velocidad reducida
                    left_x = value_rect.left - 25 - int(5 * arrow_pulse)
                    pygame.draw.polygon(
                        self.screen,
                        COLORS["WHITE"],
                        [
                            (left_x, value_rect.centery),
                            (left_x + 10, value_rect.centery - 8),
                            (left_x + 10, value_rect.centery + 8),
                        ],
                    )

                    # Flecha derecha
                    right_x = value_rect.right + 15 + int(5 * arrow_pulse)
                    pygame.draw.polygon(
                        self.screen,
                        COLORS["WHITE"],
                        [
                            (right_x, value_rect.centery),
                            (right_x - 10, value_rect.centery - 8),
                            (right_x - 10, value_rect.centery + 8),
                        ],
                    )

            option_y += 60

        # Descripción de la opción seleccionada
        description_box = pygame.Rect(self.width // 2 - 280, self.height - 150, 560, 60)

        # Fondo de la descripción
        desc_surf = pygame.Surface(
            (description_box.width, description_box.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            desc_surf,
            (40, 40, 70, 200),
            (0, 0, description_box.width, description_box.height),
            border_radius=8,
        )

        # Texto de descripción (con ajuste automático)
        max_width = description_box.width - 40
        lines = []
        words = self.current_description.split()
        if words:
            current_line = words[0]

            for word in words[1:]:
                test_line = current_line + " " + word
                if font_small.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            # Renderizar líneas
            line_height = font_small.get_height()
            for i, line in enumerate(lines):
                line_text = font_small.render(line, True, COLORS["WHITE"])
                desc_surf.blit(line_text, (20, 10 + i * line_height))

        # Mostrar descripción
        self.screen.blit(desc_surf, description_box)

        # Instrucciones
        instructions = font_medium.render(
            "↑↓: Navegar   ←→: Cambiar   Enter: Seleccionar   ESC: Volver",
            True,
            COLORS["GRAY"],
        )
        self.screen.blit(
            instructions,
            (self.width // 2 - instructions.get_width() // 2, self.height - 70),
        )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_options(self)
                self.running = False
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_options(self)
                    return "MENU"

                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(
                        self.options
                    )
                    self.description_timer = 0

                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.options
                    )
                    self.description_timer = 0

                # Cambiar valores
                elif event.key == pygame.K_LEFT:
                    option = self.options[self.selected_option]
                    if option["values"]:
                        option["selected"] = (option["selected"] - 1) % len(
                            option["values"]
                        )

                elif event.key == pygame.K_RIGHT:
                    option = self.options[self.selected_option]
                    if option["values"]:
                        option["selected"] = (option["selected"] + 1) % len(
                            option["values"]
                        )

                elif event.key == pygame.K_RETURN:
                    if self.selected_option == len(self.options) - 1:  # Volver
                        save_options(self)
                        return "MENU"

        return None

    def run(self):
        while self.running:
            self.clock.tick(60)
            result = self.handle_events()
            if result:
                return result
            self.draw()

        save_options(self)
        return "MENU"


def save_options(options_menu):
    """Guarda las opciones del menú"""
    global _CONFIG

    # Mapeos
    option_mapping = {
        "Dificultad": "difficulty",
        "Música": "music",
        "Efectos": "sound_effects",
        "Modelo IA": "ai_model",
    }

    value_mapping = {
        "Fácil": "Easy",
        "Normal": "Normal",
        "Difícil": "Hard",
        "On": True,
        "Off": False,
    }

    # Guardar opciones
    for option in options_menu.options:
        if option["name"] in option_mapping and option["values"]:
            config_key = option_mapping[option["name"]]
            selected_value = option["values"][option["selected"]]

            # Caso especial para modelos de IA
            if config_key == "ai_model":
                _CONFIG[config_key] = get_model_id(selected_value)
            else:
                _CONFIG[config_key] = value_mapping.get(selected_value, selected_value)

    print(f"Configuración guardada: {_CONFIG}")

    # Guardar en archivo
    try:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "game_config.json"
        )
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(_CONFIG, f, indent=4)
    except Exception as e:
        print(f"Error guardando configuración: {e}")


def get_config():
    """Obtiene la configuración actual"""
    global _CONFIG

    # Intentar cargar desde archivo
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config", "game_config.json"
    )

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                loaded_config = json.load(f)
                _CONFIG.update(loaded_config)
    except Exception as e:
        print(f"Error cargando configuración: {e}")

    return _CONFIG.copy()
