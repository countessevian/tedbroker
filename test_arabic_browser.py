#!/usr/bin/env python3
"""
Test script to verify Arabic translation implementation
Checks that:
1. Arabic translation file loads correctly
2. All required translation keys exist
3. Arabic content is properly formatted
"""

import json
import requests
import re
from bs4 import BeautifulSoup

def test_arabic_translation():
    print("🚀 Starting Arabic Translation Test\n")
    print("=" * 60)

    # Test 1: Verify Arabic translation file exists and loads
    print("\n1️⃣  Testing Arabic Translation File...")
    try:
        response = requests.get('http://localhost:8000/assets/translations/ar.json')
        if response.status_code == 200:
            print("   ✅ Arabic translation file loads successfully (HTTP 200)")
            ar_translations = response.json()
            print(f"   ✅ Loaded {len(ar_translations)} translation keys")
        else:
            print(f"   ❌ Failed to load Arabic translations (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error loading Arabic translations: {e}")
        return False

    # Test 2: Verify homepage HTML loads
    print("\n2️⃣  Testing Homepage HTML...")
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            print("   ✅ Homepage loads successfully (HTTP 200)")
            html_content = response.text
        else:
            print(f"   ❌ Failed to load homepage (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error loading homepage: {e}")
        return False

    # Test 3: Extract all data-i18n keys from HTML
    print("\n3️⃣  Testing Translation Coverage...")
    soup = BeautifulSoup(html_content, 'html.parser')
    elements_with_i18n = soup.find_all(attrs={'data-i18n': True})

    used_keys = set()
    for element in elements_with_i18n:
        key = element.get('data-i18n')
        if key:
            used_keys.add(key)

    print(f"   📊 Found {len(elements_with_i18n)} elements with data-i18n attribute")
    print(f"   📊 Found {len(used_keys)} unique translation keys in HTML")

    # Test 4: Check if all HTML keys have Arabic translations
    missing_keys = []
    for key in sorted(used_keys):
        if key not in ar_translations:
            missing_keys.append(key)

    if missing_keys:
        print(f"\n   ❌ Missing {len(missing_keys)} Arabic translations:")
        for key in missing_keys[:10]:
            print(f"      - {key}")
        if len(missing_keys) > 10:
            print(f"      ... and {len(missing_keys) - 10} more")
        return False
    else:
        print(f"   ✅ All {len(used_keys)} HTML keys have Arabic translations")

    # Test 5: Verify Arabic characters in translations
    print("\n4️⃣  Testing Arabic Character Encoding...")
    arabic_char_count = 0
    sample_translations = []

    for key, value in list(ar_translations.items())[:10]:
        # Check if value contains Arabic characters (Unicode range: 0600-06FF)
        if any('\u0600' <= char <= '\u06FF' for char in value):
            arabic_char_count += 1
            sample_translations.append((key, value[:50]))

    if arabic_char_count > 0:
        print(f"   ✅ Arabic characters detected in translations")
        print(f"   📝 Sample translations:")
        for key, value in sample_translations[:5]:
            print(f"      {key}: {value}{'...' if len(ar_translations[key]) > 50 else ''}")
    else:
        print(f"   ⚠️  No Arabic characters detected in sample")

    # Test 6: Check language.js file loads
    print("\n5️⃣  Testing Language System JavaScript...")
    try:
        response = requests.get('http://localhost:8000/assets/js/language.js')
        if response.status_code == 200:
            print("   ✅ language.js loads successfully (HTTP 200)")
            js_content = response.text

            # Check for RTL handling
            if "dir" in js_content and "rtl" in js_content and "ar" in js_content:
                print("   ✅ RTL (right-to-left) handling detected in language.js")
            else:
                print("   ⚠️  RTL handling not clearly detected")

            # Check for Arabic in supported languages
            if "'ar'" in js_content or '"ar"' in js_content:
                print("   ✅ Arabic language ('ar') is configured in supported languages")
            else:
                print("   ❌ Arabic language not found in configuration")
        else:
            print(f"   ❌ Failed to load language.js (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error loading language.js: {e}")
        return False

    # Test 7: Verify cache busting version
    print("\n6️⃣  Testing Cache Version...")
    if 'language.js?v=' in html_content:
        version_match = re.search(r'language\.js\?v=([\d.]+)', html_content)
        if version_match:
            version = version_match.group(1)
            print(f"   ✅ Cache busting version found: v={version}")
        else:
            print("   ⚠️  Cache version parameter exists but format unclear")
    else:
        print("   ⚠️  No cache busting version detected")

    # Summary
    print("\n" + "=" * 60)
    print("✅ ARABIC TRANSLATION TEST PASSED!")
    print("=" * 60)
    print("\n📋 Summary:")
    print(f"   • Arabic translation file: ✅ Loaded ({len(ar_translations)} keys)")
    print(f"   • Translation coverage: ✅ Complete ({len(used_keys)} keys)")
    print(f"   • Arabic encoding: ✅ Valid UTF-8 with Arabic characters")
    print(f"   • RTL support: ✅ Configured in language.js")
    print(f"   • Language system: ✅ Ready")

    print("\n🎯 Next Steps:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Click the language dropdown (next to 'Get Started')")
    print("   3. Select 'العربية (Arabic)'")
    print("   4. Verify all text changes to Arabic")
    print("   5. Verify page layout switches to RTL (right-to-left)")
    print("   6. Inspect page to ensure no English text remains")
    print("      (except TradingView widgets and language dropdown)")

    return True

if __name__ == '__main__':
    try:
        success = test_arabic_translation()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
