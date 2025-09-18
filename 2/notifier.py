"""Notification utilities (SMS via Twilio and in-app JSON store)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from config import NOTIFICATIONS_FILE


def send_sms(phone: str, message: str) -> bool:
    """Mock SMS sender for demo purposes.

    Returns True/False for success.
    """
    print(f"[MOCK SMS] -> {phone}: {message}")
    return True


def send_inapp_notification(payload: Dict[str, Any]) -> Path:
    """Append a notification payload to a local JSON file and return its path."""
    NOTIFICATIONS_FILE.parent.mkdir(exist_ok=True, parents=True)
    data = []
    if NOTIFICATIONS_FILE.exists():
        try:
            data = json.loads(NOTIFICATIONS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = []
    payload = {"ts": int(time.time()), **payload}
    data.append(payload)
    NOTIFICATIONS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return NOTIFICATIONS_FILE


