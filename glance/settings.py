import json
import os

CONFIG_PATH = "config.json"

def load_settings():
    """Load saved settings from config.json."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"api_endpoint": "", "api_key": "", "model_provider": "openai"}

def save_settings(data):
    """Save settings to config.json."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


