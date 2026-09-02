# Fixing findings on a hosted site through a session on the server

For sites that live in a CMS on a server, not in this repository. The audit session hands the findings to a second agent session running on the server (SSH, `claude` there), which has WP-CLI, the database, and the file system. Verified once on a WordPress/Elementor/Rank Math site on 2026-09-02.

## What the handover prompt contains

1. Role and stack (CMS, page builder, SEO plugin, hosting panel) as far as `config.md` knows them; the server session verifies with `wp core version`, `wp plugin list --status=active`, `wp theme list --status=active`.
2. Rules: full database backup before the first write (`wp db export`, on large databases `--single-transaction --quick --skip-lock-tables`); every write shown as `--dry-run` or a read query first, then approval, then execution; one finding at a time; no plugin installs or theme edits without asking; deploy code only as `php -l file && cp file target && chown` in one chain; name every cache layer cleared.
3. The findings with exact URLs, the source page of every link, and the replacement target, one table per check id, copied from `audits/YYYY-MM-DD-tech.md`. Decisions the owner must take are phrased as options with a recommendation; the server session collects the facts first (Search Console clicks per URL where it has access, post type, template, where the link string lives).
4. The report format to send back: one row per finding with the exact command or admin path, date, verification. That table becomes the log rows.

## What the server session finds that the crawl cannot

- Where a link string lives: `wp db search '<path>' --all-tables` shows post_content, `_elementor_data` (JSON in postmeta), menus (`_menu_item_object`), widgets, or a plugin that inserts links at render time (auto-link plugins). A crawl only sees the rendered result.
- Drafts carry the same broken links; fix them in the same run or they come back on publish.
- Orphans on a builder site are often pages linked only from JavaScript (a map widget) or an HTML widget: the fix is a rendered list from the post type, not hand-written links.
- The SEO plugin's sitemap can be a stale file cache; the page can be excluded because a manual canonical differs from the URL by a trailing slash.
- A theme option that hides the page title removes the H1 site-wide; fix in the template or plugin that wraps the content, not per post.

## Replace rules learned the hard way (2026-09-02, second pass)

The first pass on that site reported "0 hits" and left four links and six malformed hrefs in place. The second pass found why:

1. **Anchor the pattern on both sides.** Replacing `/path/` with `https://host/path/` turns a relative `href="/path/"` into `href="/https://host/path/"`. Search for `href="/path/"` and replace with `href="https://host/path/"`, or use the full host on both sides.
2. **Page-builder JSON stores escaped URLs.** In Elementor's `_elementor_data` the link is `https:\/\/host\/path\/` inside `href=\"…\"`. `wp search-replace`, `LIKE '%/path/%'`, and `grep '/path/'` miss it. Search and replace both forms, and count a re-check as complete only when both forms return zero.
3. **Validate the raw JSON.** `json_decode` on the stored meta value as is; `_elementor_data` is not slashed in the database, an unslash step before validation rejects valid JSON.
4. **Direct database writes bypass the cache plugin's auto-purge.** After `$wpdb->update` or `wp search-replace`: delete `_elementor_element_cache` on the post, `clean_post_cache`, `wp cache flush` for the object cache, then a per-URL purge through the page cache plugin's API (FlyingPress: `\FlyingPress\Purge::purge_urls([...])`, which also purges Cloudflare when connected). A dashboard "clear all" did not reach the pages in that run.
5. **Verify at the origin, not through the CDN.** Fetch `127.0.0.1:<backend port>` with the `Host` header or the plugin's bypass cookie; a `HIT` header on a public fetch proves nothing about the database.

## WP-CLI commands that carried the fixes

- Links in classic content: `wp search-replace 'https://host/old/' 'https://host/new/' <prefix>_posts --include-columns=post_content --dry-run`, then without `--dry-run`. Serialized PHP data is handled; Elementor JSON in postmeta needs a replace that validates the JSON afterwards and deletes `_elementor_element_cache` on the post.
- Rank Math per-post fields (observed meta keys on Rank Math Pro 3.0, 2026-09-02; heuristic): `wp post meta update <id> rank_math_title '...'`, `rank_math_description`, `rank_math_robots` (serialized array), `rank_math_canonical_url`; `wp post meta delete <id> rank_math_canonical_url` to drop a stray canonical.
- Rank Math sitemap file cache: `wp eval 'RankMath\Sitemap\Cache::invalidate_storage();'` (observed; the cache lives under `wp-content/uploads/rank-math/`).
- Menu items: `wp post meta update <menu_item_id> _menu_item_object product` plus `_menu_item_object_id`; verify by rendering the page with a cache-bypass query string.
