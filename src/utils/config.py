def load_json(file_path):
    import json
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(file_path, data):
    import json
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def get_game_settings():
    return load_json('config/settings.json')

def get_openai_config():
    return load_json('config/openai_config.json')