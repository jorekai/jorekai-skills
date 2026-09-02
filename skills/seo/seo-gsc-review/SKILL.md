---
name: seo-gsc-review
description: Turn a Google Search Console export into a ranked action list via scripts/gsc_opportunities.py (striking-distance queries at position 8–20, CTR gaps, decayed pages, cannibalization, unindexed URLs), after grading the actions logged in earlier weeks. Use when the user shares GSC CSVs or a zip, asks what to optimize next or which pages to update, or runs the weekly SEO review.
---

# GSC review

Reads `docs/seo/<domain>/config.md` for `brand_regex`, `expected_ctr_1`, `min_impressions`, `gsc_export_window`, and the log for actions due for a verdict. No workspace: run `seo-setup`, or ask the user for those four values and skip the log steps.

## Steps

1. **Get the export.** Needed: the zip or folder from GSC → Performance → Search results → Export → Download CSV, for the last 28 days (3 months on small sites). For decay, a second export of the preceding period of equal length. Optional: a page×query table and a not-indexed URL list. Exact clicks in [references/export-howto.md](references/export-howto.md). Without an export, send the user those steps and stop.
   Save the files as `exports/YYYY-MM-DD-gsc.zip` (and `-prev.zip`) in the workspace.
   Done when a path to a zip or folder containing the queries and pages tables exists.

2. **Grade earlier actions.** `python3 <seo-setup>/scripts/scaffold.py <domain> --due` (path relative to the `seo-setup` skill) lists rows whose verify-after date has passed. For each, find the row's URL and query in the new export and fill the week's "Outcomes of earlier actions" table: Then from the log, Now from the export, Verdict `won` when the bucket's metric moved the right way (position for `striking` and `unindexed`, CTR for `ctr`, clicks for `decay` and `content`), `no-change` otherwise; `verify` only when the export window does not yet cover the verify date. Update the row's Status in its original file.
   Done when no due row is left unsettled.

3. **Run the script.**

   ```bash
   python3 scripts/gsc_opportunities.py ./gsc-now.zip --previous ./gsc-prev.zip \
     [--page-queries pq.csv] [--not-indexed ni.csv] [--min-impressions 50] \
     [--brand "acme|acme shop"] [--expected-ctr-1 0.11]
   ```

   `--brand`, `--expected-ctr-1`, and `--min-impressions` come from `config.md`. Small sites: `--min-impressions 20`. Large sites: 200 or more. The export's locale does not matter. `--brand` keeps navigational queries out of the striking-distance and CTR buckets; `--expected-ctr-1` scales the CTR curve to the site's own position-1 CTR (read it off the top non-brand queries; write the value back to `config.md` when it changes).
   Done when the report prints six buckets.

4. **Decide one action per row** with [references/actions.md](references/actions.md). The action per bucket is fixed; the judgement is whether the query matches the page's intent. Rows where the query means something other than what the page offers get skipped, with the note "different intent".
   Done when the top 10 rows across buckets 1–4 each carry URL, query, action, and the concrete new title, H1, or section heading where the action calls for one.

5. **Deliver** one table ordered by expected gain: missed clicks for CTR gaps, impressions for striking distance, lost clicks for decay. Rows that need writing go to `seo-content`; rows that need merging follow the merge recipe in actions.md; unindexed rows get internal links and a Request indexing. Every row the user accepts becomes an `Actions` row in this week's log (`scaffold.py <domain> --log` gives the path and the next id), Status `todo`; a row applied in this session gets `applied`, today's date, and `verify after` 14 days out for `ctr`, 28 days for the rest.
   Done when the log holds one row per accepted action.

## Interpretation

- Position is an average over queries, devices, and countries. A page at 9.4 may sit at 3 for one query and 30 for another; read the query-level rows before rewriting anything.
- High impressions with CTR near zero at position 5 or better usually means an AI Overview, featured snippet, or sitelink takes the click. In GSC every link inside one AI Overview shares a single position and a click from it counts as a normal click, so the row looks like a good position with a bad snippet. Rewrite the title and meta for a reason to click (number, year, outcome), then accept the ceiling. A page that wins the featured snippet is not repeated in the ten blue links (Google, January 2020), so its position can improve while clicks stay flat.
- Decay with a stable position is demand shift or a new SERP feature; decay with a worse position is content or competition. Only the second is fixed by updating the page. Confirm with GSC Compare, last 3 months year over year, weekly granularity: if the drop repeats last year's curve it is seasonal.
- Cannibalization needs page×query data; the UI export has none. Without `--page-queries`, filter one query in GSC and read its Pages tab. Google consolidates duplicates into one canonical rather than penalizing them, and Mueller (September 2025) calls several pages in one result "not problematic just because it's more than 1"; merge only pages that duplicate each other, differentiate the rest.
- The expected-CTR curve in the script is a heuristic. Study results for calibration: Sistrix, Germany, 100M keywords (2026): position 1 about 27 % overall, 11 % with an AI Overview; Ahrefs, 300,000 keywords, desktop (December 2025): 7.3 % without and 1.6 % with an AI Overview. Set `--expected-ctr-1` from the site's own data before trusting the CTR-gap bucket.
- The Generative AI performance report (all properties since August 31, 2026) shows impressions in AI Overviews and AI Mode by page, without clicks or queries. Use it to see which pages get cited; ranking in the top 10 no longer predicts citation (Ahrefs, 863,000 keywords, March 2026: 38 % of cited pages in the top 10).
- Fewer than 50 impressions per query is noise on a 28-day window. Widen the range instead of lowering the threshold below 20.
