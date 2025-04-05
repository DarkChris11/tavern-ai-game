import os
import json
import random

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI API no disponible. Usando modo simulado local.")

# Intentar importar modelos
try:
    from src.ai.list_models import get_model_info
except ImportError:
    print("Módulo list_models no encontrado. Usando valores por defecto.")

    def get_model_info(model_name):
        return {"id": "gpt-3.5-turbo", "max_tokens": 100, "temperature": 0.7}


class ChatGPTClient:
    def __init__(
        self,
        api_key=None,
        config_path=None,
        difficulty="Normal",
        model_id="gpt-3.5-turbo",
    ):
        """
        Inicializa el cliente de ChatGPT

        Args:
            api_key: Clave API de OpenAI (opcional, por defecto usa variable de entorno)
            config_path: Ruta al archivo de configuración JSON (opcional)
            difficulty: Dificultad del juego (afecta la inteligencia de la IA)
            model_id: ID del modelo a utilizar
        """
        # Guardar dificultad y modelo para ajustar comportamiento
        self.difficulty = difficulty
        self.model_id = model_id

        # Si es un modelo local, usar configuración diferente
        self.is_local = model_id == "local"

        # Obtener API key desde parámetro o variable de entorno
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key and not self.is_local:
            print("ADVERTENCIA: No se encontró una API key para OpenAI")
            self.initialized = False
            return

        # Configuración por defecto
        self.config = {
            "model": model_id,
            "max_tokens": 100,
            "temperature": 0.7,
            "timeout": 30,
        }

        # Cargar configuración desde archivo JSON si existe
        if config_path is None:
            # Usar ruta por defecto si no se proporciona
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "openai_config.json",
            )

        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.config.update(json.load(f))
                print(f"Configuración cargada desde {config_path}")
        except Exception as e:
            print(f"No se pudo cargar la configuración desde {config_path}: {e}")
            print("Usando configuración por defecto")

        # Sobrescribir el modelo con el seleccionado
        self.config["model"] = model_id

        # Ajustar parámetros según dificultad
        self._adjust_parameters_for_difficulty()

        # Inicializar cliente de OpenAI o local según corresponda
        try:
            if self.is_local:
                # Aquí iría la inicialización de un modelo local si lo implementamos
                print("Usando modelo local")
                self.initialized = True
            else:
                self.client = OpenAI(api_key=self.api_key)
                self.context = []
                self.initialized = True

            print(
                f"Cliente ChatGPT inicializado con modelo: {self.config['model']} - Dificultad: {self.difficulty}"
            )
        except Exception as e:
            print(f"Error inicializando cliente OpenAI: {e}")
            self.initialized = False

    def is_initialized(self):
        """Verifica si el cliente está inicializado correctamente"""
        return getattr(self, "initialized", False)

    def _adjust_parameters_for_difficulty(self):
        """Ajusta los parámetros de la IA según la dificultad seleccionada"""
        if self.difficulty == "Easy":
            # En modo fácil, la IA es menos inteligente:
            # - Temperatura más alta para decisiones más aleatorias
            # - Menos tokens para respuestas más cortas
            self.config["temperature"] = 0.9
            self.config["max_tokens"] = 50
            print("Modo FÁCIL: IA con decisiones más aleatorias")
        elif self.difficulty == "Hard":
            # En modo difícil, la IA es más inteligente:
            # - Temperatura más baja para decisiones más óptimas
            # - Más tokens para respuestas más detalladas y estratégicas
            self.config["temperature"] = 0.3
            self.config["max_tokens"] = 150
            print("Modo DIFÍCIL: IA con decisiones más estratégicas")
        else:  # Normal
            # Configuración predeterminada para modo normal
            self.config["temperature"] = 0.7
            self.config["max_tokens"] = 100
            print("Modo NORMAL: IA con equilibrio de decisiones")

    def get_decision(self, game_state, available_actions):
        """
        Consulta a ChatGPT para obtener la mejor acción para un enemigo
        """
        if not self.is_initialized():
            import random

            return random.choice(available_actions)

        # Si es un modelo local, usar la implementación local
        if self.is_local:
            return self._get_local_decision(game_state, available_actions)

        # De lo contrario, usar la API normal
        prompt = self._create_prompt(game_state, available_actions)

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt_for_difficulty(),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                timeout=self.config["timeout"],
            )

            decision = response.choices[0].message.content.strip()
            return self._parse_decision(decision, available_actions)

        except Exception as e:
            print(f"Error al consultar a ChatGPT: {e}")
            # En caso de error, retornar una acción aleatoria
            import random

            return random.choice(available_actions)

    def _get_local_decision(self, game_state, available_actions):
        """Implementación simple para decisiones locales sin API"""
        import random

        # Simular que la IA piensa diferente según la dificultad
        if self.difficulty == "Easy":
            # En modo fácil, 50% de probabilidad de elegir acción aleatoria
            if random.random() < 0.5:
                return random.choice(available_actions)

            # Priorizar acciones menos dañinas
            for action in available_actions:
                if "curar" in action.lower() or "defender" in action.lower():
                    return action

        elif self.difficulty == "Hard":
            # En modo difícil, buscar el ataque más fuerte o curarse si tiene poca vida
            try:
                enemy_health_percent = (
                    game_state["enemies"][0]["health"]
                    / game_state["enemies"][0]["max_health"]
                )

                if enemy_health_percent < 0.3:
                    # Buscar acción de curación
                    for action in available_actions:
                        if "curar" in action.lower():
                            return action
            except (KeyError, IndexError, ZeroDivisionError):
                # Si hay error al acceder a datos, continuar con lógica normal
                pass

            # Buscar ataques fuertes
            for action in available_actions:
                if (
                    "fuego" in action.lower()
                    or "espada" in action.lower()
                    or "rayo" in action.lower()
                ):
                    return action

        # Comportamiento normal o fallback
        weighted_actions = []
        for action in available_actions:
            # Dar más peso a ataques y menos a acciones defensivas según la dificultad
            if "ataque" in action.lower() or "golpe" in action.lower():
                weight = 3 if self.difficulty == "Hard" else 2
            elif "defensa" in action.lower() or "proteger" in action.lower():
                weight = 1 if self.difficulty == "Hard" else 2
            else:
                weight = 1

            weighted_actions.extend([action] * weight)

        return (
            random.choice(weighted_actions)
            if weighted_actions
            else random.choice(available_actions)
        )

    def _get_system_prompt_for_difficulty(self):
        """Devuelve el prompt de sistema adaptado a la dificultad"""
        base_prompt = "Eres un asistente que ayuda a tomar decisiones estratégicas en un juego de rol por turnos."

        if self.difficulty == "Easy":
            return (
                base_prompt
                + " Tus decisiones deben ser simples y a veces subóptimas, como lo haría un enemigo poco inteligente o inexperto. Prioriza acciones básicas y predecibles. No necesitas ser muy estratégico."
            )
        elif self.difficulty == "Hard":
            return (
                base_prompt
                + " Tus decisiones deben ser altamente estratégicas y optimizadas para maximizar el daño y minimizar el riesgo. Analiza cuidadosamente la situación y elige la mejor acción posible como lo haría un enemigo experto. Prioriza destruir al jugador usando toda estrategia disponible."
            )
        else:  # Normal
            return (
                base_prompt
                + " Tu objetivo es proporcionar decisiones balanceadas basadas en el estado del juego. Usa un nivel moderado de estrategia, como lo haría un enemigo competente pero no experto."
            )

    def _create_prompt(self, game_state, available_actions):
        """Crea el prompt para ChatGPT basado en el estado del juego"""
        try:
            # Construir información sobre enemigos
            enemy_info = ""
            for i, enemy in enumerate(game_state.get("enemies", [])):
                enemy_info += f"  Enemigo {i+1}: {enemy['name']} - {enemy['health']}/{enemy['max_health']} HP"
                if enemy.get("status_effects"):
                    enemy_info += f" (Efectos: {', '.join(enemy['status_effects'])})"
                enemy_info += "\n"

            # Estado del jugador
            player_status = ""
            if game_state.get("player_status_effects"):
                player_status = (
                    f" (Efectos: {', '.join(game_state['player_status_effects'])})"
                )

            # Estado de defensa
            defense_status = (
                " [En defensa]" if game_state.get("player_defending") else ""
            )

            # Añadir información de dificultad al prompt
            difficulty_info = f"\nDificultad del juego: {self.difficulty}"
            if self.difficulty == "Easy":
                difficulty_info += " - Toma decisiones simples y a veces erróneas."
            elif self.difficulty == "Hard":
                difficulty_info += (
                    " - Toma decisiones altamente estratégicas y optimizadas."
                )

            prompt = f"""
Estado actual del juego:
- Jugador: {game_state.get('player_health', 0)}/{game_state.get('player_max_health', 100)} HP{player_status}{defense_status}
- Pociones disponibles: {game_state.get('potions', 0)}
- Enemigos:
{enemy_info}
{difficulty_info}

Acciones disponibles:
{', '.join(available_actions)}

Considerando el estado actual del juego, ¿cuál es la mejor acción para el enemigo?
Responde solo con el nombre de la acción.
            """
            return prompt
        except Exception as e:
            print(f"Error al crear prompt: {e}")
            return f"Elige la mejor acción entre: {', '.join(available_actions)}"

    def _parse_decision(self, decision, available_actions):
        """Procesa la respuesta de ChatGPT para extraer la acción"""
        # Buscar coincidencia exacta primero
        for action in available_actions:
            if action.lower() == decision.lower():
                return action

        # Si no hay coincidencia exacta, buscar acción contenida
        for action in available_actions:
            if action.lower() in decision.lower():
                return action

        # Si no se puede identificar una acción válida, elegir la primera disponible
        print(
            f"No se pudo identificar la acción '{decision}' entre las disponibles. Usando la primera acción."
        )
        return available_actions[0]

    def generate_boss_phrase(self, boss_name, player_health_pct, ally_health_pct=0):
        """
        Genera una frase amenazadora para el jefe usando IA

        Args:
            boss_name: Nombre del jefe
            player_health_pct: Porcentaje de salud del jugador (0-100)
            ally_health_pct: Porcentaje de salud del aliado (0-100)

        Returns:
            str: Frase amenazadora generada por la IA
        """
        if not self.is_initialized() or self.is_local:
            return self._get_fallback_boss_phrase()

        try:
            # Ajustar la intensidad del boss según la dificultad
            difficulty_modifier = ""
            if self.difficulty == "Easy":
                difficulty_modifier = (
                    "Tu amenaza debe ser un poco torpe y no muy aterradora."
                )
            elif self.difficulty == "Hard":
                difficulty_modifier = "Tu amenaza debe ser realmente aterradora y mostrar gran inteligencia."

            # Construir prompt para la IA
            prompt = f"""
            Eres {boss_name}, el jefe final malvado de un juego RPG. 
            Genera UNA SOLA frase corta y amenazadora (máximo 15 palabras) para intimidar al jugador y su aliado.
            El jugador tiene {player_health_pct}% de salud y su aliado {ally_health_pct}%.
            {difficulty_modifier}
            Solo devuelve la frase, sin comillas ni otros caracteres.
            """

            # Obtener respuesta de la IA
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un villano malvado en un juego RPG. Genera frases amenazadoras y aterradoras.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50,  # Menos tokens para frases cortas
                temperature=self.config[
                    "temperature"
                ],  # Usar temperatura según dificultad
                timeout=self.config["timeout"],
            )

            if response and response.choices and len(response.choices) > 0:
                phrase = response.choices[0].message.content.strip()
                # Limpiar comillas si las hay
                phrase = phrase.strip("\"'")
                return phrase

            return self._get_fallback_boss_phrase()

        except Exception as e:
            print(f"Error generando frase del jefe: {e}")
            return self._get_fallback_boss_phrase()

    def _get_fallback_boss_phrase(self):
        """Retorna una frase predefinida en caso de error"""
        import random

        phrases = [
            "¡Sus esfuerzos son inútiles contra mi poder!",
            "¡He destruido a guerreros más fuertes que ustedes!",
            "¡Arrodíllense ante su destrucción inminente!",
            "¡Sus almas alimentarán mi poder eterno!",
            "¡La oscuridad los consumirá a todos!",
            "¡Sus cuerpos decorarán mi salón de trofeos!",
            "¡Ningún héroe ha sobrevivido a mi ira!",
            "¡Contemplen el rostro de su perdición!",
            "¡Este será su último aliento!",
        ]
        return random.choice(phrases)

    def get_completion(self, prompt):
        """
        Obtiene una respuesta general de ChatGPT

        Args:
            prompt: Texto de la consulta

        Returns:
            str: Respuesta de la IA o None si hay error
        """
        if not self.is_initialized():
            return None

        if self.is_local:
            return self._get_local_response(prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente para un juego RPG. Tus respuestas deben ser breves, directas y adecuadas para un juego.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.get("max_tokens", 100),
                temperature=self.config.get("temperature", 0.7),
                timeout=self.config.get("timeout", 10),
            )

            if response and response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            return None

        except Exception as e:
            print(f"Error obteniendo respuesta de ChatGPT: {e}")
            return self._get_local_response(prompt)

    def _get_local_response(self, prompt):
        """Genera respuestas simuladas para modo local o errores"""
        import random

        # Respuestas genéricas según el contenido del prompt
        if (
            "amenaza" in prompt.lower()
            or "jefe" in prompt.lower()
            or "boss" in prompt.lower()
        ):
            return self._get_fallback_boss_phrase()

        elif "consejo" in prompt.lower() or "ayuda" in prompt.lower():
            tips = [
                "Cura cuando tu salud esté por debajo del 50%.",
                "Los ataques de fuego son efectivos contra enemigos de hielo.",
                "No olvides usar objetos de tu inventario.",
                "La defensa puede reducir significativamente el daño recibido.",
            ]
            return random.choice(tips)

        else:
            responses = [
                "Entendido. Procesando información del juego...",
                "Analizando situación táctica...",
                "Calculando mejor estrategia...",
                "Datos insuficientes para una predicción precisa.",
            ]
            return random.choice(responses)
