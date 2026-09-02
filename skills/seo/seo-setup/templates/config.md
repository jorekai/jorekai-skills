# {{DOMAIN}}: site facts

Read before running any `seo-*` skill on this domain. One `key: value` per line so agents and scripts can parse it. Unknown stays blank; a guess is worse than a blank.

## Hosts

- canonical_host: https://{{DOMAIN}}
- other_hosts_redirect: (www, http, trailing-slash variants all 301 to canonical: yes/no)
- language:
- market: (country, or global)
- hreflang_variants: (none, or the list)

## Where things live in this repo

- framework:
- content_dir: (directory the site renders pages from)
- head_template: (file that emits `<title>`, meta description, canonical)
- sitemap: (path or generator, and how `lastmod` is set)
- robots_txt: (path)
- static_dir: (directory served at the site root; the IndexNow key file goes here)
- publish: (command or process that deploys)

## Search Console calibration

- brand_regex: (RE2, case-insensitive, e.g. `acme|acme shop`)
- expected_ctr_1: (position-1 CTR of the top non-brand queries as a decimal; 0.11 until an export says otherwise)
- min_impressions: (50; 20 on small sites; 200 or more on large sites)
- gsc_export_window: (28 days; 3 months on sites under about 50 clicks a day)

## Crawler policy

- ai_search_bots: (OAI-SearchBot, PerplexityBot, Bingbot, Claude-SearchBot, Google-Extended: allowed or blocked, per bot)
- training_bots: (GPTBot, ClaudeBot, Applebot-Extended: allowed or blocked; the owner's call)

## People

- author_of_record: (name on bylines, and the author page URL)
- approver: (who signs off drafts before they move into content_dir)
