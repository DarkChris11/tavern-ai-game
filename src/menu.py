import pygame
import sys
import os
import json
from src.ui import COLORS, font_large, font_medium

# Intentar importar los modelos, con fallback si no están disponibles
try:
    from src.ai.list_models import MODEL_NAMES, get_model_index, get_model_id
except ImportError:
    print("Módulo list_models no encontrado. Usando valores por defecto.")
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


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.options = ["Jugar", "Tutorial", "Opciones", "Salir"]
        self.selected = 0
        self.clock = pygame.time.Clock()

        # Resto del código de inicialización...

    def draw(self):
        # Dibujar fondo
        self.screen.fill((20, 20, 40))  # Fondo oscuro

        # Título
        title = font_large.render("Pygame AI RPG", True, COLORS["GOLD"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))

        # Opciones
        y = 300
        for i, option in enumerate(self.options):
            color = COLORS["GOLD"] if i == self.selected else COLORS["WHITE"]
            text = font_medium.render(option, True, color)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y))
            y += 60

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected]
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "QUIT"
        return None

    def run(self):
        while self.running:
            self.clock.tick(60)
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
            self.draw()
        return "QUIT"


class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.clock = pygame.time.Clock()

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
            },
            {"name": "Música", "values": ["On", "Off"], "selected": music_idx},
            {"name": "Efectos", "values": ["On", "Off"], "selected": effects_idx},
            {
                "name": "Modelo IA",
                "values": MODEL_NAMES,
                "selected": model_idx,
            },
            {"name": "Volver", "values": None, "selected": 0},
        ]
        self.selected_option = 0

    def draw(self):
        # Dibujar fondo
        self.screen.fill((20, 20, 40))

        # Título
        title = font_large.render("Opciones", True, COLORS["GOLD"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Opciones
        y = 150
        for i, option in enumerate(self.options):
            # Color según selección
            color = COLORS["GOLD"] if i == self.selected_option else COLORS["WHITE"]

            # Nombre
            text = font_medium.render(option["name"], True, color)
            self.screen.blit(text, (200, y))

            # Valor si existe
            if option["values"]:
                value_text = font_medium.render(
                    option["values"][option["selected"]], True, COLORS["GREEN"]
                )
                self.screen.blit(value_text, (600, y))

            y += 70

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

                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.options
                    )

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
