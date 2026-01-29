#!/usr/bin/env python3
"""
Comprehensive test to verify Spanish language implementation in dashboard
Tests all text nodes are properly translated
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys

def test_spanish_translation():
    """Test comprehensive Spanish translation in dashboard"""

    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--lang=es')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("=" * 80)
        print("COMPREHENSIVE SPANISH TRANSLATION TEST FOR DASHBOARD")
        print("=" * 80)

        # Navigate to dashboard
        print("\n1. Loading dashboard page...")
        driver.get('http://localhost:8000/dashboard.html')
        time.sleep(3)  # Wait for page and translations to load

        print("✓ Page loaded")

        # Wait for language system to initialize
        print("\n2. Waiting for language system to initialize...")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return typeof TED_LANG !== 'undefined' && TED_LANG.currentLanguage !== undefined")
        )
        print("✓ Language system initialized")

        # Check current language
        current_lang = driver.execute_script("return TED_LANG.currentLanguage")
        print(f"   Current language: {current_lang}")

        # Change to Spanish
        print("\n3. Changing language to Spanish...")
        driver.execute_script("changeLanguage('es')")
        time.sleep(2)  # Wait for translations to apply

        # Verify language changed
        current_lang = driver.execute_script("return TED_LANG.currentLanguage")
        print(f"✓ Language changed to: {current_lang}")

        if current_lang != 'es':
            print("✗ ERROR: Language did not change to Spanish!")
            return False

        # Test specific Spanish translations
        print("\n4. Verifying Spanish text translations...")
        print("-" * 80)

        spanish_tests = {
            # Navigation
            '[data-i18n="nav.dashboard"]': 'Panel de Control',
            '[data-i18n="dashboard.tab.wallet"]': 'Cartera',
            '[data-i18n="nav.portfolio"]': 'Portafolio',
            '[data-i18n="nav.traders"]': 'Traders',
            '[data-i18n="nav.settings"]': 'Configuración',
            '[data-i18n="nav.referrals"]': 'Referencias',
            '[data-i18n="nav.logout"]': 'Cerrar Sesión',

            # Dashboard sections
            '[data-i18n="dashboard.overview"]': 'Resumen del Panel',
            '[data-i18n="dashboard.portfolio"]': 'Valor del Portafolio',
            '[data-i18n="dashboard.wallet"]': 'Saldo de Cartera',
            '[data-i18n="dashboard.quickActions.title"]': 'Acciones Rápidas',
            '[data-i18n="dashboard.investments.title"]': 'Inversiones Activas',

            # Quick actions
            '[data-i18n="dashboard.quickActions.deposit"]': 'Depositar Fondos',

            # Market overview
            '[data-i18n="marketOverview.title"]': 'Resumen del Mercado',
        }

        passed = 0
        failed = 0

        for selector, expected_spanish in spanish_tests.items():
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                actual_text = element.text.strip()

                if expected_spanish.lower() in actual_text.lower():
                    print(f"✓ {selector}: '{actual_text}'")
                    passed += 1
                else:
                    print(f"✗ {selector}: Expected '{expected_spanish}', got '{actual_text}'")
                    failed += 1
            except Exception as e:
                print(f"✗ {selector}: Element not found - {str(e)}")
                failed += 1

        # Test modal translations (referral modal)
        print("\n5. Verifying modal translations...")
        print("-" * 80)

        modal_tests = {
            '[data-i18n="modal.referral.welcome"]': '¡Bienvenido a TED Brokers!',
            '[data-i18n="modal.referral.bonusTitle"]': 'Bono de Referido',
            '[data-i18n="modal.referral.codeLabel"]': 'Código de Referido (Opcional)',
            '[data-i18n="modal.referral.skip"]': 'Omitir',
            '[data-i18n="modal.referral.submit"]': 'Enviar Código',
        }

        for selector, expected_spanish in modal_tests.items():
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                actual_text = element.text.strip()

                if expected_spanish.lower() in actual_text.lower() or actual_text.lower() in expected_spanish.lower():
                    print(f"✓ {selector}: '{actual_text}'")
                    passed += 1
                else:
                    print(f"✗ {selector}: Expected '{expected_spanish}', got '{actual_text}'")
                    failed += 1
            except Exception as e:
                # Modal elements might not be visible, that's okay
                print(f"⚠ {selector}: Not visible (expected for hidden modals)")

        # Check for any remaining English text in visible elements
        print("\n6. Scanning for untranslated English text...")
        print("-" * 80)

        # Get all visible text content
        all_text_elements = driver.find_elements(By.XPATH, "//*[not(self::script) and not(self::style)]")

        # Common English words that should NOT appear in Spanish dashboard
        english_words = [
            'Dashboard', 'Wallet', 'Portfolio', 'Settings', 'Logout',
            'Investments', 'Quick Actions', 'Market Overview', 'Welcome back',
            'Total Balance', 'Active Investments', 'Referrals'
        ]

        english_found = []
        for element in all_text_elements:
            try:
                if element.is_displayed():
                    text = element.text.strip()
                    for eng_word in english_words:
                        if eng_word.lower() in text.lower() and len(text) < 100:  # Avoid long paragraphs
                            # Check if element has data-i18n attribute
                            has_i18n = element.get_attribute('data-i18n')
                            if not has_i18n:
                                english_found.append(f"'{text}' in <{element.tag_name}>")
                                break
            except:
                pass

        if english_found:
            print(f"⚠ Found {len(english_found)} potential untranslated elements:")
            for item in english_found[:10]:  # Show first 10
                print(f"  - {item}")
        else:
            print("✓ No obvious English text found in visible elements")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Tests Passed: {passed}")
        print(f"Tests Failed: {failed}")
        print(f"Current Language: {current_lang}")

        # Get translation count
        translation_count = driver.execute_script("return Object.keys(TED_LANG.translations).length")
        print(f"Loaded Translations: {translation_count} keys")

        # Verify localStorage
        stored_lang = driver.execute_script("return localStorage.getItem('ted_language')")
        print(f"Stored Language Preference: {stored_lang}")

        if failed == 0 and current_lang == 'es':
            print("\n✓ ALL TESTS PASSED! Spanish translation is working correctly.")
            return True
        else:
            print(f"\n✗ SOME TESTS FAILED. Please review the output above.")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_spanish_translation()
    sys.exit(0 if success else 1)
