#!/usr/bin/env python3
"""
Script to update all HTML pages with consistent theme and clean URLs
"""
import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path("public/copytradingbroker.io")

# HTML files to update (excluding plugin files)
html_files = [
    "about-us.html",
    "contact-us.html",
    "faqs.html",
    "investors.html",
    "traders.html",
    "how_it_works.html",
    "register.html",
    "login.html",
    "forgot-password.html",
    "legal/privacy_policy.html",
    "legal/terms_conditions.html",
    "legal/aml_policy.html",
    "legal/risk_closure.html"
]

# CSS link to add
custom_css_link = '<link rel="stylesheet" href="assets/css/custom-theme.css" />'
custom_css_link_legal = '<link rel="stylesheet" href="../assets/css/custom-theme.css" />'

def update_html_file(file_path, is_legal=False):
    """Update a single HTML file"""
    full_path = BASE_DIR / file_path

    if not full_path.exists():
        print(f"Skipping {file_path} - file not found")
        return

    print(f"Updating {file_path}...")

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add custom CSS if not already present
    css_link = custom_css_link_legal if is_legal else custom_css_link
    if 'custom-theme.css' not in content:
        # Find the last stylesheet link and add our custom CSS after it
        content = re.sub(
            r'(</head>)',
            f'\t{css_link}\n\\1',
            content,
            count=1
        )

    # Update navigation links to remove .html extension
    # Update all href links ending with .html (except in scripts)
    content = re.sub(
        r'href="([^"]+?)\.html"',
        r'href="\1"',
        content
    )

    # Fix logo link if it points to index-2
    content = content.replace('href="index-2"', 'href="index"')
    content = content.replace('href="index-2.html"', 'href="index"')

    # Update logo image to have consistent styling
    if 'tedbrokers-logo.jpg' in content:
        content = re.sub(
            r'<img\s+src="([^"]*tedbrokers-logo\.jpg)"[^>]*>',
            r'<img src="\1" alt="TED Brokers" width="200" style="border-radius: 10px; border: 1px solid #D32F2F;" />',
            content
        )

    # Write updated content
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated {file_path}")

def main():
    print("Starting website theme consistency update...\n")

    # Update non-legal pages
    for html_file in html_files:
        is_legal = html_file.startswith('legal/')
        update_html_file(html_file, is_legal)

    print("\n✓ All pages updated successfully!")
    print("Theme is now consistent across all pages with clean URLs.")

if __name__ == "__main__":
    main()
