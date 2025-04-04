import os
import json
from openai import OpenAI


class ChatGPTClient:
    def __init__(self, api_key=None, config_path=None):
        """
        Inicializa el cliente de ChatGPT

        Args:
            api_key: Clave API de OpenAI (opcional, por defecto usa variable de entorno)
            config_path: Ruta al archivo de configuración JSON (opcional)
        """
        # Obtener API key desde parámetro o variable de entorno
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró una API key para OpenAI")

        # Configuración por defecto
        self.config = {
            "model": "gpt-3.5-turbo",
            "max_tokens": 100,
            "temperature": 0.7,
            "timeout": 30,
        }

        # Cargar configuración desde archivo JSON si existe
        if config_path is None:
            # Usar ruta por defecto si no se proporciona
            config_path = os.path.join("config", "openai_config.json")

        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.config.update(json.load(f))
                print(f"Configuración cargada desde {config_path}")
        except Exception as e:
            print(f"No se pudo cargar la configuración desde {config_path}: {e}")
            print("Usando configuración por defecto")

        # Inicializar cliente de OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self.context = []
        print(f"Cliente ChatGPT inicializado con modelo: {self.config['model']}")

    def get_decision(self, game_state, available_actions):
        """
        Consulta a ChatGPT para obtener la mejor acción para un enemigo

        Args:
            game_state: Estado actual del juego (salud del jugador, enemigos, etc.)
            available_actions: Lista de acciones disponibles

        Returns:
            str: La acción recomendada
        """
        prompt = self._create_prompt(game_state, available_actions)

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente que ayuda a tomar decisiones estratégicas en un juego de rol por turnos. Tu objetivo es proporcionar la mejor acción para un enemigo basándote en el estado del juego.",
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

    def _create_prompt(self, game_state, available_actions):
        """Crea el prompt para ChatGPT basado en el estado del juego"""
        # Construir información sobre enemigos
        enemy_info = ""
        for i, enemy in enumerate(game_state["enemies"]):
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
        defense_status = " [En defensa]" if game_state.get("player_defending") else ""

        prompt = f"""
Estado actual del juego:
- Jugador: {game_state['player_health']}/{game_state['player_max_health']} HP{player_status}{defense_status}
- Pociones disponibles: {game_state.get('potions', 0)}
- Enemigos:
{enemy_info}

Acciones disponibles:
{', '.join(available_actions)}

Considerando el estado actual del juego, ¿cuál es la mejor acción para el enemigo?
Responde solo con el nombre de la acción.
        """
        return prompt

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
