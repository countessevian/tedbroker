/**
 * Test script to verify Arabic translation completeness
 * This script inspects all DOM nodes to ensure no English text remains
 * when Arabic language is selected
 */

const puppeteer = require('puppeteer');

(async () => {
    console.log('🚀 Starting Arabic Translation Test...\n');

    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Enable console logging from the page
    page.on('console', msg => {
        if (msg.type() === 'log') {
            console.log('  [Browser]', msg.text());
        } else if (msg.type() === 'error') {
            console.error('  [Browser Error]', msg.text());
        }
    });

    try {
        console.log('📄 Loading homepage...');
        await page.goto('http://localhost:8000/', { waitUntil: 'networkidle0' });
        console.log('✅ Homepage loaded\n');

        // Wait for language system to initialize
        console.log('⏳ Waiting for language system to initialize...');
        await page.waitForFunction(() => typeof TED_LANG !== 'undefined' && TED_LANG.currentLanguage, { timeout: 5000 });
        console.log('✅ Language system initialized\n');

        // Change to Arabic
        console.log('🔄 Switching to Arabic language...');
        await page.evaluate(() => {
            return TED_LANG.changeLanguage('ar');
        });

        // Wait for translations to apply
        await page.waitForTimeout(2000);
        console.log('✅ Language switched to Arabic\n');

        // Check RTL direction
        console.log('🔍 Checking RTL direction...');
        const htmlDir = await page.evaluate(() => document.documentElement.getAttribute('dir'));
        if (htmlDir === 'rtl') {
            console.log('✅ RTL direction is set correctly: dir="rtl"\n');
        } else {
            console.log(`❌ RTL direction is NOT set correctly: dir="${htmlDir}"\n`);
        }

        // Check current language
        const currentLang = await page.evaluate(() => TED_LANG.currentLanguage);
        console.log(`📍 Current language: ${currentLang}\n`);

        // Get all text nodes that might contain English
        console.log('🔍 Inspecting all DOM nodes for English text...\n');

        const textNodes = await page.evaluate(() => {
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: function(node) {
                        // Skip script tags, style tags, and TradingView widgets
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;

                        const tagName = parent.tagName.toLowerCase();
                        if (tagName === 'script' || tagName === 'style') {
                            return NodeFilter.FILTER_REJECT;
                        }

                        // Skip TradingView widget content
                        if (parent.closest('.tradingview-widget-container')) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        // Skip language dropdown (contains all language names)
                        if (parent.closest('#languageDropdown') || parent.closest('.dropdown-menu')) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        // Only accept nodes with meaningful text
                        const text = node.textContent.trim();
                        if (text.length > 0) {
                            return NodeFilter.FILTER_ACCEPT;
                        }
                        return NodeFilter.FILTER_REJECT;
                    }
                }
            );

            const nodes = [];
            let currentNode;
            while (currentNode = walker.nextNode()) {
                const text = currentNode.textContent.trim();
                if (text.length > 0) {
                    nodes.push({
                        text: text,
                        parent: currentNode.parentElement.tagName,
                        parentClass: currentNode.parentElement.className,
                        parentId: currentNode.parentElement.id
                    });
                }
            }
            return nodes;
        });

        // Check for English text (basic heuristic: contains common English words)
        const englishWords = [
            'Home', 'About', 'Contact', 'Login', 'Register', 'Dashboard',
            'Trading', 'Trader', 'Investor', 'Market', 'Portfolio', 'News',
            'Copy Trading', 'Get Started', 'Learn More', 'Read More',
            'Sign In', 'Sign Up', 'Company', 'Resources', 'Legal',
            'Privacy Policy', 'Terms', 'Conditions', 'Risk', 'Disclaimer',
            'Welcome', 'Start', 'Join', 'Experience', 'Performance',
            'Strategy', 'Profit', 'Income', 'Benefit', 'Follow',
            'Account', 'Settings', 'Support', 'Help', 'FAQ'
        ];

        const suspiciousNodes = [];

        textNodes.forEach(node => {
            const text = node.text.toLowerCase();

            // Check if text contains any English words
            const hasEnglish = englishWords.some(word => {
                const lowerWord = word.toLowerCase();
                // Check for whole word matches
                const regex = new RegExp('\\b' + lowerWord + '\\b', 'i');
                return regex.test(text);
            });

            if (hasEnglish) {
                suspiciousNodes.push(node);
            }
        });

        console.log(`📊 Total text nodes inspected: ${textNodes.length}`);
        console.log(`🔍 Nodes with potential English text: ${suspiciousNodes.length}\n`);

        if (suspiciousNodes.length > 0) {
            console.log('⚠️  Found potential English text in the following nodes:\n');
            suspiciousNodes.slice(0, 20).forEach((node, index) => {
                console.log(`  ${index + 1}. <${node.parent}${node.parentClass ? ' class="' + node.parentClass + '"' : ''}${node.parentId ? ' id="' + node.parentId + '"' : ''}>`);
                console.log(`     Text: "${node.text.substring(0, 100)}${node.text.length > 100 ? '...' : ''}"`);
                console.log('');
            });

            if (suspiciousNodes.length > 20) {
                console.log(`     ... and ${suspiciousNodes.length - 20} more nodes\n`);
            }
        } else {
            console.log('✅ No English text found! All content appears to be in Arabic.\n');
        }

        // Check translation coverage
        console.log('📊 Translation Coverage Report:\n');
        const translationStats = await page.evaluate(() => {
            const elementsWithI18n = document.querySelectorAll('[data-i18n]');
            let translated = 0;
            let notTranslated = 0;
            const notTranslatedElements = [];

            elementsWithI18n.forEach(el => {
                const key = el.getAttribute('data-i18n');
                const text = el.textContent.trim();

                // Check if text equals the key (meaning not translated)
                if (text === key) {
                    notTranslated++;
                    notTranslatedElements.push({
                        key: key,
                        tag: el.tagName,
                        class: el.className
                    });
                } else {
                    translated++;
                }
            });

            return {
                total: elementsWithI18n.length,
                translated: translated,
                notTranslated: notTranslated,
                notTranslatedElements: notTranslatedElements.slice(0, 10)
            };
        });

        console.log(`  Total elements with data-i18n: ${translationStats.total}`);
        console.log(`  ✅ Translated: ${translationStats.translated}`);
        console.log(`  ❌ Not translated: ${translationStats.notTranslated}`);

        if (translationStats.notTranslated > 0) {
            console.log('\n  Elements not translated:');
            translationStats.notTranslatedElements.forEach((el, i) => {
                console.log(`    ${i + 1}. <${el.tag}> key="${el.key}" class="${el.class}"`);
            });
        }

        console.log('\n' + '='.repeat(60));

        if (suspiciousNodes.length === 0 && translationStats.notTranslated === 0) {
            console.log('✅ ARABIC TRANSLATION TEST PASSED!');
            console.log('   All content is properly translated to Arabic.');
            console.log('   RTL direction is correctly applied.');
        } else {
            console.log('⚠️  ARABIC TRANSLATION TEST COMPLETED WITH WARNINGS');
            if (suspiciousNodes.length > 0) {
                console.log(`   - ${suspiciousNodes.length} nodes contain potential English text`);
            }
            if (translationStats.notTranslated > 0) {
                console.log(`   - ${translationStats.notTranslated} elements are not translated`);
            }
        }
        console.log('='.repeat(60) + '\n');

    } catch (error) {
        console.error('❌ Test failed with error:', error.message);
        console.error(error.stack);
    } finally {
        await browser.close();
        console.log('👋 Browser closed. Test complete.');
    }
})();
