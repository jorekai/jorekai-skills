---
name: seo-tech-audit
description: Audit a URL or whole site for technical SEO and indexability: runs scripts/audit.py (bot rendering, title/meta/H1/canonical, noindex conflicts, robots.txt, sitemap lastmod, redirects and their type, hreflang, dates, images, host variants, soft 404, pagination, duplicates, orphans) and prescribes fixes. Use when asked to check a site for SEO, why a page is not indexed, before a launch, or for canonical, redirect, sitemap, or robots questions.
---

# Tech SEO audit

With a workspace, `docs/seo/<domain>/config.md` names the files to fix (`head_template`, `sitemap`, `robots_txt`, `static_dir`) and the canonical host; step 2 goes straight there.

## Steps

1. **Run the audit.** One page plus site-level checks; add `--crawl` for duplicate titles, broken links, and orphans. The crawl is polite (0.25 s between requests), so 100 pages take about a minute.

   ```bash
   python3 scripts/audit.py https://example.com/page --crawl 100
   ```

   The path is relative to this skill's directory. `--json` gives machine-readable output.
   Done when the report printed without an `http.fetch` failure. A fetch failure means DNS, TLS, or timeout: report that first, nothing else is measurable.

2. **Map every FAIL and WARN to a fix** with [references/fixes.md](references/fixes.md), keyed by check id. Inside the site's repository, apply the fix in the layout or template that emits the `<head>` instead of describing it: `head_template` from `config.md`, or grep for `<title`, `rel="canonical"`, `sitemap`, `robots`.
   Done when every FAIL has a code change or a named owner and every WARN has a decision: fixed, or accepted with the reason.

3. **Cover what the script cannot see.** GSC-only signals: Pages report reasons, Core Web Vitals, URL Inspection verdicts, manual actions. Walk [references/gsc-checks.md](references/gsc-checks.md) with the user, or ask for the screenshots and exports it names.
   Done when each item there is green or listed as open with its reason.

4. **Deliver** one list ordered Critical → High → Hygiene. Critical blocks indexing: fetch, noindex, robots (including noindex hidden behind a robots block), canonical pointing elsewhere, client-only rendering, soft 404, duplicate hosts. High costs ranking or signals: title, H1, thin text, redirect chains and temporary redirects, hreflang errors, pagination canonicals, images without src, orphans, duplicates. Hygiene is every INFO. Each row: check id, affected URLs, the fix, how to verify (re-run the script, or GSC URL Inspection → Test live URL). Each fix applied gets a `tech` row in the week's log (`scaffold.py <domain> --log` in `seo-setup`), `verify after` 14 days out.

## Reading the report

- `render.bot-html` FAIL is the most expensive finding: the index sees an empty page. Server-render or pre-render; confirm with `curl -sA Googlebot URL | grep '<h1'`.
- `head.canonical` pointing elsewhere is correct for paginated, filtered, or syndicated pages and wrong for anything meant to rank. Ask before changing it.
- `head.noindex` is a FAIL on a page meant to rank and correct on thank-you, admin, and internal search pages.
- Crawl findings cover the crawled set only. "Orphan check skipped" means raise `--crawl` until the queue drains, or accept the gap.
- The script reads HTML only. Speed is judged by GSC's Core Web Vitals report, not by the TTFB warning here.
- `head.hreflang` checks self-reference, x-default, and code format on this page only; return links on the alternates are not fetched.
- `site.sitemap-lastmod` fires when 90 % or more of URLs share one date: a generator stamping the build time. Google discards lastmod it cannot trust, so that sitemap loses its freshness signal.
