#!/usr/bin/env python3
"""Generates the weekly price check GitHub Issue body from products.json."""
import json
import sys
from datetime import date
from pathlib import Path

products_file = Path(__file__).parent / 'products.json'
articles = json.loads(products_file.read_text())

today = date.today().strftime('%B %d, %Y')
total = sum(len(a['products']) for a in articles)

lines = [
    f"## Weekly Price & Detail Check — {today}",
    "",
    f"Review {total} products across {len(articles)} articles. "
    "Check each link, update the HTML if the price or key spec changed, then tick the box.",
    "",
    "> **How to update:** Open the article file, find the product price in the HTML, "
    "edit it, commit with message `Update [Product] price to $X.XX`.",
    "",
]

for article in articles:
    lines.append(f"### [{article['article']}]({article['file']})")
    lines.append("")
    for p in article['products']:
        lines.append(
            f"- [ ] **{p['name']}** — currently listed at `{p['price']}` "
            f"→ [Check current price]({p['check_url']})"
        )
    lines.append("")

lines += [
    "---",
    "### After completing checks",
    "- [ ] All prices verified or updated",
    "- [ ] Any discontinued products noted for removal",
    "- [ ] Any new better-value products worth adding?",
    "",
    "_Generated automatically by the weekly price check workflow._",
]

print('\n'.join(lines))
