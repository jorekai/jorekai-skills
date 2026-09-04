# WordPress: recipes for a session on the server

Stack file for [../session-contract.md](../session-contract.md), which holds the protocol and the rules that apply to every stack. Everything here was verified on one WordPress site with Elementor, Rank Math, and FlyingPress on 2026-09-02 and 2026-09-03. Every line marked "observed" comes from that one site and is a heuristic anywhere else.

## Open the session with

- Stack: `wp core version`, `wp plugin list --status=active`, `wp theme list --status=active`.
- Backup before the first write: `wp db export`, on large databases with `--single-transaction --quick --skip-lock-tables`.
- Deploy code as one chain: `php -l file && cp file target && chown`.

## Where a string lives

- `wp db search '<path>' --all-tables` shows post_content, `_elementor_data` (JSON in postmeta), menus (`_menu_item_object`), widgets, or a plugin that inserts links at render time (auto-link plugins).
- The SEO plugin's sitemap can be a stale file cache; a page can be excluded because a manual canonical differs from the URL by a trailing slash.
- A theme option that hides the page title removes the H1 site-wide. Fix it in the template or in the plugin that wraps the content.

## Replace rules learned the hard way (2026-09-02, second pass)

The first pass on that site reported "0 hits" and left four links and six malformed hrefs in place. The second pass found why:

1. **Anchor the pattern on both sides.** Replacing `/path/` with `https://host/path/` turns a relative `href="/path/"` into `href="/https://host/path/"`. Search for `href="/path/"` and replace with `href="https://host/path/"`, or use the full host on both sides.
2. **Page-builder JSON stores escaped URLs.** In Elementor's `_elementor_data` the link is `https:\/\/host\/path\/` inside `href=\"…\"`. `wp search-replace`, `LIKE '%/path/%'`, and `grep '/path/'` miss it. Search and replace both forms, and count a re-check as complete only when both forms return zero.
3. **Validate the raw JSON.** `json_decode` on the stored meta value as is; `_elementor_data` is not slashed in the database, an unslash step before validation rejects valid JSON.
4. **Purge by hand after a direct write.** After `$wpdb->update` or `wp search-replace`: delete `_elementor_element_cache` on the post, `clean_post_cache`, `wp cache flush` for the object cache, then a per-URL purge through the page cache plugin's API (FlyingPress: `\FlyingPress\Purge::purge_urls([...])`, which also purges Cloudflare when connected). A dashboard "clear all" did not reach the pages in that run.
5. **Read the origin.** Fetch `127.0.0.1:<backend port>` with the `Host` header or the plugin's bypass cookie; a `HIT` header on a public fetch proves nothing about the database.
6. **Read the cache headers per user agent.** Observed 2026-09-03 right after a purge: a Googlebot user agent got `cf-cache-status: BYPASS` from Cloudflare and `MISS` from FlyingPress, a Chrome user agent got `MISS` then `HIT`; hours later the bot user agent got `HIT` from both. So a bot fetch may show the origin while the browser shows the cache, or both may show the cache. Cloudflare's own definitions: `HIT` served from cache, `MISS` cacheable but not cached yet, `BYPASS` cacheable by rule but the origin response said not to cache (see sources.md).
7. **An H1 can live in an HTML widget.** Elementor's `heading` widget is not the only place: on that site two H1s sat in `html` widgets (`_elementor_data`, escaped as `<\/h1>`, umlauts possibly as `\u00fc`). Then a raw replace in `_elementor_data` in whichever escape form the string uses, `json_decode` check, plus the same replace in `post_content` where Elementor mirrors the widget text (observed 2026-09-03).

## WP-CLI commands that carried the fixes

- Links in classic content: `wp search-replace 'https://host/old/' 'https://host/new/' <prefix>_posts --include-columns=post_content --dry-run`, then without `--dry-run`. Serialized PHP data is handled; Elementor JSON in postmeta needs a replace that validates the JSON afterwards and deletes `_elementor_element_cache` on the post.
- Rank Math per-post fields (observed meta keys on Rank Math Pro 3.0, 2026-09-02; heuristic): `wp post meta update <id> rank_math_title '...'`, `rank_math_description`, `rank_math_canonical_url`; `rank_math_robots` is a serialized array: write it as `wp post meta update <id> rank_math_robots '["noindex"]' --format=json` (passing the `a:1:{…}` string serializes it twice, observed 2026-09-03); `wp post meta delete <id> rank_math_canonical_url` to drop a stray canonical.
- Rank Math social titles: set `rank_math_facebook_title` and `rank_math_twitter_title` together, otherwise the old `og:title` or `twitter:title` stays (observed 2026-09-03). Title separators: `%sep%` in the value renders as the configured separator (sources.md, Rank Math variables).
- Rank Math home page: the fields live in the post meta of the page named by `wp option get page_on_front`; the `homepage_*` keys in `rank-math-options-titles` were empty and did not apply (observed 2026-09-03 with a static front page).
- Rank Math sitemap file cache: `wp eval 'RankMath\Sitemap\Cache::invalidate_storage();'` (observed; the cache lives under `wp-content/uploads/rank-math/`).
- Menu items: `wp post meta update <menu_item_id> _menu_item_object product` plus `_menu_item_object_id`; verify by rendering the page with a cache-bypass query string.
