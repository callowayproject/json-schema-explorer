"""Command line interface."""

import json
from pathlib import Path

import click

from json_schema_explorer.loader import LoadError, default_output_name, load_schema
from json_schema_explorer.nodes import ROOT_ID, build_node_table
from json_schema_explorer.render import render_page
from json_schema_explorer.resolve import Documents


@click.group()
def cli() -> None:
    """Turn a JSON Schema into a static HTML explorer."""


@cli.command()
@click.argument("schema")
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="Output file (default: <stem>.html).")
@click.option("--allow-remote", is_flag=True, help="Fetch remote http(s) $refs (off by default).")
@click.option(
    "--ref-root", type=click.Path(file_okay=False, path_type=Path), help="Follow local $refs anywhere under DIR."
)
def build(schema: str, output: str | None, allow_remote: bool, ref_root: Path | None) -> None:
    """Build an HTML page from SCHEMA (path, http(s) URL, or - for stdin)."""
    try:
        root = load_schema(schema)
    except LoadError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1) from exc
    is_file = schema != "-" and not schema.startswith(("http://", "https://"))
    docs = Documents(Path(schema).resolve().parent if is_file else None, ref_root if is_file else None, allow_remote)
    table = build_node_table(root, docs)
    for node in table.values():
        if node["unresolved"]:
            click.echo(f"warning: unresolved $ref {node['unresolved']!r} at {node['id']}", err=True)
    title = table[ROOT_ID]["title"] or (schema if schema != "-" else "schema")
    Path(output or default_output_name(schema)).write_text(
        render_page(table, title, [(schema, json.dumps(root, indent=2)), *docs.texts.items()]), encoding="utf-8"
    )
