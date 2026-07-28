#!/usr/bin/env python3
"""Generates the weekly SEO performance report from Google Search Console data."""
import json
import os
import sys
from datetime import date, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

SITE_URL = os.environ.get("GSC_SITE_URL", "https://www.techfordad.com/")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

key_json = os.environ.get("GSC_SERVICE_ACCOUNT_KEY")
if not key_json:
    print("Missing GSC_SERVICE_ACCOUNT_KEY secret.", file=sys.stderr)
    sys.exit(1)

creds = service_account.Credentials.from_service_account_info(
    json.loads(key_json), scopes=SCOPES
)
service = build("searchconsole", "v1", credentials=creds)

end = date.today() - timedelta(days=3)   # GSC data typically lags 2-3 days
start = end - timedelta(days=27)         # trailing 28-day window


def query(dimensions, row_limit=10):
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    resp = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return resp.get("rows", [])


totals = query([], row_limit=1)
top_pages = query(["page"])
top_queries = query(["query"])

lines = [
    f"## Weekly SEO Report — {date.today().strftime('%B %d, %Y')}",
    "",
    f"Search Console performance for `{SITE_URL}`, trailing 28 days "
    f"({start.isoformat()} to {end.isoformat()}).",
    "",
]

if totals:
    t = totals[0]
    lines += [
        "### Overview",
        "",
        f"- **Clicks:** {t['clicks']:.0f}",
        f"- **Impressions:** {t['impressions']:.0f}",
        f"- **Average CTR:** {t['ctr'] * 100:.2f}%",
        f"- **Average position:** {t['position']:.1f}",
        "",
    ]
else:
    lines += ["_No data returned for this period._", ""]

lines += [
    "### Top pages",
    "",
    "| Page | Clicks | Impressions | CTR | Avg. position |",
    "|---|---|---|---|---|",
]
for r in top_pages:
    page = r["keys"][0]
    lines.append(
        f"| {page} | {r['clicks']:.0f} | {r['impressions']:.0f} | "
        f"{r['ctr'] * 100:.1f}% | {r['position']:.1f} |"
    )

lines += [
    "",
    "### Top queries",
    "",
    "| Query | Clicks | Impressions | CTR | Avg. position |",
    "|---|---|---|---|---|",
]
for r in top_queries:
    q = r["keys"][0]
    lines.append(
        f"| {q} | {r['clicks']:.0f} | {r['impressions']:.0f} | "
        f"{r['ctr'] * 100:.1f}% | {r['position']:.1f} |"
    )

lines += [
    "",
    "---",
    "_Generated automatically by the weekly SEO report workflow._",
]

print("\n".join(lines))
