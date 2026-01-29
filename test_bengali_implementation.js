/**
 * Test Bengali translation functionality
 * Run this in browser console on dashboard page
 */

console.log('='.repeat(80));
console.log('BENGALI TRANSLATION TEST');
console.log('='.repeat(80));

// Wait for TED_LANG to be available
if (typeof TED_LANG === 'undefined') {
    console.error('✗ TED_LANG is not defined. Language system not loaded.');
} else {
    console.log('✓ TED_LANG is available');

    // Check current language
    console.log(`\nCurrent language: ${TED_LANG.currentLanguage}`);
    console.log(`Loaded translations: ${Object.keys(TED_LANG.translations).length} keys`);

    // Change to Bengali
    console.log('\nChanging language to Bengali...');
    changeLanguage('bn');

    // Wait a moment for translations to apply
    setTimeout(() => {
        console.log(`\n✓ Language changed to: ${TED_LANG.currentLanguage}`);

        // Test some specific Bengali translations
        console.log('\nTesting specific Bengali translations:');
        console.log('-'.repeat(80));

        const tests = {
            'nav.dashboard': 'ড্যাশবোর্ড',
            'dashboard.tab.wallet': 'ওয়ালেট',
            'nav.portfolio': 'পোর্টফোলিও',
            'nav.traders': 'ট্রেডার',
            'nav.settings': 'সেটিংস',
            'nav.logout': 'লগআউট',
            'dashboard.overview': 'ড্যাশবোর্ড ওভারভিউ',
            'dashboard.stats.totalBalance': 'মোট ব্যালেন্স',
            'dashboard.stats.totalProfit': 'মোট লাভ',
            'modal.referral.welcome': 'TED Brokers-এ স্বাগতম!',
            'modal.updateProfile.title': 'প্রোফাইল আপডেট করুন',
            'modal.changePassword.title': 'পাসওয়ার্ড পরিবর্তন করুন',
            'alert.referralCopied': 'রেফারেল লিংক ক্লিপবোর্ডে কপি হয়েছে!',
            'alert.logoutConfirm': 'আপনি কি নিশ্চিত যে আপনি লগআউট করতে চান?'
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
                !text.includes('2FA') &&
                !text.includes('KYC')) {
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

        if (failed === 0) {
            console.log('\n✓ ALL TESTS PASSED! Bengali translation is working correctly.');
        } else {
            console.log(`\n✗ ${failed} TEST(S) FAILED. Please review the output above.`);
        }
    }, 2000);
}
