#!/usr/bin/env python3
"""
Script to add chat widget to all HTML pages
"""
import os
import glob

# Chat widget script tag to add
CHAT_WIDGET_SCRIPT = '''    <!-- Chat Support Widget -->
    <script src="/assets/js/chat-events.js"></script>
    <script src="/assets/js/chat-widget.js"></script>
'''

def add_chat_widget_to_file(file_path):
    """Add chat widget script to an HTML file if not already present"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if already has chat widget (but update if missing chat-events.js)
        if 'chat-widget.js' in content:
            if 'chat-events.js' not in content:
                # Update to include chat-events.js
                content = content.replace(
                    '<script src="/assets/js/chat-widget.js"></script>',
                    '<script src="/assets/js/chat-events.js"></script>\n    <script src="/assets/js/chat-widget.js"></script>'
                )
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ Updated with chat-events.js: {file_path}")
                return True
            else:
                print(f"  ✓ Skipped (already has chat widget): {file_path}")
                return False

        # Find </body> tag and add chat widget before it
        if '</body>' in content:
            content = content.replace('</body>', f'{CHAT_WIDGET_SCRIPT}</body>')

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  ✓ Added chat widget to: {file_path}")
            return True
        else:
            print(f"  ✗ No </body> tag found in: {file_path}")
            return False

    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")
        return False

def main():
    # Find all HTML files
    html_dir = 'public/copytradingbroker.io'

    if not os.path.exists(html_dir):
        print(f"Error: Directory {html_dir} not found")
        return

    # Get all HTML files in the directory
    html_files = glob.glob(f'{html_dir}/*.html')
    html_files += glob.glob(f'{html_dir}/legal/*.html')

    print(f"Found {len(html_files)} HTML files\n")
    print("Adding chat widget to HTML files...\n")

    added_count = 0
    for html_file in html_files:
        if add_chat_widget_to_file(html_file):
            added_count += 1

    print(f"\n✓ Successfully added chat widget to {added_count} files")
    print(f"✓ Skipped {len(html_files) - added_count} files (already had chat widget or no </body> tag)")

if __name__ == '__main__':
    main()
