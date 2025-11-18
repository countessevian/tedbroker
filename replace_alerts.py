#!/usr/bin/env python3
"""
Script to replace all browser alert() and confirm() calls with SwalHelper calls
"""

import re
import os

# Define files to process
files_to_process = [
    "/home/taliban/websites/tedbroker.com/public/copytradingbroker.io/assets/js/dashboard.js",
    "/home/taliban/websites/tedbroker.com/public/copytradingbroker.io/assets/js/admin-dashboard.js",
    "/home/taliban/websites/tedbroker.com/public/copytradingbroker.io/assets/js/admin-chat.js",
    "/home/taliban/websites/tedbroker.com/public/copytradingbroker.io/assets/js/chat-widget.js",
]

def replace_simple_alert(content):
    """Replace simple alert('message') with Swal.fire()"""

    def determine_alert_type(message):
        """Determine the icon and title based on message content"""
        lower_msg = message.lower()
        if any(word in lower_msg for word in ['success', 'copied', 'updated', 'activated', 'approved', 'sent', 'credited']):
            return 'success', 'Success!'
        elif any(word in lower_msg for word in ['error', 'failed', 'fail', 'cannot', 'unable']):
            return 'error', 'Error!'
        elif any(word in lower_msg for word in ['please', 'minimum', 'maximum', 'required', 'must', 'invalid']):
            return 'warning', 'Warning'
        else:
            return 'info', 'Notice'

    def alert_replacement(match):
        quote = match.group(1)
        message = match.group(2)
        icon, title = determine_alert_type(message)

        # Handle multi-line messages (with \n or \\n)
        if '\\n' in message or '\n' in message:
            # Convert to HTML
            html_message = message.replace('\\n', '<br>').replace('\n', '<br>')
            return f"Swal.fire({{ title: '{title}', html: {quote}{html_message}{quote}, icon: '{icon}' }})"
        else:
            return f"Swal.fire({{ title: '{title}', text: {quote}{message}{quote}, icon: '{icon}' }})"

    # Match alert with single-quoted strings
    content = re.sub(
        r"alert\((['])([^']+)\1\)",
        alert_replacement,
        content
    )

    # Match alert with double-quoted strings
    content = re.sub(
        r'alert\((["])([^"]+)\1\)',
        alert_replacement,
        content
    )

    # Match alert with template strings
    content = re.sub(
        r"alert\(([`])([^`]+)\1\)",
        alert_replacement,
        content
    )

    return content

def replace_confirm(content):
    """Replace confirm() with Swal.fire() - needs async handling"""
    # For simple inline confirms in if statements
    # if (confirm('message'))  =>  if ((await Swal.fire({...})).isConfirmed)

    def confirm_replacement(message):
        return f"""(await Swal.fire({{
                title: 'Confirm Action',
                text: '{message}',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            }})).isConfirmed"""

    # For regular confirms: if (confirm('message'))
    content = re.sub(
        r"if\s*\(\s*confirm\('([^']+)'\)\s*\)",
        lambda m: f"if ({confirm_replacement(m.group(1))})",
        content
    )

    content = re.sub(
        r'if\s*\(\s*confirm\("([^"]+)"\)\s*\)',
        lambda m: f"if ({confirm_replacement(m.group(1))})",
        content
    )

    content = re.sub(
        r"if\s*\(\s*confirm\(`([^`]+)`\)\s*\)",
        lambda m: f"if ({confirm_replacement(m.group(1))})",
        content
    )

    # For negated confirms: if (!confirm('message'))
    content = re.sub(
        r"if\s*\(\s*!\s*confirm\('([^']+)'\)\s*\)",
        lambda m: f"if (!{confirm_replacement(m.group(1))})",
        content
    )

    content = re.sub(
        r'if\s*\(\s*!\s*confirm\("([^"]+)"\)\s*\)',
        lambda m: f"if (!{confirm_replacement(m.group(1))})",
        content
    )

    content = re.sub(
        r"if\s*\(\s*!\s*confirm\(`([^`]+)`\)\s*\)",
        lambda m: f"if (!{confirm_replacement(m.group(1))})",
        content
    )

    return content

def make_function_async(content, function_names):
    """Add async keyword to functions that use await"""
    for func_name in function_names:
        # Match function declarations
        content = re.sub(
            rf"function\s+{func_name}\s*\(",
            rf"async function {func_name}(",
            content
        )

        # Match arrow function expressions assigned to const
        content = re.sub(
            rf"const\s+{func_name}\s*=\s*\(",
            rf"const {func_name} = async (",
            content
        )

    return content

def process_file(filepath):
    """Process a single file"""
    print(f"Processing {os.path.basename(filepath)}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace alerts
    content = replace_simple_alert(content)

    # Replace confirms
    content = replace_confirm(content)

    # Make functions async if they use confirm (which is now await)
    # Extract function names that have await Swal.fire
    functions_with_await = re.findall(r'(?:function|const)\s+(\w+)\s*[=(].*?await\s+Swal\.fire', content, re.DOTALL)
    if functions_with_await:
        content = make_function_async(content, set(functions_with_await))

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {os.path.basename(filepath)}")
        return True
    else:
        print(f"  - No changes needed for {os.path.basename(filepath)}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("Replacing browser alerts/confirms with SwalHelper")
    print("=" * 60)
    print()

    updated_count = 0
    for filepath in files_to_process:
        if os.path.exists(filepath):
            if process_file(filepath):
                updated_count += 1
        else:
            print(f"  ✗ File not found: {filepath}")

    print()
    print("=" * 60)
    print(f"Complete! Updated {updated_count} file(s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
