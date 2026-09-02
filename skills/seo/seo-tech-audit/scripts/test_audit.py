#!/usr/bin/env python3
"""Offline tests for audit.py: URL normalization, tracking parameters, cart links, crawl dedupe.

Run: python3 skills/seo/seo-tech-audit/scripts/test_audit.py
No network: fetch() is replaced by a fake site.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit  # noqa: E402

HOST = "https://example.com"


def html(title, links=(), h1=True, canonical=None, robots=None):
    head = f"<title>{title}</title><meta name='description' content='desc of {title}'>"
    head += f"<link rel='canonical' href='{canonical}'>" if canonical else ""
    head += f"<meta name='robots' content='{robots}'>" if robots else ""
    body = (f"<h1>{title}</h1>" if h1 else "") + "".join(f"<a href='{l}'>x</a>" for l in links)
    return f"<html><head>{head}</head><body>{body}</body></html>"


# A fake site: one redirect lands on the host without a slash, one link carries utm_*, one links the cart.
SITE = {
    HOST + "/": (200, html("Home", [HOST + "/a/", HOST + "/old/", HOST + "/a/?utm_source=home", HOST + "/warenkorb/?add-to-cart=1", HOST + "/legal/"], canonical=HOST + "/")),
    HOST + "/a/": (200, html("A", [HOST + "/"], canonical=HOST + "/a/")),
    HOST + "/old/": (301, HOST),  # redirects to bare host: same page as "/"
    HOST: (200, html("Home", [HOST + "/a/"], canonical=HOST + "/")),
    HOST + "/legal/": (200, html("Legal", [], h1=False, canonical=HOST + "/legal/", robots="noindex")),
}


def fake_fetch(url, ua=None, timeout=15, max_hops=10, delay=0.0):
    chain = []
    current = url
    for _ in range(max_hops):
        status, payload = SITE.get(current, (404, ""))
        chain.append((current, status))
        if status in (301, 302):
            current = payload
            continue
        return {"url": url, "chain": chain, "final_url": current, "status": status,
                "headers": {"content-type": "text/html"}, "body": payload, "error": None, "elapsed": 0.01}
    raise AssertionError("redirect loop in fixture")


class Norm(unittest.TestCase):
    def test_root_with_and_without_slash_are_one_url(self):
        self.assertEqual(audit.norm(HOST), audit.norm(HOST + "/"))

    def test_trailing_slash_and_fragment_ignored(self):
        self.assertEqual(audit.norm(HOST + "/a/#x"), audit.norm(HOST + "/a"))

    def test_query_kept(self):
        self.assertNotEqual(audit.norm(HOST + "/a/?p=1"), audit.norm(HOST + "/a/"))


class Tracking(unittest.TestCase):
    def test_utm_stripped_other_params_kept(self):
        self.assertEqual(audit.strip_tracking(HOST + "/a/?utm_source=x&utm_medium=y&page=2"), HOST + "/a/?page=2")

    def test_clean_url_unchanged(self):
        self.assertEqual(audit.strip_tracking(HOST + "/a/?page=2"), HOST + "/a/?page=2")

    def test_click_ids(self):
        self.assertEqual(audit.strip_tracking(HOST + "/a/?gclid=abc"), HOST + "/a/")


class Cart(unittest.TestCase):
    def test_woocommerce_german_and_english(self):
        for u in ("/warenkorb/?add-to-cart=1", "/kasse/", "/cart/", "/checkout/", "/mein-konto/", "/a/?add-to-cart=5"):
            self.assertTrue(audit.is_cart(HOST + u), u)

    def test_content_is_not_cart(self):
        for u in ("/", "/a/", "/kassenbon-lesen/", "/carter-boats/"):
            self.assertFalse(audit.is_cart(HOST + u), u)


class Crawl(unittest.TestCase):
    def setUp(self):
        self._fetch = audit.fetch
        audit.fetch = fake_fetch
        self.rep = audit.Report()
        audit.crawl(HOST + "/", 50, self.rep, 5, 0, {HOST + "/", HOST + "/a/"})
        self.ids = {i["id"]: i for i in self.rep.items}

    def tearDown(self):
        audit.fetch = self._fetch

    def test_redirect_onto_bare_host_is_not_a_duplicate(self):
        self.assertNotIn("crawl.duplicate-title", self.ids, self.rep.items)
        self.assertIn("Crawled 3 pages", self.ids["crawl.size"]["message"])  # /, /a/, /legal/

    def test_redirected_link_reported_once(self):
        self.assertIn("crawl.redirected-link", self.ids)
        self.assertIn("/old/", self.ids["crawl.redirected-link"]["message"])

    def test_tracking_link_reported_and_clean_url_crawled(self):
        self.assertIn("crawl.tracking-params", self.ids)
        self.assertEqual(self.ids["crawl.tracking-params"]["data"], [{"from": HOST + "/", "link": HOST + "/a/?utm_source=home"}])

    def test_cart_link_counted_not_fetched(self):
        self.assertIn("crawl.cart-links", self.ids)
        self.assertNotIn("crawl.broken-link", self.ids)

    def test_h1_check_skips_noindex(self):
        self.assertNotIn("crawl.h1", self.ids)  # /legal/ has no H1 but is noindex

    def test_orphans_pass_when_queue_drained(self):
        self.assertEqual(self.ids["crawl.orphans"]["level"], "PASS")


if __name__ == "__main__":
    unittest.main(verbosity=1)
