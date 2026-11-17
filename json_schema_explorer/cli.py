"""Command line interface."""

from pathlib import Path

import click

from json_schema_explorer.loader import LoadError, default_output_name, load_schema
from json_schema_explorer.nodes import ROOT_ID, build_node_table
from json_schema_explorer.render import render_page


@click.group()
def cli() -> None:
    """Turn a JSON Schema into a static HTML explorer."""


@cli.command()
@click.argument("schema")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="Output file (default: <stem>.html).")
def build(schema: str, output: str | None) -> None:
    """Build an HTML page from SCHEMA (path, http(s) URL, or - for stdin)."""
    try:
        root = load_schema(schema)
    except LoadError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1) from exc
    table = build_node_table(root)
    title = table[ROOT_ID]["title"] or (schema if schema != "-" else "schema")
    Path(output or default_output_name(schema)).write_text(render_page(table, title), encoding="utf-8")
