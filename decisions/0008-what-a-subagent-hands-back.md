# 0008: A step that fans out names the table that comes back

Date: 2026-09-04

## Context

`jorekai-seo:review` runs two subagents and caps each brief at 400 words, so the caller gets two short reports instead of two full drafts. The steps that read the most said nothing of the kind: a crawl over hundreds of URLs, link prospecting across twenty targets, SERP recon over five results. Their reading landed in the caller's context, where it pushed out the workspace files the rest of the session needs.

## Decision

A step that fans out (a crawl, prospecting, SERP recon, a review) sends the reading to subagents and names what comes back: the columns of one table and a word limit. The pages a subagent read stay in its context, never in the caller's.

## Consequences

`STYLE.md` carries the rule, so it applies to every theme, not only to `review`. A step that cannot name its columns is not ready to fan out yet, and writing them down is the cheapest place to notice. Deterministic work stays where it is: a script that returns one table already satisfies the rule and needs no subagent.
