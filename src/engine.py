import pygame
import sys
import random
from enum import Enum

from src.characters import CharacterType
from src.enemies import create_enemies_for_biome
from src.scenarios import load_scenario
from src.ui import draw_health_bar, draw_combat_ui, draw_characters, show_message

# Inicializar pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego de Rol - Brujo vs Goblins")

# Colores
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


class GameEngine:
    def __init__(self, ai_client=None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.colors = COLORS
        self.game_state = None
        self.ai_client = ai_client
        self.running = True

    def init_game(self, game_state):
        self.game_state = game_state
        # Configurar el tutorial como el escenario inicial
        load_scenario(self.game_state, "tutorial")

    def handle_events(self):
        """Maneja eventos de teclado y mouse"""
        waiting_for_input = True

        # Si no es el turno del jugador, no esperamos input
        if self.game_state.current_turn != CharacterType.PLAYER:
            waiting_for_input = False

        while waiting_for_input and not self.game_state.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return False

                if event.type == pygame.KEYDOWN:
                    # Procesar teclas cuando es el turno del jugador
                    action_taken = self.handle_player_input(event.key)
                    if action_taken:
                        waiting_for_input = (
                            False  # Salir del bucle después de procesar una acción
                        )

                # Manejo de clics en los botones
                if (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                ):  # Clic izquierdo
                    mouse_pos = pygame.mouse.get_pos()

                    # Verificar si se hizo clic en algún botón de ataque
                    click_handled = self.handle_button_click(mouse_pos)
                    if click_handled:
                        waiting_for_input = False

            # Pequeña pausa para no saturar la CPU
            pygame.time.delay(30)

            # Actualizar pantalla mientras esperamos entrada
            self.render()

        return True

    def handle_player_input(self, key):
        """Procesa la entrada de teclado del jugador"""
        # Verificar si es el turno del jugador
        if self.game_state.current_turn != CharacterType.PLAYER:
            return False

        # Cambiar objetivo (no gasta turno)
        if key == pygame.K_TAB and len(self.game_state.enemies) > 0:
            self.game_state.selected_enemy = (self.game_state.selected_enemy + 1) % len(
                self.game_state.enemies
            )
            return False  # No cuenta como acción, solo cambio de objetivo

        # Teclas numéricas para ataques (1-5)
        attacks = list(self.game_state.player.attacks.keys())

        if key == pygame.K_1 and len(attacks) > 0:
            self.perform_attack(attacks[0])
            return True

        elif key == pygame.K_2 and len(attacks) > 1:
            self.perform_attack(attacks[1])
            return True

        elif key == pygame.K_3 and len(attacks) > 2:
            self.perform_attack(attacks[2])
            return True

        elif key == pygame.K_4 and len(attacks) > 3:
            self.perform_attack(attacks[3])
            return True

        elif key == pygame.K_5 and len(attacks) > 4:
            self.perform_attack(attacks[4])
            return True

        # Poción
        elif key == pygame.K_p and self.game_state.potions > 0:
            self.use_potion()
            return True

        # Defender
        elif key == pygame.K_d:
            self.defend()
            return True

        return False

    def handle_button_click(self, mouse_pos):
        """Maneja clics en botones de la interfaz"""
        # Verificar si es el turno del jugador
        if self.game_state.current_turn != CharacterType.PLAYER:
            return False

        # Verificar clics en botones de ataque
        button_y = 100
        current_y = button_y

        # Botones de ataque
        for i, (attack_name, stats) in enumerate(
            self.game_state.player.attacks.items()
        ):
            has_effect = "effect" in stats
            button_rect = pygame.Rect(WIDTH - 340, current_y, 200, 40)

            if button_rect.collidepoint(mouse_pos):
                self.perform_attack(attack_name)
                return True

            # Actualizar posición para el siguiente botón
            if has_effect:
                current_y += 100
            else:
                current_y += 70

        # Botón de poción
        extra_buttons_y = current_y + 20
        potion_button = pygame.Rect(WIDTH - 340, extra_buttons_y, 200, 40)
        if potion_button.collidepoint(mouse_pos) and self.game_state.potions > 0:
            self.use_potion()
            return True

        # Botón de defender
        defend_button = pygame.Rect(WIDTH - 340, extra_buttons_y + 60, 200, 40)
        if defend_button.collidepoint(mouse_pos):
            self.defend()
            return True

        # Clics en enemigos para seleccionarlos
        for i, enemy in enumerate(self.game_state.enemies):
            enemy_rect = pygame.Rect(450, 150 + i * 120, 80, 80)
            if enemy_rect.collidepoint(mouse_pos):
                self.game_state.selected_enemy = i
                return False  # No cuenta como acción, solo selección

        return False

    def perform_attack(self, attack_name):
        if len(self.game_state.enemies) == 0:
            return False

        attacker = self.game_state.player
        defender = self.game_state.enemies[self.game_state.selected_enemy]

        # Extraer esta lógica a abilities.py
        from src.abilities import execute_attack

        execute_attack(self.game_state, attacker, defender, attack_name)

        # Solo cambiar de turno si el jugador está vivo y hay enemigos
        if attacker.is_alive() and len(self.game_state.enemies) > 0:
            self.game_state.current_turn = CharacterType.ENEMY
            # Resetear defending al final del turno
            self.game_state.player.defending = False

        return True

    def use_potion(self):
        heal_amount = min(
            30, self.game_state.player.max_health - self.game_state.player.health
        )
        self.game_state.player.health += heal_amount
        self.game_state.potions -= 1
        self.game_state.add_message(
            f"Usaste una poción! +{heal_amount} HP", COLORS["GREEN"]
        )
        self.game_state.current_turn = CharacterType.ENEMY
        # Resetear defending al final del turno
        self.game_state.player.defending = False
        return True

    def defend(self):
        self.game_state.player.defending = True
        self.game_state.add_message("Te preparas para defender!", COLORS["BLUE"])
        self.game_state.current_turn = CharacterType.ENEMY
        return True

    def handle_enemy_turn(self):
        """Maneja el turno de los enemigos"""
        for enemy in self.game_state.enemies:
            # Obtener acciones disponibles
            available_attacks = list(enemy.attacks.keys())

            # Determinar posibles objetivos (jugador o aliado)
            possible_targets = [self.game_state.player]
            if self.game_state.ally and self.game_state.ally.is_alive():
                possible_targets.append(self.game_state.ally)

            if self.ai_client and self.game_state.using_ai:
                # Preparar estado para IA
                game_state_for_ai = self.game_state.get_game_state_for_ai()

                # Obtener decisión de la IA (ataque)
                best_attack = self.ai_client.get_decision(
                    game_state_for_ai, available_attacks
                )

                # Decidir objetivo usando IA avanzada
                if len(possible_targets) > 1:
                    # Calcular factores estratégicos para ambos objetivos
                    player_threat = (
                        self.game_state.player.health
                        / self.game_state.player.max_health
                    )
                    ally_threat = (
                        self.game_state.ally.health / self.game_state.ally.max_health
                    )

                    # La IA prefiere atacar:
                    # - Al objetivo con menos salud (más fácil eliminar)
                    # - Si el aliado puede curar, tiene prioridad más alta
                    # - Objetivos debilitados son preferidos

                    ally_weight = ally_threat
                    player_weight = player_threat

                    # Si el aliado tiene habilidades de curación, aumenta su prioridad
                    if any(
                        "heal" in attack
                        for attack in self.game_state.ally.attacks.values()
                    ):
                        ally_weight *= 0.7  # Prioriza eliminar al curandero

                    # Elegir objetivo basado en la ponderación
                    target = (
                        self.game_state.ally
                        if ally_weight < player_weight
                        else self.game_state.player
                    )

                    self.game_state.add_message(
                        f"{enemy.name} elige atacar a {target.name}", (30, 144, 255)
                    )
                else:
                    target = possible_targets[0]  # Solo hay un objetivo disponible
            else:
                # IA simple: elegir ataque y objetivo aleatorio
                best_attack = random.choice(available_attacks)
                target = random.choice(possible_targets)

            # Ejecutar ataque
            from src.abilities import execute_attack

            execute_attack(self.game_state, enemy, target, best_attack)

            # Verificar si el juego ha terminado
            if self.game_state.game_over:
                return

            # Pequeña pausa entre ataques de enemigos
            pygame.time.delay(500)

            # Actualizar pantalla entre ataques
            self.render()

        # Al finalizar todos los ataques enemigos, volver al turno del jugador
        if not self.game_state.game_over and len(self.game_state.enemies) > 0:
            self.game_state.current_turn = CharacterType.PLAYER
            # También ejecutar acciones del aliado si existe
            self.handle_ally_turn()

    def handle_ally_turn(self):
        """Maneja las acciones del aliado si está presente"""
        if not self.game_state.ally or not self.game_state.ally.is_alive():
            return

        # Usar sistema de IA para el aliado
        from src.abilities import perform_ally_action

        perform_ally_action(self.game_state)

        # Actualizar pantalla después de la acción del aliado
        self.render()
        pygame.time.delay(500)

    def update_status_effects(self):
        """Actualiza los efectos de estado de todos los personajes"""
        for character in [
            self.game_state.player,
            self.game_state.ally,
        ] + self.game_state.enemies:
            if not character or not hasattr(character, "status_effects"):
                continue

            # Copia para evitar modificar mientras iteramos
            effects = dict(character.status_effects)

            for effect, turns in effects.items():
                # Aplicar efecto según su tipo
                if effect == "veneno" or effect == "sangrado":
                    # Daño por turno (5% de la salud máxima)
                    damage = max(1, int(character.max_health * 0.05))
                    character.health = max(0, character.health - damage)

                    # Mostrar mensaje con formato solicitado
                    effect_msg = f"Efecto {effect} --> {character.name} (-{damage} HP)"
                    self.game_state.add_message(
                        effect_msg,
                        COLORS["GREEN"] if effect == "veneno" else COLORS["RED"],
                    )

                    # Verificar si el personaje murió por el efecto
                    if character.health <= 0:
                        from src.abilities import check_defender_death

                        check_defender_death(self.game_state, character)

                # Reducir duración del efecto
                character.status_effects[effect] -= 1
                if character.status_effects[effect] <= 0:
                    del character.status_effects[effect]
                    self.game_state.add_message(
                        f"{character.name} ya no sufre de {effect}", COLORS["WHITE"]
                    )

    def update(self):
        # Actualizar efectos de estado al inicio de cada turno
        if self.game_state.current_turn == CharacterType.PLAYER:
            self.update_status_effects()

        # Manejar turnos
        if not self.game_state.game_over:
            if self.game_state.current_turn == CharacterType.ENEMY:
                self.handle_enemy_turn()

        # Verificar condiciones de victoria/derrota
        self.check_game_state()

    def check_game_state(self):
        from src.scenarios import advance_to_next_biome

        if self.game_state.player.health <= 0:
            self.game_state.game_over = True
            self.game_state.victory = False
        elif len(self.game_state.enemies) == 0:
            advance_to_next_biome(self.game_state, self.screen)

    def render(self):
        # Limpiar pantalla
        self.screen.fill(COLORS["BLACK"])  # Fondo negro

        # Dibujar personajes
        draw_characters(self.screen, self.game_state)

        # Dibujar UI
        draw_combat_ui(self.screen, self.game_state, COLORS)

        # Mostrar pantalla de game over/victoria
        if self.game_state.game_over:
            self.show_game_over_screen()

        pygame.display.flip()

    def show_game_over_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        if self.game_state.victory:
            from src.ui import font_large

            result_text = font_large.render("¡Victoria!", True, COLORS["GOLD"])
            self.screen.blit(
                result_text,
                (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 50),
            )
        else:
            from src.ui import font_large

            result_text = font_large.render("Game Over", True, COLORS["RED"])
            self.screen.blit(
                result_text,
                (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 50),
            )

    def run(self):
        while self.running and not self.game_state.game_over:
            # El handle_events ahora maneja la espera de entrada del jugador
            if not self.handle_events():
                break

            # El update ahora solo se ejecuta cuando no es el turno del jugador
            self.update()

            # Render se llama continuamente para mantener la pantalla actualizada
            self.render()

            self.clock.tick(30)

        # Mostrar pantalla final si es game over
        if self.game_state.game_over:
            self.show_game_over_screen()
            pygame.time.wait(3000)

        pygame.quit()
        return self.game_state.victory
