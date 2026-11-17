"""Smoke and error-path tests for the build command."""

import json
import pathlib
from html.parser import HTMLParser

from click.testing import CliRunner

from json_schema_explorer.cli import cli

SCHEMA = {
    "title": "Pet",
    "type": "object",
    "required": ["name"],
    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
}
NODE_KEYS = {
    "id", "type", "title", "description", "required", "constraints", "enum", "const", "default",
    "examples", "format", "deprecated", "readOnly", "ref", "unresolved", "children",
}  # fmt: skip


class _Scripts(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.found: dict[str, str] = {}
        self._id = None

    def handle_starttag(self, tag, attrs):
        self._id = dict(attrs).get("id") if tag == "script" else None

    def handle_data(self, data):
        if self._id:
            self.found[self._id] = data

    def handle_endtag(self, tag):
        self._id = None


def _table(html: str) -> dict:
    p = _Scripts()
    p.feed(html)
    return json.loads(p.found["node-table"])


def test_build_embeds_node_table(tmp_path, monkeypatch):
    """Behaviour check."""
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "pet.json"
    src.write_text(json.dumps(SCHEMA))
    r = CliRunner().invoke(cli, ["build", str(src)])
    assert r.exit_code == 0, r.output
    table = _table((tmp_path / "pet.html").read_text())
    assert set(table) == {"#", "#/properties/name", "#/properties/age"}
    assert [c["label"] for c in table["#"]["children"]] == ["name", "age"]
    assert table["#"]["required"] == ["name"]
    assert all(set(n) == NODE_KEYS for n in table.values())


def test_output_option_and_stdin_default(tmp_path, monkeypatch):
    """Behaviour check."""
    out = tmp_path / "x.html"
    r = CliRunner().invoke(cli, ["build", "-", "-o", str(out)], input=json.dumps(SCHEMA))
    assert r.exit_code == 0
    assert out.exists()
    monkeypatch.chdir(tmp_path)
    r = CliRunner().invoke(cli, ["build", "-"], input="true")
    assert r.exit_code == 0
    assert pathlib.Path("schema.html").exists()


def test_description_is_escaped(tmp_path, monkeypatch):
    """Behaviour check."""
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "s.json"
    src.write_text(json.dumps({"title": "<i>t</i>", "description": "</script><b>x"}))
    CliRunner().invoke(cli, ["build", str(src)])
    html = (tmp_path / "s.html").read_text()
    assert "</script><b>x" not in html
    assert "<i>t</i>" not in html


def test_fatal_errors(tmp_path):
    """Behaviour check."""
    bad = tmp_path / "bad.json"
    bad.write_text("{nope")
    arr = tmp_path / "arr.json"
    arr.write_text("[]")
    for arg in (str(tmp_path / "missing.json"), str(bad), str(arr), "http://127.0.0.1:1/x.json"):
        r = CliRunner().invoke(cli, ["build", arg])
        assert r.exit_code == 1, arg
        assert "Traceback" not in r.output
        assert len(r.output.strip().splitlines()) == 1, arg
        assert r.output.startswith("error: ")


def test_page_is_self_contained(tmp_path, monkeypatch):
    """No external requests: nothing but inline script/style, so it works from file://."""
    monkeypatch.chdir(tmp_path)
    src = tmp_path / "s.json"
    src.write_text(json.dumps(SCHEMA))
    CliRunner().invoke(cli, ["build", str(src)])
    html = (tmp_path / "s.html").read_text()
    for needle in ('src="', 'href="', "url(", "@import", "fetch(", "XMLHttpRequest"):
        assert needle not in html, needle
