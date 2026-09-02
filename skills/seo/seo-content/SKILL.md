---
name: seo-content
description: Write or refresh a page for search: one target query, SERP recon of the top 5, an outline that answers better, a draft with evidence slots, and the on-page checklist (title, H1, slug, meta, FAQ, internal links, alt). Use when asked to write, rewrite, refresh, or optimize an article, landing page, "best X", "X vs Y", "X alternatives", or how-to page.
---

# SEO content

Goal: one page that answers one query better than the current top 5 and reads as first-hand experience.

Workspace: `docs/seo/<domain>/` holds `strategy.md` (clusters, evidence inventory), `glossary.md` (the words to use), `briefs/<slug>.md` (this page's brief), `drafts/<slug>.md` (the draft until review). Without a workspace the steps still run; the brief and draft then live where the user says.

## Steps

1. **Fix the target.** One primary query plus up to 5 secondary queries with the same intent. Source: this week's `seo-gsc-review` row, else the highest-priority cluster in `strategy.md` without a page, else the user. Refresh beats new: when a URL on the site already earns impressions for the query, that URL is the target.
   Done when primary query, page URL (existing, or the planned slug), and page type are written down at the top of `briefs/<slug>.md`.

2. **SERP recon.** WebSearch the primary query; fetch the top 5 organic results. Record format (listicle, guide, comparison, tool page), word-count range, the sections every result shares, the sections only the best result has, People-also-ask questions, and whether titles carry a year. The winning format is the format; a guide will not outrank five comparison tables.
   Done when a shared-sections list and a gaps list exist in the brief.

3. **Outline.** H1 = the primary query phrased naturally. H2s = shared sections, then gaps, then one section none of the top 5 has. The first paragraph answers the query in two sentences. Template from [references/page-types.md](references/page-types.md). Headings use the glossary's terms; an `_Avoid_` word never appears in an H1 or H2.
   Done when every H2 states what the reader gets and the primary query appears in the H1 and in one H2.

4. **Draft** into `drafts/<slug>.md` with evidence slots for the author: `[SCREENSHOT: …]`, `[OWN NUMBER: …]`, `[WHAT I TRIED: …]`. Fill a slot from the evidence inventory in `strategy.md` where a row fits; the rest go to the author as one numbered round of questions (slot, what is needed, why it matters), and the answers land under "Evidence answers" in the brief before the draft is called done. Everything experiential is a slot, never a sentence written as if lived. Include a byline slot and a one-line "how this was tested" slot; Google's helpful-content guidance asks who made the page, how, and why. The rater guidelines (September 2025 edition, section 4.6.6) give the Lowest rating to content that is "copied, paraphrased, embedded, auto or AI generated, or reposted" with "little to no effort, little to no originality, and little to no added value"; the tool does not matter, the added value does. Short paragraphs, concrete nouns, a table wherever the SERP shows tables. Close with a 3-question FAQ built from real GSC queries for the page or People-also-ask.
   Done when every section carries body text or a slot, and no sentence claims an experience the author has not confirmed.

5. **On-page pass** with [references/on-page-checklist.md](references/on-page-checklist.md): title ≤ 60 characters with the keyword in the first half, meta 120–160 characters with a reason to click, slug = shortened H1, alt on the first image, 2 outgoing internal links to related pages, and 2 incoming internal links from older pages named as source URL plus anchor.
   Done when every checklist line is ticked or handed to the author as open.

6. **Refresh rule** for an existing page: change the body materially (new section, updated numbers, removed stale claims), then move the visible date, `dateModified`, and `lastmod` together. Without a body change the date stays: Google reads visible and structured dates against each other, and Mueller calls a date change without a content change "noise & useless".

## Then

Run `seo-review` on the draft; it ships only on `ship` for both axes. Then move the draft into `content_dir`, run `unslop` when that skill is available, Request indexing in GSC (and a GET to the IndexNow endpoint when `connections.md` holds a key), write a `content` row to the week's log (`scaffold.py <domain> --log` in `seo-setup`; `verify after` 28 days), and pass the URL to `seo-distribution`.
