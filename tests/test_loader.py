"""Tests for default output naming."""

from json_schema_explorer.loader import default_output_name


def test_default_output_name():
    """Names follow the design rules."""
    assert default_output_name("a/b/pet.json") == "pet.html"
    assert default_output_name("-") == "schema.html"
    assert default_output_name("https://x.org/s/pet.json") == "pet.html"
    assert default_output_name("https://x.org/") == "schema.html"
