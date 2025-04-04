import pygame
import random
import pygame.font
import math

# Inicializar fuentes
pygame.font.init()
font_small = pygame.font.SysFont("Arial", 16)
font_medium = pygame.font.SysFont("Arial", 24)
font_large = pygame.font.SysFont("Arial", 48)

# Colores para facilitar referencia
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (200, 0, 0),
    "BLUE": (30, 144, 255),
    "GREEN": (50, 205, 50),
    "DARK_GREEN": (0, 100, 0),
    "GRAY": (169, 169, 169),
    "DARK_GRAY": (50, 50, 50),
    "GOLD": (255, 215, 0),
    "PURPLE": (147, 112, 219),
}


def draw_health_bar(surface, x, y, current, max_amount, width=200, height=20):
    """Dibuja una barra de salud"""
    ratio = current / max_amount
    pygame.draw.rect(surface, COLORS["DARK_GRAY"], (x, y, width, height))
    pygame.draw.rect(
        surface, COLORS["RED"], (x + 2, y + 2, (width - 4) * ratio, height - 4)
    )
    text = font_small.render(f"{current}/{max_amount}", True, COLORS["WHITE"])
    surface.blit(
        text,
        (
            x + width // 2 - text.get_width() // 2,
            y + height // 2 - text.get_height() // 2,
        ),
    )


def draw_button(surface, x, y, text, color, active=True):
    """Dibuja un botón interactivo"""
    button_width, button_height = 200, 40
    button_rect = pygame.Rect(x, y, button_width, button_height)

    # Color base del botón
    pygame.draw.rect(
        surface, color if active else COLORS["GRAY"], button_rect, border_radius=5
    )

    # Borde del botón
    pygame.draw.rect(surface, COLORS["WHITE"], button_rect, 2, border_radius=5)

    # Texto del botón
    text_surf = font_medium.render(text, True, COLORS["WHITE"])
    surface.blit(
        text_surf,
        (
            x + button_width // 2 - text_surf.get_width() // 2,
            y + button_height // 2 - text_surf.get_height() // 2,
        ),
    )

    return button_rect  # Devolver rectángulo para detectar clics


def draw_clear_messages_button(screen):
    """Dibuja un botón para borrar el historial de mensajes"""
    width, height = screen.get_width(), screen.get_height()

    # Posicionar botón en la esquina inferior derecha
    button_rect = pygame.Rect(width - 150, height - 40, 130, 30)
    pygame.draw.rect(screen, COLORS["DARK_GRAY"], button_rect, border_radius=5)
    pygame.draw.rect(screen, COLORS["WHITE"], button_rect, 2, border_radius=5)

    # Texto del botón
    clear_text = font_small.render("Borrar mensajes", True, COLORS["WHITE"])
    screen.blit(clear_text, (width - 145, height - 35))

    return button_rect  # Devolver el rectángulo para detectar clics


def draw_status_effects(screen, character, x, y):
    """Dibuja iconos para los efectos de estado activos"""
    if not hasattr(character, "status_effects") or not character.status_effects:
        return

    # Colores para diferentes efectos
    effect_colors = {
        "veneno": COLORS["GREEN"],
        "sangrado": COLORS["RED"],
        "congelado": (0, 255, 255),  # Cyan
        "quemado": (255, 128, 0),  # Naranja
        "debilitado": (150, 150, 150),  # Gris
        "bendecido": COLORS["GOLD"],
    }

    # Dibujar cada efecto activo
    spacing = 20
    for i, (effect, turns) in enumerate(character.status_effects.items()):
        # Fondo del círculo de efecto
        effect_color = effect_colors.get(effect, COLORS["PURPLE"])
        pygame.draw.circle(screen, effect_color, (x + i * spacing, y), 8)

        # Número de turnos restantes
        turns_text = font_small.render(str(turns), True, COLORS["WHITE"])
        screen.blit(turns_text, (x + i * spacing - 4, y - 6))

        # Pequeña descripción al pasar por encima (tooltip) - simulado con texto cercano
        effect_name = font_small.render(effect, True, effect_color)
        screen.blit(effect_name, (x, y + 15))


