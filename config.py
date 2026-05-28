import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "interval_minutes": 25,
    "message": "Time to take a break! Stand up and stretch.",
    "sound_path": "",
    "sound_volume": 0.8,
    "autostart": False,
}

CONFIG_PATH = Path.home() / ".take-a-break" / "config.json"


def load() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULT_CONFIG, **data}
    return DEFAULT_CONFIG.copy()


def save(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
