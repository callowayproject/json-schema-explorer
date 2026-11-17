## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-role triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a single-context domain documentation layout. See `docs/agents/domain.md`.

## Subagent briefs

- A worktree may start from `main`, not the integration branch. First run `git merge-base --is-ancestor <integration> HEAD`; if it fails, `git reset --hard <integration>`.
- Never `sed -i` on macOS (it leaves `-E` backup files); use the Edit tool or `sed -i ''`.
- Build sample/smoke output into a temp directory, never the repo root.
- Run `git status --short` before every commit and stage files by name.