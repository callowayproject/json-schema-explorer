"""Build-time Pygments highlighting for the Source view."""

from html import escape

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

_LIGHT, _DARK = "default", "monokai"


def render_source(documents: list[tuple[str, str]]) -> tuple[str, str]:
    """Return (css, html): one headed, highlighted section per (name, text) document."""
    fmt = HtmlFormatter(style=_LIGHT)
    sections = [
        f'<section class="source-doc"><h2>{escape(name)}</h2>{highlight(text, JsonLexer(), fmt)}</section>'
        for name, text in documents
    ]
    dark = HtmlFormatter(style=_DARK).get_style_defs(".highlight")
    css = fmt.get_style_defs(".highlight") + f"\n@media (prefers-color-scheme: dark) {{\n{dark}\n}}"
    return css, "\n".join(sections)
