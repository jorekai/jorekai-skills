# 0003: Skill state lives in the site's repository, never in the skill

Date: 2026-09-02

## Context

Skills that remember facts in prose or in the model's context lose them between sessions and cannot be audited. SEO work spans weeks: an action gets a verify date, and the next review grades it.

## Decision

Every skill reads and writes `docs/seo/<domain>/` in the site's repository: config, connections, strategy, glossary, a log per ISO week, briefs, drafts, exports, audits. A site without a repository gets a small private repository that holds only that workspace. The skills collection holds templates and scripts, no state.

## Consequences

The collection can be public. `scripts/check.sh` rejects any tracked file under `docs/` and any customer pattern from `.check_public.local`. A session that resumes work runs `and-now`, which reads the files, instead of relying on memory.
