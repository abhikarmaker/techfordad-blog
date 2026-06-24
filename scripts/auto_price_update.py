#!/usr/bin/env python3
"""
Auto price updater for TechForDad.
Uses Claude web search to find current prices and patches HTML files.
Runs weekly via GitHub Actions — requires ANTHROPIC_API_KEY secret.
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import date

import anthropic

ROOT = Path(__file__).parent.parent
PRODUCTS_FILE = ROOT / 'scripts' / 'products.json'
CHANGES_FILE = Path('/tmp/price_changes.json')

# Matches: $29.95  $34.95/mo  $1,950  $249
PRICE_RE = re.compile(r'\$[\d,]+(?:\.\d{2})?(?:/mo(?:nth)?)?')

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])


def find_current_price(product_name: str, check_url: str, current_price: str) -> str | None:
    """Ask Claude to web-search the current price of a product."""
    try:
        resp = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=256,
            tools=[{'type': 'web_search_20250305', 'name': 'web_search'}],
            system=(
                'You are a price-checking assistant. '
                'Search for the current retail/starting price of the product at the given URL. '
                'If the site shows "as low as $X", "from $X", or "starting at $X", use that number. '
                'Reply with ONLY the price — e.g. "$34.95/mo" or "$249". No other text.'
            ),
            messages=[{
                'role': 'user',
                'content': (
                    f'Product: {product_name}\n'
                    f'URL to check: {check_url}\n'
                    f'Currently listed on our site as: {current_price}\n\n'
                    f'What is the current price?'
                )
            }]
        )
        for block in resp.content:
            if hasattr(block, 'text') and block.text:
                match = PRICE_RE.search(block.text.strip())
                if match:
                    return match.group(0)
    except Exception as exc:
        print(f'    API error: {exc}')
    return None


def patch_html(filepath: Path, old_price: str, new_price: str) -> bool:
    """Replace every occurrence of old_price with new_price in an HTML file."""
    if not filepath.exists():
        return False
    content = filepath.read_text()
    updated = content.replace(old_price, new_price)
    if updated != content:
        filepath.write_text(updated)
        return True
    return False


def main():
    articles = json.loads(PRODUCTS_FILE.read_text())
    changes = []

    for article in articles:
        html_path = ROOT / article['file']
        print(f"\n── {article['article']}")

        for product in article['products']:
            name = product['name']
            old_price = product['price']
            check_url = product['check_url']

            print(f'  {name} ({old_price}) ...', end=' ', flush=True)
            new_price = find_current_price(name, check_url, old_price)

            if not new_price:
                print('could not determine — skipped')
                continue

            if new_price == old_price:
                print('unchanged')
                continue

            print(f'UPDATED → {new_price}')
            product['price'] = new_price
            html_patched = patch_html(html_path, old_price, new_price)

            changes.append({
                'article': article['article'],
                'file': article['file'],
                'product': name,
                'old': old_price,
                'new': new_price,
                'html_patched': html_patched,
            })

    # Always save products.json (even if no changes, to keep formatting clean)
    PRODUCTS_FILE.write_text(json.dumps(articles, indent=2) + '\n')

    # Write change log for downstream workflow steps
    CHANGES_FILE.write_text(json.dumps({
        'date': date.today().isoformat(),
        'changes': changes,
    }, indent=2))

    print(f'\n{"─" * 40}')
    if changes:
        print(f'✅ {len(changes)} price(s) updated.')
    else:
        print('✅ All prices current — no changes needed.')


if __name__ == '__main__':
    main()
