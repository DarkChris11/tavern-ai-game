import pygame
import sys
from src.ui import COLORS, font_large, font_medium, font_small, draw_button


class Tutorial:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.clock = pygame.time.Clock()

        # Etapas del tutorial
        self.steps = [
            {
                "title": "Bienvenido a Pygame AI RPG",
                "text": [
                    "Este tutorial te guiará a través de los",
                    "conceptos básicos del juego y te enseñará",
                    "cómo enfrentarte a enemigos controlados por IA.",
                ],
                "image": None,
            },
            {
                "title": "Controles Básicos",
                "text": [
                    "• Números 1-5: Usar ataques/habilidades",
                    "• Tab: Cambiar entre objetivos enemigos",
                    "• P: Usar poción de curación",
                    "• D: Defender (reduce daño recibido)",
                    "• C: Borrar historial de mensajes",
                ],
                "image": "controls.jpg",
            },
            {
                "title": "Tu Personaje: El Brujo",
                "text": [
                    "Como Brujo, tienes acceso a poderosos ataques:",
                    "• Espada: Ataque físico básico",
                    "• Lanzar Espinas: Envenena al enemigo",
                    "• Bola de Fuego: Daño mágico potente",
                    "• Rayo Helado: Congela al enemigo",
                    "• Golpe Rápido: Ataca dos veces",
                ],
                "image": "player.jpg",
            },
            {
                "title": "Tu Aliada: La Curandera",
                "text": [
                    "La Curandera te ayudará en combate:",
                    "• Toque Curativo: Restaura tu salud",
                    "• Proyectil Mágico: Ataque básico",
                    "• Bendición: Cura y aumenta tu fuerza",
                    "• Agua Bendita: Daño contra no-muertos",
                ],
                "image": "ally.jpg",
            },
            {
                "title": "Efectos de Estado",
                "text": [
                    "Algunos ataques aplican efectos especiales:",
                    "• Veneno: Daño continuo por turno",
                    "• Congelado: Reduce velocidad",
                    "• Sangrado: Daño continuo por turno",
                    "• Bendición: Aumenta daño causado",
                    "• Ataque Doble: Golpea dos veces",
                ],
                "image": "effects.jpg",
            },
            {
                "title": "Enemigos con IA",
                "text": [
                    "Los enemigos están controlados por IA:",
                    "• Analizan el estado del combate",
                    "• Seleccionan estrategias óptimas",
                    "• Se adaptan a tu estilo de juego",
                    "• Priorizan objetivos según la amenaza",
                ],
                "image": "enemies.jpg",
            },
            {
                "title": "Consejos Estratégicos",
                "text": [
                    "• Usa pociones cuando estés bajo de salud",
                    "• Prioriza enemigos con efectos peligrosos",
                    "• La defensa reduce el daño en un 50%",
                    "• Combina los ataques de tu aliada",
                    "• Analiza patrones de la IA para anticiparte",
                ],
                "image": "strategy.jpg",
            },
            {
                "title": "¡Estás listo para jugar!",
                "text": [
                    "Has completado el tutorial básico.",
                    "¿Estás listo para enfrentarte a la IA?",
                    "",
                    "Presiona ENTER para comenzar",
                    "o ESC para volver al menú principal.",
                ],
                "image": None,
            },
        ]

        self.current_step = 0
        self.max_steps = len(self.steps)

        # Cargar imágenes del tutorial
        self.images = {}
        self.load_images()

    def load_images(self):
        """Carga las imágenes para el tutorial"""
        import os

        image_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "images"
        )

        for step in self.steps:
            if step["image"]:
                img_path = os.path.join(image_dir, step["image"])
                try:
                    if os.path.exists(img_path):
                        img = pygame.image.load(img_path)
                        img = pygame.transform.scale(img, (300, 300))
                        self.images[step["image"]] = img
                except Exception as e:
                    print(f"Error cargando imagen {step['image']}: {e}")

    def draw(self):
        # Fondo con degradado
        for y in range(self.height):
            color_value = int(y / self.height * 80)
            pygame.draw.line(
                self.screen, (30, 30, 50 + color_value), (0, y), (self.width, y)
            )

        # Marco del tutorial
        tutorial_rect = pygame.Rect(50, 50, self.width - 100, self.height - 100)
        pygame.draw.rect(self.screen, (40, 40, 60), tutorial_rect, border_radius=10)
        pygame.draw.rect(
            self.screen, COLORS["GOLD"], tutorial_rect, 2, border_radius=10
        )

        # Título del paso actual
        step = self.steps[self.current_step]
        title = font_large.render(step["title"], True, COLORS["GOLD"])
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))

        # Imagen si existe
        if step["image"] and step["image"] in self.images:
            img = self.images[step["image"]]
            img_rect = img.get_rect(center=(self.width // 4, self.height // 2))
            self.screen.blit(img, img_rect)

        # Texto explicativo
        text_x = self.width // 2 if step["image"] in self.images else self.width // 2
        text_y = 180
        for line in step["text"]:
            text = font_medium.render(line, True, COLORS["WHITE"])
            text_rect = text.get_rect(center=(text_x, text_y))
            self.screen.blit(text, text_rect)
            text_y += 40

        # Indicadores de navegación
        nav_y = self.height - 80

        # Botón Anterior
        prev_button = draw_button(
            self.screen,
            100,
            nav_y,
            "Anterior",
            COLORS["BLUE"] if self.current_step > 0 else COLORS["GRAY"],
        )

        # Indicador de progreso
        progress_text = font_medium.render(
            f"{self.current_step + 1}/{self.max_steps}", True, COLORS["WHITE"]
        )
        self.screen.blit(
            progress_text,
            (self.width // 2 - progress_text.get_width() // 2, nav_y + 10),
        )

        # Botón Siguiente
        next_button = draw_button(
            self.screen,
            self.width - 250,
            nav_y,
            "Siguiente" if self.current_step < self.max_steps - 1 else "Comenzar",
            COLORS["GREEN"],
        )

        # Instrucciones
        instructions = font_small.render(
            "Navega con ← →, ESC para volver al menú", True, COLORS["GRAY"]
        )
        self.screen.blit(
            instructions,
            (self.width // 2 - instructions.get_width() // 2, self.height - 30),
        )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "BACK"

                elif event.key == pygame.K_LEFT:
                    if self.current_step > 0:
                        self.current_step -= 1

                elif event.key == pygame.K_RIGHT:
                    if self.current_step < self.max_steps - 1:
                        self.current_step += 1
                    else:
                        return "PLAY"  # Último paso, comenzar el juego

                elif event.key == pygame.K_RETURN:
                    if self.current_step == self.max_steps - 1:
                        return "PLAY"  # Último paso, comenzar el juego

            # Clic en botones
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Botón Anterior
                prev_rect = pygame.Rect(100, self.height - 80, 150, 40)
                if prev_rect.collidepoint(mouse_pos) and self.current_step > 0:
                    self.current_step -= 1

                # Botón Siguiente/Comenzar
                next_rect = pygame.Rect(self.width - 250, self.height - 80, 150, 40)
                if next_rect.collidepoint(mouse_pos):
                    if self.current_step < self.max_steps - 1:
                        self.current_step += 1
                    else:
                        return "PLAY"  # Último paso, comenzar el juego

        return None

    def run(self):
        while self.running:
            self.clock.tick(60)

            result = self.handle_events()
            if result:
                return result

            self.draw()

        return "BACK"
