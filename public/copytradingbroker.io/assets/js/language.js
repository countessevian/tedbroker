/**
 * TED Brokers Language/Internationalization System
 * Handles language detection, switching, and translation management
 */

const TED_LANG = {
    currentLanguage: 'en',
    translations: {},
    supportedLanguages: {
        'en': { name: 'English', flag: '🇺🇸', nativeName: 'English' },
        'zh': { name: 'Chinese', flag: '🇨🇳', nativeName: '中文' },
        'hi': { name: 'Hindi', flag: '🇮🇳', nativeName: 'हिन्दी' },
        'es': { name: 'Spanish', flag: '🇪🇸', nativeName: 'Español' },
        'fr': { name: 'French', flag: '🇫🇷', nativeName: 'Français' },
        'ar': { name: 'Arabic', flag: '🇸🇦', nativeName: 'العربية' },
        'bn': { name: 'Bengali', flag: '🇧🇩', nativeName: 'বাংলা' },
        'ru': { name: 'Russian', flag: '🇷🇺', nativeName: 'Русский' },
        'pt': { name: 'Portuguese', flag: '🇵🇹', nativeName: 'Português' },
        'de': { name: 'German', flag: '🇩🇪', nativeName: 'Deutsch' }
    },

    /**
     * Initialize language system
     * Detects and loads appropriate language
     */
    async init() {
        console.log('Initializing language system...');

        // Check if user is authenticated and has a saved preference
        if (typeof TED_AUTH !== 'undefined' && TED_AUTH.isAuthenticated()) {
            try {
                const response = await TED_AUTH.apiCall('/api/language/preference', {
                    method: 'GET'
                });

                if (response.ok) {
                    const data = await response.json();
                    await this.changeLanguage(data.preferred_language, false);
                    return;
                }
            } catch (error) {
                console.log('Could not fetch user language preference, using detection');
            }
        }

        // Check localStorage for saved preference
        let savedLang = localStorage.getItem('ted_language');

        if (!savedLang) {
            // Detect language from IP
            try {
                const response = await fetch('/api/language/detect');
                if (response.ok) {
                    const data = await response.json();
                    savedLang = data.detected_language || 'en';
                    console.log('Detected language from IP:', savedLang);
                }
            } catch (error) {
                console.error('Error detecting language:', error);
                savedLang = 'en';
            }
        }

        await this.changeLanguage(savedLang, false);
    },

    /**
     * Change the current language
     * @param {string} langCode - Language code (e.g., 'en', 'es')
     * @param {boolean} savePreference - Whether to save to backend
     */
    async changeLanguage(langCode, savePreference = true) {
        if (!this.supportedLanguages[langCode]) {
            console.error(`Unsupported language: ${langCode}`);
            return;
        }

        try {
            console.log(`Changing language to: ${langCode}`);

            // Load translation file
            const response = await fetch(`/assets/translations/${langCode}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load translation file for ${langCode}`);
            }

            this.translations = await response.json();
            this.currentLanguage = langCode;

            // Apply translations to page
            this.applyTranslations();

            // Update UI
            this.updateLanguageUI();

            // Handle RTL for Arabic
            if (langCode === 'ar') {
                document.documentElement.setAttribute('dir', 'rtl');
            } else {
                document.documentElement.setAttribute('dir', 'ltr');
            }

            // Save to localStorage
            localStorage.setItem('ted_language', langCode);

            // If authenticated, save to database
            if (savePreference && typeof TED_AUTH !== 'undefined' && TED_AUTH.isAuthenticated()) {
                await this.saveLanguagePreference(langCode);
            }

            console.log(`Language changed to ${langCode} successfully`);
        } catch (error) {
            console.error('Error changing language:', error);
        }
    },

    /**
     * Save language preference to backend
     * @param {string} langCode - Language code
     */
    async saveLanguagePreference(langCode) {
        try {
            await TED_AUTH.apiCall('/api/language/preference', {
                method: 'PUT',
                body: JSON.stringify({ language: langCode })
            });
            console.log('Language preference saved to database');
        } catch (error) {
            console.error('Error saving language preference:', error);
        }
    },

    /**
     * Get translated text for a key
     * @param {string} key - Translation key
     * @param {string} fallback - Fallback text if key not found
     * @returns {string} Translated text
     */
    t(key, fallback = '') {
        return this.translations[key] || fallback || key;
    },

    /**
     * Apply translations to all elements with data-i18n attribute
     */
    applyTranslations() {
        // Translate text content
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation !== key) {
                element.textContent = translation;
            }
        });

        // Translate placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            if (translation !== key) {
                element.placeholder = translation;
            }
        });

        // Translate titles
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            const translation = this.t(key);
            if (translation !== key) {
                element.title = translation;
            }
        });
    },

    /**
     * Update language selector UI
     */
    updateLanguageUI() {
        const lang = this.supportedLanguages[this.currentLanguage];

        // Update current language display (dashboard style)
        const flagElement = document.getElementById('current-language-flag');
        const textElement = document.getElementById('current-language-text');

        if (flagElement) flagElement.textContent = lang.flag;
        if (textElement) textElement.textContent = this.currentLanguage.toUpperCase();

        // Update current language display (website style)
        const webFlagElement = document.getElementById('current-lang-flag');
        const webTextElement = document.getElementById('current-lang-code');

        if (webFlagElement) webFlagElement.textContent = lang.flag;
        if (webTextElement) webTextElement.textContent = this.currentLanguage.toUpperCase();
    },

    /**
     * Toggle language dropdown
     */
    toggleDropdown() {
        const dropdown = document.getElementById('language-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    },

    /**
     * Close dropdown when clicking outside
     */
    setupDropdownClose() {
        document.addEventListener('click', (event) => {
            const selector = document.getElementById('language-selector');
            const dropdown = document.getElementById('language-dropdown');

            if (selector && dropdown && !selector.contains(event.target)) {
                dropdown.classList.remove('show');
            }
        });
    }
};

// Initialize language system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => TED_LANG.init());
} else {
    TED_LANG.init();
}

// Setup dropdown close handler
TED_LANG.setupDropdownClose();

// Helper function for easy access
function changeLanguage(langCode) {
    TED_LANG.changeLanguage(langCode);

    // Close dropdown after selection
    const dropdown = document.getElementById('language-dropdown');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
}

function toggleLanguageDropdown() {
    TED_LANG.toggleDropdown();
}
