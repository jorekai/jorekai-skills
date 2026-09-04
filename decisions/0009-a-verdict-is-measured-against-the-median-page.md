# 0009: A verdict is measured against the median page, and a row too small to measure gets no verdict

Date: 2026-09-04

## Context

The weekly review graded an action by comparing the page against its own past: position or clicks in the export before the change, the same numbers after it. Everything that moves a whole site at once, a season, a core update, a market that cooled, landed in that comparison as the result of the change. A month where the site lost 12 % across the board produced `no-change` verdicts on actions that had in fact gained, and a month where demand rose produced `won` verdicts on actions that did nothing. The log is the only place this collection learns from, so a log full of seasonality teaches the wrong lesson twice: once when it is written, once when the same action is recommended again. The other half of the problem was small rows. A query with 40 impressions moves by chance, and a forced `won` or `no-change` on it is noise recorded as evidence.

The obvious baseline is the median change of the pages that were not touched. It needs the script to know which pages were touched, which means parsing the markdown log from inside the export parser, which couples two files that are otherwise independent.

## Decision

The baseline is the median change of every page present in both exports, changed pages included. Pages the loop touched are a small share of all pages on any site the loop is worth running on, and a median ignores them. `won` means the row beat that median; `no-change` means it did not, including a row that rose by less. A row whose impressions stay under `min_impressions` in both exports gets `too-small`, which is not a loss and not a win. The starting value moved into the log itself: the `Actions` table carries `Then`, the metric at the moment the row was applied, and the outcomes table carries `Baseline`.

## Consequences

Grading needs two exports, and without a previous one the verdict falls back to the raw change with `none` in the Baseline cell, which the report says out loud. On a site with only a few dozen pages the median carries part of the change it is measuring; the interpretation section says so, and the alternative on a site that small is no baseline at all. `diagnose` reads the same number for its first hypothesis instead of a second implementation. A `too-small` verdict that keeps appearing is a signal about the threshold, not about the pages.
