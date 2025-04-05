import pygame
import sys
import os
from src.ui import COLORS, font_large, font_medium


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True

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

        # Opciones del menú
        self.options = ["Jugar", "Tutorial", "Opciones", "Salir"]
        self.selected = 0

        # Sonidos (si se implementan)
        self.select_sound = None
        self.confirm_sound = None

        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()

    def draw(self):
        # Dibujar fondo
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # Fondo gradiente si no hay imagen
            for y in range(self.height):
                color_value = int(y / self.height * 100)
                pygame.draw.line(
                    self.screen, (20, 20, 50 + color_value), (0, y), (self.width, y)
                )

        # Título del juego
        title = font_large.render("Pygame AI RPG", True, COLORS["GOLD"])
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))

        # Efecto de brillo para el título
        glow_surf = pygame.Surface(
            (title.get_width() + 10, title.get_height() + 10), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf,
            (255, 215, 0, 100),
            (0, 0, glow_surf.get_width(), glow_surf.get_height()),
            border_radius=10,
        )
        glow_rect = glow_surf.get_rect(center=title_rect.center)
        self.screen.blit(glow_surf, glow_rect)
        self.screen.blit(title, title_rect)

        # Subtítulo
        subtitle = font_medium.render(
            "Una aventura táctica con IA", True, COLORS["WHITE"]
        )
        self.screen.blit(
            subtitle,
            (
                self.width // 2 - subtitle.get_width() // 2,
                self.height // 4 + title.get_height(),
            ),
        )

        # Opciones del menú
        menu_y = self.height // 2
        for i, option in enumerate(self.options):
            color = COLORS["GOLD"] if i == self.selected else COLORS["WHITE"]
            text = font_medium.render(option, True, color)

            # Resaltar opción seleccionada
            if i == self.selected:
                # Dibujar rectángulo redondeado detrás de la opción seleccionada
                rect = pygame.Rect(
                    self.width // 2 - text.get_width() // 2 - 20,
                    menu_y - 5,
                    text.get_width() + 40,
                    text.get_height() + 10,
                )
                pygame.draw.rect(self.screen, (60, 60, 90), rect, border_radius=5)
                pygame.draw.rect(self.screen, COLORS["GOLD"], rect, 2, border_radius=5)

                # Indicador de selección (flechas)
                arrow = "➤ "
                arrow_text = font_medium.render(arrow, True, COLORS["GOLD"])
                self.screen.blit(
                    arrow_text,
                    (
                        self.width // 2
                        - text.get_width() // 2
                        - arrow_text.get_width()
                        - 5,
                        menu_y,
                    ),
                )

            # Dibujar texto de opción
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, menu_y))
            menu_y += 60

        # Información en la parte inferior
        info_text = font_medium.render(
            "© 2023 - Desarrollado con ChatGPT", True, COLORS["GRAY"]
        )
        self.screen.blit(
            info_text, (self.width // 2 - info_text.get_width() // 2, self.height - 50)
        )

        # Actualizar pantalla
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                    # Reproducir sonido si está implementado
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                    # Reproducir sonido si está implementado
                elif event.key == pygame.K_RETURN:
                    # Reproducir sonido si está implementado
                    return self.options[self.selected]
        return None

    def run(self):
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

            # Dibujar el menú
            self.draw()

        return "QUIT"


class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True

        # Opciones configurables
        self.options = [
            {
                "name": "Dificultad",
                "values": ["Fácil", "Normal", "Difícil"],
                "selected": 1,
            },
            {"name": "Música", "values": ["On", "Off"], "selected": 0},
            {"name": "Efectos", "values": ["On", "Off"], "selected": 0},
            {
                "name": "Modelo IA",
                "values": ["GPT-3.5", "GPT-4", "Local"],
                "selected": 0,
            },
            {"name": "Volver", "values": None, "selected": 0},
        ]
        self.selected_option = 0
        self.clock = pygame.time.Clock()

    def draw(self):
        # Fondo
        self.screen.fill((20, 20, 40))

        # Título
        title = font_large.render("Opciones", True, COLORS["GOLD"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Opciones
        menu_y = 150
        for i, option in enumerate(self.options):
            # Color según selección
            option_color = (
                COLORS["GOLD"] if i == self.selected_option else COLORS["WHITE"]
            )

            # Nombre de la opción
            option_text = font_medium.render(option["name"], True, option_color)
            self.screen.blit(option_text, (self.width // 4, menu_y))

            # Valores si existen
            if option["values"]:
                value_text = font_medium.render(
                    option["values"][option["selected"]],
                    True,
                    COLORS["GREEN"] if i == self.selected_option else COLORS["GRAY"],
                )
                self.screen.blit(
                    value_text,
                    (self.width * 3 // 4 - value_text.get_width() // 2, menu_y),
                )

                # Flechas para cambiar valor si está seleccionado
                if i == self.selected_option:
                    pygame.draw.polygon(
                        self.screen,
                        COLORS["WHITE"],
                        [
                            (
                                self.width * 3 // 4 - value_text.get_width() // 2 - 30,
                                menu_y + 12,
                            ),
                            (
                                self.width * 3 // 4 - value_text.get_width() // 2 - 20,
                                menu_y + 6,
                            ),
                            (
                                self.width * 3 // 4 - value_text.get_width() // 2 - 20,
                                menu_y + 18,
                            ),
                        ],
                    )
                    pygame.draw.polygon(
                        self.screen,
                        COLORS["WHITE"],
                        [
                            (
                                self.width * 3 // 4 + value_text.get_width() // 2 + 30,
                                menu_y + 12,
                            ),
                            (
                                self.width * 3 // 4 + value_text.get_width() // 2 + 20,
                                menu_y + 6,
                            ),
                            (
                                self.width * 3 // 4 + value_text.get_width() // 2 + 20,
                                menu_y + 18,
                            ),
                        ],
                    )

            menu_y += 70

        # Instrucciones
        instructions = font_medium.render(
            "↑↓: Navegar   ←→: Cambiar   Enter: Seleccionar", True, COLORS["GRAY"]
        )
        self.screen.blit(
            instructions,
            (self.width // 2 - instructions.get_width() // 2, self.height - 70),
        )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "BACK"

                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(
                        self.options
                    )
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.options
                    )

                # Cambiar valores con izquierda/derecha
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
                    if (
                        self.selected_option == len(self.options) - 1
                    ):  # Última opción (Volver)
                        return "BACK"

        return None

    def run(self):
        while self.running:
            self.clock.tick(60)

            result = self.handle_events()
            if result:
                return result

            self.draw()

        return "BACK"


def get_config():
    """Devuelve la configuración actual"""
    # Aquí se podrían cargar configuraciones de un archivo
    return {
        "difficulty": "Normal",
        "music": True,
        "sound_effects": True,
        "ai_model": "gpt-3.5-turbo",
    }
