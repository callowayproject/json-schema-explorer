# json-schema-explorer — v1 design

Agreed 2026-11-17. Derived from `opencollection/packages/oc-schema-explorer` (React/Vite SPA), rewritten in Python as a static HTML generator.

## What it is

A Python CLI that turns any JSON Schema into a single self-contained, offline HTML page with a column-by-column Explorer and a highlighted Source view.

## Repository

- GitHub: `github.com/callowayproject/json-schema-explorer`; local: `~/code/json-schema-explorer`.
- Fresh history (rewrite, not a port of commits).
- License: MIT. Credit "derived from opencollection/oc-schema-explorer" in README and LICENSE; include lucide's ISC notice for the inlined icons.
- `opencollection/packages/oc-schema-explorer` stays untouched.

## Packaging

- uv project, Python ≥ 3.14.
- PyPI name and command: `json-schema-explorer` (free on PyPI as of 2026-11-17; `jsonschema-explorer` is taken). Import name: `json_schema_explorer`.
- Dependencies: `click`, `jinja2`, `referencing`, `pygments`.
- Only the CLI is a supported interface. An internal `build_html(schema) -> str` exists but is undocumented and unstable.

## CLI

```
json-schema-explorer build SCHEMA [-o FILE] [--allow-remote] [--ref-root DIR]
```

- `SCHEMA`: file path, `http(s)` URL, or `-` for stdin. JSON only (no YAML).
- `-o` defaults to `<schema-stem>.html`.

## Architecture

1. **Load** the root schema (path / URL / stdin).
2. **Resolve** references with `referencing`: drafts 4 through 2020-12, `$id`, `$anchor`, `$defs`, `definitions`, cross-file refs.
3. **Flatten** into a node table: one entry per subschema, keyed by JSON Pointer. Each entry holds type, constraints, and children. A `$ref` becomes a link to another entry's ID (not inlined), so recursive schemas are fine.
4. **Render** one Jinja2 template with inline CSS, inline JS, the node table embedded as JSON, and inline SVG icons.
5. **Client:** ~150 lines of vanilla JS draws the columns from the table. The open column path lives in the URL hash (e.g. `#/properties/request/items`) so links reopen the same view.

Pre-rendering every column path in Python was rejected: recursive schemas have infinitely many paths.

## What the Explorer shows

**Navigable children:** `properties`, `patternProperties`, `additionalProperties` (when a schema), `items` / `prefixItems`, `oneOf` / `anyOf` / `allOf` / `not`, `if` / `then` / `else`, and root `$defs` / `definitions` as a section at the bottom of the first column.

- `allOf` is shown as a list of its parts, never merged.

**Shown in place:** constraints (`minimum`, `maxLength`, `pattern`, …), `enum`, `const`, `format`, `default`, `examples`, `deprecated`, `readOnly`.

**Types:**

- Boolean schema `true` → `any`, `false` → `never`.
- Type lists → `string | null`.
- Missing `type` is inferred: `properties` → object, `items` → array, `enum` → enum, `const` → const.

**Header:** schema `title`, falling back to the file name; generic icon (no OpenCollection branding).

## Safety

- Jinja2 autoescape on — schema descriptions are untrusted.
- Remote `http(s)` refs are fetched only with `--allow-remote` (even when the root came from a URL). Stdlib `urllib`, ~10 s timeout.
- Local file refs must stay inside the root schema's directory; widen with `--ref-root DIR`. When the root is a URL or stdin, local file refs are not followed. (Reason: referenced content is embedded in a page that may be published.)
- Unresolvable `$ref`: warning on stderr, red "unresolved: <ref>" row in the column, build still exits 0.
- Malformed schema parts (e.g. `properties: null`, `required` as a string) never crash the parser — guard with `isinstance` checks.

## Look

- Hand-written CSS (no Tailwind), dark mode via `prefers-color-scheme`.
- About a dozen lucide icons inlined as SVG.
- Source view highlighted with Pygments at build time (no Monaco, no JS).

## Not in v1

Graph view (reactflow; revisit with Mermaid/Cytoscape on demand), search, YAML input, public Python API, `--strict`, docs site, changelog tool, paste-into-editor screen, `serve` command.

Unused code from the original is not ported: `DefinitionsExplorer`, `PropertyDetails`, `SchemaTree`, `SearchBar`, and everything in `schemaParser.js` except `getSchemaType`.

## Tests

pytest with example schemas:

- self-referencing (recursive) schema
- 2020-12 `$defs` and draft-04 `definitions`
- cross-file `$ref`
- `$anchor`
- `oneOf`, `allOf`, `if` / `then` / `else`
- malformed input

Assert on the node table, plus one smoke test that runs `build` and parses the resulting HTML.

## Repo contents and CI

- `README.md` (install, usage, screenshot), `LICENSE`.
- One GitHub Actions workflow: ruff + pytest on Python 3.12 and 3.13.
- Release job: PyPI trusted publishing on tag push.
