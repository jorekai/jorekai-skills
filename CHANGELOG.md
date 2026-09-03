# Changelog

One entry per plugin version. The version at the top equals `version` in `.claude-plugin/plugin.json`; `scripts/check.sh` checks that. Dates are ISO.

## 1.2.0 (2026-09-03)

- Added: `CHANGELOG.md`, decision records under `decisions/`, `CONTRIBUTING.md`, issue and pull request templates, Dependabot for GitHub Actions.
- Added: `scripts/sources_age.py` lists rows in `references/sources.md` whose check date is older than a limit; `check.sh` warns at 180 days.
- Changed: `check.sh` verifies that the top changelog version equals the plugin version.

## 1.1.0 (2026-09-03)

- Added: `STYLE.md`, the rulebook for prose, code, commits, and private data, read by every agent through `AGENTS.md` and `CLAUDE.md`.
- Added: `scripts/check.sh` runs style, private data, gitleaks over the history, then every offline test; CI runs it on every push.
- Added: MIT license, plugin metadata (repository, homepage, license), marketplace owner.
- Changed: arrows left the prose; sequences are sentences, menu paths use `>`.

## 1.0.1 (2026-09-03)

- Changed: customer patterns for the private-data gate moved to the gitignored `.check_public.local`.
- Removed: the site workspace under `docs/`; it lives in a private repository per site. History rewritten to drop it.

## 1.0.0 (2026-09-03)

- Added: plugin `jorekai-seo` with the skills `seo` (router), `setup`, `connect`, `grill`, `tech-audit`, `gsc-review`, `content`, `review`, `links`, `distribution`, `diagnose`, `and-now`. Invocation `/jorekai-seo:<name>`.
