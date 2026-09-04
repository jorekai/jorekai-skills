# Changelog

One entry per plugin version. The version at the top equals `version` in `.claude-plugin/plugin.json`; `scripts/check.sh` checks that. Dates are ISO.

## 1.4.0 (2026-09-04)

- Fixed: `render.bot-html` also fires when the raw HTML holds no internal `<a href>`. Measured on 28 live URLs on 2026-09-04, a single-page app passed the character threshold with 386 characters of boilerplate and zero links; three shells now fail and eight content pages still pass.
- Added: `audit.py --rendered FILE` compares a saved rendered DOM of the audited URL against the raw fetch and names what exists only after JavaScript (`render.js-only`, `render.raw-only`), by fields, not by text.
- Added: `Page.script_srcs` counts `<script src>`, so an external bundle counts as JavaScript evidence; `script_bytes` measures inline code only.
- Changed: `content` step 2 drops the tool name and ends on a dated SERP observation with market, device, and the blocks above the organic results, or on the note that none was taken; `diagnose` hypothesis 2 leaves itself open without an earlier observation.

## 1.3.1 (2026-09-04)

- Fixed: `audit.py` no longer overwrites the request delay with the meta-refresh match, which made `time.sleep` raise on a thin page carrying a meta refresh.
- Fixed: `gsc_opportunities.py` reads a single-column CSV, so `--not-indexed` works with the URL export from the Pages report.
- Fixed: `status.py` reads the log's `id` column through `get`, like every other column, so a table without it still reports.
- Fixed: `snippets.py` reports a URL that is not `http://` or `https://` as a fetch error instead of raising on the missing status code.
- Fixed: `scaffold.py` accepts a host name only, so `..` never becomes a folder outside `--root`.
- Fixed: `link.sh` reaches "nothing matched" when a filter selects nothing, under bash 3.2 as well.
- Added: `skills/seo/setup/scripts/test_scaffold.py`; `check.sh` runs it and checks the `link.sh` empty-selection path.

## 1.3.0 (2026-09-03)

- Added: `decisions/0006-sourced-facts-outside-the-steps.md`, which supersedes the placement half of 0004: a sourced fact may stand in a `SKILL.md` outside `## Steps`, a step carries none.
- Changed: `STYLE.md`, `AGENTS.md`, and `README.md` carry one wording for that rule; `content`, `links`, `gsc-review`, and `setup` moved years, tool names, and platform facts out of their steps into `## Rules`, `## Interpretation`, or a pointer.
- Changed: `README.md` names `scripts/check.sh` and the router as `jorekai-seo:seo`; `setup` says `link.sh` writes `.agents/skills/` only; `and-now` prints `/jorekai-seo:<name>`.

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
