#!/usr/bin/env python3
"""
Script to add event listeners to admin-dashboard.js for all buttons that had onclick handlers removed.
This restores functionality after CSP compliance fixes.
"""

import re

# Read the admin-dashboard.js file
with open('public/copytradingbroker.io/assets/js/admin-dashboard.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Event listener code to add at the end of the DOMContentLoaded handler
event_listeners_code = """
    // ============================================================================
    // EVENT LISTENERS - Restore functionality after CSP compliance
    // ============================================================================

    // Search Users button
    const searchUsersBtn = document.querySelector('button[onclick*="searchUsers"]');
    if (searchUsersBtn) {
        searchUsersBtn.removeAttribute('onclick');
        searchUsersBtn.addEventListener('click', searchUsers);
    }

    // Add Trader button
    const addTraderBtn = document.querySelector('button:not([type="submit"]):not([type="button"])');
    const addTraderBtns = document.querySelectorAll('.btn.btn-primary');
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Add Trader')) {
            btn.addEventListener('click', showAddTraderModal);
        }
    });

    // Add Plan button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Add Plan')) {
            btn.addEventListener('click', showAddPlanModal);
        }
    });

    // Filter Deposit Requests button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Filter') && btn.closest('#tab-deposits')) {
            btn.addEventListener('click', filterDepositRequests);
        }
    });

    // Filter Withdrawal Requests button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Filter') && btn.closest('#tab-withdrawals')) {
            btn.addEventListener('click', filterWithdrawalRequests);
        }
    });

    // Add Bank Account button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Add Bank Account')) {
            btn.addEventListener('click', showAddBankAccountModal);
        }
    });

    // Add Crypto Wallet button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Add Crypto Wallet')) {
            btn.addEventListener('click', showAddCryptoWalletModal);
        }
    });

    // Create Notification button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Create Notification')) {
            btn.addEventListener('click', showCreateNotificationModal);
        }
    });

    // Filter Chats button
    addTraderBtns.forEach(btn => {
        if (btn.textContent.includes('Filter') && btn.closest('#tab-chats')) {
            btn.addEventListener('click', filterChats);
        }
    });

    // Send Admin Message button
    const sendMessageBtns = document.querySelectorAll('.btn.btn-primary');
    sendMessageBtns.forEach(btn => {
        if (btn.textContent.includes('Send')) {
            btn.addEventListener('click', sendAdminMessage);
        }
    });

    // Close Conversation button
    const closeConversationBtns = document.querySelectorAll('.btn.btn-success');
    closeConversationBtns.forEach(btn => {
        if (btn.textContent.includes('Close')) {
            btn.addEventListener('click', closeConversation);
        }
    });

    // Modal close buttons
    const modalCloseBtns = document.querySelectorAll('.btn.btn-secondary');
    modalCloseBtns.forEach(btn => {
        const text = btn.textContent.trim();
        if (text === 'Cancel' || text === 'Close') {
            const modal = btn.closest('.modal');
            if (modal) {
                const modalId = modal.id;
                if (modalId === 'addTraderModal') {
                    btn.addEventListener('click', closeAddTraderModal);
                } else if (modalId === 'editTraderModal') {
                    btn.addEventListener('click', hideEditTraderModal);
                } else if (modalId === 'addPlanModal') {
                    btn.addEventListener('click', hideAddPlanModal);
                } else if (modalId === 'editPlanModal') {
                    btn.addEventListener('click', hideEditPlanModal);
                } else if (modalId === 'addCryptoWalletModal') {
                    btn.addEventListener('click', hideAddCryptoWalletModal);
                } else if (modalId === 'userDetailsModal') {
                    btn.addEventListener('click', closeUserDetailsModal);
                } else if (modalId === 'createNotificationModal') {
                    btn.addEventListener('click', hideCreateNotificationModal);
                } else if (modalId === 'addBankAccountModal') {
                    btn.addEventListener('click', hideAddBankAccountModal);
                } else if (modalId === 'withdrawalDetailsModal') {
                    btn.addEventListener('click', closeWithdrawalDetailsModal);
                }
            }
        }
    });

    // User details modal tabs
    const userTabBtns = document.querySelectorAll('.user-tab-btn');
    userTabBtns.forEach(btn => {
        const tab = btn.getAttribute('data-tab');
        if (tab) {
            btn.addEventListener('click', function() {
                switchUserTab(tab);
            });
        }
    });

    // Logout button
    const logoutMenuItem = document.querySelector('.menu-item[style*="border-top"]');
    if (logoutMenuItem && logoutMenuItem.textContent.includes('Logout')) {
        logoutMenuItem.addEventListener('click', logout);
    }

    console.log('✓ All admin dashboard event listeners restored after CSP compliance');
"""

# Find the end of the DOMContentLoaded handler
# Look for the closing of the DOMContentLoaded function
pattern = r"(document\.addEventListener\('DOMContentLoaded', async \(\) => \{[\s\S]*?)(^\}\);$)"

match = re.search(pattern, content, re.MULTILINE)
if match:
    # Insert before the closing });
    insert_pos = match.end(1)
    new_content = content[:insert_pos] + "\n" + event_listeners_code + "\n" + content[insert_pos:]

    # Write the updated file
    with open('public/copytradingbroker.io/assets/js/admin-dashboard.js', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✓ Event listeners added successfully to admin-dashboard.js")
    print(f"✓ Inserted at position {insert_pos}")
else:
    print("✗ Could not find DOMContentLoaded handler")
    print("Trying alternative approach...")

    # Alternative: Find the last line and insert before it
    lines = content.split('\n')
    # Find the last }); or end of file
    for i in range(len(lines) - 1, -1, -1):
        if '});' in lines[i] and i < 50:  # Should be near the end
            lines.insert(i, event_listeners_code)
            new_content = '\n'.join(lines)

            with open('public/copytradingbroker.io/assets/js/admin-dashboard.js', 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✓ Event listeners added successfully at line {i}")
            break
    else:
        print("✗ Could not find suitable insertion point")
