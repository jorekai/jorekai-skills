#!/usr/bin/env python3
"""Technical SEO audit for one URL, optionally crawling the site behind it.

Stdlib only. Fetches with a Googlebot user agent (what the index sees) and
compares against a browser user agent to detect JS-only content.

Usage:
  audit.py URL [--crawl N] [--timeout S] [--delay S] [--json]

A crawl costs about one second per page (fetch plus --delay); run large crawls
in the background and write --json to a file. Cart, checkout, and account URLs
are counted but not fetched; tracking parameters are stripped before a URL is
queued and reported under crawl.tracking-params.

Exit code 0 always; findings are in the report, not the exit status.
"""
import argparse
import json
import random
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import Counter, deque
from html.parser import HTMLParser

UA_BOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
UA_BROWSER = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
MAX_BODY = 3_000_000
# Query parameters that only track a click. An internal link carrying one creates a URL variant.
TRACKING_PARAMS = re.compile(r"^(utm_\w+|gclid|gbraid|wbraid|fbclid|msclkid|dclid|mc_cid|mc_eid|_ga|_gl|ref|source)$", re.I)
# Cart, checkout, and account URLs (WooCommerce English and German slugs, Shopify, generic). Never indexable, never worth a fetch.
CART_RE = re.compile(r"[?&](add-to-cart|remove_item|wc-ajax|undo_item)=|/(cart|checkout|basket|my-account|warenkorb|kasse|mein-konto)(/|$)", re.I)
# English and German stopwords; the audit is used on sites in both languages.
STOPWORDS = set("a an the and or of for to in on with vs versus your my is are how what why "
                "best top guide de der die das und für mit von im am zu ein eine".split())

# --------------------------------------------------------------------------- fetch

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def fetch(url, ua=UA_BOT, timeout=15, max_hops=10, delay=0.0):
    """Follow redirects manually and return the full chain plus final response."""
    chain = []
    current = url
    for _ in range(max_hops):
        if delay:
            time.sleep(delay)
        req = urllib.request.Request(current, headers={"User-Agent": ua,
                                                        "Accept": "text/html,*/*;q=0.8",
                                                        "Accept-Language": "en,de;q=0.8"})
        t0 = time.time()
        try:
            with _OPENER.open(req, timeout=timeout) as resp:
                status = resp.status
                headers = {k.lower(): v for k, v in resp.headers.items()}
                raw = resp.read(MAX_BODY)
        except urllib.error.HTTPError as e:
            status = e.code
            headers = {k.lower(): v for k, v in e.headers.items()}
            try:
                raw = e.read(MAX_BODY)
            except Exception:
                raw = b""
        except Exception as e:  # DNS, timeout, TLS
            chain.append((current, None))
            return {"url": url, "chain": chain, "final_url": current, "status": None,
                    "headers": {}, "body": "", "error": str(e), "elapsed": time.time() - t0}
        elapsed = time.time() - t0
        chain.append((current, status))
        if 300 <= status < 400 and "location" in headers:
            current = urllib.parse.urljoin(current, headers["location"])
            continue
        ctype = headers.get("content-type", "")
        body = ""
        if raw and ("html" in ctype or "xml" in ctype or "text" in ctype or not ctype):
            m = re.search(r"charset=([\w-]+)", ctype)
            enc = m.group(1) if m else "utf-8"
            try:
                body = raw.decode(enc, errors="replace")
            except LookupError:
                body = raw.decode("utf-8", errors="replace")
        return {"url": url, "chain": chain, "final_url": current, "status": status,
                "headers": headers, "body": body, "error": None, "elapsed": elapsed}
    chain.append((current, "loop"))
    return {"url": url, "chain": chain, "final_url": current, "status": None,
            "headers": {}, "body": "", "error": "too many redirects", "elapsed": 0}

# --------------------------------------------------------------------------- parse

