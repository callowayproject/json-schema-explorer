"""Same-document $ref resolution tests."""

from referencing import Resource
from referencing.jsonschema import DRAFT202012

from json_schema_explorer.nodes import build_node_table


def test_ref_to_defs_links_not_inlines():
    """A $ref sets `ref` to the target node ID and adds no children."""
    t = build_node_table({"$defs": {"Id": {"type": "string"}}, "properties": {"a": {"$ref": "#/$defs/Id"}}})
    node = t["#/properties/a"]
    assert (node["ref"], node["unresolved"], node["children"]) == ("#/$defs/Id", None, [])


def test_recursive_schema_terminates():
    """A self-reference resolves to the root node."""
    t = build_node_table({"properties": {"next": {"$ref": "#"}}})
    assert t["#/properties/next"]["ref"] == "#"


def test_draft04_definitions():
    """Draft-04 `definitions` refs resolve."""
    root = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "definitions": {"x": {}},
        "items": {"$ref": "#/definitions/x"},
    }
    assert build_node_table(root)["#/items"]["ref"] == "#/definitions/x"


def test_anchor_and_id():
    """`$anchor` refs resolve, bare and through the absolute `$id`."""
    root = {
        "$id": "http://e.com/s",
        "$defs": {"a": {"$anchor": "foo", "type": "string"}},
        "oneOf": [{"$ref": "#foo"}, {"$ref": "http://e.com/s#foo"}],
    }
    t = build_node_table(root)
    assert [t[f"#/oneOf/{i}"]["ref"] for i in (0, 1)] == ["#/$defs/a"] * 2


def test_embedded_id_relative_ref():
    """A subschema `$id` changes the base for refs inside it."""
    root = {"$defs": {"b": {"$id": "http://e.com/b", "$defs": {"c": {}}, "items": {"$ref": "#/$defs/c"}}}}
    assert build_node_table(root)["#/$defs/b/items"]["ref"] == "#/$defs/b/$defs/c"


def test_dynamic_and_recursive_refs_resolve_statically():
    """$dynamicRef and $recursiveRef resolve like $ref."""
    root = {"$dynamicAnchor": "n", "properties": {"a": {"$dynamicRef": "#n"}, "b": {"$recursiveRef": "#"}}}
    t = build_node_table(root)
    assert (t["#/properties/a"]["ref"], t["#/properties/b"]["ref"]) == ("#", "#")


def test_ref_to_boolean_subschema():
    """A ref to a boolean subschema still finds its node."""
    t = build_node_table({"$defs": {"t": True}, "items": {"$ref": "#/$defs/t"}})
    assert t["#/items"]["ref"] == "#/$defs/t"


def test_unresolved():
    """Unresolvable refs set `unresolved`; non-string refs are ignored."""
    t = build_node_table({"properties": {"a": {"$ref": "#/$defs/nope"}, "b": {"$ref": 5}}})
    assert (t["#/properties/a"]["ref"], t["#/properties/a"]["unresolved"]) == (None, "#/$defs/nope")
    assert t["#/properties/b"]["unresolved"] is None


def test_retrieve_seam_is_used():
    """Unknown documents go through the `retrieve` callback."""
    seen = []

    def retrieve(uri):
        seen.append(uri)
        return Resource.from_contents({"type": "string"}, default_specification=DRAFT202012)

    t = build_node_table({"items": {"$ref": "other.json"}}, retrieve=retrieve)
    assert seen == ["other.json"]
    assert t["#/items"]["unresolved"] == "other.json"  # target not in this table until #7
