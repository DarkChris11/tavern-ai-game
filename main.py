import pygame
import sys
from src.engine import GameEngine
from src.menu import MainMenu, OptionsMenu, get_config
from src.tutorial import Tutorial


def main():
    """Función principal del juego"""
    # Inicializar pygame dentro de la función main
    pygame.init()

    # Configurar pantalla
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame AI RPG")

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
            game_engine = GameEngine(screen, config)
            victory = game_engine.run()
            game_state = "MENU"

        elif game_state == "TUTORIAL":
            tutorial = Tutorial(screen)
            game_state = tutorial.run()

        elif game_state == "OPTIONS":
            options = OptionsMenu(screen)
            game_state = options.run()
            config = get_config()

        elif game_state == "QUIT":
            running = False

    # Limpiar y salir - IMPORTANTE: solo al final
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
