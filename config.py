import json
import copy
from pathlib import Path

DEFAULT_ALERTS = [
    {
        "id": "default",
        "name": "Take a Break",
        "interval_minutes": 25,
        "message": "Time to take a break! Stand up and stretch.",
        "sound_path": "",
        "sound_volume": 0.8,
        "enabled": True,
    }
]

CONFIG_PATH = Path.home() / ".take-a-break" / "config.json"


def load() -> list:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "alerts" in data:
            return data["alerts"]
        if isinstance(data, dict):
            # Migrate old single-alert format
            return [{
                "id": "default",
                "name": "Take a Break",
                "interval_minutes": data.get("interval_minutes", 25),
                "message": data.get("message", DEFAULT_ALERTS[0]["message"]),
                "sound_path": data.get("sound_path", ""),
                "sound_volume": data.get("sound_volume", 0.8),
                "enabled": True,
            }]
    return copy.deepcopy(DEFAULT_ALERTS)


def save(alerts: list) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"alerts": alerts}, f, indent=2)
