"""Build the node table (the Python/JS contract, see docs/design.md)."""

from typing import Any

ROOT_ID = "#"


def _type_label(schema: dict) -> str:
    t = schema.get("type")
    if isinstance(t, str):
        return t
    if isinstance(t, list) and t:
        return " | ".join(str(x) for x in t)
    for key, label in (("properties", "object"), ("items", "array"), ("enum", "enum"), ("const", "const")):
        if key in schema:
            return label
    return "any"


def make_node(node_id: str, schema: dict | bool) -> dict[str, Any]:
    """Return a node with every key of the agreed shape present."""
    if not isinstance(schema, dict):
        schema = {} if schema else {"not": {}}
    str_or_none = lambda v: v if isinstance(v, str) else None  # ruff: ignore[lambda-assignment]
    required = schema.get("required")
    return {
        "id": node_id,
        "type": "never" if "not" in schema and schema["not"] == {} else _type_label(schema),
        "title": str_or_none(schema.get("title")),
        "description": str_or_none(schema.get("description")),
        "required": [r for r in required if isinstance(r, str)] if isinstance(required, list) else [],
        "constraints": {},
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


def build_node_table(root: dict | bool) -> dict[str, dict[str, Any]]:
    """Build the table for the root and its flat `properties`."""
    table = {ROOT_ID: make_node(ROOT_ID, root)}
    props = root.get("properties") if isinstance(root, dict) else None
    if isinstance(props, dict):
        for name, sub in props.items():
            child_id = f"#/properties/{name.replace('~', '~0').replace('/', '~1')}"
            table[child_id] = make_node(child_id, sub)
            table[ROOT_ID]["children"].append({"label": name, "kind": "property", "target": child_id})
    return table
