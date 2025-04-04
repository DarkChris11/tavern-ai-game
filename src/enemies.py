import pygame
from src.characters import Character, CharacterType


# Cargar imágenes
def load_enemy_images():
    images = {
        "goblin": pygame.transform.scale(
            pygame.image.load("assets/images/goblin.jpg"), (80, 80)
        ),
        "skeleton_warrior": pygame.transform.scale(
            pygame.image.load("assets/images/skeleton_warrior.jpg"), (80, 80)
        ),
        "skeleton_archer": pygame.transform.scale(
            pygame.image.load("assets/images/skeleton_archer.jpg"), (80, 80)
        ),
        "skeleton_mage": pygame.transform.scale(
            pygame.image.load("assets/images/skeleton_mage.png"), (80, 80)
        ),
        "final_boss": pygame.transform.scale(
            pygame.image.load("assets/images/final_boss.jpg"), (80, 80)
        ),
    }
    return images


# Esta función se llamará cuando sea necesario crear enemigos para un nuevo bioma
def create_enemies_for_biome(biome):
    """Crea y devuelve una lista de enemigos según el bioma"""
    enemies = []

    if biome == "tutorial":
        enemies = [
            Character(
                "Goblin 1",
                30,
                30,
                {"Mordisco": {"dice": 1, "sides": 5}},
                CharacterType.ENEMY,
            ),
            Character(
                "Goblin 2",
                30,
                30,
                {"Mordisco": {"dice": 1, "sides": 5}},
                CharacterType.ENEMY,
            ),
        ]
    elif biome == "pantano":
        enemies = [
            Character(
                "Esqueleto 1",
                40,
                40,
                {"Espada": {"dice": 1, "sides": 6}},
                CharacterType.ENEMY,
            ),
            Character(
                "Esqueleto 2",
                40,
                40,
                {"Arco": {"dice": 1, "sides": 8}},
                CharacterType.ENEMY,
            ),
        ]
    elif biome == "bosque":
        enemies = [
            Character(
                "Esqueleto Guerrero",
                50,
                50,
                {"Hacha": {"dice": 2, "sides": 6}},
                CharacterType.ENEMY,
            ),
            Character(
                "Esqueleto Arquero",
                30,
                30,
                {"Flecha": {"dice": 1, "sides": 10}},
                CharacterType.ENEMY,
            ),
        ]
    elif biome == "fortaleza":
        enemies = [
            Character(
                "Esqueleto Mago",
                60,
                60,
                {"Hechizo": {"dice": 2, "sides": 8}},
                CharacterType.ENEMY,
            ),
            Character(
                "Esqueleto Guerrero",
                50,
                50,
                {"Hacha": {"dice": 2, "sides": 6}},
                CharacterType.ENEMY,
            ),
        ]
    elif biome == "jefe_final":
        enemies = [
            Character(
                "Jefe Final",
                200,
                200,
                {
                    "Golpe Mortal": {"dice": 3, "sides": 12},
                    "Rayo de Muerte": {"dice": 4, "sides": 10},
                },
                CharacterType.ENEMY,
            )
        ]

    # Asignar imágenes a los enemigos
    try:
        images = load_enemy_images()
        for enemy in enemies:
            if "Goblin" in enemy.name:
                enemy.image = images["goblin"]
            elif "Esqueleto Guerrero" in enemy.name:
                enemy.image = images["skeleton_warrior"]
            elif "Esqueleto Arquero" in enemy.name:
                enemy.image = images["skeleton_archer"]
            elif "Esqueleto Mago" in enemy.name:
                enemy.image = images["skeleton_mage"]
            elif "Jefe Final" in enemy.name:
                enemy.image = images["final_boss"]
            elif "Esqueleto 1" in enemy.name:
                enemy.image = images["skeleton_warrior"]
            elif "Esqueleto 2" in enemy.name:
                enemy.image = images["skeleton_archer"]
    except Exception as e:
        print(f"Error cargando imágenes: {e}")

    return enemies


