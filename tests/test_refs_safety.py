"""Cross-file refs and the safety rules (design §Node IDs, §Safety). No network: fetch is mocked."""

import json

import pytest
from click.testing import CliRunner

from json_schema_explorer.cli import cli
from tests.test_cli import _table

ROOT = {"type": "object", "properties": {"id": {"$ref": "common/types.json#/$defs/Id"}}}
TYPES = {"$defs": {"Id": {"type": "string", "title": "Id"}}}
REMOTE = "https://example.com/types.json"


def _build(args, stdin=None):
    return CliRunner().invoke(cli, ["build", *args], input=stdin)


@pytest.fixture
def proj(tmp_path):
    """Behaviour check."""
    (tmp_path / "common").mkdir()
    (tmp_path / "common/types.json").write_text(json.dumps(TYPES))
    (tmp_path / "root.json").write_text(json.dumps(ROOT))
    return tmp_path


def test_cross_file_ref_gets_relative_ids_and_source_section(proj):
    """Behaviour check."""
    r = _build([str(proj / "root.json"), "-o", str(proj / "o.html")])
    assert r.exit_code == 0
    html = (proj / "o.html").read_text()
    t = _table(html)
    assert t["#/properties/id"]["ref"] == "common/types.json#/$defs/Id"
    assert t["common/types.json#/$defs/Id"]["title"] == "Id"
    assert "<h2>common/types.json</h2>" in html


def test_escape_blocked_then_ref_root_allows(proj):
    """Behaviour check."""
    sub = proj / "sub"
    sub.mkdir()
    (sub / "root.json").write_text(json.dumps({"$ref": "../common/types.json#/$defs/Id"}))
    out = str(proj / "o.html")
    assert _build([str(sub / "root.json"), "-o", out]).exit_code == 0
    assert _table((proj / "o.html").read_text())["#"]["unresolved"] == "../common/types.json#/$defs/Id"
    _build([str(sub / "root.json"), "-o", out, "--ref-root", str(proj)])
    assert _table((proj / "o.html").read_text())["#"]["ref"] == "../common/types.json#/$defs/Id"


def test_stdin_root_does_not_follow_local_refs(proj, monkeypatch):
    """Behaviour check."""
    monkeypatch.chdir(proj)
    r = _build(["-", "-o", str(proj / "o.html")], stdin=json.dumps(ROOT))
    assert r.exit_code == 0
    assert _table((proj / "o.html").read_text())["#/properties/id"]["unresolved"]


def test_remote_blocked_without_flag_and_fetched_with_it(proj, monkeypatch):
    """Behaviour check."""
    (proj / "r.json").write_text(json.dumps({"$ref": REMOTE + "#/$defs/Id"}))
    calls = []
    monkeypatch.setattr("json_schema_explorer.resolve.fetch_url", lambda u: calls.append(u) or json.dumps(TYPES))
    out = str(proj / "o.html")
    _build([str(proj / "r.json"), "-o", out])
    assert calls == []
    assert _table((proj / "o.html").read_text())["#"]["unresolved"]
    _build([str(proj / "r.json"), "-o", out, "--allow-remote"])
    t = _table((proj / "o.html").read_text())
    assert t["#"]["ref"] == REMOTE + "#/$defs/Id"
    assert REMOTE + "#/$defs/Id" in t


def test_remote_failure_is_unresolved(proj, monkeypatch):
    """Behaviour check."""
    (proj / "r.json").write_text(json.dumps({"$ref": REMOTE}))

    def boom(url):
        raise OSError("down")

    monkeypatch.setattr("json_schema_explorer.resolve.fetch_url", boom)
    r = _build([str(proj / "r.json"), "-o", str(proj / "o.html"), "--allow-remote"])
    assert r.exit_code == 0
    assert _table((proj / "o.html").read_text())["#"]["unresolved"] == REMOTE
