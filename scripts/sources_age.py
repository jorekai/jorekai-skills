#!/usr/bin/env python3
"""List rows in every references/sources.md whose check date is older than a limit.

Usage: sources_age.py [--days 180] [--today YYYY-MM-DD]
Exit 0 always; the output is a warning list, one line per stale row: file, age in days, claim.
Rows are markdown table rows whose last cell is an ISO date.
"""
import argparse
import datetime as dt
import pathlib
import re
import sys

ROW = re.compile(r"^\|(.+)\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")


def stale_rows(root: pathlib.Path, days: int, today: dt.date):
    for f in sorted(root.glob("skills/*/*/references/sources.md")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            m = ROW.match(line)
            if not m:
                continue
            age = (today - dt.date.fromisoformat(m.group(2))).days
            if age > days:
                claim = m.group(1).split("|")[0].strip()
                yield f, n, age, claim


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--root", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent)
    a = ap.parse_args(argv)
    rows = list(stale_rows(a.root, a.days, a.today))
    for f, n, age, claim in rows:
        print(f"{f.relative_to(a.root)}:{n}: {age} days: {claim[:80]}")
    print(f"{len(rows)} row(s) older than {a.days} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
