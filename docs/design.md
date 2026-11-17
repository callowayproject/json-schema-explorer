# json-schema-explorer — v1 design

Agreed 2026-11-17. Inspired by `oc-schema-explorer` (React/Vite SPA) from [opencollection-dev/opencollection](https://github.com/opencollection-dev/opencollection), rebuilt in Python as a static HTML generator.

## What it is

A Python CLI that turns any JSON Schema into a single self-contained, offline HTML page with a column-by-column Explorer and a highlighted Source view.

## Repository

- GitHub: `github.com/callowayproject/json-schema-explorer`; local: `~/code/json-schema-explorer`.
- Fresh history (rewrite, not a port of commits).
- License: MIT. Include lucide's ISC notice for the inlined icons.
- **Clean room.** The upstream repo has no license, so none of its code, CSS, or class names is copied. It is a behavioral reference only; tickets say "build X", never "port X". README and LICENSE say "inspired by" with the upstream URL (a credit, not a license claim).
- A local reference copy lives at `oc-schema-explorer/`; it is gitignored and never shipped.

## Packaging

- uv project, Python ≥ 3.14.
- PyPI name and command: `json-schema-explorer` (free on PyPI as of 2026-11-17; `jsonschema-explorer` is taken). Import name: `json_schema_explorer`.
- Dependencies: `click`, `jinja2`, `referencing`, `pygments`.
- Only the CLI is a supported interface. An internal `build_html(schema) -> str` exists but is undocumented and unstable.
- `pyproject.toml`: `name = "json-schema-explorer"`, quoted entry point `json-schema-explorer = "json_schema_explorer.cli:cli"`, no Documentation URL.

## CLI

```
json-schema-explorer build SCHEMA [-o FILE] [--allow-remote] [--ref-root DIR]
```

- `SCHEMA`: file path, `http(s)` URL, or `-` for stdin. JSON only (no YAML).
- `-o` defaults to `<schema-stem>.html`. Stdin → `schema.html`. URL → last path segment's stem, falling back to `schema.html`. An existing output file is overwritten.
- Fetching a root URL does not need `--allow-remote`; that flag governs refs only.

### Exit codes

- Fatal (one line on stderr, no traceback, exit 1): root file not found, root URL unfetchable, invalid JSON, root is neither an object nor a boolean.
- Unresolvable `$ref` is not fatal (see Safety); exit 0.

## Architecture

1. **Load** the root schema (path / URL / stdin).
2. **Resolve** references with `referencing`: drafts 4 through 2020-12, `$id` / `id`, `$anchor`, `$defs`, `definitions`, cross-file refs. No `$schema` → assume 2020-12. `$dynamicRef` and `$recursiveRef` resolve statically to their initial target, like `$ref`.
3. **Flatten** into the node table (below). A `$ref` becomes a link to another node's ID (not inlined), so recursive schemas are fine.
4. **Render** one Jinja2 template with inline CSS, inline JS, the node table embedded as JSON, and inline SVG icons.
5. **Client:** ~150 lines of vanilla JS draws the columns from the table. The open column path lives in the URL hash so links reopen the same view.

Pre-rendering every column path in Python was rejected: recursive schemas have infinitely many paths.

### Node IDs

- Root-document nodes: `#/<json-pointer>` (e.g. `#/properties/request`).
- Nodes from other documents: `<path-relative-to-root>#/<json-pointer>` (e.g. `common/types.json#/$defs/Id`). Remote documents use their absolute URL.

### Node table

A JSON object mapping node ID → node. This is the contract between the Python and JS sides; parser tests assert on it.

```
{
  "id": str,
  "type": str,                 # "object", "string | null", "any", "never", "enum", "const", …
  "title": str | null,
  "description": str | null,
  "required": [str],           # property names
  "constraints": {str: any},   # minimum, maxLength, pattern, dependentRequired, …
  "enum": [any] | null,
  "const": any | null,         # absent key vs null distinguished by presence
  "default": any | null,
  "examples": [any] | null,
  "format": str | null,
  "deprecated": bool,
  "readOnly": bool,
  "ref": node-id | null,       # target when this node is a $ref / $dynamicRef / $recursiveRef
  "unresolved": str | null,    # the raw ref string when it could not be resolved
  "children": [{"label": str, "kind": str, "target": node-id}]
}
```

`kind` is one of: `property`, `pattern`, `additional`, `item`, `prefix`, `oneOf`, `anyOf`, `allOf`, `not`, `if`, `then`, `else`, `def`, or the keyword name for the generic rule below.

### URL hash

`#c=<id>|<id>|…`: the node ID of each open column, each URL-encoded, separated by `|`. Any unknown ID → fall back to the root column.

## What the Explorer shows

**Navigable children:** `properties`, `patternProperties`, `additionalProperties` (when a schema), `items` / `prefixItems`, `oneOf` / `anyOf` / `allOf` / `not`, `if` / `then` / `else`, and root `$defs` / `definitions` as a section at the bottom of the first column.

- Generic rule: every other keyword whose value is a subschema (`contains`, `propertyNames`, `dependentSchemas`, `additionalItems`, `unevaluatedProperties`, `unevaluatedItems`, …) is a navigable child labelled with its keyword name. Nothing in a real schema is silently dropped.
- Draft-04 array-form `items: [...]` is treated like `prefixItems`.
- `allOf` is shown as a list of its parts, never merged.

**Shown in place:** constraints (`minimum`, `maxLength`, `pattern`, `dependentRequired`, …), `enum`, `const`, `format`, `default`, `examples`, `deprecated`, `readOnly`.

- Required properties carry a "required" marker.
- `description` is plain escaped text with `white-space: pre-line`; no Markdown.

**Types:**

- Boolean schema `true` → `any`, `false` → `never`.
- Type lists → `string | null`.
- Missing `type` is inferred: `properties` → object, `items` → array, `enum` → enum, `const` → const.

**Header:** schema `title`, falling back to the file name; generic icon (no OpenCollection branding).

## Source view

One section per loaded document (root first), each with a heading naming the document and highlighted with Pygments at build time. Light and dark Pygments styles both emitted, switched by `prefers-color-scheme`.

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

Graph view (reactflow; revisit with Mermaid/Cytoscape on demand), search, YAML input, public Python API, `--strict`, docs site, paste-into-editor screen, `serve` command, Markdown in descriptions.

## Tests

pytest with example schemas:

- self-referencing (recursive) schema
- 2020-12 `$defs` and draft-04 `definitions`
- cross-file `$ref`
- `$anchor`
- `oneOf`, `allOf`, `if` / `then` / `else`
- malformed input

Assert on the node table, plus one smoke test that runs `build` and parses the resulting HTML.

## Repo contents, CI, and release

- `README.md` (install, usage, screenshot).
- The template workflows stay.
  - `test.yaml`: ruff + pytest on Python 3.14. Paths: `json_schema_explorer/**`, `tests/**`, `pyproject.toml`, `.github/workflows/test.yaml`.
  - `publish-docs-preview.yaml`: `workflow_dispatch` only until a docs site exists.
- Release uses the existing template flow: on a merged PR, `bump-version` bumps the version and runs `generate-changelog`, then `build-python` builds, publishes to PyPI via trusted publishing, and creates a GitHub release. Registering the PyPI trusted publisher is a manual step.

## Delivery

One "v1" parent issue; each ticket is a sub-issue linked by native blocked-by dependencies and points to the relevant section of this doc.

1. Repo hygiene
2. Tracer bullet (CLI → load → flat `properties` → template → one column; smoke test)
3. Node table
4. Same-document refs
5. Cross-file refs and safety
6. Explorer UI
7. Source view
8. README and credits
9. Release-flow check

3–5 and 6–7 can run in parallel once 2 lands; the node table contract is the seam.
