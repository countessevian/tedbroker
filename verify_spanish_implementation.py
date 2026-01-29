#!/usr/bin/env python3
"""
Verify Spanish Language Implementation
Checks dashboard.html and es.json for proper i18n implementation
"""

import json
import re
from bs4 import BeautifulSoup
from collections import defaultdict

print("=" * 80)
print("SPANISH LANGUAGE IMPLEMENTATION VERIFICATION")
print("=" * 80)

# Load Spanish translations
print("\n1. Loading Spanish translations...")
with open('public/copytradingbroker.io/assets/translations/es.json', 'r', encoding='utf-8') as f:
    spanish_translations = json.load(f)

print(f"   ✓ Loaded {len(spanish_translations)} translation keys")

# Load dashboard HTML
print("\n2. Loading dashboard HTML...")
with open('public/copytradingbroker.io/dashboard.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')
print(f"   ✓ Loaded dashboard HTML ({len(html_content)} characters)")

# Find all elements with data-i18n attributes
print("\n3. Analyzing data-i18n attributes...")
i18n_elements = soup.find_all(attrs={'data-i18n': True})
i18n_placeholder_elements = soup.find_all(attrs={'data-i18n-placeholder': True})
i18n_title_elements = soup.find_all(attrs={'data-i18n-title': True})

print(f"   ✓ Found {len(i18n_elements)} elements with data-i18n")
print(f"   ✓ Found {len(i18n_placeholder_elements)} elements with data-i18n-placeholder")
print(f"   ✓ Found {len(i18n_title_elements)} elements with data-i18n-title")

# Collect all translation keys used in HTML
used_keys = set()
missing_keys = []

for element in i18n_elements:
    key = element.get('data-i18n')
    used_keys.add(key)
    if key not in spanish_translations:
        missing_keys.append(('data-i18n', key, element.get_text(strip=True)[:50]))

for element in i18n_placeholder_elements:
    key = element.get('data-i18n-placeholder')
    used_keys.add(key)
    if key not in spanish_translations:
        missing_keys.append(('data-i18n-placeholder', key, element.get('placeholder', '')[:50]))

for element in i18n_title_elements:
    key = element.get('data-i18n-title')
    used_keys.add(key)
    if key not in spanish_translations:
        missing_keys.append(('data-i18n-title', key, element.get('title', '')[:50]))

print(f"\n4. Translation key coverage...")
print(f"   ✓ Total unique keys used in HTML: {len(used_keys)}")
print(f"   ✓ Keys available in es.json: {len(spanish_translations)}")

if missing_keys:
    print(f"\n   ⚠ Found {len(missing_keys)} missing translation keys:")
    for attr_type, key, text in missing_keys[:10]:
        print(f"      - [{attr_type}] {key}: '{text}'")
    if len(missing_keys) > 10:
        print(f"      ... and {len(missing_keys) - 10} more")
else:
    print("   ✓ All keys used in HTML have translations!")

# Find hardcoded English text (text without data-i18n)
print("\n5. Scanning for hardcoded English text...")

# Common English words to look for
english_patterns = [
    r'\bDashboard\b', r'\bWallet\b', r'\bPortfolio\b', r'\bSettings\b',
    r'\bDeposit\b', r'\bWithdraw\b', r'\bInvestment\b', r'\bBalance\b',
    r'\bTotal\b', r'\bActive\b', r'\bPending\b', r'\bCompleted\b',
    r'\bLoading\b', r'\bSubmit\b', r'\bCancel\b', r'\bConfirm\b',
    r'\bAvailable\b', r'\bInvested\b', r'\bProfit\b', r'\bAmount\b'
]

# Find text nodes that might contain English
text_elements = soup.find_all(text=True)
potential_english = []

