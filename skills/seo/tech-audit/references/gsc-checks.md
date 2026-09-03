# Google Search Console checks the script cannot run

Ask for a screenshot or export of each; judge green / open.

## Indexing > Pages

Every reason listed under "Not indexed" maps to one action:

| Reason | Meaning | Action |
|---|---|---|
| Crawled – currently not indexed | Google saw it and declined | Strengthen: internal links, unique substance, remove near-duplicates. Request indexing once. Still out after 4 weeks: merge into a stronger page or delete with 410. |
| Discovered – currently not indexed | Known URL; Google postponed the crawl, per its docs usually to avoid overloading the site | Faster server responses, internal links from strong pages, sitemap `lastmod`, fewer thin URLs. Small sites with good content often clear this without action. |
| Duplicate without user-selected canonical | Google picked another URL | Add a self-referencing canonical; make the pages differ, or merge. |
| Duplicate, Google chose different canonical than user | Google overrode your canonical | The pages are too similar. Merge and 301. |
| Alternate page with proper canonical tag | Working as designed | Nothing. |
| Excluded by noindex tag | Page carries noindex | Remove if it should rank. |
| Blocked by robots.txt | Crawl disallowed | Open the path, or accept. A `noindex` on a blocked URL is never seen; unblock first if the goal is removal. |
| Not found (404) / Soft 404 | Gone, empty, or the text reads like an error | Restore, 301, or leave as 404 (Google drops it). Soft 404 on a real page: reword the "not found" or "no results" copy, add substance. |
| Page with redirect | URL redirects | Update sitemap and internal links to the target. |
| Blocked due to access forbidden (403) / unauthorized (401) | Bot blocked | Allow Googlebot in the WAF or auth layer. |
| Server error (5xx) | Origin failed | Fix the origin, then Validate fix. |

"Validate fix" starts a check that Google says typically takes up to about two weeks and can take longer. Started means no remaining instance found yet; Passed means every known instance is gone; Failed means a threshold of pages still shows the issue. One validation per reason; do not re-click while it runs.

Sitemaps section: status "Success", discovered URL count near the real page count. A feed URL (RSS or Atom) can be submitted as an extra sitemap for recent posts.

## Experience > Core Web Vitals

Green thresholds at the 75th percentile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1. Mobile counts. Yellow or red on URL groups: run PageSpeed Insights on one URL from the group and fix the top diagnostic. Fix once per template, not per page.

Google's framing: Core Web Vitals feed the ranking systems, but "Google Search always seeks to show the most relevant content, even if the page experience is sub-par"; other page-experience aspects do not help ranking directly. Fix red, do not chase 100. About half of origins pass all three (Web Almanac 2025 on CrUX data from July 2025: 48 % mobile, 56 % desktop).

Fixes with the largest documented effect (web.dev):

- LCP: never lazy-load the LCP image; give it `fetchpriority="high"`, and `<link rel="preload">` when CSS or JS would otherwise delay its discovery. Split LCP into TTFB, resource load delay, resource load duration, render delay in PageSpeed Insights and fix the largest part; the two "delay" parts should approach zero.
- INP: break long tasks and yield to the main thread in event handlers; avoid layout thrashing (writing then reading styles in one task); keep the DOM small.
- CLS: `width` and `height` (or `aspect-ratio`) on every image and video; preload critical web fonts and control `font-display`.

## URL Inspection for the audited URL

- The default view is the last indexed version, not the live page. After a fix, run "Test live URL": it fetches and renders now. Confirm the rendered HTML contains the H1 and body text and that no blocked resource carries content.
- "URL is on Google" with the user-declared canonical equal to the Google-selected canonical.
- "URL is unknown to Google": Google has never seen the URL. Add internal links and the sitemap entry, then Request indexing.
- "Request indexing" after every content change. One request per URL; repeats do not speed it up. Google states "a daily limit" without a number and no guarantee of indexing (sources.md, URL Inspection row); when the button greys out, the day's limit is reached. Only the property owner can click it; the agent submits the same URLs to IndexNow with `connect/scripts/indexnow.sh`.

## Security & Manual Actions

Both sections read "No issues detected". A manual action overrides everything else in this skill; fix the cause, then Request review. Site reputation abuse (third-party content on a strong host, policy effective May 5, 2024, first-party involvement no defence since November 19, 2024) is enforced by manual action. For link-based actions: remove what can be removed, then disavow only the rest; Google says most sites never need the disavow tool.

## Generative AI performance report (since 2026)

Impressions of the site's links inside AI Overviews and AI Mode by page, country, date, device; no clicks, queries, or positions. Rolled out to all properties by August 31, 2026. In the normal Performance report these appear inside the Web search type: a click from an AI Overview counts as a click, and every link in one AI Overview shares a single position. Bing Webmaster Tools has an equivalent "AI Performance" citation report (public preview since February 2026).

## Video pages (only if the site embeds video)

Indexing > Video pages lists indexed pages with an indexed video and pages whose video was not indexed, with the reason. Covers indexed pages only. Since 2023 video results need the video to be the page's main content; `VideoObject` markup belongs only on the page where the video plays.

## Settings > Crawl stats (sites above ~1,000 URLs)

Response time stable, 5xx share near zero, crawl requests dominated by 200 HTML rather than redirects or 404s.

## Removed reports

The International targeting report (hreflang errors, country targeting) was removed in September 2022. Hreflang return-link errors now need a crawler that fetches every alternate.
