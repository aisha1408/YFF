"""Simple translation utility using googletrans if available, else mock."""

from __future__ import annotations

from typing import Optional
import json
from pathlib import Path
from config import UIPREFS_FILE


def translate(text: str, target_language: str) -> str:
    """Translate text to target_language (e.g., 'hi' for Hindi, 'kn' for Kannada).

    Falls back to a mock translation suffix if googletrans isn't available.
    """
    try:
        from googletrans import Translator  # type: ignore

        translator = Translator()
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception:
        suffix = {
            "hi": "[HI]",
            "kn": "[KN]",
        }.get(target_language.lower(), f"[{target_language.upper()}]")
        return f"{text} {suffix}"


def get_ui_language(default: str = "en") -> str:
    try:
        if UIPREFS_FILE.exists():
            obj = json.loads(UIPREFS_FILE.read_text(encoding="utf-8"))
            return obj.get("lang", default)
    except Exception:
        pass
    return default


def set_ui_language(lang: str) -> None:
    try:
        UIPREFS_FILE.parent.mkdir(exist_ok=True, parents=True)
        obj = {"lang": lang}
        UIPREFS_FILE.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    except Exception:
        pass


