# Language System Implementation Plan

## Overview
Implement a multi-language system for TED Brokers platform with:
- IP-based language detection
- 10 most popular languages
- Language selector UI with country flags
- User language preference storage

## Top 10 Languages Supported
1. 🇺🇸 English (en)
2. 🇨🇳 Chinese (zh)
3. 🇮🇳 Hindi (hi)
4. 🇪🇸 Spanish (es)
5. 🇫🇷 French (fr)
6. 🇸🇦 Arabic (ar)
7. 🇧🇩 Bengali (bn)
8. 🇷🇺 Russian (ru)
9. 🇵🇹 Portuguese (pt)
10. 🇩🇪 German (de)

## ✅ Completed Components

### Backend API (app/routes/language.py)
- ✅ `/api/language/supported` - Get list of all supported languages
- ✅ `/api/language/detect` - Detect language based on IP address
- ✅ `/api/language/preference` - Get user's saved language (authenticated)
- ✅ `/api/language/preference` - Save user's language preference (authenticated)
- ✅ Integrated with existing IP geolocation (ipapi.co)
- ✅ Country-to-language mapping for automatic detection

## 📋 Remaining Tasks

### 1. Translation Files
Create JSON translation files for each language in `/public/copytradingbroker.io/assets/translations/`:

```
translations/
├── en.json (English)
├── zh.json (Chinese)
├── hi.json (Hindi)
├── es.json (Spanish)
├── fr.json (French)
├── ar.json (Arabic)
├── bn.json (Bengali)
├── ru.json (Russian)
├── pt.json (Portuguese)
└── de.json (German)
```

Each file should contain key-value pairs for all translatable text:
```json
{
  "nav.home": "Home",
  "nav.about": "About Us",
  "dashboard.welcome": "Welcome",
  ...
}
```

### 2. JavaScript i18n Utility
Create `/public/copytradingbroker.io/assets/js/i18n.js`:

```javascript
const I18N = {
    currentLanguage: 'en',
    translations: {},

    async init() {
        // Detect language or load user preference
        // Load translation file
        // Apply translations to page
    },

    async loadLanguage(langCode) {
        // Fetch translation file
        // Store in translations object
        // Apply to page
    },

    translate(key) {
        // Return translated text for key
    },

    applyTranslations() {
        // Find all elements with data-i18n attribute
        // Replace text with translations
    }
}
```

### 3. Dashboard Language Selector UI
Add to `/public/copytradingbroker.io/dashboard.html` (next to dark mode toggle):

```html
<!-- Language Selector Button -->
<div class="language-selector" id="language-selector">
    <button class="language-btn" id="language-btn" onclick="toggleLanguageDropdown()">
        <span class="flag-icon" id="current-language-flag">🇺🇸</span>
        <span class="language-text" id="current-language-text">EN</span>
        <i class="fas fa-chevron-down"></i>
    </button>
    <div class="language-dropdown" id="language-dropdown">
        <div class="language-option" onclick="changeLanguage('en')">
            <span class="flag-icon">🇺🇸</span>
            <span>English</span>
        </div>
        <div class="language-option" onclick="changeLanguage('zh')">
            <span class="flag-icon">🇨🇳</span>
            <span>中文 (Chinese)</span>
        </div>
        <!-- Add all 10 languages -->
    </div>
</div>
```

CSS styling (add to dashboard.html styles):
```css
.language-selector {
    position: fixed;
    top: 70px;
    right: 150px; /* Position left of dark mode toggle */
    z-index: 9998;
}

.language-btn {
    background: var(--bg-card);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 15px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
}

.language-dropdown {
    display: none;
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--bg-card);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    margin-top: 8px;
    min-width: 200px;
    max-height: 400px;
    overflow-y: auto;
}

.language-dropdown.show {
    display: block;
}

.language-option {
    padding: 12px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}

.language-option:hover {
    background: var(--card-hover);
}
```

### 4. Main Website Language Selector
Add to `/public/copytradingbroker.io/index.html` navigation:

```html
<!-- In navbar, after main menu items -->
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="languageDropdown" role="button"
       data-bs-toggle="dropdown" aria-expanded="false">
        <span id="current-lang-flag">🇺🇸</span>
        <span id="current-lang-code">EN</span>
    </a>
    <ul class="dropdown-menu" aria-labelledby="languageDropdown">
        <li><a class="dropdown-item" href="#" onclick="changeLanguage('en')">
            🇺🇸 English
        </a></li>
        <li><a class="dropdown-item" href="#" onclick="changeLanguage('zh')">
            🇨🇳 中文 (Chinese)
        </a></li>
        <!-- Add all 10 languages -->
    </ul>
</li>
```

### 5. Language Switching Logic
Create `/public/copytradingbroker.io/assets/js/language.js`:

