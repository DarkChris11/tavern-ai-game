from src.ui import COLORS
from src.enemies import create_enemies_for_tutorial, create_boss


def load_scenario(game_state, biome_name):
    """Carga un escenario específico en el estado del juego"""
    if biome_name == "tutorial":
        # Cargar enemigos del tutorial
        from src.enemies import create_enemies_for_tutorial

        game_state.enemies = create_enemies_for_tutorial()
        game_state.selected_enemy = 0
        game_state.add_message(
            "¡Bienvenido al juego! Enfrenta a tus enemigos.", COLORS["GOLD"]
        )
    elif biome_name == "boss":
        # Cargar jefe final
        from src.enemies import create_boss

        game_state.enemies = [create_boss(game_state.player)]
        game_state.selected_enemy = 0
        game_state.add_message("¡Te enfrentas al jefe final!", COLORS["RED"])

        # Generar frase amenazadora con IA
        try:
            boss_phrase = generate_boss_phrase(game_state)
            game_state.add_message(f"Jefe: {boss_phrase}", COLORS["RED"])
        except Exception as e:
            print(f"Error generando frase del jefe: {e}")
            game_state.add_message("Jefe: ¡No escaparás con vida!", COLORS["RED"])

    # Asignar referencia al estado del juego a todos los personajes
    game_state.player.game_state = game_state
    if game_state.ally:
        game_state.ally.game_state = game_state
    for enemy in game_state.enemies:
        enemy.game_state = game_state


def advance_to_next_biome(game_state, screen):
    """Avanza al siguiente bioma cuando se han derrotado todos los enemigos"""
    # Verificar si estamos en modo tutorial y avanzar al boss
    if len(game_state.enemies) == 0:
        if hasattr(game_state, "current_biome") and game_state.current_biome == "boss":
            # Si derrotamos al boss, declaramos victoria
            game_state.game_over = True
            game_state.victory = True
            return True
        else:
            # Si derrotamos a los enemigos normales, aparecer el boss
            game_state.current_biome = "boss"
            load_scenario(game_state, "boss")

            # Mostrar un efecto de transición si quieres
            show_boss_intro(screen, game_state)
            return False
    return False


def show_boss_intro(screen, game_state):
    """Muestra una pantalla de introducción para el jefe"""
    import pygame
    from src.ui import font_large, font_medium

    # Fondo negro
    screen.fill((0, 0, 0))

    # Texto de advertencia
    warning_text = font_large.render("¡PELIGRO!", True, COLORS["RED"])
    screen.blit(
        warning_text,
        (
            screen.get_width() // 2 - warning_text.get_width() // 2,
            screen.get_height() // 2 - 100,
        ),
    )

    # Nombre del jefe
    boss_name = game_state.enemies[0].name if game_state.enemies else "JEFE FINAL"
    boss_text = font_large.render(boss_name, True, COLORS["GOLD"])
    screen.blit(
        boss_text,
        (
            screen.get_width() // 2 - boss_text.get_width() // 2,
            screen.get_height() // 2,
        ),
    )

    # Instrucción
    press_text = font_medium.render(
        "Presiona cualquier tecla para continuar", True, COLORS["WHITE"]
    )
    screen.blit(
        press_text,
        (
            screen.get_width() // 2 - press_text.get_width() // 2,
            screen.get_height() // 2 + 100,
        ),
    )

    pygame.display.flip()

    # Esperar entrada del usuario
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        pygame.time.delay(10)


def generate_boss_phrase(game_state):
    """Genera una frase amenazadora para el jefe usando IA"""
    try:
        from src.ai.chatgpt_client import ChatGPTClient

        ai_client = ChatGPTClient()
        if not ai_client.is_initialized():
            return "¡Los aplastaré como insectos!"

        # Obtener información relevante para contextualizar la amenaza
        player_health_pct = int(
            game_state.player.health / game_state.player.max_health * 100
        )
        ally_health_pct = (
            int(game_state.ally.health / game_state.ally.max_health * 100)
            if game_state.ally
            else 0
        )
        boss_name = game_state.enemies[0].name if game_state.enemies else "Señor Oscuro"

        # Construir prompt para la IA
        prompt = f"""
        Eres {boss_name}, el jefe final malvado de un juego RPG. 
        Genera UNA SOLA frase corta y amenazadora (máximo 15 palabras) para intimidar al jugador y su aliado.
        El jugador tiene {player_health_pct}% de salud y su aliado {ally_health_pct}%.
        La frase debe ser malvada, intimidante y mostrar tu poder como jefe final.
        Solo devuelve la frase, sin comillas ni otros caracteres.
        """

        # Obtener respuesta de la IA
        response = ai_client.get_completion(prompt)

        # Limpiar y validar la respuesta
        if response:
            # Eliminar comillas y espacios extra
            response = response.strip().strip("\"'")

            # Limitar longitud si es muy larga
            if len(response) > 100:
                response = response[:97] + "..."

            return response

        return "¡He destruido a guerreros más fuertes que ustedes!"

    except Exception as e:
        print(f"Error generando frase con IA: {e}")
        return "¡Sus esfuerzos son inútiles contra mi poder!"
