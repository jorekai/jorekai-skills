# 0004: Every claim about platform behaviour has a sourced row, or is labelled a heuristic

Date: 2026-09-02

## Context

Language models state Google features, tool limits, and dates with confidence and without evidence. A skill that repeats such a claim spreads it to every run.

## Decision

Claims about how a platform, product, or Google feature behaves live only in `references/` and have a row in `references/sources.md` with URL and check date, verified against the primary source before they are written. Unverified means labelled as a heuristic or left out. `scripts/sources_age.py` lists rows whose check date is older than a limit.

## Consequences

Steps in `SKILL.md` stay free of years, tool names, and platform facts. Refreshing a skill starts with the sources table.