```javascript
// Detect and set language on page load
async function initLanguage() {
    // Check localStorage for saved preference
    let savedLang = localStorage.getItem('language');

    if (!savedLang) {
        // Detect language from IP
        try {
            const response = await fetch('/api/language/detect');
            const data = await response.json();
            savedLang = data.detected_language || 'en';
        } catch (error) {
            savedLang = 'en';
        }
    }

    await changeLanguage(savedLang, false);
}

async function changeLanguage(langCode, savePreference = true) {
    try {
        // Load translation file
        const response = await fetch(`/assets/translations/${langCode}.json`);
        const translations = await response.json();

        // Apply translations to page
        applyTranslations(translations);

        // Update UI
        updateLanguageUI(langCode);

        // Save to localStorage
        localStorage.setItem('language', langCode);

        // If user is authenticated, save to database
        if (savePreference && typeof TED_AUTH !== 'undefined') {
            await saveLanguagePreference(langCode);
        }
    } catch (error) {
        console.error('Error changing language:', error);
    }
}

async function saveLanguagePreference(langCode) {
    try {
        await TED_AUTH.apiCall('/api/language/preference', {
            method: 'PUT',
            body: JSON.stringify({ language: langCode })
        });
    } catch (error) {
        console.error('Error saving language preference:', error);
    }
}

function applyTranslations(translations) {
    // Find all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key]) {
            element.textContent = translations[key];
        }
    });

    // Find all elements with data-i18n-placeholder attribute
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
            element.placeholder = translations[key];
        }
    });
}

function updateLanguageUI(langCode) {
    const languages = {
        'en': { flag: '🇺🇸', text: 'EN' },
        'zh': { flag: '🇨🇳', text: 'ZH' },
        'hi': { flag: '🇮🇳', text: 'HI' },
        'es': { flag: '🇪🇸', text: 'ES' },
        'fr': { flag: '🇫🇷', text: 'FR' },
        'ar': { flag: '🇸🇦', text: 'AR' },
        'bn': { flag: '🇧🇩', text: 'BN' },
        'ru': { flag: '🇷🇺', text: 'RU' },
        'pt': { flag: '🇵🇹', text: 'PT' },
        'de': { flag: '🇩🇪', text: 'DE' }
    };

    const lang = languages[langCode] || languages['en'];

    // Update current language display
    const flagElement = document.getElementById('current-language-flag') ||
                       document.getElementById('current-lang-flag');
    const textElement = document.getElementById('current-language-text') ||
                       document.getElementById('current-lang-code');

    if (flagElement) flagElement.textContent = lang.flag;
    if (textElement) textElement.textContent = lang.text;
}

function toggleLanguageDropdown() {
    const dropdown = document.getElementById('language-dropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const selector = document.getElementById('language-selector');
    const dropdown = document.getElementById('language-dropdown');

    if (selector && dropdown && !selector.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Initialize language on page load
document.addEventListener('DOMContentLoaded', initLanguage);
```

### 6. Add data-i18n Attributes to HTML
Update all HTML files to add `data-i18n` attributes to translatable text:

```html
<!-- Before -->
<h1>Welcome to TED Brokers</h1>

<!-- After -->
<h1 data-i18n="home.welcome">Welcome to TED Brokers</h1>
```

### 7. RTL Language Support
For Arabic (ar), add RTL CSS:

```css
[dir="rtl"] {
    direction: rtl;
    text-align: right;
}

[dir="rtl"] .navbar {
    flex-direction: row-reverse;
}
```

## Implementation Priority

1. **High Priority - Core Functionality**:
   - Create English translation file (en.json) with all keys
   - Implement language.js with switching logic
   - Add language selector UI to dashboard
   - Test with English only

2. **Medium Priority - Multi-language**:
   - Create translation files for Spanish, French, German
   - Add language selector to main website
   - Test language switching

3. **Low Priority - Complete**:
   - Add remaining language translations
   - Implement RTL support for Arabic
   - Add language preference for logged-out users
   - Optimize translation loading

## Testing Checklist

- [ ] Language detected correctly based on IP
- [ ] Language selector displays current language with flag
- [ ] Clicking language option changes page text
- [ ] Language preference saved to database for authenticated users
- [ ] Language preference saved to localStorage for guests
- [ ] Page reloads with saved language
- [ ] All UI text translated correctly
- [ ] Forms and placeholders translated
- [ ] RTL layout works for Arabic
- [ ] Language selector works on all pages

## Notes

- Translation files can use Google Translate API or professional translation services
- Consider using a translation management platform like Lokalise or Crowdin
- Flag emojis may not display consistently across all devices - consider using SVG flags
- For production, minify translation files
- Consider lazy-loading translation files
- Add loading indicators when switching languages
