"""Resolve `$ref` targets with `referencing`.

The document registry seam: `Refs(root, retrieve)` takes a `retrieve(uri) -> Resource` callback,
so cross-file/remote documents (issue #7) plug in without touching the walker.
"""

from collections.abc import Callable
from typing import Any

from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012, specification_with

Retrieve = Callable[[str], Resource]

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
