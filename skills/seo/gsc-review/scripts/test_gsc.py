#!/usr/bin/env python3
"""Offline tests for this skill's scripts: gsc_opportunities.py (brand filter on query rows
only, locale-safe numbers, single-column exports) and snippets.py (non-HTTP URL and redirect
target, title-no-query on content words).

Run: python3 skills/seo/gsc-review/scripts/test_gsc.py
No network: a fake export directory with Queries.csv and Pages.csv is written to a temp folder.
"""
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsc_opportunities as g  # noqa: E402
import snippets  # noqa: E402

HOST = "https://example-bootsschule.de"

# German-locale export as GSC writes it: comma decimals, dot thousands, "%" in the CTR column.
QUERIES = """Suchanfragen,Klicks,Impressionen,CTR,Position
acme,"1.200","3.000","40 %","1,2"
acme bootsschule,300,900,"33,3 %","1,1"
boot mieten köln,90,"18.628","0,48 %","15,8"
bootsführerschein kosten,700,"145.000","0,5 %","5,8"
"""

PAGES = f"""Seiten,Klicks,Impressionen,CTR,Position
{HOST}/,"2.000","20.000","10 %","3,4"
{HOST}/boot-mieten-in-koeln/,90,"18.628","0,48 %","15,8"
{HOST}/bootsfuehrerschein-kosten/,700,"145.000","0,5 %","5,8"
"""


class Args:
    """The subset of argparse options the bucket functions read."""
    pos_min = 8
    pos_max = 20
    min_impressions = 50
    brand_re = re.compile("acme|acme bootsschule|akme|acme boot", re.I)


class ExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        for name, text in (("Queries.csv", QUERIES), ("Pages.csv", PAGES)):
            with open(os.path.join(cls.tmp, name), "w", encoding="utf-8") as f:
                f.write(text)
        cls.queries, cls.pages = g.split_export(g.load_export(cls.tmp))

    def test_tables_found(self):
        self.assertEqual(len(self.queries), 4)
        self.assertEqual(len(self.pages), 3)

    def test_locale_numbers(self):
        row = next(r for r in self.queries if r["key"] == "boot mieten köln")
        self.assertEqual(row["impressions"], 18628)
        self.assertAlmostEqual(row["position"], 15.8)
        self.assertAlmostEqual(row["ctr"], 0.0048)
        big = next(r for r in self.queries if r["key"] == "acme")
        self.assertEqual(big["clicks"], 1200)
        self.assertAlmostEqual(big["ctr"], 0.40)

    def test_brand_filter_drops_brand_queries(self):
        keys = [r["key"] for r in g.striking(self.queries, Args())]
        self.assertEqual(keys, ["boot mieten köln"])

    def test_brand_in_host_keeps_page_rows(self):
        """The brand regex matches the host of every page URL; page buckets must not go empty."""
        keys = [r["key"] for r in g.striking(self.pages, Args(), is_query=False)]
        self.assertEqual(keys, [HOST + "/boot-mieten-in-koeln/"])
        gap = [r["key"] for r in g.ctr_gap(self.pages, Args(), is_query=False)]
        self.assertIn(HOST + "/bootsfuehrerschein-kosten/", gap)

    def test_ctr_gap_queries_skip_brand(self):
        gap = [r["key"] for r in g.ctr_gap(self.queries, Args())]
        self.assertIn("bootsführerschein kosten", gap)
        self.assertNotIn("acme", gap)


class SingleColumnTest(unittest.TestCase):
    """The not-indexed export is one column of URLs: no delimiter for the sniffer to find."""

    def test_url_list_without_a_delimiter(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "not-indexed.csv")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"URL\n{HOST}/a/\n{HOST}/b/\n")
            self.assertEqual(g.load_url_list(path), [f"{HOST}/a/", f"{HOST}/b/"])


class SnippetsFetchTest(unittest.TestCase):
    """A URL that is not http:// or https:// answers without a status code, and that is a fetch error."""

    def test_non_http_url_reports_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "page.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write("<html><head><title>local</title></head><body></body></html>")
            r = snippets.fetch("file://" + path)
        self.assertIsNone(r["status"])
        self.assertIn("http", r["error"])


class SnippetsRedirectTest(unittest.TestCase):
    """build_opener installs a FileHandler; a redirect must never reach it."""

    class _Resp:
        status = 301
        headers = {"Location": "file:///etc/passwd"}

        def read(self, n=None):
            return b""

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def test_redirect_to_a_file_url_is_refused(self):
        opener = snippets._OPENER
        snippets._OPENER = type("O", (), {"open": staticmethod(lambda req, timeout=None: self._Resp())})()
        try:
            r = snippets.fetch("https://example.com/")
        finally:
            snippets._OPENER = opener
        self.assertIsNone(r["status"])
        self.assertIn("non-HTTP", r["error"])


class TitleQueryTest(unittest.TestCase):
    """title-no-query compares content words: a natural title drops "how", "to", "the"."""

    def test_stopwords_do_not_trigger_the_flag(self):
        self.assertEqual(snippets.terms("how to clean a boat hull") - snippets.terms("Clean a boat hull in 20 minutes"), set())

    def test_missing_content_word_is_named(self):
        self.assertEqual(snippets.terms("boot antifouling") - snippets.terms("Boot reinigen in 20 Minuten"), {"antifouling"})


class NumberTest(unittest.TestCase):
    def test_to_float(self):
        self.assertAlmostEqual(g.to_float("2,5 %"), 2.5)
        self.assertAlmostEqual(g.to_float("1.234,5"), 1234.5)
        self.assertAlmostEqual(g.to_float("1,234.5"), 1234.5)
        self.assertAlmostEqual(g.to_float("0.48%"), 0.48)

    def test_to_int(self):
        self.assertEqual(g.to_int("1.234"), 1234)
        self.assertEqual(g.to_int("1,234"), 1234)
        self.assertEqual(g.to_int(""), 0)


if __name__ == "__main__":
    unittest.main(verbosity=1)
