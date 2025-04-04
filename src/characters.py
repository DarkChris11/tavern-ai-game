# Añadir justo después de las importaciones al inicio del archivo
import pygame
import os


def load_character_images():
    """Carga las imágenes de los personajes"""
    images = {}

    # Rutas a las imágenes (en assets/images)
    image_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", "images"
    )

    # Debug para ver la ruta
    print(f"Buscando imágenes en: {image_dir}")

    # Intentar cargar las imágenes
    try:
        player_path = os.path.join(image_dir, "player.jpg")
        ally_path = os.path.join(image_dir, "ally.jpg")

        print(f"Ruta de player: {player_path}, existe: {os.path.exists(player_path)}")
        print(f"Ruta de ally: {ally_path}, existe: {os.path.exists(ally_path)}")

        if os.path.exists(player_path):
            player_img = pygame.image.load(player_path)
            player_img = pygame.transform.scale(player_img, (80, 80))
            images["player"] = player_img
            print("Imagen del jugador cargada correctamente")

        if os.path.exists(ally_path):
            ally_img = pygame.image.load(ally_path)
            ally_img = pygame.transform.scale(ally_img, (80, 80))
            images["ally"] = ally_img
            print("Imagen del aliado cargada correctamente")

    except Exception as e:
        print(f"Error cargando imágenes de personajes: {e}")

    return images
    """Carga las imágenes de los personajes"""
    images = {}

    # Rutas a las imágenes (directamente en assets, sin subcarpeta images)
    image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

    # Debug para ver la ruta
    print(f"Buscando imágenes en: {image_dir}")

    # Intentar cargar las imágenes
    try:
        player_path = os.path.join(image_dir, "player.jpg")
        ally_path = os.path.join(image_dir, "ally.jpg")

        print(f"Ruta de player: {player_path}, existe: {os.path.exists(player_path)}")
        print(f"Ruta de ally: {ally_path}, existe: {os.path.exists(ally_path)}")

        if os.path.exists(player_path):
            player_img = pygame.image.load(player_path)
            player_img = pygame.transform.scale(player_img, (80, 80))
            images["player"] = player_img
            print("Imagen del jugador cargada correctamente")

        if os.path.exists(ally_path):
            ally_img = pygame.image.load(ally_path)
            ally_img = pygame.transform.scale(ally_img, (80, 80))
            images["ally"] = ally_img
            print("Imagen del aliado cargada correctamente")

    except Exception as e:
        print(f"Error cargando imágenes de personajes: {e}")

    return images


from enum import Enum

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


class CharacterType(Enum):
    PLAYER = 1
    ENEMY = 2
    ALLY = 3


# Añade este atributo al inicializador de Character


class Character:
    def __init__(self, name, health, max_health, attacks, character_type):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.attacks = attacks
        self.type = character_type
        self.status_effects = {}
        self.defending = False
        self.image = None  # Se asignará después
        self.game_state = None  # Referencia al estado del juego, se asignará después

    def take_damage(self, damage):
        if self.defending:
            damage = max(1, damage // 2)
        self.health = max(0, self.health - damage)
        return damage

    def add_status_effect(self, effect, duration):
        self.status_effects[effect] = duration

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
                        effect_msg, COLORS["GREEN" if effect == "veneno" else "RED"]
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

    def is_alive(self):
        return self.health > 0


class GameState:
    def __init__(self):
        # Jugador con más ataques
        self.player = Character(
            name="Brujo",
            health=150,
            max_health=150,
            attacks={
                "Espada": {"dice": 1, "sides": 8, "type": "physical"},
                "Lanzar Espinas": {
                    "dice": 1,
                    "sides": 10,
                    "type": "magic",
                    "effect": "veneno",
                },
                "Bola de Fuego": {"dice": 2, "sides": 12, "type": "magic"},
                "Rayo Helado": {
                    "dice": 2,
                    "sides": 10,
                    "type": "magic",
                    "effect": "congelado",
                },
                "Golpe Rápido": {
                    "dice": 1,
                    "sides": 6,
                    "type": "physical",
                    "effect": "ataque_doble",
                },
            },
            character_type=CharacterType.PLAYER,
        )

        # Aliado siempre presente (no solo en la batalla final)
        self.ally = Character(
            name="Curandera",
            health=100,
            max_health=100,
            attacks={
                "Toque Curativo": {"heal": 20},
                "Proyectil Mágico": {"dice": 1, "sides": 8, "type": "magic"},
                "Bendición": {"heal": 10, "effect": "bendición"},
                "Agua Bendita": {"dice": 1, "sides": 10, "type": "holy"},
            },
            character_type=CharacterType.ALLY,
        )

        self.enemies = []
        self.current_turn = CharacterType.PLAYER
        self.selected_enemy = 0
        self.potions = 5
        self.messages = []  # Para guardar mensajes del juego
        self.game_over = False
        self.victory = False
        self.tutorial = True
        self.using_ai = True
        self.biome = 0

        # Ahora carga y asigna las imágenes DESPUÉS de crear los personajes
        try:
            character_images = load_character_images()
            if "player" in character_images:
                self.player.image = character_images["player"]
                print("Imagen asignada al jugador")
            if "ally" in character_images and self.ally:
                self.ally.image = character_images["ally"]
                print("Imagen asignada al aliado")
        except Exception as e:
            print(f"Error asignando imágenes a personajes: {e}")

    def add_message(self, text, color=(0, 0, 0)):
        """Añade un mensaje al registro del juego"""
        self.messages.insert(0, (text, color))
        if len(self.messages) > 5:
            self.messages.pop()

    def get_game_state_for_ai(self):
        """Prepara un resumen del estado del juego para enviar a la IA"""
        enemy_info = []
        for enemy in self.enemies:
            enemy_info.append(
                {
                    "name": enemy.name,
                    "health": enemy.health,
                    "max_health": enemy.max_health,
                    "status_effects": (
                        list(enemy.status_effects.keys())
                        if hasattr(enemy, "status_effects")
                        else []
                    ),
                }
            )

        return {
            "player_health": self.player.health,
            "player_max_health": self.player.max_health,
            "player_defending": self.player.defending,
            "player_status_effects": (
                list(self.player.status_effects.keys())
                if hasattr(self.player, "status_effects")
                else []
            ),
            "enemies": enemy_info,
            "ally": (
                {"health": self.ally.health, "max_health": self.ally.max_health}
                if self.ally
                else None
            ),
            "potions": self.potions,
            "biome": self.biome,
        }
