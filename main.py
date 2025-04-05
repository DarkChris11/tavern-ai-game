import pygame
import sys
from src.engine import GameEngine
from src.menu import MainMenu, OptionsMenu, get_config
from src.tutorial import Tutorial

# Inicializar Pygame
pygame.init()

# Configurar pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768  # Usar el mismo tamaño que en engine.py
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame AI RPG")


def main():
    """Función principal del juego"""
    # Variables de estado
    game_state = "MENU"  # MENU, PLAY, TUTORIAL, OPTIONS, QUIT

    # Configuración
    config = get_config()

    # Bucle principal
    running = True
    while running:
        if game_state == "MENU":
            # Mostrar menú principal
            menu = MainMenu(screen)
            game_state = menu.run()

        elif game_state == "PLAY":
            # Iniciar juego - ya no necesitamos inicializar game_state aquí
            # porque lo hemos movido dentro del constructor de GameEngine
            game_engine = GameEngine(screen, config)
            victory = game_engine.run()

            # Al terminar, volver al menú
            game_state = "MENU"

        elif game_state == "TUTORIAL":
            # Mostrar tutorial
            tutorial = Tutorial(screen)
            game_state = tutorial.run()

        elif game_state == "OPTIONS":
            # Mostrar opciones
            options = OptionsMenu(screen)
            game_state = options.run()

            # Actualizar configuración
            config = get_config()

        elif game_state == "QUIT":
            running = False

    # Limpiar y salir
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
