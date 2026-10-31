"""Visually reviewed image descriptions, with context for future uploads."""

from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def _descriptions():
    path = Path(__file__).with_name("image_alt.json")
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def image_alt(filename, fallback=""):
    """Look up a path relative to static/images; accept slideshow leading slashes."""
    return _descriptions().get(str(filename or "").lstrip("/"), fallback)
