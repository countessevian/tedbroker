#!/usr/bin/env python3
"""
Test Spanish Language Implementation in Dashboard
Verifies that all text content is properly translated when Spanish is selected
"""

import asyncio
import json
from playwright.async_api import async_playwright
import time

async def test_spanish_dashboard():
    """Test Spanish language switching in the dashboard"""

    print("=" * 80)
    print("SPANISH DASHBOARD LANGUAGE TEST")
    print("=" * 80)

    async with async_playwright() as p:
        # Launch browser
        print("\n1. Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to dashboard (assuming we need to be logged in)
        print("2. Navigating to dashboard...")
        await page.goto('http://localhost:8000/dashboard.html')

        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        # Check if language system is loaded
        print("3. Checking language system initialization...")
        lang_loaded = await page.evaluate("""
            typeof TED_LANG !== 'undefined' && TED_LANG.supportedLanguages
        """)

        if not lang_loaded:
            print("   ❌ Language system not loaded!")
            await browser.close()
            return

        print("   ✓ Language system loaded")

        # Get current language
        current_lang = await page.evaluate("TED_LANG.currentLanguage")
        print(f"   Current language: {current_lang}")

        # Switch to Spanish
        print("\n4. Switching to Spanish (es)...")
        await page.evaluate("TED_LANG.changeLanguage('es')")
        await asyncio.sleep(3)  # Wait for translations to apply

        # Verify language changed
        new_lang = await page.evaluate("TED_LANG.currentLanguage")
        print(f"   New language: {new_lang}")

        if new_lang != 'es':
            print("   ❌ Language did not switch to Spanish!")
            await browser.close()
            return

        print("   ✓ Language switched to Spanish")

        # Get all elements with data-i18n attribute
        print("\n5. Checking translated elements...")
        i18n_elements = await page.evaluate("""
            Array.from(document.querySelectorAll('[data-i18n]')).map(el => ({
                key: el.getAttribute('data-i18n'),
                text: el.textContent.trim(),
                tag: el.tagName
            }))
        """)

        print(f"   Found {len(i18n_elements)} elements with data-i18n")

        # Load Spanish translations
        with open('/home/taliban/websites/tedbroker.com/public/copytradingbroker.io/assets/translations/es.json', 'r', encoding='utf-8') as f:
            spanish_translations = json.load(f)

        print(f"   Loaded {len(spanish_translations)} Spanish translation keys")

        # Check for English text (common English words that shouldn't appear)
        print("\n6. Scanning for remaining English text...")
        english_indicators = [
            'Dashboard', 'Wallet', 'Portfolio', 'Settings', 'Profile',
            'Deposit', 'Withdraw', 'Investment', 'Balance', 'Total',
            'Active', 'Pending', 'Completed', 'Failed', 'Processing',
            'Login', 'Logout', 'Password', 'Email', 'Phone',
            'First Name', 'Last Name', 'Address', 'Country', 'City',
            'Loading', 'Submit', 'Cancel', 'Confirm', 'Close',
            'Available', 'Invested', 'Profit', 'Return', 'Amount'
        ]

        # Get all visible text on the page
        all_text = await page.evaluate("""
            Array.from(document.querySelectorAll('body *'))
                .filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none' &&
                           style.visibility !== 'hidden' &&
                           el.children.length === 0;  // Only leaf nodes
                })
                .map(el => el.textContent.trim())
                .filter(text => text.length > 0)
        """)

        found_english = []
        for text in all_text:
            for english_word in english_indicators:
                if english_word.lower() in text.lower():
                    found_english.append(text)
                    break

        # Check specific sections
        print("\n7. Checking specific dashboard sections...")

        sections_to_check = {
            'Navigation': 'nav',
            'Sidebar': '.sidebar',
            'Dashboard Tab': '#dashboard-tab',
            'Wallet Tab': '#wallet-tab',
            'Portfolio Tab': '#portfolio-tab',
        }

        section_results = {}
        for section_name, selector in sections_to_check.items():
            try:
                element = await page.query_selector(selector)
                if element:
                    text_content = await element.text_content()
                    # Check if common English words are present
                    has_english = any(word in text_content for word in ['Dashboard', 'Wallet', 'Portfolio', 'Balance'])
                    section_results[section_name] = {
                        'found': True,
                        'has_english': has_english,
                        'sample': text_content[:100] if text_content else ''
                    }
                else:
                    section_results[section_name] = {'found': False}
            except Exception as e:
                section_results[section_name] = {'error': str(e)}

        # Print results
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)

        print(f"\n✓ Language switched to Spanish: {new_lang == 'es'}")
        print(f"✓ Translation keys loaded: {len(spanish_translations)}")
        print(f"✓ Elements with data-i18n: {len(i18n_elements)}")

        if found_english:
            print(f"\n⚠ Found {len(found_english)} instances of potential English text:")
            for idx, text in enumerate(found_english[:10], 1):  # Show first 10
                print(f"   {idx}. {text[:60]}...")
            if len(found_english) > 10:
                print(f"   ... and {len(found_english) - 10} more")
        else:
            print("\n✓ No obvious English text detected!")

        print("\nSection Analysis:")
        for section, result in section_results.items():
            if result.get('found'):
                status = "⚠ Has English" if result.get('has_english') else "✓ Translated"
                print(f"   {status}: {section}")
            else:
                print(f"   - Not found: {section}")

        # Sample some specific translations
        print("\n8. Sampling specific translations...")
        sample_checks = [
            ('nav.dashboard', 'Panel de Control'),
            ('wallet.title', 'Mi Cartera'),
            ('portfolio.title', 'Mi Portafolio'),
            ('dashboard.stats.totalBalance', 'Balance Total'),
        ]

        for key, expected in sample_checks:
            if key in spanish_translations:
                actual = spanish_translations[key]
                match = actual == expected
                print(f"   {'✓' if match else '✗'} {key}: {actual}")
            else:
                print(f"   ✗ Missing: {key}")

        # Take screenshot
        print("\n9. Taking screenshot...")
        await page.screenshot(path='/home/taliban/websites/tedbroker.com/spanish_dashboard.png', full_page=True)
        print("   ✓ Screenshot saved to spanish_dashboard.png")

        await browser.close()

        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

if __name__ == '__main__':
    asyncio.run(test_spanish_dashboard())
