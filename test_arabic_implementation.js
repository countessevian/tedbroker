/**
 * Test Arabic translation and RTL functionality
 * Run this in browser console on dashboard page
 */

console.log('='.repeat(80));
console.log('ARABIC TRANSLATION & RTL TEST');
console.log('='.repeat(80));

// Wait for TED_LANG to be available
if (typeof TED_LANG === 'undefined') {
    console.error('✗ TED_LANG is not defined. Language system not loaded.');
} else {
    console.log('✓ TED_LANG is available');

    // Check current language
    console.log(`\nCurrent language: ${TED_LANG.currentLanguage}`);
    console.log(`Loaded translations: ${Object.keys(TED_LANG.translations).length} keys`);

    // Change to Arabic
    console.log('\nChanging language to Arabic...');
    changeLanguage('ar');

    // Wait a moment for translations to apply
    setTimeout(() => {
        console.log(`\n✓ Language changed to: ${TED_LANG.currentLanguage}`);

        // Check RTL direction
        console.log('\nChecking RTL (Right-to-Left) direction:');
        console.log('-'.repeat(80));
        const htmlDir = document.documentElement.getAttribute('dir');
        if (htmlDir === 'rtl') {
            console.log('✓ Document direction is set to RTL');
        } else {
            console.log(`✗ Document direction is ${htmlDir || 'not set'}, expected "rtl"`);
        }

        // Test some specific Arabic translations
        console.log('\nTesting specific Arabic translations:');
        console.log('-'.repeat(80));

        const tests = {
            'nav.dashboard': 'لوحة التحكم',
            'dashboard.tab.wallet': 'المحفظة',
            'nav.portfolio': 'المحفظة',
            'nav.traders': 'التجار',
            'nav.settings': 'الإعدادات',
            'nav.logout': 'تسجيل الخروج',
            'dashboard.overview': 'نظرة عامة على لوحة التحكم',
            'dashboard.stats.totalBalance': 'الرصيد الإجمالي',
            'dashboard.stats.totalProfit': 'الربح الإجمالي',
            'modal.referral.welcome': 'مرحبًا بك في TED Brokers!',
            'modal.updateProfile.title': 'تحديث الملف الشخصي',
            'modal.changePassword.title': 'تغيير كلمة المرور',
            'alert.referralCopied': 'تم نسخ رابط الإحالة إلى الحافظة!',
            'alert.logoutConfirm': 'هل أنت متأكد أنك تريد تسجيل الخروج؟'
        };

        let passed = 0;
        let failed = 0;

        for (const [key, expected] of Object.entries(tests)) {
            const actual = TED_LANG.t(key);
            if (actual === expected) {
                console.log(`✓ ${key}: "${actual}"`);
                passed++;
            } else {
                console.log(`✗ ${key}: Expected "${expected}", got "${actual}"`);
                failed++;
            }
        }

        // Check DOM elements
        console.log('\nChecking DOM elements:');
        console.log('-'.repeat(80));

        const domTests = [
            '[data-i18n="nav.dashboard"]',
            '[data-i18n="dashboard.tab.wallet"]',
            '[data-i18n="nav.portfolio"]',
            '[data-i18n="nav.traders"]',
            '[data-i18n="dashboard.overview"]',
            '[data-i18n="dashboard.stats.totalBalance"]'
        ];

        for (const selector of domTests) {
            const element = document.querySelector(selector);
            if (element) {
                const text = element.textContent.trim();
                const key = element.getAttribute('data-i18n');
                const expected = TED_LANG.t(key);

                if (text.includes(expected) || expected.includes(text)) {
                    console.log(`✓ ${selector}: "${text}"`);
                    passed++;
                } else {
                    console.log(`✗ ${selector}: Expected "${expected}", got "${text}"`);
                    failed++;
                }
            } else {
                console.log(`⚠ ${selector}: Element not found`);
            }
        }

        // Check for English text in visible elements
        console.log('\nScanning for English text in visible elements:');
        console.log('-'.repeat(80));

        const visibleElements = Array.from(document.querySelectorAll('body *'))
            .filter(el => {
                const style = window.getComputedStyle(el);
                return style.display !== 'none' &&
                       style.visibility !== 'hidden' &&
                       el.offsetWidth > 0 &&
                       el.offsetHeight > 0 &&
                       el.children.length === 0 && // Only leaf nodes
                       el.textContent.trim().length > 0;
            });

        const englishPattern = /\b[a-zA-Z]{3,}\b/;
        const possibleEnglish = [];

        visibleElements.forEach(el => {
            const text = el.textContent.trim();
            if (englishPattern.test(text) &&
                !text.includes('TED') &&
                !text.includes('ETF') &&
                !text.includes('DeFi') &&
                !text.includes('2FA')) {
                possibleEnglish.push({
                    text: text.substring(0, 50),
                    element: el.tagName
                });
            }
        });

        if (possibleEnglish.length > 0) {
            console.log(`⚠ Found ${possibleEnglish.length} elements with possible English text:`);
            possibleEnglish.slice(0, 10).forEach(item => {
                console.log(`  - <${item.element}>: "${item.text}"`);
            });
        } else {
            console.log('✓ No English text found in visible elements (excluding brand names)');
        }

        // Summary
        console.log('\n' + '='.repeat(80));
        console.log('SUMMARY');
        console.log('='.repeat(80));
        console.log(`Tests Passed: ${passed}`);
        console.log(`Tests Failed: ${failed}`);
        console.log(`Current Language: ${TED_LANG.currentLanguage}`);
        console.log(`Document Direction: ${document.documentElement.getAttribute('dir')}`);
        console.log(`Stored Preference: ${localStorage.getItem('ted_language')}`);
        console.log(`Translation Keys Loaded: ${Object.keys(TED_LANG.translations).length}`);

        if (failed === 0 && htmlDir === 'rtl') {
            console.log('\n✓ ALL TESTS PASSED! Arabic translation and RTL layout are working correctly.');
        } else {
            console.log(`\n✗ ${failed} TEST(S) FAILED or RTL not set. Please review the output above.`);
        }
    }, 2000);
}
