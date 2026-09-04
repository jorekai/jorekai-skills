# Where the AI numbers come from

Three sources, read once a month, each line dated. Two are consoles the owner exports; the third is a fixed prompt set. None of them is a ranking: assistants personalize answers and do not repeat them, so the prompt set is a trend, not a measurement (heuristic).

## Generative AI performance report (Search Console)

All reports and tools > Performance reports > Generative AI performance report. Impressions only: how often links to the site appeared in AI Overviews and AI Mode. No clicks, no queries, no position. Groupings: pages (the final URL after redirects), countries, dates, devices. An export button covers chart and table; the newest days are preliminary. Web search only, Search Labs experiments excluded. Available for every property since 2026-08-31.

Report line: impressions this month against the month before, plus the three pages with the most.

## AI Performance report (Bing Webmaster Tools)

Citations in Copilot and Bing's AI answers, public preview since February 2026. Bing's index feeds several assistants, so this is the widest citation count available for free.

Report line: citations this month against the month before, plus the pages behind them.

## The prompt set (`strategy.md`)

Ten questions a customer would ask an assistant, written once during `jorekai-seo:grill`. Ten is the default; fewer is fine, changing a prompt later is not, because it breaks every earlier month.

Ask each prompt once per assistant, in the market's language, in a session with no history. Record how many answers name the site and which pages they cite.

- Same prompts, same order, same day of the month. A prompt added later starts its own row.
- A fresh session per assistant. A session that already discussed the site measures the session.
- Personalization, location, and model updates move these answers. Treat a change under about 2 in 10 as noise (heuristic).

## A page that is never cited

Not this skill's job. The answer-first paragraph belongs to `jorekai-seo:content`, being cited elsewhere to `jorekai-seo:links`, and why a top-10 ranking no longer predicts citation stands in the interpretation section of `jorekai-seo:gsc-review`.
