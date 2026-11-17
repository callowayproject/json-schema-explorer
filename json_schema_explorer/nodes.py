"""Build the node table (the Python/JS contract, see docs/design.md)."""

from typing import Any

from json_schema_explorer.resolve import Documents, Refs, ref_of

ROOT_ID = "#"

# Keywords shown in place under `constraints`.
CONSTRAINTS = (
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems",
    "minProperties", "maxProperties", "minContains", "maxContains", "dependentRequired",
    "contentEncoding", "contentMediaType",
)  # fmt: skip
# Child specs in display order: (keyword, shape, kind, are boolean subschemas navigable?).
# Generic rule: every keyword below without a dedicated kind is a child named after the keyword.
CHILD_SPECS = (
    ("properties", "map", "property", True),
    ("patternProperties", "map", "pattern", True),
    ("additionalProperties", "one", "additional", False),
    ("prefixItems", "list", "prefix", True),
    ("items", "one", "item", True),
    ("oneOf", "list", "oneOf", True),
    ("anyOf", "list", "anyOf", True),
    ("allOf", "list", "allOf", True),
    ("if", "one", "if", True),
    ("then", "one", "then", True),
    ("else", "one", "else", True),
    ("not", "one", "not", True),
    ("contains", "one", "contains", True),
    ("propertyNames", "one", "propertyNames", True),
    ("contentSchema", "one", "contentSchema", True),
    ("additionalItems", "one", "additionalItems", False),
    ("unevaluatedProperties", "one", "unevaluatedProperties", False),
    ("unevaluatedItems", "one", "unevaluatedItems", False),
    ("dependentSchemas", "map", "dependentSchemas", True),
    ("dependencies", "map", "dependencies", True),
    ("$defs", "map", "def", True),
    ("definitions", "map", "def", True),
)  # fmt: skip
PLAIN_LABEL_KINDS = ("property", "pattern", "def")


def _pointer(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _type_label(schema: dict) -> str:
    t = schema.get("type")
    if isinstance(t, str):
        return t
    if isinstance(t, list):
        names = [x for x in t if isinstance(x, str)]
        if names:
            return " | ".join(names)
    for key, label in (
        ("properties", "object"), ("items", "array"), ("prefixItems", "array"), ("enum", "enum"), ("const", "const"),
    ):  # fmt: skip
        if key in schema:
            return label
    return "any"


def _constraints(schema: dict) -> dict[str, Any]:
    found = {k: schema[k] for k in CONSTRAINTS if k in schema}
    deps = schema.get("dependencies")
    if isinstance(deps, dict) and "dependentRequired" not in found:  # draft-07 array form
        arrays = {k: v for k, v in deps.items() if isinstance(v, list)}
        if arrays:
            found["dependentRequired"] = arrays
    return found


def make_node(node_id: str, schema: Any) -> dict[str, Any]:
    """Return a node with every key of the agreed shape present."""
    label = {True: "any", False: "never"}.get(schema) if isinstance(schema, bool) else None
    if not isinstance(schema, dict):
        schema = {}
    str_or_none = lambda v: v if isinstance(v, str) else None  # ruff: ignore[lambda-assignment]
    required = schema.get("required")
    return {
        "id": node_id,
        "type": label or _type_label(schema),
        "title": str_or_none(schema.get("title")),
        "description": str_or_none(schema.get("description")),
        "required": [r for r in required if isinstance(r, str)] if isinstance(required, list) else [],
        "constraints": _constraints(schema),
        "enum": schema.get("enum") if isinstance(schema.get("enum"), list) else None,
        "const": schema.get("const"),
        "default": schema.get("default"),
        "examples": schema.get("examples") if isinstance(schema.get("examples"), list) else None,
        "format": str_or_none(schema.get("format")),
        "deprecated": schema.get("deprecated") is True,
        "readOnly": schema.get("readOnly") is True,
        "ref": None,
        "unresolved": None,
        "children": [],
    }


def _children(schema: dict) -> list[tuple[str, str, str, Any]]:
    """Return (pointer-suffix, label, kind, subschema) for every navigable child."""
    out: list[tuple[str, str, str, Any]] = []
    for kw, shape, kind, bools in CHILD_SPECS:
        value = schema.get(kw)

        def ok(v: Any, bools: bool = bools) -> bool:
            return isinstance(v, dict) or (bools and isinstance(v, bool))

        if shape == "one" and ok(value):
            out.append((kw, kw, kind, value))
        elif shape == "one" and kw == "items" and isinstance(value, list):  # draft-04 array form
            out.extend((f"items/{i}", str(i), "prefix", s) for i, s in enumerate(value) if ok(s))
        elif shape == "list" and isinstance(value, list):
            fmt = "{i}" if kw == "prefixItems" else kw + " {i}"
            out.extend((f"{kw}/{i}", fmt.format(i=i), kind, s) for i, s in enumerate(value) if ok(s))
        elif shape == "map" and isinstance(value, dict):
            fmt = "{k}" if kind in PLAIN_LABEL_KINDS else kw + "/{k}"
            out.extend((f"{kw}/{_pointer(k)}", fmt.format(k=k), kind, s) for k, s in value.items() if ok(s))
    return out


def build_node_table(root: Any, documents: Documents | None = None) -> dict[str, dict[str, Any]]:
    """Flatten `root` and every document its refs load into the node table.

    `$ref` nodes get `ref` set to the target's node ID; unresolvable ones get `unresolved` set to the ref string.
    Other documents' nodes are named `<document name>#/<pointer>` (see resolve.Documents).
    """
    table: dict[str, dict[str, Any]] = {}
    ids: dict[int, str] = {}  # id(subschema object) -> node ID, so any lookup result maps back to a node
    pending: list[tuple[str, str, Any]] = []
    refs = Refs(root, documents.retrieve if documents else None)

    def walk(node_id: str, schema: Any, scope: Any, entered: bool = False) -> None:
        node = table[node_id] = make_node(node_id, schema)
        if not isinstance(schema, dict):
            return
        ids[id(schema)] = node_id
        scope = scope if entered else refs.enter(scope, schema)
        if (ref := ref_of(schema)) is not None:
            pending.append((node_id, ref, scope))
        for suffix, label, kind, sub in _children(schema):
            target = f"{node_id}/{suffix}"
            node["children"].append({"label": label, "kind": kind, "target": target})
            walk(target, sub, scope)

    walk(ROOT_ID, root, refs.root, entered=True)
    looked: list[tuple[str, str, bool, Any]] = []
    walked: set[str] = set()
    while True:  # looking refs up loads documents; walk those, which may add refs, until stable
        while len(looked) < len(pending):
            node_id, ref, scope = pending[len(looked)]
            looked.append((node_id, ref, *refs.lookup(scope, ref)))
        new = [u for u in (documents.names if documents else {}) if u not in walked]
        if not new:
            break
        for uri in new:
            walked.add(uri)
            resolved = refs.root.lookup(uri)
            walk(documents.names[uri] + "#", resolved.contents, resolved.resolver, entered=True)
    for node_id, ref, found, target in looked:
        target_id = _target_id(table, ids, ref, found, target)
        table[node_id]["ref" if target_id else "unresolved"] = target_id or ref
    return table


def _target_id(table: dict, ids: dict[int, str], ref: str, found: bool, target: Any) -> str | None:
    if found and isinstance(target, dict):
        return ids.get(id(target))
    if found and isinstance(target, bool):  # booleans are singletons, so fall back to the pointer
        guess = "#" + ref.partition("#")[2]
        return guess if guess in table else None
    return None
