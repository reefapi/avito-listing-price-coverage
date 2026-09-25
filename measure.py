#!/usr/bin/env python3
"""How many classifieds rows actually carry a price, broken down by category.

The point is the breakdown. An aggregate "price coverage" number for a classifieds site is
meaningless, and worse than meaningless if you use it to judge a provider: a job ad has no price,
a puppy given away has no price, and a phone always does. Measure the whole site at once and you
get a middling percentage that describes your query mix rather than the data.

This also separates the three things a null price can mean, which is the part most integrations
get wrong:
  * genuinely free          -> is_free = true
  * deliberately withheld   -> price_not_published = true
  * absent for any other reason
If your provider collapses all three into `price: null`, you cannot tell a free sofa from a
scraping failure.

Usage:
    export REEFAPI_KEY=...      # free key, 1,000 credits, no card
    python measure.py
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://api.reefapi.com/avito/v1/search"

# One query per category, chosen so the categories behave differently on purpose.
BASKET: list[tuple[str, str]] = [
    ("iphone", "electronics"),
    ("квартира", "property to rent"),
    ("диван", "furniture"),
    ("велосипед", "bicycles"),
    ("работа", "job ads"),
    ("щенок", "pets"),
]


def fetch(query: str, key: str, timeout: int = 120) -> dict:
    """The only provider-specific function. Port this to compare another classifieds API."""
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"query": query}).encode(),
        headers={"content-type": "application/json", "x-api-key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def summarise(query: str, category: str, payload: dict) -> dict:
    rows = ((payload.get("data") or {}).get("listings")) or []
    n = len(rows)
    no_price = [r for r in rows if not r.get("price")]
    return {
        "query": query,
        "category": category,
        "rows": n,
        "with_price": n - len(no_price),
        "no_price": len(no_price),
        # of the price-less rows, how many are EXPLAINED rather than simply missing
        "explained_free": sum(1 for r in no_price if r.get("is_free")),
        "explained_withheld": sum(1 for r in no_price if r.get("price_not_published")),
        "unexplained": sum(1 for r in no_price
                           if not r.get("is_free") and not r.get("price_not_published")),
        "no_coordinates": sum(1 for r in rows if not r.get("coordinates")),
        "coordinates_withheld": sum(1 for r in rows if r.get("coordinates_withheld")),
        "price_fill_rate": round((n - len(no_price)) / n, 4) if n else None,
        "site_total_for_query": (payload.get("data") or {}).get("total"),
        "ok": payload.get("ok"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    args = ap.parse_args()
    key = os.environ.get("REEFAPI_KEY")
    if not key:
        print("REEFAPI_KEY is not set. Free key: https://reefapi.com/signup?utm_source=github&utm_medium=repo&utm_campaign=avito-listing-price-coverage", file=sys.stderr)
        return 2

    out_rows = []
    print(f"{'category':18s} {'rows':>5s} {'priced':>7s} {'no price':>9s} {'free':>5s} {'withheld':>9s} {'other':>6s}")
    print("-" * 66)
    for query, category in BASKET:
        r = summarise(query, category, fetch(query, key))
        out_rows.append(r)
        print(f"{category:18s} {r['rows']:5d} {r['with_price']:7d} {r['no_price']:9d} "
              f"{r['explained_free']:5d} {r['explained_withheld']:9d} {r['unexplained']:6d}")

    n = sum(r["rows"] for r in out_rows)
    npx = sum(r["no_price"] for r in out_rows)
    print("-" * 66)
    print(f"{'TOTAL':18s} {n:5d} {n - npx:7d} {npx:9d} "
          f"{sum(r['explained_free'] for r in out_rows):5d} "
          f"{sum(r['explained_withheld'] for r in out_rows):9d} "
          f"{sum(r['unexplained'] for r in out_rows):6d}")
    print(f"\nAggregate price coverage: {round(100 * (n - npx) / n)}% — a number that describes "
          f"the query mix, not the data.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = {"measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "endpoint": ENDPOINT, "results": out_rows,
           "totals": {"rows": n, "with_price": n - npx, "no_price": npx}}
    (out / "coverage.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / "coverage.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"Wrote {out / 'coverage.json'} and {out / 'coverage.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
