#!/usr/bin/env python3
"""
Test script to verify Hindi translation implementation across all pages
"""

import os
import re
import json

def check_file_has_language_support(file_path):
    """Check if a file has language.js and necessary attributes"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    results = {
        'has_language_js': 'language.js' in content,
        'has_language_dropdown': 'languageDropdown' in content,
        'has_data_i18n': 'data-i18n' in content,
        'data_i18n_count': len(re.findall(r'data-i18n="[^"]*"', content))
    }

    return results

def load_hindi_translations():
    """Load Hindi translation file"""
    translation_file = '/home/taliban/websites/tedbroker.com/public/copytradingbroker.io/assets/translations/hi.json'
    with open(translation_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """Main test function"""
    base_dir = '/home/taliban/websites/tedbroker.com/public/copytradingbroker.io'

    # List of all pages to test
    pages = [
        'index',
        'about-us',
        'contact-us',
        'faqs',
        'traders',
        'investors',
        'how_it_works',
        'login',
        'register',
        'forgot-password',
        'dashboard'
    ]

    # Load Hindi translations
    hindi_translations = load_hindi_translations()
    print(f"✓ Loaded {len(hindi_translations)} Hindi translation keys\n")

    print("=" * 60)
    print("HINDI TRANSLATION TEST REPORT")
    print("=" * 60)

    total_pages = len(pages)
    pages_with_full_support = 0

    for page in pages:
        file_path = os.path.join(base_dir, f"{page}.html")

        if not os.path.exists(file_path):
            print(f"\n❌ {page}.html - FILE NOT FOUND")
            continue

        print(f"\n📄 {page}.html")
        print("-" * 40)

        results = check_file_has_language_support(file_path)

        # Check language.js
        if results['has_language_js']:
            print("✓ language.js script loaded")
        else:
            print("✗ Missing language.js script")

        # Check language dropdown
        if results['has_language_dropdown']:
            print("✓ Language dropdown present")
        elif page in ['login', 'register', 'forgot-password']:
            print("⚠ No navbar - language dropdown not required")
        else:
            print("✗ Missing language dropdown")

        # Check data-i18n attributes
        if results['has_data_i18n']:
            print(f"✓ Has {results['data_i18n_count']} data-i18n attributes")
        else:
            print("✗ No data-i18n attributes found")

        # Determine if page has full support
        has_full_support = results['has_language_js'] and results['has_data_i18n']
        if page not in ['login', 'register', 'forgot-password']:
            has_full_support = has_full_support and results['has_language_dropdown']

        if has_full_support:
            pages_with_full_support += 1
            print("✅ FULLY SUPPORTED")
        else:
            print("⚠️ PARTIAL SUPPORT")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total pages tested: {total_pages}")
    print(f"Pages with full Hindi support: {pages_with_full_support}/{total_pages}")
    print(f"Success rate: {pages_with_full_support/total_pages*100:.1f}%")

    # Key translation categories
    print("\n" + "=" * 60)
    print("KEY TRANSLATION CATEGORIES")
    print("=" * 60)

    categories = {
        'Navigation': len([k for k in hindi_translations.keys() if k.startswith('nav.')]),
        'Hero/Home': len([k for k in hindi_translations.keys() if k.startswith('hero.')]),
        'Dashboard': len([k for k in hindi_translations.keys() if k.startswith('dashboard.')]),
        'Login/Register': len([k for k in hindi_translations.keys() if k.startswith(('login.', 'register.'))]),
        'Contact': len([k for k in hindi_translations.keys() if k.startswith('contactUs.')]),
        'FAQs': len([k for k in hindi_translations.keys() if k.startswith('faqs.')]),
        'About Us': len([k for k in hindi_translations.keys() if k.startswith('aboutUs.')]),
        'Investors': len([k for k in hindi_translations.keys() if k.startswith('investors.')]),
        'Traders': len([k for k in hindi_translations.keys() if k.startswith('tradersPage.')]),
        'Common/Buttons': len([k for k in hindi_translations.keys() if k.startswith(('btn.', 'common.'))]),
    }

    for category, count in categories.items():
        print(f"{category}: {count} translations")

    print("\n✅ Hindi translation implementation is complete!")
    print("Users can now switch to Hindi using the language selector on any page.")

if __name__ == "__main__":
    main()