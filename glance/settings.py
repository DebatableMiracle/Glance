import json
import os

CONFIG_PATH = "config.json"

def load_settings():
    """Load saved settings from config.json."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"api_endpoint": "", "api_key": "", "transparency": 85}

def save_settings(data):
    """Save settings to config.json."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_transparency():
    """Return saved transparency setting (default 85%)."""
    settings = load_settings()
    return settings.get("transparency", 85) / 100

def set_transparency(value):
    """Update transparency value in config.json."""
    settings = load_settings()
    settings["transparency"] = value
    save_settings(settings)
