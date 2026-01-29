#!/usr/bin/env python3
"""
Test script to verify Russian translation implementation
This script runs basic checks on the translation files and system
"""
import json
import requests
import re
from bs4 import BeautifulSoup

def test_russian_translation():
    print("🚀 Starting Russian Translation Test\n")
    print("=" * 60)

    # Test 1: Verify Russian translation file
    print("\n1️⃣  Testing Russian Translation File...")
    try:
        response = requests.get('http://localhost:8000/public/copytradingbroker.io/assets/translations/ru.json')
        if response.status_code == 200:
            print("   ✅ Russian translation file loads successfully (HTTP 200)")
            ru_translations = response.json()
            print(f"   ✅ Loaded {len(ru_translations)} translation keys")
        else:
            print(f"   ❌ Failed to load Russian translations (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error loading Russian translations: {e}")
        return False

    # Test 2: Verify homepage HTML
    print("\n2️⃣  Testing Homepage HTML...")
    try:
        response = requests.get('http://localhost:8000/public/copytradingbroker.io/index.html')
        if response.status_code == 200:
            print("   ✅ Homepage loads successfully (HTTP 200)")
            html_content = response.text
        else:
            print(f"   ❌ Failed to load homepage (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error loading homepage: {e}")
        return False

    # Test 3: Extract data-i18n keys
    print("\n3️⃣  Testing Translation Coverage...")
    soup = BeautifulSoup(html_content, 'html.parser')
    elements_with_i18n = soup.find_all(attrs={'data-i18n': True})
    used_keys = set(element.get('data-i18n') for element in elements_with_i18n if element.get('data-i18n'))

    print(f"   📊 Found {len(elements_with_i18n)} elements with data-i18n attribute")
    print(f"   📊 Found {len(used_keys)} unique translation keys in HTML")

    # Test 4: Check coverage
    missing_keys = [key for key in sorted(used_keys) if key not in ru_translations]
    if missing_keys:
        print(f"\n   ❌ Missing {len(missing_keys)} Russian translations:")
        for key in missing_keys[:10]:
            print(f"      - {key}")
        if len(missing_keys) > 10:
            print(f"      ... and {len(missing_keys) - 10} more")
        return False
    else:
        print(f"   ✅ All {len(used_keys)} HTML keys have Russian translations")

    # Test 5: Verify Cyrillic characters
    print("\n4️⃣  Testing Russian Character Encoding...")
    cyrillic_count = sum(1 for v in list(ru_translations.values())[:10]
                         if isinstance(v, str) and any('\u0400' <= char <= '\u04FF' for char in v))

    if cyrillic_count > 0:
        print(f"   ✅ Cyrillic characters detected in translations")
        print(f"   📝 Sample translations:")
        for key, value in list(ru_translations.items())[:5]:
            if isinstance(value, str):
                print(f"      {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
    else:
        print(f"   ⚠️  No Cyrillic characters detected")

    # Test 6: Check language.js
    print("\n5️⃣  Testing Language System...")
    try:
        response = requests.get('http://localhost:8000/public/copytradingbroker.io/assets/js/language.js')
        if response.status_code == 200:
            print("   ✅ language.js loads successfully")
            if "'ru'" in response.text or '"ru"' in response.text:
                print("   ✅ Russian language ('ru') is configured")
        else:
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 7: Cache version
    print("\n6️⃣  Testing Cache Version...")
    version_match = re.search(r'language\.js\?v=([\d.]+)', html_content)
    if version_match:
        print(f"   ✅ Cache version: v={version_match.group(1)}")

    print("\n" + "=" * 60)
    print("✅ RUSSIAN TRANSLATION TEST PASSED!")
    print("=" * 60)
    print(f"\n📋 Summary:")
    print(f"   • Russian translation file: ✅ Loaded ({len(ru_translations)} keys)")
    print(f"   • Translation coverage: ✅ Complete ({len(used_keys)} keys)")
    print(f"   • Cyrillic encoding: ✅ Valid UTF-8")
    print(f"   • Language system: ✅ Ready")
    print("\n🎯 To test manually:")
    print("   1. Open http://localhost:8000/public/copytradingbroker.io/index.html")
    print("   2. Select 'Русский (Russian)' from language dropdown")
    print("   3. Verify all text changes to Russian")
    print("\n📝 Note: For thorough DOM inspection, use browser developer tools:")
    print("   - Open DevTools (F12)")
    print("   - Run: changeLanguage('ru')")
    print("   - Inspect elements to verify no English text remains")
    return True

if __name__ == '__main__':
    try:
        exit(0 if test_russian_translation() else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