class Page(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.title = None
        self._in_title = False
        self._skip = 0  # inside script/style/noscript/template
        self._in_h1 = False
        self.h1s = []
        self.metas = {}
        self.canonicals = []
        self.images = []  # (src, has_alt)
        self.links = []  # (href, rel)
        self.text_chars = 0
        self.script_bytes = 0
        self._in_script = False
        self.jsonld = 0
        self.lang = None
        self.hreflang = []  # (hreflang, href)
        self.feeds = []  # (type, href)
        self.meta_refresh = None
        self.jsonld_texts = []
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag in ("script", "style", "noscript", "template"):
            self._skip += 1
            if tag == "script":
                self._in_script = True
                if (a.get("type") or "").lower() == "application/ld+json":
                    self.jsonld += 1
                    self._in_jsonld = True
                    self.jsonld_texts.append("")
        elif tag == "h1":
            self._in_h1 = True
            self.h1s.append("")
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if key:
                self.metas.setdefault(key, a.get("content", ""))
            if key == "refresh":
                self.meta_refresh = a.get("content", "")
        elif tag == "link":
            rel = (a.get("rel") or "").lower().split()
            if "canonical" in rel and a.get("href"):
                self.canonicals.append(urllib.parse.urljoin(self.base, a["href"].strip()))
            if "alternate" in rel and (a.get("type") or "").lower() in ("application/rss+xml", "application/atom+xml") and a.get("href"):
                self.feeds.append((a["type"].lower(), urllib.parse.urljoin(self.base, a["href"].strip())))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append((a["hreflang"].strip(), urllib.parse.urljoin(self.base, (a.get("href") or "").strip())))
        elif tag == "img":
            self.images.append({"src": a.get("src") or a.get("data-src") or "", "alt": "alt" in a,
                                "has_src": bool(a.get("src")), "lazy": (a.get("loading") or "").lower() == "lazy",
                                "sized": bool(a.get("width") and a.get("height"))})
        elif tag == "a" and a.get("href"):
            href = a["href"].strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                self.links.append((urllib.parse.urljoin(self.base, href), (a.get("rel") or "").lower()))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("script", "style", "noscript", "template"):
            self._skip = max(0, self._skip - 1)
            if tag == "script":
                self._in_script = False
                self._in_jsonld = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_title:
            self.title = ((self.title or "") + data).strip()
            return
        if self._in_script:
            self.script_bytes += len(data)
            if self._in_jsonld and self.jsonld_texts:
                self.jsonld_texts[-1] += data
        if self._skip:
            return
        stripped = data.strip()
        if stripped:
            self.text_chars += len(stripped)
            if self._in_h1 and self.h1s:
                self.h1s[-1] = (self.h1s[-1] + " " + stripped).strip()


def parse(body, base):
    p = Page(base)
    try:
        p.feed(body)
    except Exception:
        pass
    return p

# --------------------------------------------------------------------------- helpers

def tokens(s):
    return {t for t in re.split(r"[^a-z0-9äöüß]+", (s or "").lower()) if len(t) > 2 and t not in STOPWORDS}


def norm(url):
    """Normalize for comparisons: drop fragment, lowercase host, strip trailing slash (not root)."""
    u = urllib.parse.urlsplit(url)
    path = u.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return urllib.parse.urlunsplit((u.scheme.lower(), u.netloc.lower(), path, u.query, ""))


def strip_tracking(url):
    """Return the URL without tracking parameters (utm_*, gclid, fbclid, ...), other parameters kept."""
    u = urllib.parse.urlsplit(url)
    if not u.query:
        return url
    kept = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True) if not TRACKING_PARAMS.match(k)]
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, urllib.parse.urlencode(kept), u.fragment))


def is_cart(url):
    return bool(CART_RE.search(url))


def same_site(a, b):
    ha = urllib.parse.urlsplit(a).netloc.lower().removeprefix("www.")
    hb = urllib.parse.urlsplit(b).netloc.lower().removeprefix("www.")
    return ha == hb


def looks_random(slug):
    return bool(re.search(r"[0-9a-f]{8,}|\d{6,}|(?=[a-z]*\d)(?=\d*[a-z])[a-z0-9]{14,}", slug))


class Report:
    def __init__(self):
        self.items = []  # (section, level, check_id, message)

    def add(self, section, level, cid, msg, data=None):
        """data: the full list behind a message that shows only examples; printed by --json."""
        item = {"section": section, "level": level, "id": cid, "message": msg}
        if data is not None:
            item["data"] = data
        self.items.append(item)

    def counts(self):
        return Counter(i["level"] for i in self.items)

# --------------------------------------------------------------------------- page checks

