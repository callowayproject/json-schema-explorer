"""Resolve `$ref` targets with `referencing`.

The document registry seam: `Refs(root, retrieve)` takes a `retrieve(uri) -> Resource` callback,
so cross-file/remote documents (issue #7) plug in without touching the walker.
"""

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse
from urllib.request import urlopen

from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012, specification_with

Retrieve = Callable[[str], Resource]
TIMEOUT = 10


def fetch_url(url: str) -> str:
    """Fetch `url` as text (the network seam; tests replace it)."""
    with urlopen(url, timeout=TIMEOUT) as resp:  # ruff: ignore[suspicious-url-open-usage]
        return resp.read().decode("utf-8")


class Documents:
    """Loads other documents for `$ref`, enforcing the safety rules (design §Safety).

    `names` maps retrieved URI -> display name (node-ID prefix); `texts` maps name -> source text.
    """

    def __init__(self, root_dir: Path | None = None, ref_root: Path | None = None, allow_remote: bool = False) -> None:
        self.root_dir = root_dir.resolve() if root_dir else None
        self.allowed = (ref_root or root_dir).resolve() if (ref_root or root_dir) else None
        self.allow_remote = allow_remote
        self.names: dict[str, str] = {}
        self.texts: dict[str, str] = {}
        self.resources: dict[str, Resource] = {}

    def _load(self, uri: str) -> tuple[str, str]:
        """Return (name, text) for `uri`, or raise if it is not allowed or unreadable."""
        parsed = urlparse(uri)
        if parsed.scheme in {"http", "https"}:
            if not self.allow_remote:
                raise PermissionError(f"remote refs need --allow-remote: {uri}")
            return uri, fetch_url(uri)
        if parsed.scheme not in {"", "file"} or self.root_dir is None or self.allowed is None:
            raise PermissionError(f"not following {uri}")
        raw = unquote(parsed.path)
        path = (Path(raw) if parsed.scheme == "file" else self.root_dir / raw).resolve()
        if not path.is_relative_to(self.allowed):
            raise PermissionError(f"{uri} escapes {self.allowed}")
        return os.path.relpath(path, self.root_dir).replace(os.sep, "/"), path.read_text(encoding="utf-8")

    def retrieve(self, uri: str) -> Resource:
        """`Registry` retrieve callback: any failure surfaces as an unresolved ref."""
        if uri not in self.resources:  # cached: node IDs are matched by object identity
            name, text = self._load(uri)
            self.resources[uri] = Resource.from_contents(json.loads(text), default_specification=DRAFT202012)
            self.texts[name] = text
            self.names[uri] = name
        return self.resources[uri]


# $dynamicRef / $recursiveRef resolve statically, exactly like $ref.
REF_KEYWORDS = ("$ref", "$dynamicRef", "$recursiveRef")


def ref_of(schema: dict) -> str | None:
    """Return the first reference keyword value of `schema`, if it is a string."""
    for kw in REF_KEYWORDS:
        if isinstance(schema.get(kw), str):
            return schema[kw]
    return None


class Refs:
    """Scoped reference lookup for one root schema (no `$schema` means 2020-12)."""

    def __init__(self, root: Any, retrieve: Retrieve | None = None) -> None:
        resource = Resource.from_contents(root, default_specification=DRAFT202012)
        dialect = root.get("$schema") if isinstance(root, dict) else None
        self.spec = specification_with(dialect if isinstance(dialect, str) else "", default=DRAFT202012)
        registry = Registry(retrieve=retrieve) if retrieve else Registry()
        self.root = registry.resolver_with_root(resource)

    def enter(self, scope: Any, schema: Any) -> Any:
        """Return `scope` narrowed to `schema`, following `$id` / `id` base-URI changes."""
        if not isinstance(schema, dict):
            return scope
        return scope.in_subresource(Resource.from_contents(schema, default_specification=self.spec))

    @staticmethod
    def lookup(scope: Any, ref: str) -> tuple[bool, Any]:
        """Return (found, target schema) for `ref` seen from `scope`."""
        try:
            return True, scope.lookup(ref).contents
        except Unresolvable:
            return False, None
