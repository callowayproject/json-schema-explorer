"""Render the node table into a single HTML page."""

import json

from jinja2 import Environment, PackageLoader, select_autoescape

from json_schema_explorer.source import render_source

_env = Environment(loader=PackageLoader("json_schema_explorer"), autoescape=select_autoescape(["html"]))


def render_page(table: dict, title: str, documents: list[tuple[str, str]] | None = None) -> str:
    """Render `table` with `title` (the header text) and source `documents` (name, text) into HTML."""
    # `<` escaped so schema text can never close the script element.
    data = json.dumps(table).replace("<", "\\u003c")
    source_css, source_html = render_source(documents or [])
    return _env.get_template("page.html").render(
        title=title, node_table=data, source_css=source_css, source_html=source_html
    )
