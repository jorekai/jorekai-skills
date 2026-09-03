# 0006: A sourced platform fact may stand in a SKILL.md outside its steps; 0004 keeps the source, not the place

Date: 2026-09-03

## Context

0004 asks for a source per platform claim, and its consequences send years, tool names, and platform facts out of the steps. Three files then said three things. `README.md` sent every such fact to `references/`, `STYLE.md` asked only for the source row, and `AGENTS.md` named neither placement. The skills followed the weakest reading: eight `SKILL.md` files carried dated, sourced facts outside their steps, and five steps carried one inside.

## Decision

The source half of 0004 stands unchanged. A claim about a platform, product, or Google feature needs a row in `skills/seo/seo/references/sources.md` with URL and check date, or it is labelled a heuristic, or it goes. The placement half now covers the steps alone. A sourced fact may stand in a `SKILL.md` outside `## Steps`, in `## Rules`, in `## Interpretation`, or in the opening paragraph, where the model reads it while it judges. A line inside `## Steps` carries the work, its inputs, and its completion criterion, and no year, no tool name, no platform fact.

## Consequences

`STYLE.md`, `AGENTS.md`, and `README.md` carry this one wording. A fact that explains a rule stays next to the rule. Material a reader looks up, such as a checklist or a fix table, still goes to `references/`. 0005 is untouched, with one line drawn: a tool named as something to use belongs in `references/tools.md` and appears in no step, while a vendor named as the author of a study is a source and may stand where the study's number stands.
