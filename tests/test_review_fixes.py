"""Regression tests for the issue #2 code-review fixes."""

import json

import pytest
from click.testing import CliRunner

from json_schema_explorer import loader
from json_schema_explorer.cli import cli
from json_schema_explorer.nodes import build_node_table
from json_schema_explorer.resolve import Documents
from tests.test_cli import _table

ROOT_URL = "https://example.com/schemas/root.json"
ROOT = {"properties": {"a": {"$ref": "types.json#/$defs/A"}}}
TYPES = {"$defs": {"A": {"type": "string"}}}


def test_const_present_only_when_schema_has_it():
    """Absent key and null are distinguished by presence."""
    t = build_node_table({"properties": {"n": {"const": None}, "z": {"const": 0}, "x": {}}})
    assert t["#/properties/n"]["const"] is None
    assert "const" in t["#/properties/n"]
    assert t["#/properties/z"]["const"] == 0
    assert "const" not in t["#/properties/x"]


def test_root_source_is_original_text_and_named_by_basename(tmp_path):
    """Source view keeps the loaded text verbatim and heads it with the file name."""
    f = tmp_path / "s.json"
    f.write_text('{"title":   "T",\n"type":"object"}')
    out = tmp_path / "o.html"
    CliRunner().invoke(cli, ["build", str(f), "-o", str(out)])
    html = out.read_text()
    assert "<h2>s.json</h2>" in html
    assert '<span class="w">   </span>' in html.partition('id="source"')[2]  # odd spacing survives: not re-dumped
    assert "<span>T</span>" in html


def test_header_fallback_and_stdin_name(tmp_path):
    """No title: header is the file basename; stdin is named "stdin"."""
    f = tmp_path / "plain.json"
    f.write_text("{}")
    out = tmp_path / "o.html"
    CliRunner().invoke(cli, ["build", str(f), "-o", str(out)])
    assert "<span>plain.json</span>" in out.read_text()
    CliRunner().invoke(cli, ["build", "-", "-o", str(out)], input="{}")
    html = out.read_text()
    assert "<span>stdin</span>" in html
    assert "<h2>stdin</h2>" in html


def _urls(monkeypatch, calls):
    def fake(url):
        calls.append(url)
        return json.dumps(ROOT if url == ROOT_URL else TYPES)

    monkeypatch.setattr(loader, "fetch_url", fake)
    monkeypatch.setattr("json_schema_explorer.resolve.fetch_url", fake)


def test_url_root_relative_refs_need_allow_remote(tmp_path, monkeypatch):
    """Relative refs from a URL root resolve against it only with --allow-remote."""
    calls: list[str] = []
    _urls(monkeypatch, calls)
    out = tmp_path / "o.html"
    CliRunner().invoke(cli, ["build", ROOT_URL, "-o", str(out)])
    assert calls == [ROOT_URL]
    assert _table(out.read_text())["#/properties/a"]["unresolved"] == "types.json#/$defs/A"
    CliRunner().invoke(cli, ["build", ROOT_URL, "-o", str(out), "--allow-remote"])
    t = _table(out.read_text())
    assert "https://example.com/schemas/types.json" in calls
    assert t["#/properties/a"]["ref"] == "https://example.com/schemas/types.json#/$defs/A"


def test_deep_schema_is_one_line_error(tmp_path):
    """A pathologically deep schema exits 1 with no traceback."""
    f = tmp_path / "deep.json"
    f.write_text('{"not":' * 3000 + "{}" + "}" * 3000)
    r = CliRunner().invoke(cli, ["build", str(f), "-o", str(tmp_path / "o.html")])
    assert r.exit_code == 1
    assert "too deeply" in r.output or "invalid JSON" in r.output
    assert "Traceback" not in r.output


def test_malformed_ref_document_is_unresolved(tmp_path):
    """A ref'd file that is not JSON leaves the ref unresolved, no crash."""
    (tmp_path / "bad.json").write_text("{nope")
    docs = Documents(tmp_path)
    with pytest.raises(ValueError, match="invalid JSON"):
        docs.retrieve("bad.json")
    t = build_node_table({"$ref": "bad.json"}, docs)
    assert t["#"]["unresolved"] == "bad.json"


def test_fetch_url_size_cap(monkeypatch):
    """Bodies over the cap are refused."""
    import io

    monkeypatch.setattr(loader, "MAX_BYTES", 5)
    monkeypatch.setattr(loader, "urlopen", lambda *a, **k: io.BytesIO(b"123456789"))
    with pytest.raises(OSError, match="larger"):
        loader.fetch_url("https://x.test/")
