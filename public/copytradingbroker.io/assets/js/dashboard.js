/**
 * Dashboard Page Handler
 * Manages user dashboard data display and authentication
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Check for OAuth token in URL (from redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
        // Save token from OAuth redirect
        TED_AUTH.saveToken(token);
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }

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

    // Load active investments on dashboard
    loadDashboardActiveInvestments();

    // Check if user is new and hasn't been referred yet
    checkAndShowReferralModal(userData);

    // Load expert traders when traders tab is clicked
    const tradersTab = document.querySelector('.menu-item[data-tab="traders"]');
    if (tradersTab) {
        tradersTab.addEventListener('click', loadExpertTraders);
    }

    // Load investment plans when subscription tab is clicked
    const subscriptionTab = document.querySelector('.menu-item[data-tab="subscription"]');
    if (subscriptionTab) {
        subscriptionTab.addEventListener('click', function() {
            // Force reload each time to ensure fresh data
            loadInvestmentPlans(true);
        });
    }

    // Load wallet data when wallet tab is clicked
    const walletTab = document.querySelector('.menu-item[data-tab="wallet"]');
    if (walletTab) {
        walletTab.addEventListener('click', loadWalletData);
    }

    // Load referral data when referrals tab is clicked
    const referralsTab = document.querySelector('.menu-item[data-tab="referrals"]');
    if (referralsTab) {
        referralsTab.addEventListener('click', loadReferralData);
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
let tradersCache = null; // Cache traders data

async function loadExpertTraders(forceReload = false) {
    // Skip if already loaded and not forcing reload
    if (tradersLoaded && !forceReload && tradersCache) {
        // Display cached traders
        displayTraders(tradersCache);
        return;
    }

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

        // Cache the traders
        tradersCache = traders;
        tradersLoaded = true;

        // Display traders
        displayTraders(traders);
    } catch (error) {
        console.error('Error loading traders:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load traders. Please try again later.</p>';
    }
}

/**
 * Display traders in the container
 */
