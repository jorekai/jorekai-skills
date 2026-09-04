# Handing findings to a session on the server

For sites that live in a CMS on a server, not in this repository (`framework` in `config.md` names a hosted CMS, `head_template` is blank). The local session hands the findings to a second agent session running on the server (SSH, an agent CLI there), which has the CMS command line, the database, and the file system. Used by `jorekai-seo:tech-audit` (audit findings) and `jorekai-seo:gsc-review` (accepted snippet and content rows).

This file is the protocol and holds for every stack. The recipes for one stack sit next to it: [stacks/wordpress.md](stacks/wordpress.md). A new stack costs one file there and nothing here.

## What the handover prompt contains

1. Role and stack (CMS, page builder, SEO plugin, hosting panel) as far as `config.md` knows them. The server session verifies the versions itself before it touches anything, with the commands in the stack file.
2. Rules: a full database backup before the first write; every write shown as a dry run or a read query first, then approval, then execution; one finding at a time; no plugin installs or theme edits without asking; code deployed only through the chain in `deploy_rule` from `config.md`; every cache layer from `cache_layers` named and cleared.
3. The findings with exact URLs, the source page of every link, and the replacement target, one table per check id, copied from `audits/YYYY-MM-DD-tech.md`. Snippet rows from `jorekai-seo:gsc-review` come as one table per URL with the log id, the reason (impressions, position, CTR, what the current snippet gets wrong), and the exact new value per field (title, description, og:title, H1), characters counted. Decisions the owner must take are phrased as options with a recommendation; the server session collects the facts first (Search Console clicks per URL where it has access, post type, template, where the link string lives).
4. Two phases: VALIDATE (read and report, then stop) and CHANGE after an explicit go. The report format to send back: one row per finding with the exact command or admin path, date and time in UTC, verification; plus a section "Open, owner decision" for anything the session saw and did not touch. The table becomes the log rows (Outcome column, Status `applied`); every item under "Open, owner decision" becomes its own log row with bucket `tech` and Status `todo`, so `jorekai-seo:and-now` lists it. Save prompt and report as `audits/YYYY-MM-DD-vps-prompt.md` and `-vps-report.md`.

## What holds on every stack

- A crawl sees the rendered page; the server session sees where the string lives: post content, the page builder's own storage, menus, widgets, or a plugin that writes it at render time. Search the database for the string before reporting that it is not there.
- Drafts carry the same broken links as published pages. Fix them in the same run or they come back on the next publish.
- Orphans on a builder site are often pages linked only from JavaScript or from an embedded HTML block. The fix is a generated list from the post type, not hand-written links.
- A direct database write bypasses the cache plugin's own purge hook. Clear every layer by hand afterwards: object cache, page cache, CDN.
- Verify at the origin, not through the CDN, and with a bot and a browser user agent, reading the cache headers each time. A fix counts as verified only when both user agents show the new value and the headers say where the response came from.
- A theme or template option can remove an element site-wide (the page title, and with it the H1). Fix it where the element is emitted, not per page.
- Ad campaigns can still point at URLs that now redirect; they surface while redirects are cleaned. Report them as an owner decision and never remove a redirect or a page for that reason.
