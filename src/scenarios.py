from src.ui import COLORS


def load_scenario(game_state, biome_name):
    """Carga un escenario específico en el estado del juego"""
    # Para simplificar, solo cargamos el tutorial con enemigos variados
    from src.enemies import create_enemies_for_tutorial

    game_state.enemies = create_enemies_for_tutorial()
    game_state.selected_enemy = 0

    # Asignar referencia al estado del juego a todos los personajes
    game_state.player.game_state = game_state
    if game_state.ally:
        game_state.ally.game_state = game_state
    for enemy in game_state.enemies:
        enemy.game_state = game_state

    game_state.add_message(
        "¡Bienvenido al juego! Enfrenta a tus enemigos.", COLORS["GOLD"]
    )


def advance_to_next_biome(game_state, screen):
    """Avanza al siguiente bioma cuando se han derrotado todos los enemigos"""
    # Como solo hay un nivel, declaramos victoria
    game_state.game_over = True
    game_state.victory = True