function displayTraders(traders) {
    const container = document.getElementById('traders-container');

    if (traders.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No expert traders available at the moment.</p>';
        return;
    }

    container.innerHTML = '';
    traders.forEach(trader => {
        const traderCard = createTraderCard(trader);
        container.appendChild(traderCard);
    });
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

    // Check if trader is selected
    const userData = TED_AUTH.getUser();
    const selectedTraders = userData?.selected_traders || [];
    const isSelected = selectedTraders.includes(trader.id);

    const buttonText = isSelected ? 'Stop Copying' : 'Copy Trader';
    const buttonStyle = isSelected ? 'background: #ff6b6b;' : '';

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
                <h3 style="margin: 0;">${trader.full_name}${isSelected ? ' <span style="color: #4caf50; font-size: 14px;"><i class="fa fa-check-circle"></i> Selected</span>' : ''}</h3>
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
                    <div style="font-size: 24px; color: #D32F2F; font-weight: bold;">${trader.win_rate}%</div>
                    <div style="color: #8b93a7; font-size: 12px;">Win Rate</div>
                </div>
                <div>
                    <div style="font-size: 24px; color: #ff9800; font-weight: bold;">${trader.copiers}</div>
                    <div style="color: #8b93a7; font-size: 12px;">Copiers</div>
                </div>
            </div>
            <button class="btn-primary-custom" style="${buttonStyle}" onclick="copyTrader('${trader.id}', '${trader.full_name}')">${buttonText}</button>
        </div>

        ${tradesHTML}
    `;

    return card;
}

/**
 * Handle copy trader action - select/unselect trader for copying
 */
async function copyTrader(traderId, traderName) {
    try {
        // Get current user data to check if trader is already selected
        const userData = TED_AUTH.getUser();
        const selectedTraders = userData?.selected_traders || [];
        const isSelected = selectedTraders.includes(traderId);

        if (isSelected) {
            // Unselect trader
            if (!confirm(`Stop copying ${traderName}?`)) {
                return;
            }

            TED_AUTH.showLoading('Unselecting trader...');

            const response = await TED_AUTH.apiCall(`/api/traders/unselect/${traderId}`, {
                method: 'DELETE'
            });

            TED_AUTH.closeLoading();

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to unselect trader');
            }

            const result = await response.json();

            // Update user data
            const freshUserData = await TED_AUTH.fetchCurrentUser();
            if (freshUserData.success) {
                TED_AUTH.saveUser(freshUserData.data);
            }

            // Reload traders to update button state
            await loadExpertTraders(true);

            alert(`Successfully stopped copying ${traderName}.\nYou now have ${result.selected_traders_count} trader(s) selected.`);

        } else {
            // Select trader
            if (!confirm(`Start copying ${traderName}?`)) {
                return;
            }

            TED_AUTH.showLoading('Selecting trader...');

            const response = await TED_AUTH.apiCall(`/api/traders/select/${traderId}`, {
                method: 'POST'
            });

            TED_AUTH.closeLoading();

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to select trader');
            }

            const result = await response.json();

            // Update user data
            const freshUserData = await TED_AUTH.fetchCurrentUser();
            if (freshUserData.success) {
                TED_AUTH.saveUser(freshUserData.data);
            }

            // Reload traders to update button state
            await loadExpertTraders(true);

            alert(`Successfully started copying ${traderName}!\nYou now have ${result.selected_traders_count} trader(s) selected.`);
        }

    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Error copying/uncopying trader:', error);
        alert(`Error: ${error.message}`);
    }
}

/**
 * Load and display investment plans from API
 */
let plansLoaded = false; // Flag to prevent multiple loads
let plansCache = null; // Cache plans data
let userWalletBalance = 0; // Store user's wallet balance

async function loadInvestmentPlans(forceReload = false) {
    // Skip if already loaded and not forcing reload
    if (plansLoaded && !forceReload && plansCache) {
        // Display cached plans
        displayPlans(plansCache);
        return;
    }

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
        const walletBalanceElement = document.getElementById('wallet-balance');
        if (walletBalanceElement) {
            walletBalanceElement.textContent = `$${userWalletBalance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        }

        // Fetch investment plans from API
        const response = await TED_AUTH.apiCall('/api/plans/', {
            method: 'GET'
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to fetch investment plans: ${response.statusText}`);
        }

        const plans = await response.json();

        // Cache the plans
        plansCache = plans;
        plansLoaded = true;

        // Display plans
        displayPlans(plans);
    } catch (error) {
        console.error('Error loading investment plans:', error);
        plansLoaded = false; // Reset flag so user can retry
        container.innerHTML = `
            <div style="text-align: center; padding: 40px 0;">
                <p style="color: #ff6b6b; margin-bottom: 15px;">
                    <i class="fa fa-exclamation-circle" style="font-size: 24px; margin-bottom: 10px;"></i><br>
                    Failed to load investment plans
                </p>
                <p style="color: #8b93a7; font-size: 14px; margin-bottom: 20px;">${error.message}</p>
                <button class="btn-primary-custom" onclick="loadInvestmentPlans(true)">
                    <i class="fa fa-refresh"></i> Retry
                </button>
            </div>
        `;
    }
}

/**
 * Display plans in the container
 */
function displayPlans(plans) {
    const container = document.getElementById('plans-container');

    if (plans.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No investment plans available at the moment.</p>';
        return;
    }

    container.innerHTML = '';
    plans.forEach(plan => {
        const planCard = createPlanCard(plan);
        container.appendChild(planCard);
    });
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
        <h3 style="color: #D32F2F; margin-bottom: 10px;">${plan.name}</h3>

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
                <div style="font-size: 24px; font-weight: bold; color: #D32F2F;">${plan.holding_period_months} mo</div>
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
async function investInPlan(planId, planName, minimumInvestment) {
    // Confirm investment
    if (!confirm(`Invest in ${planName}?\n\nMinimum Investment: $${minimumInvestment.toLocaleString()}\n\nThis amount will be deducted from your wallet.`)) {
        return;
    }

    try {
        TED_AUTH.showLoading('Processing your investment...');

        const response = await TED_AUTH.apiCall('/api/investments/invest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plan_id: planId,
                amount: minimumInvestment
            })
        });

        TED_AUTH.closeLoading();

        if (!response.ok) {
            const error = await response.json();
            TED_AUTH.closeLoading();

            // Check if error is about trader selection
            if (error.detail && error.detail.includes('select at least 1 trader')) {
                alert(`Unable to invest: ${error.detail}\n\nPlease go to the Traders tab and select at least one trader to copy before activating a copy trading plan.`);

                // Navigate to traders tab
                document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
                const tradersTab = document.querySelector('.menu-item[data-tab="traders"]');
                if (tradersTab) {
                    tradersTab.classList.add('active');
                    tradersTab.click();
                }
                return;
            }

            throw new Error(error.detail || 'Investment failed');
        }

        const result = await response.json();

        // Update wallet balance
        userWalletBalance = result.new_wallet_balance;
        document.getElementById('wallet-balance').textContent = `$${userWalletBalance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

        // Update user data in localStorage
        const userData = TED_AUTH.getUser();
        if (userData) {
            userData.wallet_balance = result.new_wallet_balance;
            TED_AUTH.saveUser(userData);
        }

        // Reload investment plans to update balances
        await loadInvestmentPlans(true);

        // Show success message and navigate to portfolio
        alert(`Investment successful!\n\nInvested: $${result.amount_invested.toLocaleString()}\nPlan: ${result.plan_name}\nMaturity Date: ${new Date(result.maturity_date).toLocaleDateString()}\n\nView your investment in the Portfolio tab.`);

        // Navigate to portfolio tab
        document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
        const portfolioTab = document.querySelector('.menu-item[data-tab="portfolio"]');
        if (portfolioTab) {
            portfolioTab.classList.add('active');
            portfolioTab.click();
        }

    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Investment error:', error);
        alert(`Investment failed: ${error.message}`);
    }
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
    // Hide all payment method fields initially
    hideAllDepositPaymentFields();
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
    const password = document.getElementById('deposit-password').value;

    if (!amount || !paymentMethod) {
        alert('Please fill in all required fields');
        return;
    }

    if (!password) {
        alert('Please enter your password to confirm this deposit');
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

    // Collect payment method specific details
    const paymentDetails = {
        amount: amount,
        payment_method: paymentMethod,
        password: password
    };

    // Add method-specific fields
    switch(paymentMethod) {
        case 'Bank Transfer':
            const bankName = document.getElementById('bank-name').value;
            const bankReference = document.getElementById('bank-reference').value;
            if (!bankName || !bankReference) {
                alert('Please fill in all bank transfer details');
                return;
            }
            paymentDetails.bank_name = bankName;
            paymentDetails.reference_number = bankReference;
            break;

        case 'Cryptocurrency':
            const cryptoType = document.getElementById('crypto-type').value;
            const cryptoTxHash = document.getElementById('crypto-tx-hash').value;
            if (!cryptoType || !cryptoTxHash) {
                alert('Please select cryptocurrency and enter transaction hash');
                return;
            }
            paymentDetails.crypto_type = cryptoType;
            paymentDetails.transaction_hash = cryptoTxHash;
            break;

        case 'Credit Card':
            const cardNumber = document.getElementById('card-number').value;
            const cardExpiry = document.getElementById('card-expiry').value;
            const cardCvv = document.getElementById('card-cvv').value;
            const cardHolderName = document.getElementById('card-holder-name').value;
            if (!cardNumber || !cardExpiry || !cardCvv || !cardHolderName) {
                alert('Please fill in all credit card details');
                return;
            }
            paymentDetails.card_number = cardNumber;
            paymentDetails.card_expiry = cardExpiry;
            paymentDetails.card_cvv = cardCvv;
            paymentDetails.card_holder_name = cardHolderName;
            break;

        case 'PayPal':
            const paypalEmail = document.getElementById('paypal-email').value;
            if (!paypalEmail) {
                alert('Please enter your PayPal email');
                return;
            }
            paymentDetails.paypal_email = paypalEmail;
            break;
    }

    try {
        TED_AUTH.showLoading('Processing deposit...');

        const response = await TED_AUTH.apiCall('/api/wallet/deposit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(paymentDetails)
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

        alert(`Deposit request submitted successfully!\nAmount: $${amount.toLocaleString()}\nPayment Method: ${paymentMethod}\nReference: ${result.transaction.reference_number}\n\nYour deposit will be processed shortly.`);
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

/**
 * Check if user should see referral modal (new users)
 */
async function checkAndShowReferralModal(userData) {
    // Check if the user has already been referred or seen the modal
    const hasSeenReferralModal = localStorage.getItem('hasSeenReferralModal');

    // Only show if user hasn't seen the modal before
    if (!hasSeenReferralModal) {
        // Mark as seen immediately to prevent showing again
        localStorage.setItem('hasSeenReferralModal', 'true');

        // Small delay to let dashboard load first
        setTimeout(() => {
            showReferralModal();
        }, 1000);
    }
}

/**
 * Show referral modal for new users
 */
function showReferralModal() {
    const modal = document.getElementById('referral-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

/**
 * Close referral modal
 */
function closeReferralModal() {
    const modal = document.getElementById('referral-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Handle referral code submission
 */
async function handleReferralSubmission(event) {
    event.preventDefault();

    const referralCode = document.getElementById('referral-code-input').value.trim();

    if (!referralCode) {
        alert('Please enter a referral code');
        return;
    }

    try {
        TED_AUTH.showLoading('Verifying referral code...');

        const response = await TED_AUTH.apiCall('/api/referrals/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                referral_code: referralCode
            })
        });

        TED_AUTH.closeLoading();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Invalid referral code');
        }

        const result = await response.json();

        // Close modal
        closeReferralModal();

        // Show success message
        alert(`Success! Your referrer has been credited with $${result.bonus_amount}. Thank you for using their referral link!`);

    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Referral submission error:', error);
        alert(`Referral submission failed: ${error.message}`);
    }
}

/**
 * Skip referral (user doesn't have a code)
 */
function skipReferral() {
    if (confirm('Are you sure you want to skip? You won\'t be able to submit a referral code later.')) {
        closeReferralModal();
    }
}

/**
 * Load and display referral data
 */
let referralDataLoaded = false;

async function loadReferralData() {
    // Only load once
    if (referralDataLoaded) return;

    try {
        TED_AUTH.showLoading('Loading your referral data...');

        // Get referral link
        const linkResponse = await TED_AUTH.apiCall('/api/referrals/my-link');
        if (linkResponse.ok) {
            const linkData = await linkResponse.json();
            document.getElementById('referral-link').textContent = linkData.referral_link;
        }

        // Get referral statistics
        const statsResponse = await TED_AUTH.apiCall('/api/referrals/my-statistics');
        if (statsResponse.ok) {
            const stats = await statsResponse.json();

            // Update stat boxes
            document.querySelector('#tab-referrals .stat-box:nth-child(1) .stat-value').textContent = stats.total_referrals;
            document.querySelector('#tab-referrals .stat-box:nth-child(2) .stat-value').textContent =
                `$${stats.total_earnings.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.querySelector('#tab-referrals .stat-box:nth-child(3) .stat-value').textContent = stats.active_referrals;

            // Display referred users
            displayReferredUsers(stats.referred_users);
        }

        TED_AUTH.closeLoading();
        referralDataLoaded = true;
    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Error loading referral data:', error);
        alert('Failed to load referral data. Please try again later.');
    }
}

/**
 * Display referred users list
 */
function displayReferredUsers(referredUsers) {
    const container = document.querySelector('#tab-referrals .dashboard-card:last-child');

    if (!referredUsers || referredUsers.length === 0) {
        container.innerHTML = `
            <h3 style="margin-bottom: 20px;">Your Referrals</h3>
            <p style="text-align: center; color: #8b93a7; padding: 40px 0;">You haven't referred anyone yet. Start sharing your referral link to earn rewards!</p>
        `;
        return;
    }

    let tableHTML = `
        <h3 style="margin-bottom: 20px;">Your Referrals (${referredUsers.length})</h3>
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 2px solid rgba(123, 182, 218, 0.2);">
                        <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">User</th>
                        <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">Email</th>
                        <th style="text-align: left; padding: 12px; color: #8b93a7; font-weight: 600;">Joined Date</th>
                        <th style="text-align: right; padding: 12px; color: #8b93a7; font-weight: 600;">Bonus Earned</th>
                        <th style="text-align: center; padding: 12px; color: #8b93a7; font-weight: 600;">Status</th>
                    </tr>
                </thead>
                <tbody>
    `;

    referredUsers.forEach(user => {
        const joinedDate = user.joined_date ? new Date(user.joined_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }) : 'N/A';

        const statusClass = user.status === 'completed' ? 'badge-active' : 'badge-pending';

        tableHTML += `
            <tr style="border-bottom: 1px solid rgba(123, 182, 218, 0.1);">
                <td style="padding: 15px; color: #000;">
                    <div style="font-weight: 600;">${user.full_name || user.username}</div>
                    <div style="color: #8b93a7; font-size: 12px;">@${user.username}</div>
                </td>
                <td style="padding: 15px; color: #8b93a7;">${user.email}</td>
                <td style="padding: 15px; color: #000;">${joinedDate}</td>
                <td style="padding: 15px; text-align: right; font-weight: 600; color: #4caf50;">
                    +$${user.bonus_earned.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                </td>
                <td style="padding: 15px; text-align: center;">
                    <span class="badge-status ${statusClass}">${user.status.charAt(0).toUpperCase() + user.status.slice(1)}</span>
                </td>
            </tr>
        `;
    });

    tableHTML += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = tableHTML;
}

/**
 * Copy referral link to clipboard
 */
function copyReferralLink() {
    const linkText = document.getElementById('referral-link').textContent;
    navigator.clipboard.writeText(linkText).then(() => {
        alert('Referral link copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy link. Please try selecting and copying manually.');
    });
}

/**
 * Quick Action: Navigate to subscription/trading plans tab
 */
function quickActionStartCopyTrading() {
    // Activate subscription tab
    document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
    const subscriptionTab = document.querySelector('.menu-item[data-tab="subscription"]');
    if (subscriptionTab) {
        subscriptionTab.classList.add('active');
    }

    // Show subscription tab content
    document.querySelectorAll('.tab-content-wrapper').forEach(tc => tc.classList.remove('active'));
    const subscriptionContent = document.getElementById('tab-subscription');
    if (subscriptionContent) {
        subscriptionContent.classList.add('active');
    }

    // Load investment plans
    loadInvestmentPlans();
}

/**
 * Quick Action: Navigate to wallet tab
 */
function quickActionDepositFunds() {
    // Activate wallet tab
    document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
    const walletTab = document.querySelector('.menu-item[data-tab="wallet"]');
    if (walletTab) {
        walletTab.classList.add('active');
    }

    // Show wallet tab content
    document.querySelectorAll('.tab-content-wrapper').forEach(tc => tc.classList.remove('active'));
    const walletContent = document.getElementById('tab-wallet');
    if (walletContent) {
        walletContent.classList.add('active');
    }

    // Load wallet data
    loadWalletData();
}

/**
 * Quick Action: Navigate to traders tab
 */
function quickActionBrowseTraders() {
    // Activate traders tab
    document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
    const tradersTab = document.querySelector('.menu-item[data-tab="traders"]');
    if (tradersTab) {
        tradersTab.classList.add('active');
    }

    // Show traders tab content
    document.querySelectorAll('.tab-content-wrapper').forEach(tc => tc.classList.remove('active'));
    const tradersContent = document.getElementById('tab-traders');
    if (tradersContent) {
        tradersContent.classList.add('active');
    }

    // Load expert traders
    loadExpertTraders();
}

/**
 * Show update profile modal
 */
function showUpdateProfileModal() {
    const modal = document.getElementById('update-profile-modal');
    modal.style.display = 'flex';

    // Pre-fill form with current user data
    const userData = TED_AUTH.getUser();
    if (userData) {
        document.getElementById('update-full-name').value = userData.full_name || '';
        document.getElementById('update-phone').value = userData.phone || '';
        document.getElementById('update-gender').value = userData.gender || '';
        document.getElementById('update-country').value = userData.country || '';
    }
}

/**
 * Close update profile modal
 */
function closeUpdateProfileModal() {
    const modal = document.getElementById('update-profile-modal');
    modal.style.display = 'none';
}

/**
 * Handle update profile form submission
 */
async function handleUpdateProfile(event) {
    event.preventDefault();

    const fullName = document.getElementById('update-full-name').value.trim();
    const phone = document.getElementById('update-phone').value.trim();
    const gender = document.getElementById('update-gender').value;
    const country = document.getElementById('update-country').value.trim();

    try {
        TED_AUTH.showLoading('Updating your profile...');

        const response = await TED_AUTH.apiCall('/api/auth/update-profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                full_name: fullName,
                phone: phone,
                gender: gender,
                country: country
            })
        });

        TED_AUTH.closeLoading();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Profile update failed');
        }

        const result = await response.json();

        // Update user data in localStorage
        TED_AUTH.saveUser(result);

        // Refresh dashboard data
        populateDashboard(result);

        // Close modal
        closeUpdateProfileModal();

        alert('Profile updated successfully!');
    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Profile update error:', error);
        alert(`Profile update failed: ${error.message}`);
    }
}

/**
 * Show change password modal
 */
function showChangePasswordModal() {
    const modal = document.getElementById('change-password-modal');
    modal.style.display = 'flex';
    document.getElementById('change-password-form').reset();
}

/**
 * Close change password modal
 */
function closeChangePasswordModal() {
    const modal = document.getElementById('change-password-modal');
    modal.style.display = 'none';
}

/**
 * Handle change password form submission
 */
async function handleChangePassword(event) {
    event.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmNewPassword = document.getElementById('confirm-new-password').value;

    // Validate passwords match
    if (newPassword !== confirmNewPassword) {
        alert('New passwords do not match!');
        return;
    }

    // Validate password strength
    if (newPassword.length < 8) {
        alert('Password must be at least 8 characters long');
        return;
    }

    if (!/[A-Z]/.test(newPassword)) {
        alert('Password must contain at least one uppercase letter');
        return;
    }

    if (!/[a-z]/.test(newPassword)) {
        alert('Password must contain at least one lowercase letter');
        return;
    }

    if (!/[0-9]/.test(newPassword)) {
        alert('Password must contain at least one number');
        return;
    }

    try {
        TED_AUTH.showLoading('Changing your password...');

        const response = await TED_AUTH.apiCall('/api/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                old_password: currentPassword,
                new_password: newPassword
            })
        });

        TED_AUTH.closeLoading();

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Password change failed');
        }

        // Close modal
        closeChangePasswordModal();

        alert('Password changed successfully! Please login with your new password.');

        // Log out user to force re-login with new password
        setTimeout(() => {
            TED_AUTH.logout();
        }, 1000);
    } catch (error) {
        TED_AUTH.closeLoading();
        console.error('Password change error:', error);
        alert(`Password change failed: ${error.message}`);
    }
}

/**
 * Hide all deposit payment method fields
 */
function hideAllDepositPaymentFields() {
    document.getElementById('bank-transfer-fields').style.display = 'none';
    document.getElementById('crypto-fields').style.display = 'none';
    document.getElementById('credit-card-fields').style.display = 'none';
    document.getElementById('paypal-fields').style.display = 'none';
}

/**
 * Toggle deposit payment method fields based on selection
 */
function toggleDepositPaymentFields() {
    const paymentMethod = document.getElementById('deposit-payment-method').value;

    // Hide all fields first
    hideAllDepositPaymentFields();

    // Show relevant fields based on selected payment method
    switch(paymentMethod) {
        case 'Bank Transfer':
            document.getElementById('bank-transfer-fields').style.display = 'block';
            break;
        case 'Cryptocurrency':
            document.getElementById('crypto-fields').style.display = 'block';
            break;
        case 'Credit Card':
            document.getElementById('credit-card-fields').style.display = 'block';
            break;
        case 'PayPal':
            document.getElementById('paypal-fields').style.display = 'block';
            break;
    }
}

/**
 * Cryptocurrency wallet addresses (managed by admin)
 */
const cryptoWallets = {
    'Bitcoin': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
    'Ethereum': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
    'Tether': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
    'USD Coin': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'
};

/**
 * Handle crypto type selection to show wallet address
 */
document.addEventListener('DOMContentLoaded', function() {
    const cryptoTypeSelect = document.getElementById('crypto-type');
    if (cryptoTypeSelect) {
        cryptoTypeSelect.addEventListener('change', function() {
            const selectedCrypto = this.value;
            const walletInfo = document.getElementById('crypto-wallet-info');
            const walletAddress = document.getElementById('crypto-wallet-address');

            if (selectedCrypto && cryptoWallets[selectedCrypto]) {
                walletAddress.textContent = cryptoWallets[selectedCrypto];
                walletInfo.style.display = 'block';
            } else {
                walletInfo.style.display = 'none';
            }
        });
    }
});

/**
 * Copy crypto wallet address to clipboard
 */
function copyCryptoAddress() {
    const address = document.getElementById('crypto-wallet-address').textContent;
    if (address && address !== '-') {
        navigator.clipboard.writeText(address).then(() => {
            alert('Wallet address copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy address. Please try selecting and copying manually.');
        });
    }
}

/**
 * Load and display portfolio performance
 */
let portfolioLoaded = false;

async function loadPortfolioPerformance(forceReload = false) {
    // Skip if already loaded and not forcing reload
    if (portfolioLoaded && !forceReload) {
        return;
    }

    const container = document.getElementById('investments-container');
    container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading your investments...</p>';

    try {
        const response = await TED_AUTH.apiCall('/api/investments/portfolio', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch portfolio: ${response.statusText}`);
        }

        const portfolio = await response.json();

        // Update summary stats
        document.getElementById('portfolio-total-invested').textContent =
            `$${portfolio.total_invested.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

        document.getElementById('portfolio-current-value').textContent =
            `$${portfolio.current_value.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

        const profitLossElement = document.getElementById('portfolio-profit-loss');
        const profitLossColor = portfolio.total_profit_loss >= 0 ? '#4caf50' : '#f44336';
        const profitLossSign = portfolio.total_profit_loss >= 0 ? '+' : '';
        profitLossElement.textContent = `${profitLossSign}$${portfolio.total_profit_loss.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${profitLossSign}${portfolio.total_profit_loss_percent.toFixed(2)}%)`;
        profitLossElement.style.color = profitLossColor;

        document.getElementById('portfolio-active-investments').textContent = portfolio.active_investments;

        // Display investments
        if (portfolio.investments.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No investments yet. Start investing to see your portfolio here!</p>';
        } else {
            displayInvestments(portfolio.investments);
        }

        portfolioLoaded = true;
    } catch (error) {
        console.error('Error loading portfolio:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load portfolio. Please try again later.</p>';
    }
}

/**
 * Display investments in the container
 */
function displayInvestments(investments) {
    const container = document.getElementById('investments-container');
    container.innerHTML = '';

    investments.forEach(investment => {
        const card = createInvestmentCard(investment);
        container.appendChild(card);
    });
}

/**
 * Create an investment card element
 */
function createInvestmentCard(investment) {
    const card = document.createElement('div');
    card.className = 'plan-card';

    const profitColor = investment.profit_loss >= 0 ? '#4caf50' : '#f44336';
    const profitSign = investment.profit_loss >= 0 ? '+' : '';

    const statusClass = investment.status === 'active' ? 'badge-active' :
                        investment.status === 'matured' ? 'badge-pending' : 'badge-inactive';
    const statusText = investment.status.charAt(0).toUpperCase() + investment.status.slice(1);

    const startDate = new Date(investment.start_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    const maturityDate = new Date(investment.maturity_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    // Calculate progress percentage
    const totalDays = investment.days_elapsed + investment.days_remaining;
    const progressPercent = totalDays > 0 ? (investment.days_elapsed / totalDays * 100) : 0;

    card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style="color: #D32F2F; margin: 0;">${investment.plan_name}</h3>
            <span class="badge-status ${statusClass}">${statusText}</span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div>
                <div style="font-size: 24px; font-weight: bold; color: #000;">$${investment.amount_invested.toLocaleString()}</div>
                <div style="font-size: 12px; color: #8b93a7;">Amount Invested</div>
            </div>
            <div>
                <div style="font-size: 24px; font-weight: bold; color: ${profitColor};">${profitSign}$${Math.abs(investment.profit_loss).toLocaleString()}</div>
                <div style="font-size: 12px; color: #8b93a7;">Profit/Loss (${profitSign}${investment.profit_loss_percent.toFixed(2)}%)</div>
            </div>
        </div>

        <div style="background: rgba(123, 182, 218, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #8b93a7; font-size: 14px;">Current Value:</span>
                <span style="color: #000; font-weight: 600;">$${investment.current_value.toLocaleString()}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #8b93a7; font-size: 14px;">Expected Return:</span>
                <span style="color: #4caf50; font-weight: 600;">${investment.expected_return_percent}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #8b93a7; font-size: 14px;">Holding Period:</span>
                <span style="color: #000; font-weight: 600;">${investment.holding_period_months} months</span>
            </div>
        </div>

        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #8b93a7; font-size: 12px;">Investment Progress</span>
                <span style="color: #000; font-size: 12px; font-weight: 600;">${progressPercent.toFixed(0)}%</span>
            </div>
            <div style="width: 100%; height: 8px; background: rgba(123, 182, 218, 0.2); border-radius: 4px; overflow: hidden;">
                <div style="width: ${progressPercent}%; height: 100%; background: linear-gradient(90deg, #D32F2F, #5a9abf); border-radius: 4px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span style="color: #8b93a7; font-size: 11px;">${investment.days_elapsed} days elapsed</span>
                <span style="color: #8b93a7; font-size: 11px;">${investment.days_remaining} days remaining</span>
            </div>
        </div>

        <div style="background: rgba(123, 182, 218, 0.05); border-radius: 8px; padding: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #8b93a7; font-size: 13px;">Start Date:</span>
                <span style="color: #000; font-weight: 600; font-size: 13px;">${startDate}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #8b93a7; font-size: 13px;">Maturity Date:</span>
                <span style="color: #000; font-weight: 600; font-size: 13px;">${maturityDate}</span>
            </div>
        </div>
    `;

    return card;
}

// Add portfolio tab click listener
document.addEventListener('DOMContentLoaded', function() {
    const portfolioTab = document.querySelector('.menu-item[data-tab="portfolio"]');
    if (portfolioTab) {
        portfolioTab.addEventListener('click', () => loadPortfolioPerformance(true));
    }
});

/**
 * Load and display active investments on the dashboard home tab
 */
async function loadDashboardActiveInvestments() {
    try {
        const response = await TED_AUTH.apiCall('/api/investments/portfolio', {
            method: 'GET'
        });

        if (!response.ok) {
            console.error('Failed to fetch portfolio for dashboard');
            return;
        }

        const portfolio = await response.json();

        // Only show active investments section if user has active investments
        if (portfolio.active_investments > 0 && portfolio.investments.length > 0) {
            const activeInvestmentsCard = document.getElementById('active-investments-card');
            const container = document.getElementById('dashboard-active-investments-container');

            if (activeInvestmentsCard && container) {
                activeInvestmentsCard.style.display = 'block';

                // Filter only active investments
                const activeInvestments = portfolio.investments.filter(inv => inv.status === 'active');

                // Display up to 3 active investments on dashboard
                const displayInvestments = activeInvestments.slice(0, 3);

                container.innerHTML = '';
                displayInvestments.forEach(investment => {
                    const card = createDashboardInvestmentCard(investment);
                    container.appendChild(card);
                });

                // Show message if there are more investments
                if (activeInvestments.length > 3) {
                    const moreMessage = document.createElement('div');
                    moreMessage.style.cssText = 'text-align: center; padding: 15px; color: #8b93a7; font-size: 14px;';
                    moreMessage.innerHTML = `<i class="fa fa-info-circle"></i> And ${activeInvestments.length - 3} more active investment${activeInvestments.length - 3 > 1 ? 's' : ''}. <a href="#" onclick="viewFullPortfolio(); return false;" style="color: #D32F2F; text-decoration: underline;">View all</a>`;
                    container.appendChild(moreMessage);
                }
            }
        }
    } catch (error) {
        console.error('Error loading dashboard active investments:', error);
    }
}

/**
 * Create a compact investment card for dashboard display
 */
function createDashboardInvestmentCard(investment) {
    const card = document.createElement('div');
    card.className = 'plan-card';
    card.style.marginBottom = '15px';

    const profitColor = investment.profit_loss >= 0 ? '#4caf50' : '#f44336';
    const profitSign = investment.profit_loss >= 0 ? '+' : '';

    const maturityDate = new Date(investment.maturity_date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    // Calculate progress percentage
    const totalDays = investment.days_elapsed + investment.days_remaining;
    const progressPercent = totalDays > 0 ? (investment.days_elapsed / totalDays * 100) : 0;

    card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
            <div>
                <h3 style="color: #D32F2F; margin: 0 0 5px 0; font-size: 18px;">${investment.plan_name}</h3>
                <span class="badge-status badge-active" style="font-size: 11px;">Active</span>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 20px; font-weight: bold; color: #000;">$${investment.amount_invested.toLocaleString()}</div>
                <div style="font-size: 11px; color: #8b93a7;">Invested</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px; padding: 12px; background: rgba(123, 182, 218, 0.05); border-radius: 8px;">
            <div>
                <div style="font-size: 16px; font-weight: bold; color: ${profitColor};">${profitSign}$${Math.abs(investment.profit_loss).toLocaleString()}</div>
                <div style="font-size: 11px; color: #8b93a7;">Profit/Loss</div>
            </div>
            <div>
                <div style="font-size: 16px; font-weight: bold; color: #000;">$${investment.current_value.toLocaleString()}</div>
                <div style="font-size: 11px; color: #8b93a7;">Current Value</div>
            </div>
            <div>
                <div style="font-size: 16px; font-weight: bold; color: #4caf50;">${investment.expected_return_percent}%</div>
                <div style="font-size: 11px; color: #8b93a7;">Expected Return</div>
            </div>
        </div>

        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color: #8b93a7; font-size: 11px;">Progress to Maturity</span>
                <span style="color: #000; font-size: 11px; font-weight: 600;">${progressPercent.toFixed(0)}%</span>
            </div>
            <div style="width: 100%; height: 6px; background: rgba(123, 182, 218, 0.2); border-radius: 3px; overflow: hidden;">
                <div style="width: ${progressPercent}%; height: 100%; background: linear-gradient(90deg, #D32F2F, #5a9abf); border-radius: 3px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span style="color: #8b93a7; font-size: 10px;">${investment.days_remaining} days remaining</span>
                <span style="color: #8b93a7; font-size: 10px;">Matures: ${maturityDate}</span>
            </div>
        </div>
    `;

    return card;
}

/**
 * Navigate to full portfolio view
 */
function viewFullPortfolio() {
    // Activate portfolio tab
    document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
    const portfolioTab = document.querySelector('.menu-item[data-tab="portfolio"]');
    if (portfolioTab) {
        portfolioTab.classList.add('active');
    }

    // Show portfolio tab content
    document.querySelectorAll('.tab-content-wrapper').forEach(tc => tc.classList.remove('active'));
    const portfolioContent = document.getElementById('tab-portfolio');
    if (portfolioContent) {
        portfolioContent.classList.add('active');
    }

    // Load portfolio data
    loadPortfolioPerformance(true);
}

// Export functions for use in HTML
window.handleLogout = handleLogout;
window.copyTrader = copyTrader;
window.investInPlan = investInPlan;
window.loadInvestmentPlans = loadInvestmentPlans;
window.viewFullPortfolio = viewFullPortfolio;
window.showDepositModal = showDepositModal;
window.closeDepositModal = closeDepositModal;
window.showWithdrawModal = showWithdrawModal;
window.closeWithdrawModal = closeWithdrawModal;
window.handleDeposit = handleDeposit;
window.handleWithdraw = handleWithdraw;
window.copyReferralLink = copyReferralLink;
window.handleReferralSubmission = handleReferralSubmission;
window.closeReferralModal = closeReferralModal;
window.skipReferral = skipReferral;
window.showUpdateProfileModal = showUpdateProfileModal;
window.closeUpdateProfileModal = closeUpdateProfileModal;
window.handleUpdateProfile = handleUpdateProfile;
window.showChangePasswordModal = showChangePasswordModal;
window.closeChangePasswordModal = closeChangePasswordModal;
window.handleChangePassword = handleChangePassword;
window.quickActionStartCopyTrading = quickActionStartCopyTrading;
window.quickActionDepositFunds = quickActionDepositFunds;
window.quickActionBrowseTraders = quickActionBrowseTraders;
window.toggleDepositPaymentFields = toggleDepositPaymentFields;
window.copyCryptoAddress = copyCryptoAddress;
