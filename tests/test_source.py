"""Source view: Pygments-highlighted documents, light and dark."""

from json_schema_explorer.source import render_source


def test_one_highlighted_section_per_document():
    """Each document gets a headed, highlighted section."""
    css, html = render_source([("root.json", '{"a": 1}'), ("other.json", '{"b": "<x>"}')])
    assert html.index("root.json") < html.index("other.json")
    assert html.count('class="highlight"') == 2
    assert '<span class="nt">' in html  # token markup, not plain text
    assert "&lt;x&gt;" in html  # escaped
    assert "prefers-color-scheme: dark" in css


def test_build_emits_source_section(tmp_path):
    """The build command embeds the root document source."""
    from click.testing import CliRunner

    from json_schema_explorer.cli import cli

    src = tmp_path / "pet.json"
    src.write_text('{"title": "Pet", "type": "object"}')
    out = tmp_path / "pet.html"
    assert CliRunner().invoke(cli, ["build", str(src), "-o", str(out)]).exit_code == 0
    page = out.read_text()
    assert 'class="highlight"' in page and "pet.json" in page and "prefers-color-scheme: dark" in page
