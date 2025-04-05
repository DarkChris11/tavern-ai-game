import pygame
import sys
import math
import random
import os
from src.ui import COLORS, font_large, font_medium, font_small, draw_button

# Colores temáticos para Tavern AI
TAVERN_COLORS = {
    "BACKGROUND": (20, 15, 35),  # Fondo oscuro con tono púrpura
    "PANEL": (35, 30, 60),  # Panel más claro
    "GOLD": (255, 215, 0),  # Dorado para acentos
    "AMBER": (255, 191, 0),  # Ámbar para detalles
    "WOOD": (133, 94, 66),  # Color madera para bordes
    "HIGHLIGHT": (220, 180, 100),  # Resaltado
    "TEXT_NORMAL": (220, 220, 220),  # Texto regular
    "TEXT_HIGHLIGHT": (255, 255, 200),  # Texto resaltado
    "BUTTON_ACTIVE": (70, 40, 90),  # Botón activo
    "BUTTON_HOVER": (90, 50, 120),  # Botón con hover
    "BUTTON_INACTIVE": (50, 30, 70),  # Botón inactivo
}


class TutorialParticle:
    """Clase para partículas decorativas en el tutorial"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(1.5, 4)
        self.speed = random.uniform(0.2, 1)
        self.direction = random.uniform(0, 2 * math.pi)
        self.life = random.uniform(0.5, 1)
        self.max_life = self.life

    def update(self):
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        self.life -= 0.01
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))


class Tutorial:
    def __init__(self, screen):
        print("Inicializando tutorial de Tavern AI...")
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.running = True
        self.clock = pygame.time.Clock()

        # Crear superficie para partículas
        self.particle_surface = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA
        )
        self.particles = []

        # Efecto de transición
        self.fade_alpha = 255
        self.fade_direction = -1  # -1 = fade in, 1 = fade out
        self.transition_speed = 5
        self.transitioning = True

        # Animación del título
        self.title_scale = 0.8
        self.title_direction = 0.001

        # Logo de DarkChris
        self.logo_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.logo_angle = 0

        # Variables para transición de página
        self.next_step = None
        self.page_offset = 0

        # Etapas del tutorial
        self.steps = [
            {
                "title": "Bienvenido a Tavern AI",
                "text": [
                    "Este tutorial te guiará a través de los",
                    "conceptos básicos del juego y te enseñará",
                    "cómo enfrentarte a enemigos controlados por IA.",
                    "",
                    "Una experiencia única creada por DarkChris",
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
                "title": "¡Estás listo para la aventura!",
                "text": [
                    "Has completado el tutorial básico.",
                    "¿Estás listo para adentrarte en el mundo de Tavern AI?",
                    "",
                    "Presiona ENTER para comenzar",
                    "o ESC para volver al menú principal.",
                    "",
                    "Creado con pasión por DarkChris",
                ],
                "image": None,
            },
        ]

        self.current_step = 0
        self.max_steps = len(self.steps)

        # Cargar imágenes del tutorial
        self.images = {}
        self.load_images()
        print("Tutorial inicializado correctamente")

    def load_images(self):
        """Carga las imágenes para el tutorial con manejo de errores mejorado"""
        print("Cargando imágenes para el tutorial...")
        try:
            image_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "assets", "images"
            )

            # Asegurar que el directorio existe
            if not os.path.exists(image_dir):
                print(f"Creando directorio de imágenes: {image_dir}")
                os.makedirs(image_dir, exist_ok=True)

            for step in self.steps:
                if step["image"]:
                    img_path = os.path.join(image_dir, step["image"])
                    try:
                        if os.path.exists(img_path):
                            img = pygame.image.load(img_path)
                            img = pygame.transform.scale(img, (300, 300))
                            # Agregar un borde dorado a la imagen
                            bordered_img = pygame.Surface((316, 316))
                            bordered_img.fill(TAVERN_COLORS["GOLD"])
                            bordered_img.blit(img, (8, 8))
                            self.images[step["image"]] = bordered_img
                            print(f"Imagen cargada: {step['image']}")
                        else:
                            print(f"Imagen no encontrada: {img_path}")
                            # Crear una imagen placeholder con texto
                            placeholder = pygame.Surface((300, 300))
                            placeholder.fill(TAVERN_COLORS["PANEL"])

                            # Texto informativo
                            text = font_medium.render(
                                f"Imagen no disponible",
                                True,
                                TAVERN_COLORS["TEXT_HIGHLIGHT"],
                            )
                            text_rect = text.get_rect(center=(150, 150))
                            placeholder.blit(text, text_rect)

                            # Agregar borde
                            bordered_img = pygame.Surface((316, 316))
                            bordered_img.fill(TAVERN_COLORS["GOLD"])
                            bordered_img.blit(placeholder, (8, 8))
                            self.images[step["image"]] = bordered_img
                    except Exception as e:
                        print(f"Error cargando imagen {step['image']}: {e}")
                        # No lanzar excepción, solo registrar el error
        except Exception as e:
            print(f"Error general cargando imágenes: {e}")
            import traceback

            traceback.print_exc()

    def create_particles(self, x, y, count=5):
        """Crea partículas decorativas en la posición dada"""
        for _ in range(count):
            particle_color = (
                random.randint(200, 255),
                random.randint(170, 230),
                random.randint(0, 100),
                random.randint(150, 255),
            )
            self.particles.append(TutorialParticle(x, y, particle_color))

    def update_particles(self):
        """Actualiza y dibuja todas las partículas activas"""
        self.particle_surface.fill((0, 0, 0, 0))
        self.particles = [p for p in self.particles if p.update()]
        for particle in self.particles:
            particle.draw(self.particle_surface)

    def draw_developer_logo(self):
        """Dibuja un logo animado para DarkChris"""
        try:
            self.logo_angle = (self.logo_angle + 0.5) % 360
            logo_text = self.logo_font.render("DarkChris", True, TAVERN_COLORS["GOLD"])

            # Crear superficie rotada
            logo_surf = pygame.Surface(
                (logo_text.get_width() + 20, logo_text.get_height() + 20),
                pygame.SRCALPHA,
            )
            logo_surf.fill((0, 0, 0, 0))

            # Dibujar texto
            logo_surf.blit(logo_text, (10, 10))

            # Dibujar borde decorativo
            size = min(logo_text.get_width(), logo_text.get_height()) + 15
            rect = pygame.Rect(
                (logo_surf.get_width() - size) // 2,
                (logo_surf.get_height() - size) // 2,
                size,
                size,
            )

            # Dibujar un borde decorativo con efecto de rotación
            for i in range(4):
                angle = self.logo_angle + i * 90
                rad = math.radians(angle)
                start = (
                    rect.centerx + math.cos(rad) * (size // 2),
                    rect.centery + math.sin(rad) * (size // 2),
                )
                end = (
                    rect.centerx + math.cos(rad + math.pi / 4) * (size // 2),
                    rect.centery + math.sin(rad + math.pi / 4) * (size // 2),
                )
                pygame.draw.line(logo_surf, TAVERN_COLORS["AMBER"], start, end, 2)

            # Posicionar en esquina
            self.screen.blit(logo_surf, (self.width - logo_surf.get_width() - 10, 10))
        except Exception as e:
            print(f"Error dibujando logo del desarrollador: {e}")

    def update_animations(self):
        """Actualiza todas las animaciones y efectos visuales"""
        try:
            # Actualizar animación del título
            self.title_scale += self.title_direction
            if self.title_scale > 1.05:
                self.title_direction = -0.001
            elif self.title_scale < 0.95:
                self.title_direction = 0.001

            # Actualizar transición de fade
            if self.transitioning:
                self.fade_alpha += self.fade_direction * self.transition_speed
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.transitioning = False
                elif self.fade_alpha >= 255:
                    self.fade_alpha = 255
                    self.transitioning = False
                    self.page_offset = 0
                    # Si estamos haciendo fade out, pasar al siguiente estado
                    if self.fade_direction > 0:
                        return True

            # Actualizar desplazamiento de página
            if abs(self.page_offset) > 0:
                self.page_offset *= 0.9
                if abs(self.page_offset) < 1:
                    self.page_offset = 0

            # Crear partículas aleatorias ocasionales
            if random.random() < 0.05:
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                self.create_particles(x, y, 2)

            self.update_particles()
            return False
        except Exception as e:
            print(f"Error en animaciones: {e}")
            return False

    def start_transition(self, direction):
        """Inicia una transición de fade (direction: -1=fade in, 1=fade out)"""
        self.transitioning = True
        self.fade_direction = direction

        if direction > 0:  # fade out
            self.fade_alpha = 0
        else:  # fade in
            self.fade_alpha = 255

    def change_step(self, new_step):
        """Cambia al paso especificado con una animación"""
        # Iniciar animación de transición
        self.start_transition(1)  # fade out

        # Guardar el nuevo paso para después de la transición
        self.next_step = new_step

        # Ajustar desplazamiento para animación
        self.page_offset = -300 if new_step > self.current_step else 300

    def draw(self):
        """Dibuja la interfaz completa del tutorial"""
        try:
            # Fondo con degradado y textura
            for y in range(0, self.height, 2):
                color_value = int(y / self.height * 50)
                pygame.draw.line(
                    self.screen,
                    (
                        TAVERN_COLORS["BACKGROUND"][0],
                        TAVERN_COLORS["BACKGROUND"][1] + color_value // 2,
                        TAVERN_COLORS["BACKGROUND"][2] + color_value,
                    ),
                    (0, y),
                    (self.width, y),
                    2,
                )

            # Agregar textura al fondo
            for _ in range(100):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                size = random.randint(1, 3)
                alpha = random.randint(30, 100)
                s = pygame.Surface((size, size), pygame.SRCALPHA)
                s.fill((255, 255, 255, alpha))
                self.screen.blit(s, (x, y))

            # Marco del tutorial con efecto de madera de taberna
            tutorial_rect = pygame.Rect(
                50 + self.page_offset, 50, self.width - 100, self.height - 100
            )

            # Panel principal con borde decorativo
            pygame.draw.rect(
                self.screen, TAVERN_COLORS["PANEL"], tutorial_rect, border_radius=15
            )

            # Borde exterior tipo madera
            border_rect = tutorial_rect.copy()
            border_rect.inflate_ip(8, 8)
            pygame.draw.rect(
                self.screen, TAVERN_COLORS["WOOD"], border_rect, 4, border_radius=15
            )

            # Borde interior dorado
            pygame.draw.rect(
                self.screen, TAVERN_COLORS["GOLD"], tutorial_rect, 2, border_radius=15
            )

            # Título del paso actual con efecto de brillo
            step = self.steps[self.current_step]

            # Título con escala animada
            title_font = pygame.font.SysFont(
                "Arial", int(40 * self.title_scale), bold=True
            )
            title = title_font.render(step["title"], True, TAVERN_COLORS["GOLD"])

            # Sombra del título
            title_shadow = title_font.render(step["title"], True, (0, 0, 0))
            self.screen.blit(
                title_shadow, (self.width // 2 - title.get_width() // 2 + 2, 82)
            )

            # Título principal
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))

            # Decoración bajo el título
            title_width = title.get_width()
            pygame.draw.line(
                self.screen,
                TAVERN_COLORS["GOLD"],
                (self.width // 2 - title_width // 2, 120),
                (self.width // 2 + title_width // 2, 120),
                2,
            )

            # Decoraciones en las esquinas del título
            corner_size = 15
            # Esquina superior izquierda
            pygame.draw.line(
                self.screen,
                TAVERN_COLORS["AMBER"],
                (self.width // 2 - title_width // 2, 120),
                (self.width // 2 - title_width // 2, 120 - corner_size),
                2,
            )
            pygame.draw.line(
                self.screen,
                TAVERN_COLORS["AMBER"],
                (self.width // 2 - title_width // 2, 120),
                (self.width // 2 - title_width // 2 + corner_size, 120),
                2,
            )

            # Esquina superior derecha
            pygame.draw.line(
                self.screen,
                TAVERN_COLORS["AMBER"],
                (self.width // 2 + title_width // 2, 120),
                (self.width // 2 + title_width // 2, 120 - corner_size),
                2,
            )
            pygame.draw.line(
                self.screen,
                TAVERN_COLORS["AMBER"],
                (self.width // 2 + title_width // 2, 120),
                (self.width // 2 + title_width // 2 - corner_size, 120),
                2,
            )

            # Imagen si existe
            if step["image"] and step["image"] in self.images:
                img = self.images[step["image"]]
                # Posición animada
                offset = math.sin(pygame.time.get_ticks() / 1000) * 5
                img_rect = img.get_rect(
                    center=(self.width // 4, self.height // 2 + offset)
                )
                self.screen.blit(img, img_rect)

                # Crear partículas ocasionales alrededor de la imagen
                if random.random() < 0.1:
                    angle = random.uniform(0, 2 * math.pi)
                    radius = img_rect.width // 2 + 10
                    x = img_rect.centerx + math.cos(angle) * radius
                    y = img_rect.centery + math.sin(angle) * radius
                    self.create_particles(x, y, 3)

            # Texto explicativo con mejor formato
            text_x = (
                self.width // 2 + 100
                if step["image"] in self.images
                else self.width // 2
            )
            text_y = 180

            # Fondo para el texto (panel semi-transparente)
            if step["image"] in self.images:
                text_panel = pygame.Rect(
                    self.width // 2 - 50, 160, self.width // 2, self.height - 300
                )
                s = pygame.Surface(
                    (text_panel.width, text_panel.height), pygame.SRCALPHA
                )
                s.fill((30, 20, 50, 150))
                self.screen.blit(s, text_panel)
                pygame.draw.rect(
                    self.screen, TAVERN_COLORS["WOOD"], text_panel, 2, border_radius=8
                )

            for i, line in enumerate(step["text"]):
                # Detectar si es una línea de DarkChris
                if "DarkChris" in line:
                    text = font_medium.render(line, True, TAVERN_COLORS["GOLD"])
                    text_rect = text.get_rect(center=(text_x, text_y))
                    self.screen.blit(text, text_rect)

                    # Añadir partículas alrededor del nombre del desarrollador
                    if random.random() < 0.2:
                        # Encontrar la posición de "DarkChris" en el texto
                        dc_pos = line.find("DarkChris")
                        if dc_pos >= 0:
                            dc_x = text_rect.x + dc_pos * 14  # Estimación aproximada
                            self.create_particles(dc_x + 40, text_y, 2)
                else:
                    # Determinar si es un punto de lista
                    if line.startswith("•"):
                        # Línea con viñeta, usar color diferente para la viñeta
                        bullet = font_medium.render("•", True, TAVERN_COLORS["AMBER"])
                        rest = font_medium.render(
                            line[1:], True, TAVERN_COLORS["TEXT_NORMAL"]
                        )

                        # Calcular posiciones
                        if step["image"] in self.images:
                            bullet_x = self.width // 2 - 30
                            rest_x = self.width // 2 - 10
                        else:
                            bullet_x = text_x - 80
                            rest_x = text_x - 60

                        # Dibujar viñeta y texto
                        self.screen.blit(bullet, (bullet_x, text_y - 10))
                        self.screen.blit(rest, (rest_x, text_y - 10))
                    else:
                        # Texto normal
                        text = font_medium.render(
                            line, True, TAVERN_COLORS["TEXT_NORMAL"]
                        )
                        text_rect = text.get_rect(center=(text_x, text_y))
                        self.screen.blit(text, text_rect)

                text_y += 40

            # Indicadores de navegación con mejor diseño
            nav_y = self.height - 80

            # Botón Anterior
            prev_enabled = self.current_step > 0
            prev_color = (
                TAVERN_COLORS["BUTTON_ACTIVE"]
                if prev_enabled
                else TAVERN_COLORS["BUTTON_INACTIVE"]
            )
            prev_button = self.draw_fancy_button(
                100, nav_y, "« Anterior", prev_color, enabled=prev_enabled
            )

            # Indicador de progreso con decoración
            progress_rect = pygame.Rect(self.width // 2 - 60, nav_y, 120, 40)
            pygame.draw.rect(
                self.screen, TAVERN_COLORS["PANEL"], progress_rect, border_radius=10
            )
            pygame.draw.rect(
                self.screen, TAVERN_COLORS["GOLD"], progress_rect, 1, border_radius=10
            )

            progress_text = font_medium.render(
                f"{self.current_step + 1}/{self.max_steps}",
                True,
                TAVERN_COLORS["TEXT_HIGHLIGHT"],
            )
            self.screen.blit(
                progress_text,
                (self.width // 2 - progress_text.get_width() // 2, nav_y + 10),
            )

            # Botón Siguiente
            next_text = (
                "Siguiente »"
                if self.current_step < self.max_steps - 1
                else "¡Comenzar! »"
            )
            next_button = self.draw_fancy_button(
                self.width - 250, nav_y, next_text, TAVERN_COLORS["BUTTON_ACTIVE"]
            )

            # Instrucciones con mejor estética
            instructions_panel = pygame.Rect(
                self.width // 2 - 200, self.height - 40, 400, 30
            )
            pygame.draw.rect(
                self.screen, (0, 0, 0, 128), instructions_panel, border_radius=15
            )

            instructions = font_small.render(
                "Navega con ← →, ESC para volver al menú",
                True,
                TAVERN_COLORS["TEXT_NORMAL"],
            )
            self.screen.blit(
                instructions,
                (self.width // 2 - instructions.get_width() // 2, self.height - 35),
            )

            # Dibujar logo de desarrollador
            self.draw_developer_logo()

            # Dibujar partículas
            self.screen.blit(self.particle_surface, (0, 0))

            # Aplicar efecto de transición si está activo
            if self.transitioning:
                fade_surface = pygame.Surface(
                    (self.width, self.height), pygame.SRCALPHA
                )
                fade_surface.fill((0, 0, 0, self.fade_alpha))
                self.screen.blit(fade_surface, (0, 0))

            pygame.display.flip()
        except Exception as e:
            print(f"Error en método draw(): {e}")
            import traceback

            traceback.print_exc()

    def draw_fancy_button(self, x, y, text, color, width=150, height=40, enabled=True):
        """Dibuja un botón decorativo con efectos visuales"""
        try:
            button_rect = pygame.Rect(x, y, width, height)

            # Dibujar fondo con gradiente
            for i in range(height):
                gradient_color = (color[0], color[1], min(255, color[2] + i // 2))
                pygame.draw.line(
                    self.screen, gradient_color, (x, y + i), (x + width, y + i)
                )

            # Borde exterior
            pygame.draw.rect(
                self.screen,
                TAVERN_COLORS["WOOD"] if enabled else TAVERN_COLORS["PANEL"],
                button_rect,
                2,
                border_radius=10,
            )

            # Texto con sombra
            text_color = (
                TAVERN_COLORS["TEXT_HIGHLIGHT"] if enabled else TAVERN_COLORS["GRAY"]
            )

            # Primero la sombra
            text_surf_shadow = font_medium.render(text, True, (0, 0, 0))
            text_rect_shadow = text_surf_shadow.get_rect(
                center=(button_rect.center[0] + 1, button_rect.center[1] + 1)
            )
            self.screen.blit(text_surf_shadow, text_rect_shadow)

            # Luego el texto
            text_surf = font_medium.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)

            # Si el botón está activo, agregar partículas ocasionales
            if enabled and random.random() < 0.05:
                self.create_particles(
                    button_rect.x + random.randint(0, button_rect.width),
                    button_rect.y + random.randint(0, button_rect.height),
                    2,
                )

            return button_rect
        except Exception as e:
            print(f"Error dibujando botón: {e}")
            # Devolver un rectángulo vacío en caso de error
            return pygame.Rect(x, y, width, height)

    def handle_events(self):
        """Maneja eventos de teclado y ratón"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Evento QUIT detectado")
                    self.running = False
                    return "QUIT"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("ESC presionado - volviendo al menú")
                        return "BACK"

                    elif event.key == pygame.K_LEFT and not self.transitioning:
                        if self.current_step > 0:
                            print(f"Cambiando al paso anterior: {self.current_step-1}")
                            self.change_step(self.current_step - 1)

                    elif event.key == pygame.K_RIGHT and not self.transitioning:
                        if self.current_step < self.max_steps - 1:
                            print(f"Cambiando al siguiente paso: {self.current_step+1}")
                            self.change_step(self.current_step + 1)
                        else:
                            print("Último paso - iniciando juego")
                            return "PLAY"  # Último paso, comenzar el juego

                    elif event.key == pygame.K_RETURN and not self.transitioning:
                        if self.current_step == self.max_steps - 1:
                            print("ENTER presionado en último paso - iniciando juego")
                            return "PLAY"  # Último paso, comenzar el juego

                # Clic en botones
                if event.type == pygame.MOUSEBUTTONDOWN and not self.transitioning:
                    mouse_pos = pygame.mouse.get_pos()

                    # Verificar botón anterior
                    prev_rect = pygame.Rect(100, self.height - 80, 150, 40)
                    if prev_rect.collidepoint(mouse_pos) and self.current_step > 0:
                        print(
                            f"Clic en 'Anterior' - cambiando al paso {self.current_step-1}"
                        )
                        self.change_step(self.current_step - 1)

                    # Verificar botón siguiente/comenzar
                    next_rect = pygame.Rect(self.width - 250, self.height - 80, 150, 40)
                    if next_rect.collidepoint(mouse_pos):
                        if self.current_step < self.max_steps - 1:
                            print(
                                f"Clic en 'Siguiente' - cambiando al paso {self.current_step+1}"
                            )
                            self.change_step(self.current_step + 1)
                        else:
                            print("Clic en 'Comenzar' - iniciando juego")
                            return "PLAY"  # Último paso, comenzar el juego

            # Actualizar animaciones
            change_complete = self.update_animations()

            # Si la transición de fade out terminó, aplicar el cambio
            if change_complete and hasattr(self, "next_step"):
                print(f"Transición completa - cambiando al paso {self.next_step}")
                self.current_step = self.next_step
                del self.next_step
                self.start_transition(-1)  # Iniciar fade in

            return None
        except Exception as e:
            print(f"Error en handle_events: {e}")
            import traceback

            traceback.print_exc()
            return None

    def run(self):
        """Ejecuta el bucle principal del tutorial"""
        try:
            print("Iniciando tutorial de Tavern AI...")
            # Iniciar con un fade in
            self.start_transition(-1)

            while self.running:
                self.clock.tick(60)

                result = self.handle_events()
                if result:
                    print(f"Tutorial terminado con resultado: {result}")
                    return result

                self.draw()

            print("Bucle del tutorial finalizado - retornando a MENU")
            return "BACK"

        except Exception as e:
            print(f"Error fatal en tutorial: {e}")
            import traceback

            traceback.print_exc()
            return "BACK"  # En caso de error, volver al menú
