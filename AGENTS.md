# Working in this collection

Skills live under `skills/<theme>/<skill>/`; `README.md` explains the layout and the SEO loop; `STYLE.md` holds the writing rules for every file and every agent; `decisions/` holds the reasons behind the rules, one file per decision. Rules for editing:

- Read `STYLE.md` before writing a line. English only, no em dashes, no arrows in prose, no filler, sources for every platform claim. Steps stay free of years, tool names, and platform facts; a sourced fact stands outside `## Steps`.
- The collection is public. No customer domain, key, analytics id, server path, or workspace under `docs/` is ever committed; site workspaces live in a private repository per site.
- `bash scripts/check.sh` runs before every commit and must print `ok`. It checks style, private data, then every offline test and syntax check. Customer names to reject sit in `.check_public.local` (gitignored, one regex per line).
- Test a script before editing the SKILL.md that calls it; `scripts/check.sh` lists the commands. Scripts stay Python stdlib or bash.
- The router must not lie: adding, renaming, or changing a sub-skill updates `skills/seo/seo/SKILL.md` and the tables in `README.md` in the same commit, and bumps `version` in `.claude-plugin/plugin.json` with an entry at the top of `CHANGELOG.md`. `check.sh` fails on a skill that is missing from either place, on a `jorekai-<theme>:<name>` written anywhere that names no directory, and when the version and the changelog's top entry differ.
- Skill directories carry no theme prefix (`skills/seo/setup`); the plugin `jorekai-seo` (`.claude-plugin/plugin.json`, `skills` points at `skills/seo`) supplies it, so the invocation is `/jorekai-seo:setup`; prose refers to skills by that full name.
- A new skill is user-invoked (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`) unless the agent must reach it on its own; then it gets a model-facing `description` with one trigger per branch. Every skill has `agents/openai.yaml`.
