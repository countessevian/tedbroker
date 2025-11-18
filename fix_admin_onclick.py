#!/usr/bin/env python3
"""
Remove all onclick attributes from admin-dashboard.js dynamically generated HTML
and replace with data attributes for event delegation
"""

import re

# Read the file
with open('public/copytradingbroker.io/assets/js/admin-dashboard.js', 'r') as f:
    content = f.read()

# Pattern to find onclick attributes and extract the function call
onclick_pattern = r'onclick="(\w+)\(\'([^\']+)\'\)"'

# Replace with data attribute
def replace_onclick(match):
    function_name = match.group(1)
    id_value = match.group(2)

    # Map function names to data attributes
    data_attr_map = {
        'viewUser': 'data-user-id',
        'activateUser': 'data-user-id',
        'deactivateUser': 'data-user-id',
        'showEditTraderModal': 'data-trader-id',
        'deleteTrader': 'data-trader-id',
        'showEditPlanModal': 'data-plan-id',
        'deletePlan': 'data-plan-id',
        'approveDeposit': 'data-request-id',
        'rejectDeposit': 'data-request-id',
        'viewWithdrawalDetails': 'data-request-id',
        'approveWithdrawal': 'data-request-id',
        'rejectWithdrawal': 'data-request-id',
        'deleteCryptoWallet': 'data-wallet-id',
        'deleteBankAccount': 'data-account-id',
        'deleteNotification': 'data-notification-id',
        'selectUserForNotification': 'data-user-id',
        'showAddTraderModal': '',
        'showAddPlanModal': '',
        'showAddCryptoWalletModal': '',
        'showAddBankAccountModal': '',
        'showCreateNotificationModal': '',
    }

    data_attr = data_attr_map.get(function_name, 'data-id')
    if data_attr:
        return f'{data_attr}="{id_value}"'
    else:
        return ''

# Replace all onclick attributes
content = re.sub(onclick_pattern, replace_onclick, content)

# Special case: selectUserForNotification has 3 parameters
# onclick="selectUserForNotification('${user.id}', '${user.username}', '${user.email}')"
select_user_pattern = r'onclick="selectUserForNotification\(\'([^\']+)\',\s*\'([^\']+)\',\s*\'([^\']+)\'\)"'
content = re.sub(select_user_pattern, r'data-user-id="\1" data-username="\2" data-email="\3"', content)

# Write back
with open('public/copytradingbroker.io/assets/js/admin-dashboard.js', 'w') as f:
    f.write(content)

print("✅ Successfully removed onclick attributes and added data attributes")
print("✅ Admin dashboard buttons will now use event delegation")
