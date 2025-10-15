/**
 * Dashboard Page Handler
 * Manages user dashboard data display and authentication
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Protect the page - redirect to login if not authenticated
    TED_AUTH.protectPage();

    // Get user data from localStorage
    let userData = TED_AUTH.getUser();

    // If no user data in localStorage, fetch from API
    if (!userData) {
        TED_AUTH.showLoading('Loading your profile...');
        const result = await TED_AUTH.fetchCurrentUser();
        TED_AUTH.closeLoading();

        if (!result.success) {
            TED_AUTH.showError('Failed to load user data. Please login again.');
            TED_AUTH.logout();
            return;
        }

        userData = result.data;
    }

    // Populate dashboard with user data
    populateDashboard(userData);

    // Load expert traders when traders tab is clicked
    const tradersTab = document.querySelector('.menu-item[data-tab="traders"]');
    if (tradersTab) {
        tradersTab.addEventListener('click', loadExpertTraders);
    }

    // Load investment plans when subscription tab is clicked
    const subscriptionTab = document.querySelector('.menu-item[data-tab="subscription"]');
    if (subscriptionTab) {
        subscriptionTab.addEventListener('click', loadInvestmentPlans);
    }

    // Load wallet data when wallet tab is clicked
    const walletTab = document.querySelector('.menu-item[data-tab="wallet"]');
    if (walletTab) {
        walletTab.addEventListener('click', loadWalletData);
    }
});

/**
 * Populate dashboard with user information
 */
function populateDashboard(userData) {
    // Display name (use full name if available, otherwise username)
    const displayName = userData.full_name || userData.username;
    document.getElementById('user-display-name').textContent = displayName;

    // User avatar (first letter of name)
    const avatarLetter = displayName.charAt(0).toUpperCase();
    document.getElementById('user-avatar').textContent = avatarLetter;

    // Populate mobile app bar
    document.getElementById('mobile-user-avatar').textContent = avatarLetter;
    document.getElementById('mobile-user-name').textContent = displayName;

    // Full name
    document.getElementById('user-fullname').textContent = userData.full_name || userData.username;

    // Username
    document.getElementById('user-username').textContent = '@' + userData.username;

    // Email
    document.getElementById('user-email').textContent = userData.email;

    // Phone (show only if provided)
    if (userData.phone) {
        document.getElementById('user-phone').textContent = userData.phone;
        document.getElementById('user-phone-row').style.display = 'flex';
    }

    // Gender (show only if provided)
    if (userData.gender) {
        document.getElementById('user-gender').textContent = userData.gender;
        document.getElementById('user-gender-row').style.display = 'flex';
    }

    // Country (show only if provided)
    if (userData.country) {
        document.getElementById('user-country').textContent = userData.country;
        document.getElementById('user-country-row').style.display = 'flex';
    }

    // Account types (show only if provided)
    if (userData.account_types && userData.account_types.length > 0) {
        const accountTypesText = userData.account_types.join(', ');
        document.getElementById('user-account-types').textContent = accountTypesText;
        document.getElementById('user-account-types-row').style.display = 'flex';
    }

    // Account status
    const statusElement = document.getElementById('user-status');
    if (userData.is_active) {
        statusElement.textContent = 'Active';
        statusElement.className = 'badge-status badge-active';
    } else {
        statusElement.textContent = 'Inactive';
        statusElement.className = 'badge-status badge-inactive';
    }

    // Verification status
    const verificationElement = document.getElementById('user-verification');
    if (userData.is_verified) {
        verificationElement.textContent = 'Verified';
        verificationElement.className = 'badge-status badge-active';
    } else {
        verificationElement.textContent = 'Pending';
        verificationElement.className = 'badge-status badge-pending';
    }

    // Member since date
    if (userData.created_at) {
        const createdDate = new Date(userData.created_at);
        const formattedDate = formatDate(createdDate);
        document.getElementById('user-created').textContent = formattedDate;
    }

    console.log('Dashboard populated with user data:', userData);
}

