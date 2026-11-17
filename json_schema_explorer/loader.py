"""Load the root schema from a path, an http(s) URL, or stdin."""

import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

TIMEOUT = 10


class LoadError(Exception):
    """A fatal, user-facing loading problem."""


def _is_url(source: str) -> bool:
    return urlparse(source).scheme in {"http", "https"}


def default_output_name(source: str) -> str:
    """Return the default output file name for `source`."""
    if source == "-":
        return "schema.html"
    path = urlparse(source).path if _is_url(source) else source
    stem = Path(path).stem if path.rstrip("/") == path else ""
    return f"{stem}.html" if stem else "schema.html"


def _read(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    if _is_url(source):
        try:
            with urlopen(source, timeout=TIMEOUT) as resp:  # ruff: ignore[suspicious-url-open-usage]
                return resp.read().decode("utf-8")
        except (URLError, OSError, ValueError) as exc:
            raise LoadError(f"cannot fetch {source}: {exc}") from exc
    try:
        return Path(source).read_text(encoding="utf-8")
    except OSError as exc:
        raise LoadError(f"cannot read {source}: {exc.strerror or exc}") from exc


def load_schema(source: str) -> dict | bool:
    """Load and sanity-check the root schema.

    Raises:
        LoadError: on unreadable input, invalid JSON, or a root that is not an object/boolean.
    """
    try:
        data: Any = json.loads(_read(source))
    except ValueError as exc:
        raise LoadError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(data, (dict, bool)):
        raise LoadError(f"root schema in {source} must be an object or boolean")
    return data
