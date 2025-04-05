"""
Lista de modelos de IA disponibles para el juego
"""

# Modelos disponibles con sus configuraciones
AVAILABLE_MODELS = {
    "GPT-3.5": {
        "id": "gpt-3.5-turbo",
        "description": "Modelo rápido y eficiente con buen equilibrio",
        "max_tokens": 100,
        "temperature": 0.7,
    },
    "GPT-4": {
        "id": "gpt-4",
        "description": "Modelo avanzado con mayor capacidad estratégica",
        "max_tokens": 150,
        "temperature": 0.5,
    },
    "Local": {
        "id": "local",
        "description": "Modo sin conexión (simulación básica)",
        "max_tokens": 80,
        "temperature": 0.8,
    },
}

# Nombres simplificados para el menú
MODEL_NAMES = list(AVAILABLE_MODELS.keys())  # ["GPT-3.5", "GPT-4", "Local"]


def get_model_info(model_name):
    """Obtiene la información completa de un modelo por su nombre de menú"""
    if model_name in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[model_name]
    return AVAILABLE_MODELS["GPT-3.5"]  # Modelo por defecto


def get_model_id(model_name):
    """Obtiene el ID del modelo para usar con la API"""
    model_info = get_model_info(model_name)
    return model_info["id"]


def get_model_index(model_id):
    """Obtiene el índice de un modelo por su ID"""
    for i, name in enumerate(MODEL_NAMES):
        if AVAILABLE_MODELS[name]["id"] == model_id:
            return i
    return 0  # Índice del modelo por defecto
