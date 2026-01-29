/**
 * Test Spanish translation functionality
 * Run this in browser console on dashboard page
 */

console.log('='.repeat(80));
console.log('SPANISH TRANSLATION TEST');
console.log('='.repeat(80));

// Wait for TED_LANG to be available
if (typeof TED_LANG === 'undefined') {
    console.error('✗ TED_LANG is not defined. Language system not loaded.');
} else {
    console.log('✓ TED_LANG is available');

    // Check current language
    console.log(`\nCurrent language: ${TED_LANG.currentLanguage}`);
    console.log(`Loaded translations: ${Object.keys(TED_LANG.translations).length} keys`);

    // Change to Spanish
    console.log('\nChanging language to Spanish...');
    changeLanguage('es');

    // Wait a moment for translations to apply
    setTimeout(() => {
        console.log(`\n✓ Language changed to: ${TED_LANG.currentLanguage}`);

        // Test some specific translations
        console.log('\nTesting specific translations:');
        console.log('-'.repeat(80));

        const tests = {
            'nav.dashboard': 'Panel de Control',
            'dashboard.tab.wallet': 'Cartera',
            'nav.portfolio': 'Portafolio',
            'nav.traders': 'Traders',
            'nav.settings': 'Configuración',
            'nav.logout': 'Cerrar Sesión',
            'dashboard.overview': 'Resumen del Panel',
            'dashboard.wallet': 'Saldo de Cartera',
            'modal.referral.welcome': '¡Bienvenido a TED Brokers!',
            'modal.updateProfile.title': 'Actualizar Perfil',
            'modal.changePassword.title': 'Cambiar Contraseña',
            'alert.referralCopied': '¡Enlace de referido copiado al portapapeles!',
            'alert.logoutConfirm': '¿Estás seguro de que quieres cerrar sesión?'
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
            '[data-i18n="dashboard.overview"]'
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

        // Summary
        console.log('\n' + '='.repeat(80));
        console.log('SUMMARY');
        console.log('='.repeat(80));
        console.log(`Tests Passed: ${passed}`);
        console.log(`Tests Failed: ${failed}`);
        console.log(`Current Language: ${TED_LANG.currentLanguage}`);
        console.log(`Stored Preference: ${localStorage.getItem('ted_language')}`);

        if (failed === 0) {
            console.log('\n✓ ALL TESTS PASSED! Spanish translation is working correctly.');
        } else {
            console.log(`\n✗ ${failed} TEST(S) FAILED. Please review the output above.`);
        }
    }, 2000);
}
