# Changelog

## 0.1.1 (2026-11-17)

[Compare the full difference.](https://github.com/callowayproject/json-schema-explorer/compare/0.1.0...0.1.1)

### Fixes

- Fix code-review findings: const presence, source text, URL-root refs, fetch cap, lint. [cb8fb31](https://github.com/callowayproject/json-schema-explorer/commit/cb8fb3157c202c75726b623fea93a12ffbddee9d)

### New

- Add agent skills documentation and memory index. [99a7d35](https://github.com/callowayproject/json-schema-explorer/commit/99a7d35c1bba246f485f09915fdf965202cc5647)

  - AGENTS.md: register issue tracker, triage labels, and domain docs skills
  - docs/agents/issue-tracker.md: GitHub issue conventions and wayfinding operations
  - docs/agents/triage-labels.md: five-role triage vocabulary mapping
  - docs/agents/domain.md: domain documentation consumption guidelines
  - .claude/memory/memory.md: initial memory index

### Other

- Build: add ruff to dev dependencies for CI lint step. [ea6b532](https://github.com/callowayproject/json-schema-explorer/commit/ea6b5327e87ac78d6ecd89ae8e64aee397143573)

- Docs: subagent brief rules, ticket CI-gate rule, ignore worktrees and root html. [75d3d82](https://github.com/callowayproject/json-schema-explorer/commit/75d3d823648547fcc05998b2a02ec8fec08fa677)

- Follow cross-file and remote refs with safety rules (#7). [40ac9de](https://github.com/callowayproject/json-schema-explorer/commit/40ac9dec837422c0e191ed1627f68e86585bff69)

- Chore: remove stray backup file. [8aff41c](https://github.com/callowayproject/json-schema-explorer/commit/8aff41c96ecd46d1595d8a7a3df1fafb908be23c)

- Docs: README, screenshot, credits and lucide ISC notice (#10). [ce27413](https://github.com/callowayproject/json-schema-explorer/commit/ce27413902a8b98fc3638f6e1e6d03fd71105d26)

- Resolve same-document refs via referencing (#6). [912c346](https://github.com/callowayproject/json-schema-explorer/commit/912c3465885e6ab5f2ef189fcfda3b3a5ef4e3bc)

- Feat: explorer UI columns, hash state, refs, defs (#8). [a546459](https://github.com/callowayproject/json-schema-explorer/commit/a5464596efb8b3a1aa28ec800c7ca56bb18bd423)

- Test: docstrings. [95be223](https://github.com/callowayproject/json-schema-explorer/commit/95be2235d32ef5845d03f11df893476d2423f286)

- Feat: Pygments-highlighted Source view (#9). [3b8c9e0](https://github.com/callowayproject/json-schema-explorer/commit/3b8c9e09d7bc04e709bd6587bf993bd0b6b03ae3)

- Feat: node table full keyword coverage (#5). [fef1da3](https://github.com/callowayproject/json-schema-explorer/commit/fef1da360f0e34597fd27ad825f8397e9d695b37)

- Feat: tracer bullet build command (#4). [b1fe903](https://github.com/callowayproject/json-schema-explorer/commit/b1fe903eeaf62b7a537fb028056d6d3c9877a8f7)

- Chore: repo hygiene (pyproject, gitignore, CI) for #3. [b8d9380](https://github.com/callowayproject/json-schema-explorer/commit/b8d9380bb915d246497c142bdfcac25ae2cead4c)

- Expand design doc with v1 delivery plan and node table contract. [237b3a6](https://github.com/callowayproject/json-schema-explorer/commit/237b3a6fbdfdbf54f643ddfdb3b513ffe4084db1)

  - Clarify upstream relationship as clean-room "inspired by" with local reference copy
  - Add node ID scheme, node table schema, and URL hash format
  - Document exit codes, stdin/URL fallback naming, and --allow-remote scope
  - List navigable children, generic keyword rule, and source view section
  - Add delivery sequence with parallel tracks and CI/release details

- Bump the github-actions group with 10 updates. [37613d8](https://github.com/callowayproject/json-schema-explorer/commit/37613d822d09305624b9f15d69a61333aa8537de)

  Bumps the github-actions group with 10 updates:

  | Package | From | To |
  | --- | --- | --- |
  | [actions/checkout](https://github.com/actions/checkout) | `4` | `7` |
  | [actions/download-artifact](https://github.com/actions/download-artifact) | `4` | `8` |
  | [actions/setup-python](https://github.com/actions/setup-python) | `5` | `7` |
  | [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) | `5` | `7` |
  | [github/codeql-action](https://github.com/github/codeql-action) | `3` | `4` |
  | [docker/login-action](https://github.com/docker/login-action) | `3` | `4` |
  | [docker/metadata-action](https://github.com/docker/metadata-action) | `5` | `6` |
  | [docker/build-push-action](https://github.com/docker/build-push-action) | `6` | `7` |
  | [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance) | `2` | `4` |
  | [softprops/action-gh-release](https://github.com/softprops/action-gh-release) | `2` | `3` |

  Updates `actions/checkout` from 4 to 7

  - [Release notes](https://github.com/actions/checkout/releases)
  - [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/actions/checkout/compare/v4...v7)

  Updates `actions/download-artifact` from 4 to 8

  - [Release notes](https://github.com/actions/download-artifact/releases)
  - [Commits](https://github.com/actions/download-artifact/compare/v4...v8)

  Updates `actions/setup-python` from 5 to 7

  - [Release notes](https://github.com/actions/setup-python/releases)
  - [Commits](https://github.com/actions/setup-python/compare/v5...v7)

  Updates `astral-sh/setup-uv` from 5 to 7

  - [Release notes](https://github.com/astral-sh/setup-uv/releases)
  - [Commits](https://github.com/astral-sh/setup-uv/compare/v5...v7)

  Updates `github/codeql-action` from 3 to 4

  - [Release notes](https://github.com/github/codeql-action/releases)
  - [Changelog](https://github.com/github/codeql-action/blob/main/CHANGELOG.md)
  - [Commits](https://github.com/github/codeql-action/compare/v3...v4)

  Updates `docker/login-action` from 3 to 4

  - [Release notes](https://github.com/docker/login-action/releases)
  - [Commits](https://github.com/docker/login-action/compare/v3...v4)

  Updates `docker/metadata-action` from 5 to 6

  - [Release notes](https://github.com/docker/metadata-action/releases)
  - [Commits](https://github.com/docker/metadata-action/compare/v5...v6)

  Updates `docker/build-push-action` from 6 to 7

  - [Release notes](https://github.com/docker/build-push-action/releases)
  - [Commits](https://github.com/docker/build-push-action/compare/v6...v7)

  Updates `actions/attest-build-provenance` from 2 to 4

  - [Release notes](https://github.com/actions/attest-build-provenance/releases)
  - [Changelog](https://github.com/actions/attest-build-provenance/blob/main/RELEASE.md)
  - [Commits](https://github.com/actions/attest-build-provenance/compare/v2...v4)

  Updates `softprops/action-gh-release` from 2 to 3

  - [Release notes](https://github.com/softprops/action-gh-release/releases)
  - [Changelog](https://github.com/softprops/action-gh-release/blob/master/CHANGELOG.md)
  - [Commits](https://github.com/softprops/action-gh-release/compare/v2...v3)

  ______________________________________________________________________

  **updated-dependencies:** - dependency-name: actions/checkout
  dependency-version: '7'
  dependency-type: direct:production
  update-type: version-update:semver-major
  dependency-group: github-actions

  **signed-off-by:** dependabot[bot] <support@github.com>

### Updates

- Updated packaging instructions and dependencies. [977941b](https://github.com/callowayproject/json-schema-explorer/commit/977941bc8b5b99f77d56b52742d7671814e1cb0d)

## 0.1.0 (2026-11-17)

### Other

- Initial commit. [7b36bfb](https://github.com/callowayproject/json-schema-explorer/commit/7b36bfbf13e80e16763231ad1b84d3098d14827d)