for text in text_elements:
    # Skip scripts, styles, comments
    if text.parent.name in ['script', 'style', '[document]', 'noscript']:
        continue

    # Skip empty or whitespace-only text
    clean_text = text.strip()
    if not clean_text or len(clean_text) < 3:
        continue

    # Skip if parent has data-i18n (already translated)
    if text.parent.get('data-i18n'):
        continue

    # Check for English patterns
    for pattern in english_patterns:
        if re.search(pattern, clean_text, re.IGNORECASE):
            # Check if this element or its parent has data-i18n
            element = text.parent
            has_i18n = False
            for _ in range(3):  # Check up to 3 levels up
                if element and (element.get('data-i18n') or element.get('data-i18n-placeholder')):
                    has_i18n = True
                    break
                element = element.parent if element else None

            if not has_i18n:
                potential_english.append((clean_text[:60], text.parent.name, pattern))
            break

print(f"   Found {len(potential_english)} potential untranslated English text instances")

if potential_english:
    print("\n   Sample untranslated text (first 15):")
    seen = set()
    count = 0
    for text, tag, pattern in potential_english:
        if text not in seen and count < 15:
            print(f"      <{tag}>: {text}")
            seen.add(text)
            count += 1

# Check specific dashboard sections
print("\n6. Checking specific sections...")

sections = {
    'Navigation/Sidebar': ['nav', 'sidebar', 'menu'],
    'Dashboard Tab': ['dashboard-tab', 'dashboard-content'],
    'Wallet Tab': ['wallet-tab', 'wallet-content'],
    'Portfolio Tab': ['portfolio-tab', 'portfolio-content'],
    'Modals': ['modal', 'depositModal', 'withdrawModal'],
}

for section_name, selectors in sections.items():
    found_sections = []
    for selector in selectors:
        elements = soup.find_all(id=selector) + soup.find_all(class_=selector)
        found_sections.extend(elements)

    if found_sections:
        total_i18n = sum(len(section.find_all(attrs={'data-i18n': True})) for section in found_sections)
        print(f"   ✓ {section_name}: {total_i18n} translated elements")
    else:
        print(f"   - {section_name}: Not found")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✓ Translation keys in es.json: {len(spanish_translations)}")
print(f"✓ Elements with data-i18n: {len(i18n_elements)}")
print(f"✓ Elements with data-i18n-placeholder: {len(i18n_placeholder_elements)}")
print(f"✓ Elements with data-i18n-title: {len(i18n_title_elements)}")
print(f"✓ Total i18n attributes: {len(i18n_elements) + len(i18n_placeholder_elements) + len(i18n_title_elements)}")

if missing_keys:
    print(f"\n⚠ Missing translations: {len(missing_keys)}")
else:
    print("\n✓ All HTML keys have translations!")

if potential_english:
    print(f"⚠ Potential untranslated text: {len(potential_english)}")
else:
    print("✓ No obvious untranslated English text found!")

# Check dashboard-specific translations
print("\n7. Verifying dashboard-specific translations...")
dashboard_keys = [k for k in spanish_translations.keys() if k.startswith('dashboard.')]
wallet_keys = [k for k in spanish_translations.keys() if k.startswith('wallet.')]
portfolio_keys = [k for k in spanish_translations.keys() if k.startswith('portfolio.')]
modal_keys = [k for k in spanish_translations.keys() if k.startswith('modal.')]

print(f"   ✓ Dashboard translations: {len(dashboard_keys)}")
print(f"   ✓ Wallet translations: {len(wallet_keys)}")
print(f"   ✓ Portfolio translations: {len(portfolio_keys)}")
print(f"   ✓ Modal translations: {len(modal_keys)}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

# Overall assessment
total_i18n = len(i18n_elements) + len(i18n_placeholder_elements) + len(i18n_title_elements)
if total_i18n > 100 and not missing_keys:
    print("\n✓✓✓ EXCELLENT: Dashboard is well-prepared for Spanish translation!")
elif total_i18n > 50:
    print("\n✓✓ GOOD: Dashboard has substantial translation coverage")
else:
    print("\n⚠ NEEDS WORK: Dashboard needs more i18n attributes")
