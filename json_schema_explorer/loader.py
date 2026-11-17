"""Load the root schema from a path, an http(s) URL, or stdin."""

import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

TIMEOUT = 10
MAX_BYTES = 10 * 1024 * 1024


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


def display_name(source: str) -> str:
    """Return the human name of `source`: file basename, the URL, or "stdin"."""
    if source == "-":
        return "stdin"
    return source if _is_url(source) else Path(source).name


def fetch_url(url: str) -> str:
    """Fetch `url` as text, refusing bodies over MAX_BYTES (the network seam; tests replace it)."""
    with urlopen(url, timeout=TIMEOUT) as resp:  # ruff: ignore[suspicious-url-open-usage]
        body = resp.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise OSError(f"response larger than {MAX_BYTES} bytes")
    return body.decode("utf-8")


def read_source(source: str) -> str:
    """Return the raw text of `source`."""
    if source == "-":
        return sys.stdin.read()
    if _is_url(source):
        try:
            return fetch_url(source)
        except (URLError, OSError, ValueError) as exc:
            raise LoadError(f"cannot fetch {source}: {exc}") from exc
    try:
        return Path(source).read_text(encoding="utf-8")
    except OSError as exc:
        raise LoadError(f"cannot read {source}: {exc.strerror or exc}") from exc


def load_schema(source: str) -> dict | bool:
    """Read and parse the root schema (see `parse_schema`)."""
    return parse_schema(read_source(source), source)


def parse_schema(text: str, source: str) -> dict | bool:
    """Parse and sanity-check the root schema.

    Raises:
        LoadError: on invalid JSON, or a root that is not an object/boolean.
    """
    try:
        data: Any = json.loads(text)
    except (ValueError, RecursionError) as exc:
        raise LoadError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(data, (dict, bool)):
        raise LoadError(f"root schema in {source} must be an object or boolean")
    return data