def check_page(url, rep, timeout, delay, section="Page", compare_ua=True):
    bot = fetch(url, UA_BOT, timeout, delay=delay)
    if bot["error"] or bot["status"] is None:
        rep.add(section, "FAIL", "http.fetch", f"{url}: {bot['error']}")
        return bot, None
    final = bot["final_url"]
    hops = len(bot["chain"]) - 1
    if hops:
        chain = " -> ".join(f"{u} [{s}]" for u, s in bot["chain"])
        level = "WARN" if hops > 1 else "INFO"
        rep.add(section, level, "http.redirect-chain",
                f"{hops} redirect hop(s): {chain}" + (" (collapse to a single 301)" if hops > 1 else "")
                + (" (Google's crawlers follow at most 10 hops; Mueller advises under 5)" if hops >= 5 else ""))
        temp = [s for _, s in bot["chain"] if s in (302, 303, 307)]
        if temp:
            rep.add(section, "WARN", "http.redirect-temporary",
                    f"Chain uses temporary redirect(s) {temp}: Google follows them but does not treat the target as canonical. "
                    "Use 301 or 308 for a permanent move.")
    if bot["status"] != 200:
        rep.add(section, "FAIL", "http.status", f"{final} returned {bot['status']}")
        return bot, None
    if not final.startswith("https://"):
        rep.add(section, "FAIL", "http.https", f"{final} is served without HTTPS")
    xrobots = bot["headers"].get("x-robots-tag", "")
    p = parse(bot["body"], final)
    robots_meta = (p.metas.get("robots", "") + " " + p.metas.get("googlebot", "") + " " + xrobots).lower()
    noindex = "noindex" in robots_meta
    if noindex:
        rep.add(section, "FAIL", "head.noindex", f"{final} carries noindex ({robots_meta.strip()}). Intended?")
    if p.meta_refresh is not None:
        delay = re.match(r"\s*(\d+)", p.meta_refresh or "")
        instant = delay and int(delay.group(1)) == 0
        rep.add(section, "WARN", "head.meta-refresh",
                f"Meta refresh present ({p.meta_refresh!r}): Google reads an instant one as a permanent redirect and a delayed one as temporary. "
                "Prefer a server-side 301/308." if instant else
                f"Delayed meta refresh ({p.meta_refresh!r}): Google treats it as a temporary redirect. Prefer a server-side 301/308.")

    # Rendering: does the bot response carry real content?
    if compare_ua:
        if p.text_chars < 300:
            browser = fetch(final, UA_BROWSER, timeout, delay=delay)
            pb = parse(browser["body"], final) if browser["body"] else None
            if pb and pb.text_chars > p.text_chars * 2 + 200:
                rep.add(section, "FAIL", "render.bot-html",
                        f"Googlebot UA gets {p.text_chars} chars of text, browser UA gets {pb.text_chars}: "
                        "server discriminates by user agent")
            elif p.script_bytes > 20_000 or len(re.findall(r"<script", bot["body"], re.I)) > 5:
                rep.add(section, "FAIL", "render.bot-html",
                        f"Only {p.text_chars} chars of visible text in the HTML but heavy JS: "
                        "content is probably client-rendered. Serve it as HTML (SSR/SSG).")
            else:
                rep.add(section, "WARN", "render.thin", f"Only {p.text_chars} chars of visible text in the HTML")
        else:
            rep.add(section, "PASS", "render.bot-html", f"{p.text_chars} chars of visible text in raw HTML")

    # Head
    if not p.title:
        rep.add(section, "FAIL", "head.title", "No <title>")
    else:
        n = len(p.title)
        if n > 60:
            rep.add(section, "WARN", "head.title", f"Title is {n} chars (heuristic: about 60, Google truncates by pixel width; keyword first): “{p.title}”")
        elif n < 20:
            rep.add(section, "WARN", "head.title", f"Title is only {n} chars: “{p.title}”")
        else:
            rep.add(section, "PASS", "head.title", f"“{p.title}” ({n} chars)")
    desc = p.metas.get("description")
    if not desc:
        rep.add(section, "WARN", "head.meta-description", "No meta description (Google will invent one)")
    elif len(desc) > 160:
        rep.add(section, "WARN", "head.meta-description", f"Meta description is {len(desc)} chars (heuristic: 120–160; Google sets no limit)")
    else:
        rep.add(section, "PASS", "head.meta-description", f"{len(desc)} chars")
    if not p.canonicals:
        rep.add(section, "FAIL", "head.canonical", "No canonical link. Add a self-referencing absolute canonical.")
    elif len(p.canonicals) > 1:
        rep.add(section, "FAIL", "head.canonical", f"{len(p.canonicals)} canonical links: {p.canonicals}")
    else:
        c = p.canonicals[0]
        if not c.startswith("http"):
            rep.add(section, "WARN", "head.canonical", f"Canonical is not absolute: {c}")
        elif norm(c) != norm(final):
            rep.add(section, "WARN", "head.canonical", f"Canonical points elsewhere: {c} (this page will not be indexed on its own URL. Intended?)")
            if noindex:
                rep.add(section, "WARN", "head.noindex-canonical",
                        "noindex plus a canonical to another URL on the same page: mixed signals. Pick one (Mueller, 2024).")
            m = re.search(r"(?:[?&]page=|/page/|/seite/)(\d+)", final)
            if m and int(m.group(1)) >= 2:
                rep.add(section, "WARN", "url.pagination-canonical",
                        f"Paginated page {m.group(1)} canonicalizes to another URL. Google: give each page its own canonical, do not point page 2+ at page 1.")
        else:
            rep.add(section, "PASS", "head.canonical", "self-referencing")
    if "viewport" not in p.metas:
        rep.add(section, "FAIL", "head.viewport", "No viewport meta: page is not mobile-friendly")
    if not p.lang:
        rep.add(section, "WARN", "head.lang", "No lang attribute on <html>")
    if p.hreflang:
        codes = [c.lower() for c, _ in p.hreflang]
        problems = []
        if not any(norm(h) == norm(final) for _, h in p.hreflang):
            problems.append("no self-referencing alternate (each version must list itself)")
        if "x-default" not in codes:
            problems.append("no x-default")
        bad = [c for c, _ in p.hreflang if c.lower() != "x-default" and not re.fullmatch(r"[a-z]{2,3}(-[a-z]{2}|-[0-9]{3}|-[a-z]{4}(-[a-z]{2})?)?", c.lower())]
        bad += [c for c, _ in p.hreflang if c.lower().split("-")[-1] in ("uk", "eu", "un")]
        if bad:
            problems.append(f"invalid codes {sorted(set(bad))} (language first, ISO 3166 region; UK/EU/UN are ignored)")
        if problems:
            rep.add(section, "WARN", "head.hreflang", f"{len(p.hreflang)} hreflang alternates, " + "; ".join(problems))
        else:
            rep.add(section, "PASS", "head.hreflang", f"{len(p.hreflang)} alternates incl. self and x-default (return links not verified)")
    dates = {}
    for t in p.jsonld_texts:
        for key in ("datePublished", "dateModified"):
            m = re.search(r'"%s"\s*:\s*"(\d{4}-\d{2}-\d{2})' % key, t)
            if m:
                dates.setdefault(key, m.group(1))
    if dates:
        today = time.strftime("%Y-%m-%d")
        future = [f"{k}={v}" for k, v in dates.items() if v > today]
        if future:
            rep.add(section, "WARN", "head.dates", f"Structured-data date in the future: {future}. Google: dates must be the real publish/update date, never a future date.")
        elif "datePublished" in dates and "dateModified" in dates and dates["dateModified"] < dates["datePublished"]:
            rep.add(section, "WARN", "head.dates", f"dateModified {dates['dateModified']} is before datePublished {dates['datePublished']}")
        else:
            rep.add(section, "INFO", "head.dates", f"JSON-LD dates {dates}; the visible date on the page must match them (not checked)")
    if not p.jsonld:
        rep.add(section, "INFO", "head.json-ld", "No JSON-LD structured data")
    missing_og = [k for k in ("og:title", "og:description", "og:image") if k not in p.metas]
    if missing_og:
        rep.add(section, "INFO", "head.open-graph", f"Missing Open Graph tags: {', '.join(missing_og)}")

    # Body
    if not p.h1s:
        rep.add(section, "WARN", "body.h1", "No <h1> (Google does not require one; readers and the title/H1 keyword match do)")
    elif len(p.h1s) > 1:
        rep.add(section, "INFO", "body.h1", f"{len(p.h1s)} <h1> elements (Google accepts several; one is the convention): {p.h1s[:3]}")
    else:
        rep.add(section, "PASS", "body.h1", f"“{p.h1s[0]}”")
    # English and German error phrases (soft-404 detection).
    err_words = r"not found|no results|nicht gefunden|keine ergebnisse|page unavailable|seite nicht verfügbar|404"
    err_hit = [x for x in ([p.title or ""] + p.h1s[:1]) if re.search(err_words, x, re.I)]
    if err_hit:
        rep.add(section, "WARN", "body.error-text", f"Title or H1 reads like an error page: {err_hit[:1]}. Google may classify a 200 page as soft 404 from its text alone.")
    if p.h1s and p.title:
        overlap = tokens(p.h1s[0]) & tokens(p.title)
        if not overlap:
            rep.add(section, "WARN", "body.h1-title-match", "H1 and title share no keyword")
    slug = urllib.parse.urlsplit(final).path.rstrip("/").split("/")[-1]
    if urllib.parse.urlsplit(final).query:
        rep.add(section, "WARN", "url.query-string", "Indexable URL carries a query string")
    if slug:
        if looks_random(slug):
            rep.add(section, "WARN", "url.slug", f"Slug looks machine-generated: {slug}")
        if "_" in slug or slug != slug.lower():
            rep.add(section, "WARN", "url.slug", f"Slug uses underscores or uppercase: {slug}")
        if p.h1s and not (tokens(slug.replace("-", " ")) & tokens(p.h1s[0])):
            rep.add(section, "INFO", "url.slug-h1-match", f"Slug “{slug}” shares no keyword with the H1 (a very small ranking factor; matters for readers and link previews)")
    imgs = [i for i in p.images if not i["src"].startswith("data:")]
    noalt = [i["src"] for i in imgs if not i["alt"]]
    if imgs and noalt:
        rep.add(section, "WARN", "img.alt", f"{len(noalt)}/{len(imgs)} images without alt attribute, e.g. {noalt[:3]}")
    elif imgs:
        rep.add(section, "PASS", "img.alt", f"all {len(imgs)} images have alt")
    nosrc = [i["src"] for i in imgs if not i["has_src"]]
    if nosrc:
        rep.add(section, "WARN", "img.src-fallback", f"{len(nosrc)} <img> without a src attribute (data-src only), e.g. {nosrc[:3]}. Google asks for a fallback src; JS-only lazy loading hides the image until rendering.")
    if imgs and imgs[0]["lazy"]:
        rep.add(section, "WARN", "img.lcp-lazy", f"First image is loading=\"lazy\" ({imgs[0]['src']}). If it is the LCP element, lazy-loading delays LCP; use fetchpriority=\"high\" instead (web.dev).")
    unsized = [i["src"] for i in imgs if not i["sized"]]
    if imgs and len(unsized) > len(imgs) // 2:
        rep.add(section, "INFO", "img.dimensions", f"{len(unsized)}/{len(imgs)} images without width and height attributes (layout shift risk, CLS)")
    internal = [h for h, _ in p.links if same_site(h, final)]
    if not internal:
        rep.add(section, "WARN", "links.internal", "No internal links on the page")
    else:
        rep.add(section, "PASS", "links.internal", f"{len(internal)} internal links")
    if bot["elapsed"] > 2.5:
        rep.add(section, "WARN", "http.ttfb", f"HTML took {bot['elapsed']:.1f}s to arrive")
    return bot, p

