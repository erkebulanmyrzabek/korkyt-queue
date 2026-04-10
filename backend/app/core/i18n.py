from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import settings

LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"
SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "kk": "Қазақша",
    "en": "English",
}


@lru_cache
def load_catalog(language: str) -> dict[str, Any]:
    file_path = LOCALES_DIR / f"{language}.json"
    if not file_path.exists():
        file_path = LOCALES_DIR / f"{settings.default_language}.json"
    return json.loads(file_path.read_text(encoding="utf-8"))


def resolve_language(language: str | None) -> str:
    if language in SUPPORTED_LANGUAGES:
        return language
    return settings.default_language


def translate(key: str, language: str | None = None, **kwargs: Any) -> str:
    resolved_language = resolve_language(language)
    for candidate in (resolved_language, settings.default_language):
        current: Any = load_catalog(candidate)
        found = True
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                found = False
                break
            current = current[part]
        if found and isinstance(current, str):
            try:
                return current.format(**kwargs)
            except KeyError:
                return current
    return key

