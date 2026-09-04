# The six hypotheses

Ordered by how cheaply they are ruled out. For each: the shape that fits, the prediction, the check, the fix. Sources in `seo/references/sources.md`.

## 1. Seasonality or demand shift

- Shape: impressions down, position flat, often sitewide or a topic cluster.
- Prediction: the same dip appears last year at the same weeks.
- Check: the site baseline from `jorekai-seo:gsc-review`'s script first, because it costs one command: a page that fell no further than the median page did not drop, the site did. Then Performance > Compare "last 3 months year over year", weekly granularity, plus "Last 16 months" for the curve. Google Trends for the head query.
- Fix: none on the page. Close as expected `no-change`; plan content for the next peak.

## 2. A SERP feature took the click

- Shape: impressions flat, position flat or better, clicks and CTR down. Single query or page.
- Prediction: the live SERP for the query shows an AI Overview, featured snippet, video carousel, or a competitor's rich result that was not there before; in Search Console, a link inside an AI Overview shares one position with every other link in it.
- Check: search the query in the target market; compare against the dated lines under "SERP observations" in the page's brief; compare the CTR-gap bucket in the last `jorekai-seo:gsc-review`; the Generative AI performance report for AI Overview impressions. A block that stands there today confirms nothing about the week the clicks fell: without an earlier dated observation this hypothesis stays open, and saying so is the finding.
- Fix: title and meta for a reason to click, a direct answer in the first paragraph to be the cited source; accept the ceiling. `jorekai-seo:gsc-review` actions.md, CTR gap.

## 3. Google update

- Shape: sitewide, sharp, starts within a day or two of an announced update; many pages move together.
- Prediction: the drop's start date matches an entry in Google's ranking-updates history (core update, spam update, or another announced change), and the Pages table shows a broad move rather than one URL.
- Check: `https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history` for dates; Manual actions and Security issues reports both empty (a manual action overrides everything else).
- Fix: no quick edit exists. Spam or site-reputation issues: remove the violating content, then Request review. Core update: the pages that lost are compared against the helpful-content questions and improved through `jorekai-seo:content` refreshes; recovery is measured over the next update, not the next week.

## 4. Technical regression

- Shape: sudden, page or template group, impressions and position both gone or falling; "Page with redirect", "Excluded by noindex", "Crawled, currently not indexed" rising in the Pages report.
- Prediction: the audit script or URL Inspection shows a blocker on the affected URLs that was not there before the drop date.
- Check: `jorekai-seo:tech-audit` on three affected URLs (render, noindex, canonical, redirect, soft 404, hosts); URL Inspection live test; `git log --since=<drop date>` on `head_template`, `robots_txt`, the sitemap generator, redirects and routing config; Crawl stats for 5xx and response time.
- Fix: the audit's fix per check id; then Request indexing on the touched URLs and Validate fix in the Pages report.

## 5. Own-site change

- Shape: one page or a cluster, starting right after a deploy, redesign, migration, or a new page on the same topic.
- Prediction: `git log` around the drop date touched the page, its internal links, its URL, or added a page competing for the same query; Search Console shows a second URL rising for the query while the first falls.
- Check: `git log --grep="SEO-Log:" --since=<drop date>` lists the changes the loop itself made, each with its log row id; then the git history of the page and of navigation and templates; the cannibalization bucket in `jorekai-seo:gsc-review` (needs page×query data); internal link count to the page before and after (the audit's crawl mode). Site outside a repository: the CMS revision history of the page, the redirect map of the last move, and the log's `tech` rows covering the drop date.
- Fix: restore what was removed (sections, internal links, the old URL via 301), or merge and 301 the competing page; then Request indexing.

## 6. Competition or content decay

- Shape: gradual, one page or a cluster, position sliding over weeks, impressions roughly flat at first.
- Prediction: the current top 3 for the query show pages newer or fuller than yours: a section you lack, fresher numbers, a format the SERP now prefers.
- Check: fetch the top 3; diff their H2s and format against the page; check their dates.
- Fix: the decay recipe in `jorekai-seo:gsc-review` actions.md: material update, new section, fresh evidence, date moved only after the body changed; via `jorekai-seo:content` refresh.
