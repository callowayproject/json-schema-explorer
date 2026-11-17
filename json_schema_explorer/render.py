"""Render the node table into a single HTML page."""

import json

from jinja2 import Environment, PackageLoader, select_autoescape

_env = Environment(loader=PackageLoader("json_schema_explorer"), autoescape=select_autoescape(["html"]))


def render_page(table: dict, title: str) -> str:
    """Render `table` with `title` (the header text) into HTML."""
    # `<` escaped so schema text can never close the script element.
    data = json.dumps(table).replace("<", "\\u003c")
    return _env.get_template("page.html").render(title=title, node_table=data)
