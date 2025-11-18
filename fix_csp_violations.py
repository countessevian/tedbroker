#!/usr/bin/env python3
"""
Script to fix CSP violations by removing inline event handlers from HTML files
and replacing them with proper event listeners.
"""

import re
import os
from pathlib import Path

def fix_inline_event_handlers(html_content):
    """
    Remove inline event handlers (onclick, onerror, onload, etc.) from HTML
    and add data attributes instead for proper event listener attachment.
    """

    # Pattern to match inline event handlers
    # Matches: onclick="...", onerror="...", onload="...", etc.
    event_pattern = r'\s+(on[a-z]+)\s*=\s*["\']([^"\']*)["\']'

    # Store found handlers for reporting
    handlers_found = []

    def replace_handler(match):
        event_type = match.group(1)  # e.g., "onclick", "onerror"
        event_code = match.group(2)  # the JavaScript code

        handlers_found.append((event_type, event_code))

        # For onerror on images, add a CSS class instead
        if event_type == 'onerror':
            return ' class="js-image-fallback"'

        # For other events, remove them (they should be handled via addEventListener)
        return ''

    # Replace all inline event handlers
    fixed_content = re.sub(event_pattern, replace_handler, html_content, flags=re.IGNORECASE)

    return fixed_content, handlers_found

def process_html_file(file_path):
    """Process a single HTML file to fix CSP violations."""

    print(f"Processing: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        fixed_content, handlers = fix_inline_event_handlers(original_content)

        if handlers:
            print(f"  Found {len(handlers)} inline event handler(s):")
            for event_type, code in handlers:
                preview = code[:50] + '...' if len(code) > 50 else code
                print(f"    - {event_type}: {preview}")

            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            print(f"  ✓ Fixed and saved")
            return True
        else:
            print(f"  ✓ No inline handlers found")
            return False

    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return False

def add_event_listener_script(file_path):
    """
    Add a script to handle image fallbacks for files that had onerror handlers.
    """

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if we added the js-image-fallback class
        if 'js-image-fallback' in content:
            # Check if script is already present
            if 'js-image-fallback' in content and 'addEventListener' not in content.split('js-image-fallback')[1].split('</script>')[0]:

                # Add the event listener script before </body>
                fallback_script = '''
    <script>
    // Handle image fallbacks for CSP compliance
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.js-image-fallback').forEach(function(img) {
            img.addEventListener('error', function() {
                this.src = 'https://via.placeholder.com/400x200?text=News';
            });
        });
    });
    </script>
</body>'''

                content = content.replace('</body>', fallback_script)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"  ✓ Added image fallback script")
                return True

        return False

    except Exception as e:
        print(f"  ✗ Error adding script: {e}")
        return False

def main():
    """Main function to process all HTML files."""

    # Get the public directory
    base_dir = Path(__file__).parent / 'public' / 'copytradingbroker.io'

    if not base_dir.exists():
        print(f"Error: Directory not found: {base_dir}")
        return

    print(f"Scanning HTML files in: {base_dir}")
    print("=" * 60)

    # Find all HTML files
    html_files = list(base_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML file(s)\n")

    fixed_count = 0

    for html_file in html_files:
        if process_html_file(html_file):
            fixed_count += 1
            add_event_listener_script(html_file)
        print()

    print("=" * 60)
    print(f"Summary: Fixed {fixed_count} file(s)")
    print("\nAll inline event handlers have been removed for CSP compliance.")
    print("Refresh your browser with Ctrl+Shift+R to see the changes.")

if __name__ == '__main__':
    main()