/**
 * Format date to readable string
 */
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Handle logout
 */
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        TED_AUTH.logout();
    }
}

/**
 * Load and display expert traders from API
 */
let tradersLoaded = false; // Flag to prevent multiple loads

async function loadExpertTraders() {
    // Only load once
    if (tradersLoaded) return;

    const container = document.getElementById('traders-container');
    container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading traders...</p>';

    try {
        // Get JWT token using the auth utility
        const token = TED_AUTH.getToken();
        if (!token) {
            container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Authentication required. Please login again.</p>';
            return;
        }

        // Fetch traders from API using the auth utility
        const response = await TED_AUTH.apiCall('/api/traders/', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch traders: ${response.statusText}`);
        }

        const traders = await response.json();

        // Display traders
        if (traders.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No expert traders available at the moment.</p>';
            return;
        }

        container.innerHTML = '';
        traders.forEach(trader => {
            const traderCard = createTraderCard(trader);
            container.appendChild(traderCard);
        });

        tradersLoaded = true;
    } catch (error) {
        console.error('Error loading traders:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load traders. Please try again later.</p>';
    }
}

/**
 * Create a trader card element
 */
function createTraderCard(trader) {
    const card = document.createElement('div');
    card.className = 'trader-card';

    // Determine return color
    const returnColor = trader.ytd_return > 0 ? '#4caf50' : '#f44336';
    const returnSign = trader.ytd_return > 0 ? '+' : '';

    // Create trades HTML
    const tradesHTML = trader.trades && trader.trades.length > 0 ? `
        <div class="trader-trades">
            <div class="trader-trades-title">Recent Trades (${trader.trades.length})</div>
            <div class="trades-grid">
                ${trader.trades.map(trade => `
                    <div class="trade-item">
                        <div class="trade-ticker">${trade.ticker}</div>
                        <div class="trade-price">$${trade.current_price.toLocaleString()}</div>
                        <span class="trade-position ${trade.position}">${trade.position.toUpperCase()}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    ` : '';

    card.innerHTML = `
        <div class="trader-profile">
            <img src="${trader.profile_photo}" alt="${trader.full_name}" class="trader-profile-photo" />
            <div>
                <h3 style="margin: 0;">${trader.full_name}</h3>
                <p style="color: #8b93a7; margin: 5px 0 0 0; font-size: 14px;">${trader.specialization}</p>
            </div>
        </div>

        <p style="color: #8b93a7; margin-bottom: 15px;">${trader.description}</p>

        <div class="trader-header">
            <div class="trader-stats-grid">
                <div>
                    <div style="font-size: 24px; color: ${returnColor}; font-weight: bold;">${returnSign}${trader.ytd_return}%</div>
                    <div style="color: #8b93a7; font-size: 12px;">YTD Return</div>
                </div>
                <div>
                    <div style="font-size: 24px; color: #7bb6da; font-weight: bold;">${trader.win_rate}%</div>
                    <div style="color: #8b93a7; font-size: 12px;">Win Rate</div>
                </div>
                <div>
                    <div style="font-size: 24px; color: #ff9800; font-weight: bold;">${trader.copiers}</div>
                    <div style="color: #8b93a7; font-size: 12px;">Copiers</div>
                </div>
            </div>
            <button class="btn-primary-custom" onclick="copyTrader('${trader.id}', '${trader.full_name}')">Copy Trader</button>
        </div>

        ${tradesHTML}
    `;

    return card;
}

/**
 * Handle copy trader action
 */
function copyTrader(traderId, traderName) {
    // For now, just show an alert. In production, this would start the copy trading process
    alert(`You are about to copy ${traderName}. This feature will be available soon!`);
    console.log('Copy trader:', traderId);
}

/**
 * Load and display investment plans from API
 */
let plansLoaded = false; // Flag to prevent multiple loads
let userWalletBalance = 0; // Store user's wallet balance

async function loadInvestmentPlans() {
    // Only load once
    if (plansLoaded) return;

    const container = document.getElementById('plans-container');
    container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading investment plans...</p>';

    try {
        // Fetch user data to get wallet balance
        const userData = TED_AUTH.getUser();
        if (!userData || !userData.wallet_balance) {
            // Try to fetch fresh user data
            const userResponse = await TED_AUTH.apiCall('/api/auth/me');
            if (userResponse.ok) {
                const freshUserData = await userResponse.json();
                userWalletBalance = freshUserData.wallet_balance || 0;
                TED_AUTH.saveUser(freshUserData);
            } else {
                userWalletBalance = 0;
            }
        } else {
            userWalletBalance = userData.wallet_balance;
        }

        // Update wallet balance display
        document.getElementById('wallet-balance').textContent = `$${userWalletBalance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

        // Fetch investment plans from API
        const response = await TED_AUTH.apiCall('/api/plans/', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch investment plans: ${response.statusText}`);
        }

        const plans = await response.json();

        // Display plans
        if (plans.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No investment plans available at the moment.</p>';
            return;
        }

        container.innerHTML = '';
        plans.forEach(plan => {
            const planCard = createPlanCard(plan);
            container.appendChild(planCard);
        });

        plansLoaded = true;
    } catch (error) {
        console.error('Error loading investment plans:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load investment plans. Please try again later.</p>';
    }
}

/**
 * Create a plan card element
 */
function createPlanCard(plan) {
    const card = document.createElement('div');
    card.className = 'plan-card';

    // Check if user has sufficient funds
    const hasSufficientFunds = userWalletBalance >= plan.minimum_investment;
    const buttonDisabled = !hasSufficientFunds;

    // Calculate potential profit
    const potentialProfit = (plan.minimum_investment * plan.expected_return_percent / 100).toFixed(2);

    card.innerHTML = `
        <h3 style="color: #7bb6da; margin-bottom: 10px;">${plan.name}</h3>

        <div style="margin: 20px 0;">
            <div style="font-size: 36px; font-weight: bold; color: #000;">$${plan.minimum_investment.toLocaleString()}</div>
            <div style="font-size: 14px; color: #8b93a7;">Minimum Investment</div>
        </div>

        <p style="color: #8b93a7; margin-bottom: 20px; line-height: 1.6;">${plan.description}</p>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; padding: 15px; background: rgba(123, 182, 218, 0.05); border-radius: 8px;">
            <div>
                <div style="font-size: 24px; font-weight: bold; color: #4caf50;">${plan.expected_return_percent}%</div>
                <div style="font-size: 12px; color: #8b93a7;">Expected Return</div>
            </div>
            <div>
                <div style="font-size: 24px; font-weight: bold; color: #7bb6da;">${plan.holding_period_months} mo</div>
                <div style="font-size: 12px; color: #8b93a7;">Holding Period</div>
            </div>
        </div>

        <div style="padding: 12px; background: rgba(123, 182, 218, 0.05); border-radius: 8px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #8b93a7; font-size: 14px;">Potential Profit:</span>
                <span style="color: #4caf50; font-weight: 600; font-size: 14px;">$${parseFloat(potentialProfit).toLocaleString()}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #8b93a7; font-size: 14px;">Current Subscribers:</span>
                <span style="color: #000; font-weight: 600; font-size: 14px;">${plan.current_subscribers.toLocaleString()}</span>
            </div>
        </div>

        ${!hasSufficientFunds ? `
            <div style="background: rgba(255, 107, 107, 0.1); border: 1px solid rgba(255, 107, 107, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 15px;">
                <p style="color: #ff6b6b; font-size: 13px; margin: 0;">
                    <i class="fa fa-exclamation-triangle"></i> Insufficient funds. You need $${(plan.minimum_investment - userWalletBalance).toLocaleString()} more.
                </p>
            </div>
        ` : ''}

        <button
            class="btn-primary-custom"
            style="width: 100%; margin-top: 10px;"
            onclick="investInPlan('${plan.id}', '${plan.name}', ${plan.minimum_investment})"
            ${buttonDisabled ? 'disabled' : ''}
        >
            ${hasSufficientFunds ? 'Invest Now' : 'Insufficient Funds'}
        </button>
    `;

    return card;
}

/**
 * Handle invest in plan action
 */
function investInPlan(planId, planName, minimumInvestment) {
    // For now, just show an alert. In production, this would process the investment
    alert(`You are about to invest in ${planName} with a minimum investment of $${minimumInvestment.toLocaleString()}. This feature will be available soon!`);
    console.log('Invest in plan:', planId);
}

/**
 * Load wallet data (balance and transactions)
 */
let walletDataLoaded = false; // Flag to prevent multiple loads

async function loadWalletData() {
    // Only load once
    if (walletDataLoaded) return;

    try {
        // Fetch wallet balance
        const balanceResponse = await TED_AUTH.apiCall('/api/wallet/balance');
        if (balanceResponse.ok) {
            const balanceData = await balanceResponse.json();
            const balance = balanceData.balance || 0;

            // Update balance displays
            document.getElementById('wallet-balance-display').textContent =
                `$${balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('withdraw-available-balance').textContent =
                `$${balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        // Load transactions
        await loadTransactions();

        walletDataLoaded = true;
    } catch (error) {
        console.error('Error loading wallet data:', error);
    }
}

/**
 * Load and display transaction history
 */
async function loadTransactions() {
    const container = document.getElementById('transactions-container');
    container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading transactions...</p>';

    try {
        const response = await TED_AUTH.apiCall('/api/wallet/transactions');

        if (!response.ok) {
            throw new Error('Failed to fetch transactions');
        }

        const transactions = await response.json();

        if (transactions.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No transactions yet. Make your first deposit to get started!</p>';
            return;
        }

        // Create transaction table
        let tableHTML = `
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 2px solid rgba(123, 182, 218, 0.2);">
                            <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">Date</th>
                            <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">Type</th>
                            <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">Method</th>
                            <th style="text-align: right; padding: 12px; color: #8b93a7; font-weight: 600;">Amount</th>
                            <th style="text-align: center; padding: 12px; color: #8b93a7; font-weight: 600;">Status</th>
                            <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">Reference</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        transactions.forEach(txn => {
            const date = new Date(txn.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            const typeColor = txn.transaction_type === 'deposit' ? '#4caf50' : '#ff9800';
            const typeIcon = txn.transaction_type === 'deposit' ? 'fa-arrow-down' : 'fa-arrow-up';
            const amountSign = txn.transaction_type === 'deposit' ? '+' : '-';

            const statusClass = txn.status === 'completed' ? 'badge-active' :
                               txn.status === 'pending' ? 'badge-pending' : 'badge-inactive';

            tableHTML += `
                <tr style="border-bottom: 1px solid rgba(123, 182, 218, 0.1);">
                    <td style="padding: 15px; color: #000;">${date}</td>
                    <td style="padding: 15px;">
                        <span style="color: ${typeColor};">
                            <i class="fa ${typeIcon}"></i> ${txn.transaction_type.charAt(0).toUpperCase() + txn.transaction_type.slice(1)}
                        </span>
                    </td>
                    <td style="padding: 15px; color: #8b93a7;">${txn.payment_method}</td>
                    <td style="padding: 15px; text-align: right; font-weight: 600; color: ${typeColor};">
                        ${amountSign}$${txn.amount.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                    </td>
                    <td style="padding: 15px; text-align: center;">
                        <span class="badge-status ${statusClass}">${txn.status.charAt(0).toUpperCase() + txn.status.slice(1)}</span>
                    </td>
                    <td style="padding: 15px; color: #8b93a7; font-family: monospace; font-size: 12px;">${txn.reference_number}</td>
                </tr>
            `;
        });

        tableHTML += `
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHTML;
    } catch (error) {
        console.error('Error loading transactions:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load transactions. Please try again later.</p>';
    }
}

/**
 * Show deposit modal
 */
function showDepositModal() {
    const modal = document.getElementById('deposit-modal');
    modal.style.display = 'flex';
    document.getElementById('deposit-form').reset();
}

/**
 * Close deposit modal
 */
function closeDepositModal() {
    const modal = document.getElementById('deposit-modal');
    modal.style.display = 'none';
}

/**
 * Show withdraw modal
 */
async function showWithdrawModal() {
    const modal = document.getElementById('withdraw-modal');
    modal.style.display = 'flex';
    document.getElementById('withdraw-form').reset();

    // Update available balance in modal
    try {
        const response = await TED_AUTH.apiCall('/api/wallet/balance');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('withdraw-available-balance').textContent =
                `$${data.balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }
    } catch (error) {
        console.error('Error fetching balance:', error);
    }
}

/**
 * Close withdraw modal
 */
function closeWithdrawModal() {
    const modal = document.getElementById('withdraw-modal');
    modal.style.display = 'none';
}

/**
 * Handle deposit form submission
 */
async function handleDeposit(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById('deposit-amount').value);
    const paymentMethod = document.getElementById('deposit-payment-method').value;

    if (!amount || !paymentMethod) {
        alert('Please fill in all fields');
        return;
    }

    if (amount < 10) {
        alert('Minimum deposit amount is $10');
        return;
    }

    if (amount > 1000000) {
        alert('Maximum deposit amount is $1,000,000');
        return;
    }

    try {
        TED_AUTH.showLoading('Processing deposit...');

        const response = await TED_AUTH.apiCall('/api/wallet/deposit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount,
                payment_method: paymentMethod
            })
        });

        TED_AUTH.closeLoading();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Deposit failed');
        }

        const result = await response.json();

        // Update balance displays
        document.getElementById('wallet-balance-display').textContent =
            `$${result.new_balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

        // Update user data in localStorage
        const userData = TED_AUTH.getUser();
        if (userData) {
            userData.wallet_balance = result.new_balance;
            TED_AUTH.saveUser(userData);
        }

        // Reload transactions
        await loadTransactions();

        // Close modal
        closeDepositModal();

        alert(`Deposit successful! $${amount.toLocaleString()} has been added to your wallet.\nReference: ${result.transaction.reference_number}`);
    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Deposit error:', error);
        alert(`Deposit failed: ${error.message}`);
    }
}

/**
 * Handle withdraw form submission
 */
async function handleWithdraw(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById('withdraw-amount').value);
    const paymentMethod = document.getElementById('withdraw-payment-method').value;

    if (!amount || !paymentMethod) {
        alert('Please fill in all fields');
        return;
    }

    if (amount < 10) {
        alert('Minimum withdrawal amount is $10');
        return;
    }

    try {
        TED_AUTH.showLoading('Processing withdrawal...');

        const response = await TED_AUTH.apiCall('/api/wallet/withdraw', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount,
                payment_method: paymentMethod
            })
        });

        TED_AUTH.closeLoading();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Withdrawal failed');
        }

        const result = await response.json();

        // Update balance displays
        document.getElementById('wallet-balance-display').textContent =
            `$${result.new_balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById('withdraw-available-balance').textContent =
            `$${result.new_balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

        // Update user data in localStorage
        const userData = TED_AUTH.getUser();
        if (userData) {
            userData.wallet_balance = result.new_balance;
            TED_AUTH.saveUser(userData);
        }

        // Reload transactions
        await loadTransactions();

        // Close modal
        closeWithdrawModal();

        alert(`Withdrawal successful! $${amount.toLocaleString()} will be sent to your ${paymentMethod}.\nReference: ${result.transaction.reference_number}`);
    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Withdrawal error:', error);
        alert(`Withdrawal failed: ${error.message}`);
    }
}

// Export functions for use in HTML
window.handleLogout = handleLogout;
window.copyTrader = copyTrader;
window.investInPlan = investInPlan;
window.showDepositModal = showDepositModal;
window.closeDepositModal = closeDepositModal;
window.showWithdrawModal = showWithdrawModal;
window.closeWithdrawModal = closeWithdrawModal;
window.handleDeposit = handleDeposit;
window.handleWithdraw = handleWithdraw;
