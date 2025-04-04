import os
import sys
import pygame
from dotenv import load_dotenv

# Agregar el directorio actual al path para encontrar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno desde .env
load_dotenv()

from src.engine import GameEngine
from src.characters import GameState
from src.ai.chatgpt_client import ChatGPTClient


def main():
    # Inicializar pygame
    pygame.init()

    # Crear el cliente de ChatGPT
    try:
        ai_client = ChatGPTClient(config_path="config/openai_config.json")
        print("ChatGPT API inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar ChatGPT: {e}")
        print("El juego usará IA básica en su lugar")
        ai_client = None

    # Crear el motor del juego
    game_engine = GameEngine(ai_client)

    # Crear el estado inicial del juego
    game_state = GameState()

    # Inicializar el juego
    game_engine.init_game(game_state)

    # Ejecutar el bucle principal del juego
    victory = game_engine.run()

    # Mostrar resultado final
    if victory:
        print("¡Felicidades! Has completado el juego.")
    else:
        print("Game Over. ¡Inténtalo de nuevo!")

    # Limpiar y salir
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
