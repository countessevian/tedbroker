#!/usr/bin/env python3
"""
Verify that all data-i18n keys in index.html have corresponding Chinese translations
"""
import json
import re

# Read Chinese translation file
with open('public/copytradingbroker.io/assets/translations/zh.json', 'r', encoding='utf-8') as f:
    zh_translations = json.load(f)

# Read index.html
with open('public/copytradingbroker.io/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find all data-i18n attributes
pattern = r'data-i18n="([^"]+)"'
used_keys = set(re.findall(pattern, html_content))

print(f"Found {len(used_keys)} unique translation keys in index.html")
print(f"Found {len(zh_translations)} translation keys in zh.json\n")

# Check for missing translations
missing_keys = []
for key in sorted(used_keys):
    if key not in zh_translations:
        missing_keys.append(key)

if missing_keys:
    print(f"❌ Missing {len(missing_keys)} translations in zh.json:")
    for key in missing_keys:
        print(f"  - {key}")
    exit(1)
else:
    print("✅ All translation keys in index.html have Chinese translations!")
    print("\nSample translations:")
    sample_keys = list(sorted(used_keys))[:10]
    for key in sample_keys:
        print(f"  {key}: {zh_translations[key]}")