# --------------------------------------------------------------------------- site checks

def check_site(start_final, rep, timeout, delay, page=None):
    u = urllib.parse.urlsplit(start_final)
    origin = f"{u.scheme}://{u.netloc}"
    host = u.netloc
    sitemap_urls = set()

    # robots.txt
    rtxt = fetch(origin + "/robots.txt", UA_BOT, timeout, delay=delay)
    rp = None
    if rtxt["status"] == 200 and rtxt["body"]:
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(rtxt["body"].splitlines())
        if not rp.can_fetch("Googlebot", start_final):
            rep.add("Site", "FAIL", "site.robots", f"robots.txt blocks Googlebot from {start_final}")
            if page is not None and "noindex" in (page.metas.get("robots", "") + page.metas.get("googlebot", "")).lower():
                rep.add("Site", "FAIL", "site.robots-noindex",
                        "Page is blocked by robots.txt and carries noindex: Google never sees the noindex, the URL can stay indexed. Unblock it if the goal is removal.")
        else:
            rep.add("Site", "PASS", "site.robots", "robots.txt present, page allowed")
        blocked_ai = [b for b in ("OAI-SearchBot", "PerplexityBot", "Bingbot", "Claude-SearchBot") if not rp.can_fetch(b, start_final)]
        if blocked_ai:
            rep.add("Site", "WARN", "site.robots-ai-search", f"robots.txt blocks {', '.join(blocked_ai)}: the page cannot be cited by ChatGPT search / Perplexity / Bing-based assistants / Claude")
        sm = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", rtxt["body"])
        if sm:
            sitemap_urls.update(sm)
        else:
            rep.add("Site", "WARN", "site.robots-sitemap", "robots.txt has no Sitemap: line")
    else:
        rep.add("Site", "WARN", "site.robots", f"robots.txt returned {rtxt['status']} (add one: allow public paths, list the sitemap)")
    if not sitemap_urls:
        sitemap_urls.add(origin + "/sitemap.xml")

    # sitemap
    urls_in_sitemap = set()
    lastmod = 0
    lastmod_values = []
    seen_maps = set()
    queue = deque(sitemap_urls)
    while queue and len(seen_maps) < 20:
        smu = queue.popleft()
        if smu in seen_maps:
            continue
        seen_maps.add(smu)
        r = fetch(smu, UA_BOT, timeout, delay=delay)
        if r["status"] != 200 or not r["body"]:
            rep.add("Site", "FAIL", "site.sitemap", f"{smu} returned {r['status'] if r['status'] else 'no response (' + str(r['error']) + ')'}")
            continue
        body = r["body"]
        if "<sitemapindex" in body:
            queue.extend(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body))
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
        urls_in_sitemap.update(locs)
        mods = re.findall(r"<lastmod>\s*([^<\s]+)\s*</lastmod>", body)
        lastmod += len(mods)
        lastmod_values.extend(mods)
    if urls_in_sitemap:
        foreign = [x for x in urls_in_sitemap if not same_site(x, origin)]
        http_only = [x for x in urls_in_sitemap if x.startswith("http://")]
        msg = f"{len(urls_in_sitemap)} URLs in {len(seen_maps)} sitemap file(s), {lastmod} with <lastmod>"
        rep.add("Site", "PASS" if lastmod else "WARN", "site.sitemap",
                msg + ("" if lastmod else ". Add real <lastmod> dates; Google ignores priority/changefreq"))
        if lastmod_values:
            today = time.strftime("%Y-%m-%d")
            days = [v[:10] for v in lastmod_values]
            future = [v for v in days if v > today]
            top, top_n = Counter(days).most_common(1)[0]
            if future:
                rep.add("Site", "WARN", "site.sitemap-lastmod", f"{len(future)} <lastmod> values lie in the future (e.g. {future[:2]}); Google discards lastmod it cannot trust")
            if len(days) >= 10 and top_n >= 0.9 * len(days):
                rep.add("Site", "WARN", "site.sitemap-lastmod",
                        f"{top_n}/{len(days)} URLs share the same <lastmod> {top}: looks like the generation date, not real changes. "
                        "Google uses lastmod only when it is consistently accurate and stops trusting it otherwise.")
        if foreign:
            rep.add("Site", "WARN", "site.sitemap-hosts", f"{len(foreign)} sitemap URLs on another host, e.g. {foreign[:2]}")
        if http_only:
            rep.add("Site", "WARN", "site.sitemap-hosts", f"{len(http_only)} sitemap URLs use http://")
        if norm(start_final) not in {norm(x) for x in urls_in_sitemap} and len(urls_in_sitemap) < 50_000:
            rep.add("Site", "INFO", "site.sitemap-membership", "The audited URL is not listed in the sitemap")

    # RSS/Atom feed: Google accepts it as a sitemap, and WebSub can push changes
    if page is not None and page.feeds:
        rep.add("Site", "INFO", "site.feed", f"Feed found ({page.feeds[0][1]}): submit it in GSC as an extra sitemap for fast discovery of new posts")

    # www / non-www and http -> https
    alt_host = host[4:] if host.startswith("www.") else "www." + host
    alt = fetch(f"{u.scheme}://{alt_host}{u.path}", UA_BOT, timeout, delay=delay)
    if alt["status"] == 200 and norm(alt["final_url"]) != norm(start_final):
        rep.add("Site", "FAIL", "site.host-variant", f"{alt_host} serves the page too (200) without redirecting. Pick one host and 301 the other")
    elif alt["status"] == 200:
        rep.add("Site", "PASS", "site.host-variant", f"{alt_host} redirects to {host}")
    elif alt["status"] is None:
        rep.add("Site", "INFO", "site.host-variant", f"{alt_host} does not resolve (fine if you never advertised it)")
    else:
        rep.add("Site", "WARN", "site.host-variant", f"{alt_host} returned {alt['status']}")
    if u.scheme == "https":
        plain = fetch(f"http://{host}{u.path}", UA_BOT, timeout, delay=delay)
        if plain["status"] == 200 and plain["final_url"].startswith("http://"):
            rep.add("Site", "FAIL", "site.http-redirect", "http:// serves content instead of redirecting to https://")
        elif plain["status"] == 200:
            rep.add("Site", "PASS", "site.http-redirect", "http:// redirects to https://")
    hsts = rtxt["headers"].get("strict-transport-security")
    if not hsts:
        rep.add("Site", "INFO", "site.hsts", "No Strict-Transport-Security header")

    # soft 404
    junk = "".join(random.choices(string.ascii_lowercase, k=12))
    nf = fetch(f"{origin}/{junk}-does-not-exist", UA_BOT, timeout, delay=delay)
    if nf["status"] == 200:
        rep.add("Site", "FAIL", "site.soft-404", "Unknown URLs return 200 (soft 404). Return a real 404/410")
    elif nf["status"] in (404, 410):
        rep.add("Site", "PASS", "site.soft-404", f"unknown URLs return {nf['status']}")
    elif nf["status"]:
        rep.add("Site", "WARN", "site.soft-404", f"Unknown URL returned {nf['status']}")

    # trailing slash variant
    if len(u.path) > 1:
        variant = start_final[:-1] if start_final.endswith("/") else start_final + "/"
        v = fetch(variant, UA_BOT, timeout, delay=delay)
        if v["status"] == 200 and norm(v["final_url"]) == norm(start_final) and len(v["chain"]) == 1:
            pv = parse(v["body"], variant)
            if not pv.canonicals:
                rep.add("Site", "WARN", "site.trailing-slash", "Both slash and no-slash variants return 200 without a canonical: duplicate URLs")
    return urls_in_sitemap

