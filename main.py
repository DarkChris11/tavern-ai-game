import pygame
import sys
import os
from src.engine import GameEngine
from src.menu import MainMenu, OptionsMenu, get_config, WisdomGenerator
from src.tutorial import Tutorial

# Asegúrate que la carpeta config exista
os.makedirs(os.path.join(os.path.dirname(__file__), "config"), exist_ok=True)


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

    # Generar la frase sabia UNA SOLA VEZ al iniciar el juego
    wisdom_generator = WisdomGenerator(model_id=config["ai_model"])
    global_wisdom = wisdom_generator.generate_new_phrase()

    # Bucle principal
    running = True
    while running:
        try:
            if game_state == "MENU":
                # Mostrar menú principal
                menu = MainMenu(screen)
                # Establecer la frase generada al inicio
                menu.current_wisdom = global_wisdom
                # Hacerla visible inmediatamente
                menu.wisdom_visible = True
                menu.wisdom_opacity = 255

                next_state = menu.run()
                # Solamente cambiar el estado si no es None
                if next_state:
                    game_state = next_state

            elif game_state == "PLAY":
                game_engine = GameEngine(screen, config)
                victory = game_engine.run()
                game_state = "MENU"

            elif game_state == "TUTORIAL":
                tutorial = Tutorial(screen)
                next_state = tutorial.run()
                # Solamente cambiar el estado si no es None
                if next_state:
                    game_state = next_state
                else:
                    game_state = "MENU"

            elif game_state == "OPTIONS":
                options = OptionsMenu(screen)
                next_state = options.run()
                # Solamente cambiar el estado si no es None
                if next_state:
                    game_state = next_state
                else:
                    game_state = "MENU"
                config = get_config()

            elif game_state == "QUIT":
                running = False
        except Exception as e:
            print(f"Error en el bucle de juego: {e}")
            # Si hay un error, volver al menú principal
            game_state = "MENU"

    # Limpiar y salir al final del programa
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error fatal: {e}")
        pygame.quit()
        sys.exit(1)
