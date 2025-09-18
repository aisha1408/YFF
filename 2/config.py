"""Config utilities for environment variables and app settings.

Loads API keys and configuration from environment variables (.env).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


# Auto-load .env if present
load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read an environment variable with an optional default."""
    return os.getenv(name, default)


# API keys removed - using mock data only


NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"

# Weather provider and caching
WEATHER_PROVIDER = get_env("WEATHER_PROVIDER", "openweather")
CACHE_FILE = DATA_DIR / "cache.json"
CACHE_TTL_MINUTES = int(get_env("CACHE_TTL_MINUTES", "30"))

SNAPSHOTS_FILE = DATA_DIR / "snapshots.json"
FEEDBACK_FILE = DATA_DIR / "feedback.json"
LABELS_FILE = DATA_DIR / "labels.json"
UIPREFS_FILE = DATA_DIR / "ui_prefs.json"
ACTIONS_FILE = DATA_DIR / "actions.json"


