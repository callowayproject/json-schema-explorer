"""Node table tests."""

import pytest

from json_schema_explorer.nodes import build_node_table

KEYS = {
    "id",
    "type",
    "title",
    "description",
    "required",
    "constraints",
    "enum",
    "default",
    "examples",
    "format",
    "deprecated",
    "readOnly",
    "ref",
    "unresolved",
    "children",
}


def kids(table, node_id="#"):
    """Return (kind, label, target) per child."""
    return [(c["kind"], c["label"], c["target"]) for c in table[node_id]["children"]]


def test_one_of_children():
    """Check test_one_of_children."""
    t = build_node_table({"oneOf": [{"type": "string"}, {"type": "null"}]})
    assert kids(t) == [("oneOf", "oneOf 0", "#/oneOf/0"), ("oneOf", "oneOf 1", "#/oneOf/1")]
    assert t["#/oneOf/1"]["type"] == "null"


def test_all_of_kept_as_parts_not_merged():
    """Check test_all_of_kept_as_parts_not_merged."""
    t = build_node_table({"allOf": [{"properties": {"a": {}}}, {"required": ["a"]}]})
    assert [k for k, _, _ in kids(t)] == ["allOf", "allOf"]
    assert t["#"]["required"] == []
    assert t["#/allOf/1"]["required"] == ["a"]
    assert t["#/allOf/0"]["type"] == "object"


def test_if_then_else_not():
    """Check test_if_then_else_not."""
    t = build_node_table({"if": {}, "then": {"type": "string"}, "else": {"type": "integer"}, "not": {"const": 1}})
    assert kids(t) == [
        ("if", "if", "#/if"),
        ("then", "then", "#/then"),
        ("else", "else", "#/else"),
        ("not", "not", "#/not"),
    ]


def test_properties_pattern_additional_items():
    """Check test_properties_pattern_additional_items."""
    t = build_node_table(
        {
            "properties": {"a/b": {}},
            "patternProperties": {"^x": {"type": "string"}},
            "additionalProperties": {"type": "integer"},
            "items": {"type": "number"},
        }
    )
    assert kids(t) == [
        ("property", "a/b", "#/properties/a~1b"),
        ("pattern", "^x", "#/patternProperties/^x"),
        ("additional", "additionalProperties", "#/additionalProperties"),
        ("item", "items", "#/items"),
    ]


def test_additional_properties_bool_is_not_a_child():
    """Check test_additional_properties_bool_is_not_a_child."""
    assert build_node_table({"additionalProperties": False})["#"]["children"] == []


def test_prefix_items_and_draft04_array_items():
    """Check test_prefix_items_and_draft04_array_items."""
    t = build_node_table({"prefixItems": [{}, {}], "items": [{"type": "string"}]})
    assert kids(t) == [
        ("prefix", "0", "#/prefixItems/0"),
        ("prefix", "1", "#/prefixItems/1"),
        ("prefix", "0", "#/items/0"),
    ]
    assert t["#"]["type"] == "array"


def test_defs_and_definitions():
    """Check test_defs_and_definitions."""
    t = build_node_table({"$defs": {"A": {}}, "definitions": {"B": {"type": "string"}}})
    assert kids(t) == [("def", "A", "#/$defs/A"), ("def", "B", "#/definitions/B")]


def test_generic_keywords_become_children():
    """Check test_generic_keywords_become_children."""
    t = build_node_table(
        {
            "contains": {"type": "string"},
            "propertyNames": {"pattern": "^a"},
            "dependentSchemas": {"a": {"required": ["b"]}},
            "unevaluatedProperties": {"type": "string"},
        }
    )
    assert kids(t) == [
        ("contains", "contains", "#/contains"),
        ("propertyNames", "propertyNames", "#/propertyNames"),
        ("unevaluatedProperties", "unevaluatedProperties", "#/unevaluatedProperties"),
        ("dependentSchemas", "dependentSchemas/a", "#/dependentSchemas/a"),
    ]


def test_boolean_schemas():
    """Check test_boolean_schemas."""
    t = build_node_table({"properties": {"y": True, "n": False}})
    assert t["#/properties/y"]["type"] == "any"
    assert t["#/properties/n"]["type"] == "never"
    assert build_node_table(False)["#"]["type"] == "never"


def test_type_lists_and_inference():
    """Check test_type_lists_and_inference."""

    def ty(s):
        return build_node_table(s)["#"]["type"]

    assert ty({"type": ["string", "null"]}) == "string | null"
    assert ty({"properties": {}}) == "object"
    assert ty({"items": {}}) == "array"
    assert ty({"enum": [1]}) == "enum"
    assert ty({"const": None}) == "const"
    assert ty({}) == "any"


def test_in_place_facts():
    """Check test_in_place_facts."""
    n = build_node_table(
        {
            "type": "object",
            "required": ["a"],
            "minProperties": 1,
            "maxLength": 3,
            "dependentRequired": {"a": ["b"]},
            "enum": [1],
            "const": 1,
            "format": "email",
            "default": 2,
            "examples": [3],
            "deprecated": True,
            "readOnly": True,
            "title": "T",
            "description": "D",
        }
    )["#"]
    assert set(n) == KEYS | {"const"}
    assert n["required"] == ["a"]
    assert n["constraints"] == {"minProperties": 1, "maxLength": 3, "dependentRequired": {"a": ["b"]}}
    assert (n["enum"], n["const"], n["format"], n["default"], n["examples"]) == ([1], 1, "email", 2, [3])
    assert n["deprecated"] is True and n["readOnly"] is True
    assert (n["title"], n["description"]) == ("T", "D")


@pytest.mark.parametrize(
    "schema",
    [
        {"properties": None},
        {"properties": {"a": 3, "b": None}},
        {"required": "x"},
        {"required": [1, None]},
        {"items": 3},
        {"items": [3, None]},
        {"prefixItems": "x"},
        {"oneOf": None},
        {"oneOf": [1, "x"]},
        {"allOf": {"a": 1}},
        {"patternProperties": []},
        {"additionalProperties": 3},
        {"$defs": [1]},
        {"definitions": "x"},
        {"dependentSchemas": 5},
        {"contains": "x"},
        {"if": 3},
        {"type": 5},
        {"type": [1, None]},
        {"enum": "x"},
        {"examples": 4},
        {"title": 1, "description": []},
        {"dependentRequired": None},
    ],
)
def test_malformed_never_raises(schema):
    """Check test_malformed_never_raises."""
    t = build_node_table(schema)
    assert all(set(n) == KEYS for n in t.values())
    assert all(c["target"] in t for n in t.values() for c in n["children"])
