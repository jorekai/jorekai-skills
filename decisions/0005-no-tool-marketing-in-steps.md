# 0005: Tools appear only in references/tools.md and are interchangeable

Date: 2026-09-02

## Context

Skill collections age fastest where they name tools in the steps. A named tool becomes a dependency, then a recommendation, then stale advice.

## Decision

Steps describe the work and its completion criterion. Tools, with what they are good for and what they cost, sit in `references/tools.md` per theme and can be swapped without touching a step.

## Consequences

A step never says "open Ahrefs"; it says "get the top 10 for the query and their titles". Scripts stay Python stdlib or bash for the same reason.