def draw_characters(screen, game_state):
    """Dibuja los personajes en pantalla con efectos de estado visibles"""
    # Dibujar jugador
    player_x, player_y = 100, 300
    if hasattr(game_state.player, "image") and game_state.player.image:
        screen.blit(game_state.player.image, (player_x, player_y))
    else:
        # Si no hay imagen, crear un rectángulo azul
        pygame.draw.rect(screen, (0, 0, 150), (player_x, player_y, 80, 80))

    # Barra de salud del jugador arriba
    draw_health_bar(
        screen,
        player_x,
        player_y - 35,  # Aumentamos separación
        game_state.player.health,
        game_state.player.max_health,
        80,
        10,
    )

    # Nombre del jugador DEBAJO de la barra de salud, con MÁS separación
    player_text = font_small.render(game_state.player.name, True, COLORS["WHITE"])
    screen.blit(
        player_text, (player_x + 40 - player_text.get_width() // 2, player_y - 20)
    )

    # Mostrar efectos de estado del jugador
    draw_status_effects(screen, game_state.player, player_x, player_y + 85)

    # Dibujar aliado (si existe)
    if game_state.ally:
        ally_x, ally_y = 200, 300
        if hasattr(game_state.ally, "image") and game_state.ally.image:
            screen.blit(game_state.ally.image, (ally_x, ally_y))
        else:
            # Si no hay imagen, crear un rectángulo cyan
            pygame.draw.rect(screen, (0, 150, 150), (ally_x, ally_y, 80, 80))

        # Barra de salud del aliado arriba
        draw_health_bar(
            screen,
            ally_x,
            ally_y - 35,  # Aumentamos separación
            game_state.ally.health,
            game_state.ally.max_health,
            80,
            10,
        )

        # Nombre del aliado DEBAJO de la barra de salud, con MÁS separación
        ally_text = font_small.render(game_state.ally.name, True, COLORS["WHITE"])
        screen.blit(ally_text, (ally_x + 40 - ally_text.get_width() // 2, ally_y - 20))

        # Mostrar efectos de estado del aliado
        draw_status_effects(screen, game_state.ally, ally_x, ally_y + 85)

    # Dibujar enemigos - EN VERTICAL
    for i, enemy in enumerate(game_state.enemies):
        # Posición para alineación vertical
        x = 500
        y = 150 + i * 160  # Mayor espaciado vertical entre enemigos

        if hasattr(enemy, "image") and enemy.image:
            screen.blit(enemy.image, (x, y))
        else:
            # Si no hay imagen, crear un rectángulo de color
            pygame.draw.rect(screen, COLORS["RED"], (x, y, 80, 80))

        # Dibujar un rectángulo alrededor del enemigo seleccionado
        if i == game_state.selected_enemy:
            pygame.draw.rect(screen, COLORS["GOLD"], (x - 5, y - 5, 90, 90), 3)

        # Barra de salud arriba
        draw_health_bar(screen, x, y - 35, enemy.health, enemy.max_health, 80, 10)

        # Nombre del enemigo DEBAJO de la barra de salud, con MÁS separación
        name_text = font_small.render(enemy.name, True, COLORS["WHITE"])
        screen.blit(name_text, (x + 40 - name_text.get_width() // 2, y - 20))

        # Mostrar efectos de estado del enemigo
        draw_status_effects(screen, enemy, x, y + 85)

        # Mostrar ataques disponibles del enemigo - alejado más a la izquierda
        draw_enemy_attacks(screen, enemy, x - 190, y)


def draw_enemy_attacks(screen, enemy, x, y):
    """Muestra los ataques disponibles de un enemigo"""
    if not hasattr(enemy, "attacks") or not enemy.attacks:
        return

    # Hacemos el panel más ancho para evitar superposición
    attack_width = 180  # Aumentamos el ancho

    # Fondo semi-transparente para los ataques
    attack_bg = pygame.Surface(
        (attack_width, len(enemy.attacks) * 20 + 10), pygame.SRCALPHA
    )
    attack_bg.fill((0, 0, 0, 128))
    screen.blit(attack_bg, (x, y))

    # Título
    title = font_small.render("Ataques:", True, COLORS["GOLD"])
    screen.blit(title, (x + 5, y - 20))

    # Listar ataques
    for i, (name, stats) in enumerate(enemy.attacks.items()):
        # Determinar color según tipo de ataque
        attack_color = COLORS["WHITE"]
        if "type" in stats:
            if stats["type"] == "magic":
                attack_color = COLORS["BLUE"]
            elif stats["type"] == "physical":
                attack_color = COLORS["RED"]
            elif stats["type"] == "holy":
                attack_color = COLORS["GOLD"]

        # Mostrar nombre del ataque
        attack_text = font_small.render(name, True, attack_color)
        screen.blit(attack_text, (x + 5, y + 5 + i * 20))

        # Mostrar daño potencial - más a la derecha
        if "dice" in stats and "sides" in stats:
            damage_text = font_small.render(
                f"{stats['dice']}d{stats['sides']}", True, COLORS["GRAY"]
            )
            # Posicionamos el texto a la derecha con más espacio
            damage_x = x + attack_width - damage_text.get_width() - 10
            screen.blit(damage_text, (damage_x, y + 5 + i * 20))


def draw_combat_ui(screen, game_state, colors=COLORS):
    """Dibuja la interfaz de combate"""
    width, height = screen.get_width(), screen.get_height()

    # Panel lateral - hacerlo un poco más ancho para evitar solapamientos
    pygame.draw.rect(screen, colors["DARK_GRAY"], (width - 350, 0, 350, height))

    # Información del jugador
    potion_text = font_medium.render(
        f"Pociones: {game_state.potions}", True, colors["WHITE"]
    )
    screen.blit(potion_text, (width - 340, 20))

    # Título para las habilidades
    title_text = font_medium.render("Habilidades:", True, colors["GOLD"])
    screen.blit(title_text, (width - 340, 60))

    # Botones de acción - más espaciados
    button_y = 100
    current_y = button_y

    # Mostrar botones de ataque con mayor espacio para los que tienen efectos
    for i, (attack_name, stats) in enumerate(game_state.player.attacks.items()):
        # Determinar si la habilidad tiene efecto de estado
        has_effect = "effect" in stats

        # Dibujar fondo para destacar habilidades con efectos
        if has_effect:
            effect_bg = pygame.Rect(width - 345, current_y - 5, 340, 90)
            pygame.draw.rect(screen, (60, 60, 70), effect_bg, border_radius=5)

        # Dibujar el botón principal
        button_rect = draw_button(
            screen,
            width - 340,
            current_y,
            f"{i+1}: {attack_name}",
            colors["BLUE"] if not has_effect else colors["PURPLE"],
        )

        # Mostrar estadísticas del ataque debajo del botón - con mejor alineación
        if "dice" in stats and "sides" in stats:
            stats_text = font_small.render(
                f"{stats['dice']}d{stats['sides']} - {stats.get('type', 'físico')}",
                True,
                colors["WHITE"],
            )
            screen.blit(stats_text, (width - 340, current_y + 42))

        # Mostrar efecto especial si existe (con más espacio y destacado)
        if has_effect:
            effect_name = stats["effect"]
            effect_text = font_small.render(
                f"Efecto: {effect_name}", True, colors["GREEN"]
            )
            screen.blit(effect_text, (width - 340, current_y + 60))

            # Descripción adicional según el tipo de efecto
            effect_desc = ""
            if "veneno" in effect_name:
                effect_desc = "Daño continuo por 3 turnos"
            elif "congelado" in effect_name:
                effect_desc = "Reduce velocidad por 2 turnos"
            elif "sangrado" in effect_name:
                effect_desc = "Daño continuo por 3 turnos"
            elif "debilitar" in effect_name:
                effect_desc = "Reduce daño causado por 2 turnos"
            elif "bendición" in effect_name:
                effect_desc = "Aumenta ataques por 3 turnos"
            elif "drenaje" in effect_name:
                effect_desc = "Recupera vida igual al daño"
            elif "ataque_doble" in effect_name:
                effect_desc = "Ataca dos veces en un turno"

            if effect_desc:
                desc_text = font_small.render(effect_desc, True, (180, 180, 180))
                screen.blit(desc_text, (width - 320, current_y + 78))

            # Aumentar espacio para el siguiente botón si tiene efecto
            current_y += 100
        else:
            # Espacio normal para habilidades sin efectos
            current_y += 70

    # Botones adicionales para pociones y defender
    extra_buttons_y = current_y + 20

    potion_button = draw_button(
        screen,
        width - 340,
        extra_buttons_y,
        "P: Poción",
        colors["GREEN"] if game_state.potions > 0 else colors["GRAY"],
    )

    defend_button = draw_button(
        screen, width - 340, extra_buttons_y + 60, "D: Defender", colors["BLUE"]
    )

    # Registro de mensajes en la parte inferior
    message_y = height - 30
    for i, (text, color) in enumerate(game_state.messages[:5]):
        text_surf = font_small.render(text, True, color)
        screen.blit(text_surf, (20, message_y - i * 30))

    # Dibujar botón para borrar mensajes
    draw_clear_messages_button(screen)


def show_attack_effect(
    screen, attacker, defender, attack_name, damage, attack_type="physical"
):
    """
    Muestra un efecto visual para el ataque con curvas para aliados
    """
    # Calcula las posiciones de los personajes
    if attacker.type.name == "PLAYER":
        attacker_pos = (140, 340)  # Centro del sprite del jugador
    elif attacker.type.name == "ALLY":
        attacker_pos = (240, 340)  # Centro del sprite del aliado
    else:
        # Para enemigos, calculamos basados en su índice (ahora en vertical)
        if hasattr(attacker, "game_state") and attacker.game_state:
            enemy_index = next(
                (i for i, e in enumerate(attacker.game_state.enemies) if e == attacker),
                0,
            )
            attacker_pos = (
                490,  # X fijo para enemigos
                190 + enemy_index * 160,  # Y variable según posición vertical
            )
        else:
            attacker_pos = (490, 190)  # Posición por defecto

    # Similar para el defensor
    if defender.type.name == "PLAYER":
        defender_pos = (140, 340)
    elif defender.type.name == "ALLY":
        defender_pos = (240, 340)
    else:
        if hasattr(defender, "game_state") and defender.game_state:
            enemy_index = next(
                (i for i, e in enumerate(defender.game_state.enemies) if e == defender),
                0,
            )
            defender_pos = (
                490,  # X fijo para enemigos
                190 + enemy_index * 160,  # Y variable según posición vertical
            )
        else:
            defender_pos = (490, 190)

    # Colores para diferentes tipos de ataque
    attack_colors = {
        "physical": COLORS["RED"],
        "magic": COLORS["BLUE"],
        "holy": COLORS["GOLD"],
        "veneno": COLORS["GREEN"],
        "fire": (255, 128, 0),  # Naranja para fuego
        "ice": (0, 255, 255),  # Cyan para hielo
        "healing": (50, 255, 50),  # Verde brillante para curación
    }

    # Determinar si es curación en lugar de ataque
    is_healing = "heal" in attack_name.lower() or damage < 0

    # Color personalizado para el aliado
    if attacker.type.name == "ALLY":
        color = (
            attack_colors["healing"] if is_healing else (0, 255, 255)
        )  # Cyan para aliado
    else:
        color = attack_colors.get(attack_type, COLORS["WHITE"])

    # Dibujar línea indicadora de objetivo con texto antes de la animación
    screen_copy = screen.copy()

    # Línea diferente para aliado (curva)
    if attacker.type.name == "ALLY":
        # Para aliados, dibujar una curva en lugar de una línea recta
        control_point = (
            (attacker_pos[0] + defender_pos[0]) // 2,
            min(attacker_pos[1], defender_pos[1]) - 50,
        )

        # Dibujar curva con múltiples líneas (aproximación)
        points = []
        for t in range(0, 11):
            t = t / 10
            # Fórmula de curva Bezier cuadrática
            x = (
                (1 - t) ** 2 * attacker_pos[0]
                + 2 * (1 - t) * t * control_point[0]
                + t**2 * defender_pos[0]
            )
            y = (
                (1 - t) ** 2 * attacker_pos[1]
                + 2 * (1 - t) * t * control_point[1]
                + t**2 * defender_pos[1]
            )
            points.append((int(x), int(y)))

        for i in range(len(points) - 1):
            pygame.draw.line(screen_copy, color, points[i], points[i + 1], 2)
    else:
        # Para otros personajes, línea recta
        pygame.draw.line(screen_copy, color, attacker_pos, defender_pos, 2)

    # Texto de acción
    action_text = "CURA" if is_healing else "OBJETIVO"
    target_text = font_small.render(action_text, True, color)
    arrow_pos = (
        (attacker_pos[0] + defender_pos[0]) // 2,
        (attacker_pos[1] + defender_pos[1]) // 2,
    )
    screen_copy.blit(
        target_text, (arrow_pos[0] - target_text.get_width() // 2, arrow_pos[1] - 15)
    )
    pygame.display.flip()
    pygame.time.delay(300)

    # 1. Dibujar proyectil animado del atacante al defensor
    steps = 15
    for i in range(steps + 1):
        # Hacemos una copia de la pantalla actual
        screen_copy = screen.copy()

        # Posición interpolada para el proyectil, diferente para aliados (con curva)
        if attacker.type.name == "ALLY":
            progress = i / steps
            # Usar la misma curva Bezier para el movimiento del proyectil
            t = progress
            x = (
                (1 - t) ** 2 * attacker_pos[0]
                + 2 * (1 - t) * t * control_point[0]
                + t**2 * defender_pos[0]
            )
            y = (
                (1 - t) ** 2 * attacker_pos[1]
                + 2 * (1 - t) * t * control_point[1]
                + t**2 * defender_pos[1]
            )
        else:
            # Interpolación lineal para otros
            progress = i / steps
            x = attacker_pos[0] + (defender_pos[0] - attacker_pos[0]) * progress
            y = attacker_pos[1] + (defender_pos[1] - attacker_pos[1]) * progress

        # Dibujar proyectil más vistoso según el tipo
        if is_healing:
            # Proyectil de curación (círculo brillante con partículas)
            pygame.draw.circle(
                screen_copy, attack_colors["healing"], (int(x), int(y)), 8
            )
            for _ in range(4):  # Partículas alrededor
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                pygame.draw.circle(
                    screen_copy,
                    (200, 255, 200),
                    (int(x + offset_x), int(y + offset_y)),
                    2,
                )
        else:
            # Proyectil de ataque según tipo
            if attack_type == "physical":
                # Para ataques físicos, dibujar una línea
                start_x = attacker_pos[0] + (defender_pos[0] - attacker_pos[0]) * max(
                    0, progress - 0.1
                )
                start_y = attacker_pos[1] + (defender_pos[1] - attacker_pos[1]) * max(
                    0, progress - 0.1
                )
                pygame.draw.line(
                    screen_copy, color, (start_x, start_y), (int(x), int(y)), 3
                )
            else:
                # Para otros ataques, dibuja un círculo
                pygame.draw.circle(screen_copy, color, (int(x), int(y)), 8)

        # Mostrar nombre del ataque en el medio del trayecto
        if i == steps // 2:
            attack_text = font_small.render(attack_name, True, color)
            screen_copy.blit(attack_text, (x - attack_text.get_width() // 2, y - 25))

        # Actualizar pantalla
        pygame.display.flip()
        pygame.time.delay(20)  # Pequeña pausa

    # 2. Efecto en el objetivo (diferente para curación vs daño)
    if is_healing:
        # Efecto de curación: destellos verdes ascendentes
        for _ in range(3):
            # Partículas ascendentes
            for i in range(10):
                screen_copy = screen.copy()
                for j in range(5):
                    offset_x = random.randint(-30, 30)
                    particle_y = defender_pos[1] - 10 - i * 5
                    pygame.draw.circle(
                        screen_copy,
                        attack_colors["healing"],
                        (defender_pos[0] + offset_x, particle_y),
                        3,
                    )
                pygame.display.flip()
                pygame.time.delay(30)

            # Mostrar "+salud" flotando
            healing_text = font_medium.render(
                f"+{abs(damage)}", True, attack_colors["healing"]
            )
            for i in range(15):
                screen_copy = screen.copy()
                screen_copy.blit(
                    healing_text,
                    (
                        defender_pos[0] - healing_text.get_width() // 2,
                        defender_pos[1] - 60 - i * 2,
                    ),
                )
                pygame.display.flip()
                pygame.time.delay(30)
    else:
        # Efecto de daño: destello rojo
        for _ in range(3):
            # Dibujar rectángulo rojo sobre el defensor
            flash_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, 150))  # Rojo semi-transparente
            screen.blit(flash_surface, (defender_pos[0] - 40, defender_pos[1] - 40))
            pygame.display.flip()
            pygame.time.delay(80)

            # Restaurar pantalla
            pygame.display.flip()
            pygame.time.delay(80)

        # 3. Mostrar daño como número flotante
        damage_text = font_medium.render(f"-{damage}", True, COLORS["RED"])
        for i in range(15):
            screen_copy = screen.copy()
            screen_copy.blit(
                damage_text,
                (
                    defender_pos[0] - damage_text.get_width() // 2,
                    defender_pos[1] - 60 - i * 2,
                ),
            )
            pygame.display.flip()
            pygame.time.delay(30)


def show_message(screen, title, message):
    """Muestra un mensaje en pantalla completa"""
    # Fondo semi-transparente
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    # Título
    title_text = font_large.render(title, True, COLORS["GOLD"])
    screen.blit(
        title_text,
        (
            screen.get_width() // 2 - title_text.get_width() // 2,
            screen.get_height() // 2 - 100,
        ),
    )

    # Mensaje
    message_text = font_medium.render(message, True, COLORS["WHITE"])
    screen.blit(
        message_text,
        (
            screen.get_width() // 2 - message_text.get_width() // 2,
            screen.get_height() // 2,
        ),
    )

    # Instrucción
    instruction = font_small.render(
        "Presiona cualquier tecla para continuar", True, COLORS["GRAY"]
    )
    screen.blit(
        instruction,
        (
            screen.get_width() // 2 - instruction.get_width() // 2,
            screen.get_height() // 2 + 100,
        ),
    )

    pygame.display.flip()

    # Esperar a que el usuario presione una tecla
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        pygame.time.delay(100)