# --------------------------------------------------------------------------- crawl

def crawl(start_final, limit, rep, timeout, delay, urls_in_sitemap):
    seen = {norm(start_final): start_final}
    q = deque([start_final])
    pages = {}  # final_url -> dict(title, desc, canonical, status)
    pages_seen = set()  # norm(final_url), so one page parsed twice via redirects counts once
    link_targets = Counter()
    link_sources = {}  # norm(target) -> first page linking to it
    redirected_links = {}
    broken = {}
    tracking_links = []  # (source page, href with tracking parameters)
    cart_links = Counter()  # cart/checkout targets, not fetched
    while q and len(pages) < limit:
        url = q.popleft()
        r = fetch(url, UA_BOT, timeout, delay=delay)
        if r["status"] is None:
            broken[url] = r["error"]
            continue
        if len(r["chain"]) > 1 and url != start_final:
            redirected_links[url] = r["final_url"]
        if r["status"] != 200:
            broken[url] = r["status"]
            continue
        if "html" not in r["headers"].get("content-type", "html"):
            continue
        final = r["final_url"]
        if not same_site(final, start_final):
            continue  # redirected off-site: not our page
        if norm(final) in pages_seen:
            continue  # a redirect landed on a page already parsed (e.g. host vs host/)
        pages_seen.add(norm(final))
        p = parse(r["body"], final)
        pages[final] = {"title": p.title, "desc": p.metas.get("description"),
                        "canonical": p.canonicals[0] if p.canonicals else None,
                        "h1": len(p.h1s), "noindex": "noindex" in p.metas.get("robots", "").lower()}
        for href, rel in p.links:
            if not same_site(href, start_final):
                continue
            href = href.split("#")[0]
            if re.search(r"\.(png|jpe?g|gif|svg|webp|pdf|zip|mp4|css|js|ico|xml)$", href, re.I) or "/cdn-cgi/" in href:
                continue
            if is_cart(href):
                cart_links[norm(href)] += 1
                continue
            clean = strip_tracking(href)
            if clean != href:
                tracking_links.append((final, href))
                href = clean
            link_targets[norm(href)] += 1
            link_sources.setdefault(norm(href), final)
            if norm(href) not in seen:
                seen[norm(href)] = href
                q.append(href)
    truncated = bool(q)
    rep.add("Crawl", "INFO", "crawl.size",
            f"Crawled {len(pages)} pages" + (f" (limit hit, {len(q)} URLs left in queue, orphan check skipped)" if truncated else " (site exhausted)"))
    for url, status in list(broken.items())[:30]:
        rep.add("Crawl", "FAIL", "crawl.broken-link", f"Internal link target {url} -> {status} (linked from {link_sources.get(norm(url), '?')})")
    if len(broken) > 30:
        rep.add("Crawl", "FAIL", "crawl.broken-link", f"{len(broken) - 30} more broken link targets not listed (full list in --json)",
                data=[{"link": u, "status": st, "from": link_sources.get(norm(u))} for u, st in broken.items()])
    redirected_links = {s: d for s, d in redirected_links.items() if not is_cart(d)}  # a shortlink into the cart is a cart link
    for src, dst in list(redirected_links.items())[:30]:
        rep.add("Crawl", "WARN", "crawl.redirected-link", f"Internal link points at redirecting URL {src} -> {dst} (link the final URL; linked from {link_sources.get(norm(src), '?')})")
    if len(redirected_links) > 30:
        rep.add("Crawl", "INFO", "crawl.redirected-link", f"{len(redirected_links) - 30} more redirecting link targets not listed (full list in --json)",
                data=[{"link": s, "final": d, "from": link_sources.get(norm(s))} for s, d in redirected_links.items()])
    if tracking_links:
        pages_with = sorted({src for src, _ in tracking_links})
        rep.add("Crawl", "WARN", "crawl.tracking-params",
                f"{len(tracking_links)} internal links carry tracking parameters (utm_*, gclid, ...), e.g. {[h for _, h in tracking_links[:3]]}. "
                f"Each variant can be crawled and indexed as a duplicate of the clean URL; link the clean URL and measure in analytics by referrer. Linked from {len(pages_with)} page(s)",
                data=[{"from": s, "link": h} for s, h in tracking_links])
    if cart_links:
        rep.add("Crawl", "INFO", "crawl.cart-links",
                f"{sum(cart_links.values())} links to {len(cart_links)} cart/checkout/account URLs not crawled (noindex by design)",
                data=sorted(cart_links))
    indexable = {u: v for u, v in pages.items()
                 if not v["noindex"] and (not v["canonical"] or norm(v["canonical"]) == norm(u))}
    skipped = len(pages) - len(indexable)
    if skipped:
        rep.add("Crawl", "INFO", "crawl.non-indexable", f"{skipped} crawled URLs are noindex or canonicalize elsewhere (cart, tracking, variants); excluded from duplicate checks")
    by_title = Counter(v["title"] for v in indexable.values() if v["title"])
    for t, n in by_title.items():
        if n > 1:
            urls = [u for u, v in indexable.items() if v["title"] == t][:5]
            paginated = all(re.search(r"(?:[?&]page=|/page/|/seite/)\d+", u) for u in urls[1:])
            rep.add("Crawl", "INFO" if paginated else "WARN", "crawl.duplicate-title",
                    f"{n} pages share title “{t}”: {urls}" + (" (paginated series: add the page number to the title)" if paginated else ""),
                    data=[u for u, v in indexable.items() if v["title"] == t])
    by_desc = Counter(v["desc"] for v in indexable.values() if v["desc"])
    for d, n in by_desc.items():
        if n > 1:
            urls = [u for u, v in indexable.items() if v["desc"] == d][:5]
            paginated = all(re.search(r"(?:[?&]page=|/page/|/seite/)\d+", u) for u in urls[1:])
            rep.add("Crawl", "INFO" if paginated else "WARN", "crawl.duplicate-description", f"{n} pages share the same meta description: {urls}",
                    data=[u for u, v in indexable.items() if v["desc"] == d])
    no_canon = [u for u, v in pages.items() if not v["canonical"] and not v["noindex"]]
    if no_canon:
        rep.add("Crawl", "FAIL", "crawl.canonical", f"{len(no_canon)} crawled pages without canonical, e.g. {no_canon[:5]}", data=no_canon)
    pag = [u for u, v in pages.items() if v["canonical"] and norm(v["canonical"]) != norm(u)
           and (m := re.search(r"(?:[?&]page=|/page/|/seite/)(\d+)", u)) and int(m.group(1)) >= 2]
    if pag:
        rep.add("Crawl", "WARN", "crawl.pagination-canonical", f"{len(pag)} paginated pages canonicalize elsewhere (Google: each page keeps its own canonical), e.g. {pag[:3]}")
    multi_h1 = [u for u, v in indexable.items() if v["h1"] != 1]
    if multi_h1:
        rep.add("Crawl", "INFO", "crawl.h1", f"{len(multi_h1)} indexable pages with zero or multiple H1, e.g. {multi_h1[:5]}", data=multi_h1)
    if urls_in_sitemap:
        crawled = {norm(u) for u in pages}
        orphans = [x for x in urls_in_sitemap if norm(x) not in crawled and norm(x) not in link_targets]
        if orphans and not truncated:
            rep.add("Crawl", "WARN", "crawl.orphans", f"{len(orphans)} sitemap URLs have no internal link pointing at them, e.g. {orphans[:5]}", data=orphans)
        elif not orphans and not truncated:
            rep.add("Crawl", "PASS", "crawl.orphans", "every sitemap URL is internally linked")
        not_in_map = [u for u in pages if norm(u) not in {norm(x) for x in urls_in_sitemap} and not pages[u]["noindex"]]
        if not_in_map:
            rep.add("Crawl", "INFO", "crawl.not-in-sitemap", f"{len(not_in_map)} crawled pages missing from the sitemap, e.g. {not_in_map[:5]}", data=not_in_map)

