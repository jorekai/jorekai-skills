# Getting the data out of Google Search Console

## Performance export (required)

1. GSC > Performance > Search results.
2. Date: Last 28 days (Last 3 months on sites under ~50 clicks/day).
3. Top right: Export > Download CSV. The zip contains Queries, Pages, Countries, Devices, Dates, Search appearance. Localized file names are fine.
4. For decay: repeat with a custom range covering the preceding period of the same length. Pass it as `--previous`.

The export is capped at 1,000 rows per table. Above that, use the API (50,000 rows per request) or the Bulk data export to BigQuery: the full table daily with no row limit, anonymised queries kept as rows without query text so totals stay complete; set a partition expiry, storage is billed after the free tier. GSC keeps 16 months of history; store exports if you need more.

## Filters worth applying before exporting

Query filters accept regular expressions (RE2 syntax, case-insensitive by default, prefix `(?-i)` for case-sensitive). No lookaheads or backreferences. Starting patterns, all heuristics, each with English and German terms; drop the German ones for other markets:

- Questions: `^(how|what|why|when|which|can|does|is|are|should|wie|was|warum|wann|welche|kann|ist)\b`
- Non-brand: "Doesn't match regex" with `acme|acme shop|akme`
- Commercial modifiers: `\b(best|vs|alternative|review|price|cost|beste|vergleich|erfahrung|preis|kosten)\b`
- Long tail (6+ words): `^(\S+\s+){5,}\S+$`

Compare mode (filter dialog > Compare) adds a Difference column; one comparison at a time; use weekly or monthly granularity so weekdays do not distort it. "Compare last 3 months year over year" separates seasonality from loss.

## Page × query table (for cannibalization)

Any of:

- Looker Studio with the Search Console connector: table with Landing page, Query, Clicks, Impressions, Position > Export CSV.
- Search Console API (`searchanalytics.query`, dimensions `page,query`) via a script or a sheet add-on.
- Manual: in GSC filter one query, open the Pages tab, note the URLs. Enough for the top 10 queries.

Header names are matched loosely: page/url, query/keyword, clicks, impressions, position.

## Not-indexed URL list

GSC > Indexing > Pages > click a reason under "Why pages aren't indexed" (usually "Crawled – currently not indexed") > Export. The CSV has `URL` and `Last crawled`; pass it as `--not-indexed`.
