# Page types and their skeletons

Beyond the weekly post, these four types earn commercial traffic. One query intent each.

## Weekly post (informational)

Query: a question the product's users ask. Skeleton: answer in two sentences, then why it matters, then step-by-step or breakdown with `[WHAT I TRIED]`, then pitfalls, then tools or resources, then FAQ. Original evidence is what separates it from the AI-generated copies competing for the same query.

## "Best X" (listicle)

Query: `best [category]`, `top [category] tools`. Skeleton: one-paragraph verdict with the top pick, then comparison table (name, best for, price, one standout, one limit), then one section per item: what it is, who it is for, `[OWN NUMBER]` or `[SCREENSHOT]`, price, verdict, then how we chose, then FAQ. 7–12 items. Your own product gets the same treatment as the rest, limits included.

## "X vs Y" (comparison)

Query: `[a] vs [b]`. Skeleton: verdict up front (which for whom), then side-by-side table, then one section per criterion (price, core feature, ease, integrations, support), then when to pick A, when to pick B, then FAQ. Neutral tone; the reader is choosing between the two.

## "X alternatives"

Query: `[competitor] alternatives`. Skeleton: why people leave X (three real reasons), then table of alternatives with "best for", then one section per alternative, then migration notes, then FAQ. Your product is one entry among the others.

## "How to [job]" (the exact job the product does)

Query: `how to [job]`. Skeleton: the answer in two sentences, then prerequisites, then numbered steps with a `[SCREENSHOT]` slot per step, then the manual way and the product way, side by side, then common errors, then FAQ. The product appears as one of the ways, with its trade-offs.

## Structured data note

`Article`, `Product`, `Organization`, and `BreadcrumbList` JSON-LD are worth adding when the template supports them; breadcrumbs show on desktop only since January 2025. FAQ and HowTo rich results have not been shown for ordinary sites since 2023; keep the FAQ section for readers and People-also-ask coverage, skip the schema. The sitelinks search box is gone since November 2024; its `SearchAction` markup does nothing. `VideoObject` only on the page where the video plays (`name`, `thumbnailUrl`, `uploadDate`; `Clip` or `SeekToAction` for key moments), and since 2023 only pages whose main content is the video get video results. `DiscussionForumPosting` is for user-generated forum posts only. `Organization`: `url`, `logo` (at least 112 by 112 px), `sameAs` to the company's profile pages; Google's docs do not mention Wikidata, so a Wikidata entry is unverified folklore, not a documented lever. A service business with an address adds `LocalBusiness` with `name`, `address`, `geo`, `telephone`, `openingHoursSpecification`.

## AI Overviews, AI Mode, and AI assistants

Google states there are "no additional requirements" for AI Overviews or AI Mode: the page must be indexed and snippet-eligible, and `nosnippet`, `data-nosnippet`, `max-snippet`, and `noindex` are the only controls. No file, tag, or schema opts a page in; llms.txt has no known consumer (Mueller, 2026). What changes the odds is a direct, quotable answer near the top and being findable for the sub-questions Google fans out into. Study results, not rules: Ahrefs (863,000 keywords, March 2026) found only 38 % of AI-Overview-cited pages in the organic top 10; Seer Interactive (3,119 terms, September 2025) found cited brands earn 35 % more organic CTR than uncited ones on the same SERP.

## Featured snippets

Google picks the passage that answers the question; there is no markup. The winning page is not repeated in the ten blue links (January 2020). `max-snippet` set too low removes eligibility; `data-nosnippet` hides a passage from all snippets.

## Google Discover

Eligibility is automatic for indexed pages that meet the content policies; Google warns against clickbait. Large image cards need an image at least 1200 px wide, more than 300,000 pixels, ideally 16:9, and `max-image-preview:large`. Discover has been expanding to desktop since 2025.