# --------------------------------------------------------------------------- main

LEVEL_ORDER = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}


def render(rep, url):
    c = rep.counts()
    out = [f"# Tech SEO audit: {url}", "",
           f"FAIL {c.get('FAIL', 0)} · WARN {c.get('WARN', 0)} · INFO {c.get('INFO', 0)} · PASS {c.get('PASS', 0)}", ""]
    for section in ("Page", "Site", "Crawl"):
        items = [i for i in rep.items if i["section"] == section]
        if not items:
            continue
        out.append(f"## {section}")
        out.append("")
        for i in sorted(items, key=lambda x: LEVEL_ORDER[x["level"]]):
            out.append(f"- **{i['level']}** `{i['id']}`: {i['message']}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--crawl", type=int, default=0, metavar="N", help="crawl up to N internal pages for duplicates, broken links, orphans")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--delay", type=float, default=0.25, help="seconds between requests")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    url = a.url if a.url.startswith("http") else "https://" + a.url
    rep = Report()
    bot, page = check_page(url, rep, a.timeout, a.delay)
    final = bot["final_url"] if bot["status"] == 200 else url
    sitemap = set()
    if bot["status"]:
        sitemap = check_site(final, rep, a.timeout, a.delay, page)
        if a.crawl:
            crawl(final, a.crawl, rep, a.timeout, a.delay, sitemap)
    if a.json:
        print(json.dumps({"url": url, "final_url": final, "counts": rep.counts(), "items": rep.items}, indent=2, ensure_ascii=False))
    else:
        print(render(rep, url))
    if a.crawl and not a.json:
        print("Full lists (every broken link, duplicate, orphan) are in the --json output.", file=sys.stderr)


if __name__ == "__main__":
    main()
