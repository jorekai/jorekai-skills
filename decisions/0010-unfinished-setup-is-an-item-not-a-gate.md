# 0010: Unfinished setup is an item in the list, never a gate in front of it

Date: 2026-09-04

## Context

`jorekai-seo:and-now` answers "what next" by reading the workspace. Its script returned early when the connect wizard had not recorded a Search Console property, or when `strategy.md` was still the template: stage `setup`, one item, nothing else. The reasoning was that the loop cannot be graded without a property, so the wizard comes first.

A flow test against a live site showed what that costs. The workspace held a filled strategy and glossary, an audit with zero FAIL, thirteen log rows, an export, two briefs, a draft and a monthly report, and the script printed `stage: setup` and one line. Filling two keys in `connections.md` and changing nothing else turned the same folder into `stage: loop` with nine items. Everything the loop had produced was invisible, including rows past their verify date and the missing monthly report the script does look for. A workspace where the wizard was skipped once stalls without ever saying what is open.

The same shape appeared elsewhere: `jorekai-seo:connect` demanded `static_dir` and `publish` for a site that is correctly hosted outside the repository, `jorekai-seo:links` offered only a content directory to grep, `jorekai-seo:migrate` assumed the move was still ahead, and hypothesis 5 of `jorekai-seo:diagnose` had only a git-based check. Each one reads as a precondition and is really an assumption about where the site lives.

## Decision

A missing piece of setup is an item in the `now` list, ranked with the rest. The stage comes from the whole folder: a workspace holding an audit, log rows, briefs or drafts is in the loop whether or not a wizard ran. The early return survives only for a folder with nothing in it at all.

The same rule applies to the skills that assumed a repository. Every step that reads the site names what to do when the site is hosted elsewhere, and every step that reads history names what to do when the event it describes has already happened.

## Consequences

The `now` list is longer, so its order carries the weight the early return used to: rows past their verify date first, then the audit, then open `tech` rows, then the missing monthly report, then the setup items. `jorekai-seo:and-now` shows at most three of them and the script's order decides which three. A workspace can now report `stage: loop` while its Search Console property is still unrecorded, which is accurate: the loop is running and one connection is missing. Verdicts on such a workspace stay ungraded until an export exists, which the verdict rule already says.
