import random
import pygame

# Colores para los mensajes
RED = (200, 0, 0)
GREEN = (50, 205, 50)
GOLD = (255, 215, 0)
BLUE = (30, 144, 255)
DARK_GREEN = (0, 100, 0)


def roll_dice(dice, sides):
    """Simula lanzar dados (dice x d(sides))"""
    return sum(random.randint(1, sides) for _ in range(dice))


def execute_attack(game_state, attacker, defender, attack_name):
    """Ejecuta un ataque de un personaje a otro"""
    # Verificar que el ataque existe
    if attack_name not in attacker.attacks:
        game_state.add_message(f"¡Ataque {attack_name} no disponible!", RED)
        return

    # Obtener estadísticas del ataque
    attack = attacker.attacks[attack_name]

    # Determinar el tipo de ataque
    attack_type = attack.get("type", "physical")

    # Lógica de daño
    damage = roll_dice(attack["dice"], attack["sides"])

    # Probabilidad de crítico (5%)
    if random.random() < 0.05:
        damage *= 2
        game_state.add_message("¡Golpe crítico!", GOLD)

    # Aplicar daño
    actual_damage = defender.take_damage(damage)

    # Formato solicitado para el mensaje: "Atacante --> Defensor {Ataque}"
    game_state.add_message(
        f"{attacker.name} --> {defender.name} {{-{actual_damage} HP - {attack_name}}}",
        DARK_GREEN,
    )

    # Mostrar efecto visual del ataque
    attacker.game_state = game_state
    defender.game_state = game_state
    from src.ui import show_attack_effect

    try:
        show_attack_effect(
            pygame.display.get_surface(),
            attacker,
            defender,
            attack_name,
            actual_damage,
            attack_type,
        )
    except Exception as e:
        print(f"Error mostrando efecto visual: {e}")

    # Efectos especiales según el tipo de ataque
    apply_attack_effects(
        game_state, attacker, defender, attack_name, damage, actual_damage
    )

    # Verificar si el defensor murió
    check_defender_death(game_state, defender)


def apply_attack_effects(
    game_state, attacker, defender, attack_name, damage, actual_damage
):
    """Aplica efectos especiales según el tipo de ataque"""
    # Si el ataque tiene un efecto específico definido
    if "effect" in attacker.attacks.get(attack_name, {}):
        effect_name = attacker.attacks[attack_name]["effect"]

        # Aplicar el efecto según su tipo
        if effect_name == "veneno":
            defender.add_status_effect("veneno", 3)
            game_state.add_message(
                f"{defender.name} ha sido envenenado por 3 turnos", GREEN
            )

        elif effect_name == "sangrado":
            defender.add_status_effect("sangrado", 3)
            game_state.add_message(
                f"{defender.name} está sangrando y perderá salud por 3 turnos", RED
            )

        elif effect_name == "congelado":
            defender.add_status_effect("congelado", 2)
            game_state.add_message(
                f"{defender.name} ha sido congelado por 2 turnos", BLUE
            )

        elif effect_name == "debilitar":
            defender.add_status_effect("debilitado", 2)
            game_state.add_message(
                f"{defender.name} ha sido debilitado y causará menos daño",
                (150, 150, 150),
            )

        elif effect_name == "bendición":
            attacker.add_status_effect("bendecido", 3)
            game_state.add_message(
                f"{attacker.name} ha sido bendecido, aumentando sus capacidades", GOLD
            )

        elif effect_name == "drenaje":
            heal_amount = min(actual_damage, attacker.max_health - attacker.health)
            if heal_amount > 0:
                attacker.health += heal_amount
                game_state.add_message(
                    f"{attacker.name} drena la vida y recupera {heal_amount} HP", GREEN
                )

        elif effect_name == "ataque_doble":
            # Realizar un segundo ataque con la mitad de daño
            second_damage = max(1, damage // 2)
            actual_second_damage = defender.take_damage(second_damage)
            game_state.add_message(
                f"{attacker.name} ataca rápidamente una segunda vez (-{actual_second_damage} HP)",
                DARK_GREEN,
            )


def check_defender_death(game_state, defender):
    """Verifica si el defensor murió y actualiza el estado del juego"""
    if defender.health <= 0:
        if defender in game_state.enemies:
            game_state.enemies.remove(defender)
            game_state.add_message(f"{defender.name} ha sido derrotado!", RED)

            # Asegurarse de que selected_enemy esté dentro del rango
            if game_state.selected_enemy >= len(game_state.enemies):
                game_state.selected_enemy = max(0, len(game_state.enemies) - 1)
        elif defender.type.name == "PLAYER":
            game_state.game_over = True
            game_state.victory = False
            game_state.add_message("¡Has sido derrotado!", RED)
        elif defender.type.name == "ALLY":
            game_state.ally = None
            game_state.add_message(f"{defender.name} ha caído en batalla", RED)


def perform_ally_action(game_state):
    """Realiza la acción del aliado controlada por IA"""
    if not game_state.ally or not game_state.ally.is_alive():
        return

    attacker = game_state.ally

    # Evaluar la situación para tomar decisiones inteligentes
    player_health_ratio = game_state.player.health / game_state.player.max_health

    # Si el jugador está muy herido, priorizar curación
    if player_health_ratio < 0.4 and "Toque Curativo" in attacker.attacks:
        attack_name = "Toque Curativo"
        heal_amount = attacker.attacks[attack_name]["heal"]

        # Aplicar curación al jugador
        old_health = game_state.player.health
        game_state.player.health = min(
            game_state.player.max_health, game_state.player.health + heal_amount
        )
        actual_heal = game_state.player.health - old_health

        game_state.add_message(
            f"{attacker.name} --> {game_state.player.name} {{+{actual_heal} HP - {attack_name}}}",
            GREEN,
        )

        # Mostrar efecto visual de curación
        from src.ui import show_attack_effect

        try:
            show_attack_effect(
                pygame.display.get_surface(),
                attacker,
                game_state.player,
                attack_name,
                -actual_heal,  # Negativo para indicar curación
                "healing",
            )
        except Exception as e:
            print(f"Error mostrando efecto visual: {e}")

    # Si el jugador está en estado decente, el aliado ataca
    elif len(game_state.enemies) > 0:
        # Elegir un enemigo (preferir al que tenga menos salud)
        defender = min(game_state.enemies, key=lambda e: e.health)

        # Elegir un ataque ofensivo
        offensive_attacks = [
            name for name, attack in attacker.attacks.items() if "dice" in attack
        ]

        if offensive_attacks:
            # Elegir ataque basado en la situación
            if defender.health < 15 and "Proyectil Mágico" in offensive_attacks:
                # Si el enemigo está débil, usar un ataque más preciso
                attack_name = "Proyectil Mágico"
            elif "Agua Bendita" in offensive_attacks and any(
                enemy.health > 30 for enemy in game_state.enemies
            ):
                # Contra enemigos fuertes, usar ataque más potente
                attack_name = "Agua Bendita"
            else:
                # Por defecto, usar el primer ataque
                attack_name = offensive_attacks[0]

            # Ejecutar el ataque
            execute_attack(game_state, attacker, defender, attack_name)