def create_enemies_for_tutorial():
    """Crea un conjunto de enemigos diversos para el tutorial/único nivel"""
    enemies = [
        Character(
            "Goblin Guerrero",
            40,
            40,
            {
                "Mordisco": {"dice": 1, "sides": 5, "type": "physical"},
                "Garras": {
                    "dice": 1,
                    "sides": 6,
                    "type": "physical",
                    "effect": "sangrado",
                },
                "Golpe de Mazo": {"dice": 2, "sides": 4, "type": "physical"},
            },
            CharacterType.ENEMY,
        ),
        Character(
            "Arquero Esqueleto",
            30,
            30,
            {
                "Flecha Precisa": {"dice": 1, "sides": 8, "type": "physical"},
                "Flecha Venenosa": {
                    "dice": 1,
                    "sides": 6,
                    "type": "physical",
                    "effect": "veneno",
                },
                "Lluvia de Flechas": {
                    "dice": 2,
                    "sides": 4,
                    "type": "physical",
                    "effect": "área",
                },
            },
            CharacterType.ENEMY,
        ),
        Character(
            "Mago Oscuro",
            35,
            35,
            {
                "Proyectil Oscuro": {"dice": 2, "sides": 6, "type": "magic"},
                "Drenaje de Vida": {
                    "dice": 1,
                    "sides": 8,
                    "type": "magic",
                    "effect": "drenaje",
                },
                "Maldición": {
                    "dice": 1,
                    "sides": 4,
                    "type": "magic",
                    "effect": "debilitar",
                },
            },
            CharacterType.ENEMY,
        ),
    ]

    # Asignar imágenes a los enemigos
    try:
        images = load_enemy_images()
        enemies[0].image = images["goblin"]
        enemies[1].image = images["skeleton_archer"]
        enemies[2].image = images["skeleton_mage"]
    except Exception as e:
        print(f"Error cargando imágenes: {e}")

    return enemies


def create_enemies_for_tutorial():
    """Crea un conjunto de enemigos diversos para el tutorial/único nivel"""
    enemies = [
        Character(
            "Goblin Guerrero",
            40,
            40,
            {
                "Mordisco": {"dice": 1, "sides": 5, "type": "physical"},
                "Garras": {
                    "dice": 1,
                    "sides": 6,
                    "type": "physical",
                    "effect": "sangrado",
                },
                "Golpe de Mazo": {"dice": 2, "sides": 4, "type": "physical"},
            },
            CharacterType.ENEMY,
        ),
        Character(
            "Arquero Esqueleto",
            30,
            30,
            {
                "Flecha Precisa": {"dice": 1, "sides": 8, "type": "physical"},
                "Flecha Venenosa": {
                    "dice": 1,
                    "sides": 6,
                    "type": "physical",
                    "effect": "veneno",
                },
                "Lluvia de Flechas": {
                    "dice": 2,
                    "sides": 4,
                    "type": "physical",
                    "effect": "área",
                },
            },
            CharacterType.ENEMY,
        ),
        Character(
            "Mago Oscuro",
            35,
            35,
            {
                "Proyectil Oscuro": {"dice": 2, "sides": 6, "type": "magic"},
                "Drenaje de Vida": {
                    "dice": 1,
                    "sides": 8,
                    "type": "magic",
                    "effect": "drenaje",
                },
                "Maldición": {
                    "dice": 1,
                    "sides": 4,
                    "type": "magic",
                    "effect": "debilitar",
                },
            },
            CharacterType.ENEMY,
        ),
    ]

    # Asignar imágenes a los enemigos
    try:
        images = load_enemy_images()
        enemies[0].image = images["goblin"]
        enemies[1].image = images["skeleton_archer"]
        enemies[2].image = images["skeleton_mage"]
    except Exception as e:
        print(f"Error asignando imágenes a enemigos: {e}")

    return enemies
