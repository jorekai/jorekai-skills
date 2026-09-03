# 0001: One Claude Code plugin per theme, invoked as /jorekai-<theme>:<skill>

Date: 2026-09-03

## Context

Skills linked into `.claude/skills/` appear as flat names (`/seo-setup`) and collide with skills from other collections. A plugin namespaces them and gives autocomplete after the prefix. Skill directory names must equal the skill name, so a prefix in the directory would double it (`/jorekai-seo:seo-setup`).

## Decision

The repository is a marketplace named `jorekai` with one plugin per theme, named `jorekai-<theme>`. Skill directories carry no theme prefix (`skills/seo/setup`); the plugin's `skills` field points at the theme directory. Prose refers to skills by the full invocation name.

## Consequences

Codex, which has no plugin namespace, sees plain names (`$setup`); `scripts/link.sh` links them. A plugin install is a copy, so every change bumps `version` in `plugin.json` and gets a changelog entry, otherwise `claude plugin update` reports the latest version and nothing changes.
