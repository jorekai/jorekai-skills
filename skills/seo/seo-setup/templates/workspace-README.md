# SEO workspace

Working files for search work on this repository. One folder per canonical host. Agents read `<domain>/config.md` before running any `seo-*` skill; humans start with `<domain>/strategy.md`.

## Domains

<!-- domains:start -->
| Domain | Folder | Filled |
|---|---|---|
<!-- domains:end -->

## Layout per domain

- `config.md`: site facts the skills need (hosts, content directory, head template, sitemap, brand pattern, CTR calibration). Written by `seo-setup`; edit by hand when the site changes.
- `connections.md`: what is connected where (Search Console property, sitemap submission, Bing, IndexNow). Written by the `seo-connect` wizard.
- `strategy.md`: niche, audience, offer, competitors, keyword clusters, evidence inventory, constraints. Written by `seo-grill`.
- `glossary.md`: the niche's vocabulary, one term per entry with the words to avoid. Written by `seo-grill`; every draft, title, and anchor uses these terms.
- `log/YYYY-Www.md`: one file per ISO week. The only place actions and their outcomes are recorded.
- `briefs/<slug>.md`: per-page brief from `seo-content` (target query, SERP recon, outline, evidence answers).
- `drafts/<slug>.md`: drafts before they move into the site's content directory.
- `exports/`: Search Console exports, named `YYYY-MM-DD-<what>.zip` or `.csv`. Ignored by git.
- `outreach.csv`: link targets from `seo-links` (`url, site, contact, why, status`).

## Log format

File `log/YYYY-Www.md`; `scaffold.py <domain> --log` (in the `seo-setup` skill) creates the current week's file and prints the next free id. Ids are `YYYY-Www-nn`.

```markdown
# 2026-W36 (2026-08-31 to 2026-09-06)

Source: exports/2026-09-01-gsc.zip vs exports/2026-08-04-gsc.zip

## Outcomes of earlier actions

| id | URL | Applied | Then | Now | Verdict |
|---|---|---|---|---|---|
| 2026-W34-01 | /pricing | 2026-08-20 | pos 11.2, CTR 1.8 % | pos 8.9, CTR 2.6 % | won |

## Actions

| id | Bucket | URL | Query | Action | Status | Applied | Verify after | Outcome |
|---|---|---|---|---|---|---|---|---|
| 2026-W36-01 | striking | /blog/x | x tool | query into title and H1, new section "y" | applied | 2026-09-02 | 2026-09-16 | |
```

Status, in order: `todo` → `applied` (date set) → `verify` (verify-after date reached, outcome pending) → `won` | `no-change` | `dropped`. A `won` row names the metric that moved in Outcome; `no-change` after two verify windows becomes `dropped` with the reason in Outcome.

Buckets: `striking`, `ctr`, `decay`, `cannibal`, `unindexed`, `tech`, `links`, `content`, `distribution`, `diagnose`.

Every skill that changes the site appends a row to the current week's file. The next `seo-gsc-review` fills "Outcomes of earlier actions" for every row whose verify-after date has passed (`scaffold.py <domain> --due` lists them).
