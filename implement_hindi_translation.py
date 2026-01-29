#!/usr/bin/env python3
"""
Script to implement Hindi translation on all pages
"""

import os
import re

# Pages that need updates
PAGES_WITH_LANGUAGE_JS = ['faqs', 'traders', 'investors']
PAGES_WITHOUT_LANGUAGE_JS = ['login', 'register', 'forgot-password', 'privacy-policy', 'how_it_works']

# Language dropdown HTML
LANGUAGE_DROPDOWN = '''			<!-- Language Selector -->
			<div class="dropdown">
				<button class="btn btn-outline-primary-dark dropdown-toggle d-flex align-items-center gap-2" type="button" id="languageDropdown" data-bs-toggle="dropdown" aria-expanded="false" style="min-width: 120px;">
					<span id="current-lang-flag">🇺🇸</span>
					<span id="current-lang-code">EN</span>
				</button>
				<ul class="dropdown-menu dropdown-menu-end" aria-labelledby="languageDropdown">
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('en'); return false;">
						<span>🇺🇸</span> <span>English</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('zh'); return false;">
						<span>🇨🇳</span> <span>中文 (Chinese)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('hi'); return false;">
						<span>🇮🇳</span> <span>हिन्दी (Hindi)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('es'); return false;">
						<span>🇪🇸</span> <span>Español (Spanish)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('fr'); return false;">
						<span>🇫🇷</span> <span>Français (French)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('ar'); return false;">
						<span>🇸🇦</span> <span>العربية (Arabic)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('bn'); return false;">
						<span>🇧🇩</span> <span>বাংলা (Bengali)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('ru'); return false;">
						<span>🇷🇺</span> <span>Русский (Russian)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('pt'); return false;">
						<span>🇵🇹</span> <span>Português (Portuguese)</span>
					</a></li>
					<li><a class="dropdown-item d-flex align-items-center gap-2" href="#" onclick="changeLanguage('de'); return false;">
						<span>🇩🇪</span> <span>Deutsch (German)</span>
					</a></li>
				</ul>
			</div>'''

# Language script HTML
LANGUAGE_SCRIPT = '''    <!-- Language System -->
    <script src="/assets/js/language.js?v=3.0"></script>'''

def add_language_dropdown(file_path):
    """Add language dropdown to navbar if not present"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if dropdown already exists
    if 'languageDropdown' in content:
        print(f"  ✓ Language dropdown already exists in {file_path}")
        return False

    # Find the position to insert dropdown
    # Look for the "Get started" button and wrap it with the dropdown
    pattern = r'(\s*<div class="">\s*<a href="register" class="btn btn-outline-primary-dark"[^>]*>Get started</a>\s*</div>)'

    replacement = r'\t\t<div class="d-flex align-items-center gap-3">\n\t\t\t<a href="register" class="btn btn-outline-primary-dark" data-i18n="btn.getStarted">Get started</a>\n' + LANGUAGE_DROPDOWN + '\n\t\t</div>'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✓ Added language dropdown to {file_path}")
        return True
    else:
        print(f"  ⚠ Could not find insertion point for dropdown in {file_path}")
        return False

def add_language_script(file_path):
    """Add language.js script before closing body tag if not present"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if script already exists
    if 'language.js' in content:
        print(f"  ✓ Language script already exists in {file_path}")
        return False

    # Find closing body tag
    pattern = r'(</body>)'
    replacement = LANGUAGE_SCRIPT + '\n' + r'\1'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✓ Added language script to {file_path}")
        return True
    else:
        print(f"  ⚠ Could not add language script to {file_path}")
        return False

def process_pages():
    """Process all pages to add language support"""
    base_dir = '/home/taliban/websites/tedbroker.com/public/copytradingbroker.io'

    # Process pages that have language.js but need dropdown
    print("\n=== Processing pages with language.js (need dropdown only) ===")
    for page in PAGES_WITH_LANGUAGE_JS:
        file_path = os.path.join(base_dir, f"{page}.html")
        if os.path.exists(file_path):
            print(f"\nProcessing {page}.html:")
            add_language_dropdown(file_path)
        else:
            print(f"  ✗ File not found: {file_path}")

    # Process pages that need both language.js and dropdown
    print("\n=== Processing pages without language.js (need both) ===")
    for page in PAGES_WITHOUT_LANGUAGE_JS:
        file_path = os.path.join(base_dir, f"{page}.html")
        if os.path.exists(file_path):
            print(f"\nProcessing {page}.html:")
            add_language_dropdown(file_path)
            add_language_script(file_path)
        else:
            print(f"  ✗ File not found: {file_path}")

if __name__ == "__main__":
    process_pages()
    print("\n✓ Processing complete!")