const API_BASE = '';
let currentTab = 'dashboard';

// Simple TED_AUTH helper for loading indicators
const TED_AUTH = {
    showLoading(message = 'Please wait...') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: message,
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        }
    },
    closeLoading() {
        if (typeof Swal !== 'undefined') {
            Swal.close();
        }
    }
};

// Check authentication on load
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        window.location.href = '/admin/login';
        return;
    }
    
    try {
        const response = await adminFetch('/api/admin/me');
        if (!response.ok) throw new Error('Unauthorized');
        
        const admin = await response.json();
        document.getElementById('admin-name').textContent = admin.full_name || admin.username;
        
        loadDashboardStats();
        setupTabSwitching();
    } catch (error) {
        localStorage.removeItem('admin_token');
        window.location.href = '/admin/login';
    }
});

// Admin authenticated fetch
async function adminFetch(url, options = {}) {
    const token = localStorage.getItem('admin_token');
    return fetch(API_BASE + url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
}

// Setup tab switching
function setupTabSwitching() {
    console.log('Setting up tab switching...');
    const menuItems = document.querySelectorAll('.menu-item[data-tab]');
    console.log('Found menu items:', menuItems.length);
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab');
            console.log('Switching to tab:', tab);
            switchTab(tab);
        });
    });
}

// Switch tabs
function switchTab(tab) {
    console.log('switchTab called with tab:', tab);

    // Remove active class from all menu items
    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));

    // Add active class to selected menu item
    const selectedMenuItem = document.querySelector(`.menu-item[data-tab="${tab}"]`);
    console.log('Selected menu item:', selectedMenuItem);
    if (selectedMenuItem) {
        selectedMenuItem.classList.add('active');
    }

    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

    // Show selected tab content
    const selectedTab = document.getElementById(`tab-${tab}`);
    console.log('Selected tab content:', selectedTab);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    currentTab = tab;

    // Load data for specific tabs
    if (tab === 'users') loadUsers();
    if (tab === 'traders') loadTraders();
    if (tab === 'plans') loadPlans();
    if (tab === 'deposits') loadDepositRequests();
    if (tab === 'withdrawals') loadWithdrawalRequests();
    if (tab === 'bank-accounts') loadBankAccounts();
    if (tab === 'crypto-wallets') loadCryptoWallets();
    if (tab === 'notifications') loadNotifications();
    if (tab === 'chats') {
        // Initialize chat manager if not already initialized
        if (typeof adminChatManager !== 'undefined') {
            adminChatManager.init();
        }
    }
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await adminFetch('/api/admin/statistics');
        const stats = await response.json();
        
        document.getElementById('stat-total-users').textContent = stats.users.total;
        document.getElementById('stat-active-users').textContent = stats.users.active;
        document.getElementById('stat-total-balance').textContent = `$${stats.wallet.total_balance.toLocaleString()}`;
        document.getElementById('stat-total-traders').textContent = stats.traders.total;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load users with full onboarding data
async function loadUsers(search = '') {
    const container = document.getElementById('users-table-container');
    container.innerHTML = 'Loading...';

    try {
        const url = search ? `/api/admin/users?search=${encodeURIComponent(search)}` : '/api/admin/users';
        const response = await adminFetch(url);
        const data = await response.json();

        if (data.users.length === 0) {
            container.innerHTML = '<p>No users found</p>';
            return;
        }

        let html = '<div style="display: grid; gap: 20px;">';

        // For each user, fetch full details including onboarding data
        for (const user of data.users) {
            // Fetch detailed user data
            let fullUserData = user;
            try {
                const detailResponse = await adminFetch(`/api/admin/users/${user.id}`);
                fullUserData = await detailResponse.json();
            } catch (err) {
                console.error(`Error fetching details for user ${user.id}:`, err);
            }

            const kyc = fullUserData.kyc || {};
            const date = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A';
            const statusBadge = `badge-${user.is_active ? 'active' : 'inactive'}`;
            const verifiedBadge = user.is_verified ? '<span class="badge badge-approved" style="margin-left: 8px; font-size: 11px;">Verified</span>' : '<span class="badge badge-pending" style="margin-left: 8px; font-size: 11px;">Unverified</span>';

            // KYC status badge
            let kycStatusClass = 'badge-pending';
            let kycStatusText = 'Not Submitted';
            if (kyc.kyc_status === 'approved') {
                kycStatusClass = 'badge-approved';
                kycStatusText = 'Approved';
            } else if (kyc.kyc_status === 'rejected') {
                kycStatusClass = 'badge-rejected';
                kycStatusText = 'Rejected';
            } else if (kyc.kyc_status === 'not_submitted') {
                kycStatusText = 'Not Submitted';
            } else if (kyc.kyc_status) {
                kycStatusText = kyc.kyc_status.replace('_', ' ').toUpperCase();
            }

            html += `
                <div style="border: 1px solid #e2e8f0; padding: 24px; border-radius: 12px; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <!-- User Header -->
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 2px solid #f7fafc;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 8px 0; color: #2D3748; display: flex; align-items: center; font-size: 20px;">
                                <i class="fas fa-user-circle" style="color: #D32F2F; margin-right: 12px; font-size: 24px;"></i>
                                ${user.username}
                                <span class="badge ${statusBadge}" style="margin-left: 12px;">${user.is_active ? 'Active' : 'Inactive'}</span>
                                ${verifiedBadge}
                            </h3>
                            <p style="margin: 0; color: #8b93a7; font-size: 14px;">
                                <i class="fas fa-envelope" style="margin-right: 6px;"></i>
                                ${user.email}
                            </p>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn btn-primary" style="padding: 10px 18px;" onclick="viewUser('${user.id}')">
                                <i class="fas fa-eye"></i> Full Details
                            </button>
                            ${user.is_active ?
                                `<button class="btn btn-danger" style="padding: 10px 18px;" onclick="deactivateUser('${user.id}')">
                                    <i class="fas fa-ban"></i> Deactivate
                                </button>` :
                                `<button class="btn btn-success" style="padding: 10px 18px;" onclick="activateUser('${user.id}')">
                                    <i class="fas fa-check"></i> Activate
                                </button>`
                            }
                        </div>
                    </div>

                    <!-- Basic Info Section -->
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #2D3748; font-size: 14px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">
                            <i class="fas fa-info-circle" style="margin-right: 8px; color: #D32F2F;"></i>
                            Account Information
                        </h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; padding: 16px; background: #f7fafc; border-radius: 8px; border-left: 4px solid #D32F2F;">
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Full Name</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">${user.full_name || '-'}</p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Phone</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">${user.phone || '-'}</p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Country</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                    ${user.country ? `<i class="fas fa-globe" style="margin-right: 6px;"></i>${user.country}` : '-'}
                                </p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Gender</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">${user.gender || '-'}</p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Wallet Balance</label>
                                <p style="margin: 0; color: #D32F2F; font-size: 20px; font-weight: 700;">
                                    <i class="fas fa-wallet" style="margin-right: 6px; font-size: 16px;"></i>
                                    $${user.wallet_balance.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                </p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Auth Provider</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">${fullUserData.auth_provider || 'local'}</p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Referral Code</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                    ${user.referral_code ? `<code style="background: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${user.referral_code}</code>` : '-'}
                                </p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Referred By</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">${user.referred_by || '-'}</p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Account Created</label>
                                <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                    <i class="fas fa-calendar" style="margin-right: 6px;"></i>
                                    ${date}
                                </p>
                            </div>
                            <div>
                                <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">User ID</label>
                                <p style="margin: 0; color: #2D3748; font-family: monospace; font-size: 11px;">${user.id}</p>
                            </div>
                        </div>
                    </div>

                    <!-- KYC/Onboarding Section -->
                    <div style="margin-bottom: 0;">
                        <h4 style="margin: 0 0 12px 0; color: #2D3748; font-size: 14px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; display: flex; align-items: center; justify-content: space-between;">
                            <span>
                                <i class="fas fa-id-card" style="margin-right: 8px; color: #D32F2F;"></i>
                                KYC / Onboarding Information
                            </span>
                            <span class="badge ${kycStatusClass}" style="font-size: 11px;">${kycStatusText}</span>
                        </h4>

                        <!-- Personal Information -->
                        <div style="margin-bottom: 16px;">
                            <h5 style="margin: 0 0 8px 0; color: #5a5a5a; font-size: 12px; font-weight: 600; text-transform: uppercase;">Personal Information</h5>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; padding: 14px; background: #fffbf5; border-radius: 8px; border-left: 3px solid #ff9800;">
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">First Name</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.first_name || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Last Name</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.last_name || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Gender</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.gender || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Completed</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.personal_info_completed ? '<i class="fas fa-check-circle" style="color: #4caf50;"></i> Yes' : '<i class="fas fa-times-circle" style="color: #f44336;"></i> No'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- Address Information -->
                        <div style="margin-bottom: 16px;">
                            <h5 style="margin: 0 0 8px 0; color: #5a5a5a; font-size: 12px; font-weight: 600; text-transform: uppercase;">Address Information</h5>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; padding: 14px; background: #f0f9ff; border-radius: 8px; border-left: 3px solid #2196F3;">
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Street Address</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.street || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">City</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.city || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">State/Province</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.state || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">ZIP/Postal Code</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">${kyc.zip_code || '-'}</p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Country</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.country ? `<i class="fas fa-globe" style="margin-right: 6px;"></i>${kyc.country}` : '-'}
                                    </p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Completed</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.address_completed ? '<i class="fas fa-check-circle" style="color: #4caf50;"></i> Yes' : '<i class="fas fa-times-circle" style="color: #f44336;"></i> No'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- Verification Documents -->
                        <div>
                            <h5 style="margin: 0 0 8px 0; color: #5a5a5a; font-size: 12px; font-weight: 600; text-transform: uppercase;">Verification Documents</h5>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; padding: 14px; background: #f3f4f6; border-radius: 8px; border-left: 3px solid #6366f1;">
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Document Number</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.document_number ? `<code style="background: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${kyc.document_number}</code>` : '-'}
                                    </p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Document Photo</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.document_photo ? '<i class="fas fa-check-circle" style="color: #4caf50;"></i> Uploaded' : '<i class="fas fa-times-circle" style="color: #f44336;"></i> Not Uploaded'}
                                    </p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">KYC Submitted</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.kyc_submitted_at ? new Date(kyc.kyc_submitted_at).toLocaleDateString() : '-'}
                                    </p>
                                </div>
                                <div>
                                    <label style="display: block; color: #8b93a7; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; font-weight: 600;">Completed</label>
                                    <p style="margin: 0; color: #2D3748; font-weight: 600;">
                                        ${kyc.kyc_completed ? '<i class="fas fa-check-circle" style="color: #4caf50;"></i> Yes' : '<i class="fas fa-times-circle" style="color: #f44336;"></i> No'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading users:', error);
        container.innerHTML = '<p style="color: red;">Error loading users. Please try again.</p>';
    }
}

// Search users
function searchUsers() {
    const search = document.getElementById('user-search').value;
    loadUsers(search);
}

// View user details
async function viewUser(userId) {
    const modal = document.getElementById('user-details-modal');
    const loading = document.getElementById('user-details-loading');
    const content = document.getElementById('user-details-content');

    // Show modal and loading state
    modal.classList.add('show');
    loading.style.display = 'block';
    content.style.display = 'none';

    try {
        const response = await adminFetch(`/api/admin/users/${userId}`);
        const user = await response.json();

        // Populate overview tab
        document.getElementById('detail-username').textContent = user.username || '-';
        document.getElementById('detail-email').textContent = user.email || '-';
        document.getElementById('detail-fullname').textContent = user.full_name || '-';
        document.getElementById('detail-phone').textContent = user.phone || '-';
        document.getElementById('detail-gender').textContent = user.gender || '-';
        document.getElementById('detail-country').textContent = user.country || '-';
        document.getElementById('detail-wallet').textContent = `$${user.wallet_balance.toLocaleString()}`;

        // Status badge
        const statusBadge = user.is_active ?
            '<span class="badge badge-active">Active</span>' :
            '<span class="badge badge-inactive">Inactive</span>';
        document.getElementById('detail-status').innerHTML = statusBadge;

        document.getElementById('detail-2fa').textContent = user.two_fa_enabled ? 'Yes' : 'No';
        document.getElementById('detail-auth-provider').textContent = user.auth_provider || 'local';
        document.getElementById('detail-referral-code').textContent = user.referral_code || '-';
        document.getElementById('detail-referred-by').textContent = user.referred_by || '-';
        document.getElementById('detail-created').textContent = user.created_at ? new Date(user.created_at).toLocaleString() : '-';
        document.getElementById('detail-updated').textContent = user.updated_at ? new Date(user.updated_at).toLocaleString() : '-';

        // Populate KYC tab
        const kyc = user.kyc || {};

        // KYC status badge
        let kycStatusClass = 'badge-pending';
        if (kyc.kyc_status === 'approved') kycStatusClass = 'badge-approved';
        else if (kyc.kyc_status === 'rejected') kycStatusClass = 'badge-rejected';

        document.getElementById('kyc-status-badge').className = `badge ${kycStatusClass}`;
        document.getElementById('kyc-status-badge').textContent = kyc.kyc_status ? kyc.kyc_status.replace('_', ' ').toUpperCase() : 'NOT SUBMITTED';
        document.getElementById('kyc-submitted-at').textContent = kyc.kyc_submitted_at ? new Date(kyc.kyc_submitted_at).toLocaleString() : '-';

        document.getElementById('kyc-first-name').textContent = kyc.first_name || '-';
        document.getElementById('kyc-last-name').textContent = kyc.last_name || '-';
        document.getElementById('kyc-gender').textContent = kyc.gender || '-';
        document.getElementById('kyc-document-number').textContent = kyc.document_number || '-';
        document.getElementById('kyc-street').textContent = kyc.street || '-';
        document.getElementById('kyc-city').textContent = kyc.city || '-';
        document.getElementById('kyc-state').textContent = kyc.state || '-';
        document.getElementById('kyc-zip').textContent = kyc.zip_code || '-';
        document.getElementById('kyc-country').textContent = kyc.country || '-';

        // KYC document photo
        const docContainer = document.getElementById('kyc-document-container');
        if (kyc.document_photo) {
            docContainer.innerHTML = `<img src="${kyc.document_photo}" alt="KYC Document" style="max-width: 100%; max-height: 500px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">`;
        } else {
            docContainer.innerHTML = '<p style="color: #8b93a7;">No document uploaded</p>';
        }

        // Populate login statistics
        const stats = user.login_statistics || {};
        document.getElementById('login-stat-total').textContent = stats.successful_logins || 0;
        document.getElementById('login-stat-ips').textContent = stats.unique_ips || 0;
        document.getElementById('login-stat-devices').textContent = stats.unique_devices || 0;

        // Populate login history
        const loginHistory = user.login_history || [];
        const historyContainer = document.getElementById('login-history-container');

        if (loginHistory.length === 0) {
            historyContainer.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px;">No login history available</p>';
        } else {
            let historyHtml = '';
            loginHistory.forEach(login => {
                const successClass = login.success ? '' : ' failed';
                const statusIcon = login.success ? '<i class="fas fa-check-circle" style="color: #4caf50;"></i>' : '<i class="fas fa-times-circle" style="color: #f44336;"></i>';
                const timestamp = new Date(login.timestamp).toLocaleString();

                historyHtml += `
                    <div class="login-history-item${successClass}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                ${statusIcon}
                                <strong>${login.success ? 'Successful Login' : 'Failed Login'}</strong>
                            </div>
                            <span style="color: #8b93a7; font-size: 13px;">${timestamp}</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                            <div>
                                <strong>IP Address:</strong> ${login.ip_address || 'Unknown'}
                            </div>
                            <div>
                                <strong>Location:</strong> ${login.location ? `${login.location.city}, ${login.location.country}` : 'Unknown'}
                            </div>
                            <div>
                                <strong>Device:</strong> ${login.device_info ? login.device_info.device : 'Unknown'}
                            </div>
                            <div>
                                <strong>Browser:</strong> ${login.device_info ? login.device_info.browser : 'Unknown'}
                            </div>
                            ${!login.success && login.failure_reason ? `<div style="grid-column: span 2; color: #f44336;"><strong>Reason:</strong> ${login.failure_reason}</div>` : ''}
                        </div>
                    </div>
                `;
            });
            historyContainer.innerHTML = historyHtml;
        }

        // Hide loading and show content
        loading.style.display = 'none';
        content.style.display = 'block';

        // Switch to overview tab by default
        switchUserTab('overview');

    } catch (error) {
        console.error('Error loading user details:', error);
        Swal.fire({ title: 'Error!', text: 'Error loading user details', icon: 'error' });
        modal.classList.remove('show');
    }
}

// Close user details modal
function closeUserDetailsModal() {
    const modal = document.getElementById('user-details-modal');
    modal.classList.remove('show');
}

// Switch user detail tabs
function switchUserTab(tabName) {
    // Remove active class from all buttons
    document.querySelectorAll('.user-tab-btn').forEach(btn => btn.classList.remove('active'));

    // Add active class to selected button
    const selectedBtn = document.querySelector(`.user-tab-btn[data-tab="${tabName}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }

    // Hide all tab contents
    document.querySelectorAll('.user-tab-content').forEach(content => content.classList.remove('active'));

    // Show selected tab content
    const selectedTab = document.getElementById(`user-tab-${tabName}`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

// Activate user
async function activateUser(userId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Activate this user?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        TED_AUTH.showLoading('Activating user...');
        await adminFetch(`/api/admin/users/${userId}/activate`, { method: 'PUT' });
        TED_AUTH.closeLoading();
        Swal.fire({ title: 'Success!', text: 'User activated', icon: 'success' });
        loadUsers();
    } catch (error) {
        TED_AUTH.closeLoading();
        Swal.fire({ title: 'Error!', text: 'Error activating user', icon: 'error' });
    }
}

// Deactivate user
async function deactivateUser(userId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Deactivate this user?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        TED_AUTH.showLoading('Deactivating user...');
        await adminFetch(`/api/admin/users/${userId}/deactivate`, { method: 'PUT' });
        TED_AUTH.closeLoading();
        Swal.fire({ title: 'Success!', text: 'User deactivated', icon: 'success' });
        loadUsers();
    } catch (error) {
        TED_AUTH.closeLoading();
        Swal.fire({ title: 'Error!', text: 'Error deactivating user', icon: 'error' });
    }
}

// Load traders
async function loadTraders() {
    const container = document.getElementById('traders-container');
    container.innerHTML = 'Loading...';

    try {
        const response = await adminFetch('/api/admin/traders');
        const traders = await response.json();

        if (traders.length === 0) {
            container.innerHTML = '<p>No traders found. <button class="btn btn-primary" onclick="showAddTraderModal()">Add First Trader</button></p>';
            return;
        }

        let html = '<div style="display: grid; gap: 20px;">';
        traders.forEach(trader => {
            html += `
                <div style="border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px;">
                    <h4>${trader.full_name}</h4>
                    <p>${trader.description}</p>
                    <p><strong>Specialization:</strong> ${trader.specialization}</p>
                    <p><strong>YTD Return:</strong> ${trader.ytd_return}% | <strong>Win Rate:</strong> ${trader.win_rate}%</p>
                    <p><strong>Copiers:</strong> ${trader.copiers || 0}</p>
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <button class="btn btn-primary" style="padding: 8px 16px;" onclick="showEditTraderModal('${trader.id}')">Edit</button>
                        <button class="btn btn-danger" style="padding: 8px 16px;" onclick="deleteTrader('${trader.id}')">Delete</button>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading traders</p>';
    }
}

// Show add trader modal
function showAddTraderModal() {
    const modal = document.getElementById('addTraderModal');
    modal.classList.add('show');

    // Setup form submission if not already done
    const form = document.getElementById('add-trader-form');
    if (!form.dataset.listenerAdded) {
        form.addEventListener('submit', handleAddTraderSubmit);
        form.dataset.listenerAdded = 'true';
    }
}

// Close add trader modal
function closeAddTraderModal() {
    const modal = document.getElementById('addTraderModal');
    modal.classList.remove('show');
    document.getElementById('add-trader-form').reset();
}

// Handle add trader form submission
async function handleAddTraderSubmit(e) {
    e.preventDefault();

    const formData = {
        full_name: document.getElementById('trader-full-name').value,
        profile_photo: document.getElementById('trader-profile-photo').value,
        description: document.getElementById('trader-description').value,
        specialization: document.getElementById('trader-specialization').value,
        ytd_return: parseFloat(document.getElementById('trader-ytd-return').value),
        win_rate: parseFloat(document.getElementById('trader-win-rate').value),
        copiers: parseInt(document.getElementById('trader-copiers').value) || 0
    };

    try {
        const response = await adminFetch('/api/admin/traders', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Trader added successfully!', icon: 'success' });
            closeAddTraderModal();
            loadTraders(); // Reload traders list
        } else {
            const error = await response.json();
            alert('Error adding trader: ' + (error.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding trader:', error);
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
    }
}

// Show edit trader modal
async function showEditTraderModal(traderId) {
    try {
        // Fetch trader details
        const response = await adminFetch(`/api/admin/traders/${traderId}`);
        const trader = await response.json();

        // Populate form fields
        document.getElementById('edit-trader-id').value = trader.id;
        document.getElementById('edit-trader-full-name').value = trader.full_name;
        document.getElementById('edit-trader-profile-photo').value = trader.profile_photo;
        document.getElementById('edit-trader-description').value = trader.description;
        document.getElementById('edit-trader-specialization').value = trader.specialization;
        document.getElementById('edit-trader-ytd-return').value = trader.ytd_return;
        document.getElementById('edit-trader-win-rate').value = trader.win_rate;
        document.getElementById('edit-trader-copiers').value = trader.copiers || 0;

        // Show modal
        const modal = document.getElementById('edit-trader-modal');
        if (modal) {
            modal.classList.add('show');
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Error loading trader details', icon: 'error' });
        console.error(error);
    }
}

// Hide edit trader modal
function hideEditTraderModal() {
    const modal = document.getElementById('edit-trader-modal');
    if (modal) {
        modal.classList.remove('show');
        document.getElementById('edit-trader-form').reset();
    }
}

// Submit edited trader
async function submitEditedTrader(event) {
    event.preventDefault();

    const traderId = document.getElementById('edit-trader-id').value;
    const traderData = {
        full_name: document.getElementById('edit-trader-full-name').value,
        profile_photo: document.getElementById('edit-trader-profile-photo').value,
        description: document.getElementById('edit-trader-description').value,
        specialization: document.getElementById('edit-trader-specialization').value,
        ytd_return: parseFloat(document.getElementById('edit-trader-ytd-return').value),
        win_rate: parseFloat(document.getElementById('edit-trader-win-rate').value),
        copiers: parseInt(document.getElementById('edit-trader-copiers').value) || 0
    };

    try {
        const response = await adminFetch(`/api/admin/traders/${traderId}`, {
            method: 'PUT',
            body: JSON.stringify(traderData)
        });

        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Trader updated successfully!', icon: 'success' });
            hideEditTraderModal();
            loadTraders();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: `Error: ${error.detail || 'Failed to update trader'}`, icon: 'error' });
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Delete trader
async function deleteTrader(traderId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Are you sure you want to delete this trader? This action cannot be undone.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/traders/${traderId}`, { method: 'DELETE' });
        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Trader deleted successfully', icon: 'success' });
            loadTraders();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to delete trader'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Load plans
async function loadPlans() {
    const container = document.getElementById('plans-container');
    container.innerHTML = 'Loading...';

    try {
        const response = await adminFetch('/api/admin/plans');
        const plans = await response.json();

        if (plans.length === 0) {
            container.innerHTML = '<p>No plans found. <button class="btn btn-primary" onclick="showAddPlanModal()">Add First Plan</button></p>';
            return;
        }

        let html = '<div style="display: grid; gap: 20px;">';
        plans.forEach(plan => {
            html += `
                <div style="border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px;">
                    <h4>${plan.name}</h4>
                    <p>${plan.description}</p>
                    <p><strong>Min Investment:</strong> $${plan.minimum_investment.toLocaleString()}</p>
                    <p><strong>Return:</strong> ${plan.expected_return_percent}% | <strong>Period:</strong> ${plan.holding_period_months} months</p>
                    <p><strong>Subscribers:</strong> ${plan.current_subscribers || 0}</p>
                    <p><span class="badge badge-${plan.is_active ? 'active' : 'inactive'}">${plan.is_active ? 'Active' : 'Inactive'}</span></p>
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <button class="btn btn-primary" style="padding: 8px 16px;" onclick="showEditPlanModal('${plan.id}')">Edit</button>
                        <button class="btn btn-danger" style="padding: 8px 16px;" onclick="deletePlan('${plan.id}')">Delete</button>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading plans</p>';
    }
}

// Show add plan modal
function showAddPlanModal() {
    const modal = document.getElementById('add-plan-modal');
    if (modal) {
        modal.classList.add('show');
    }
}

// Hide add plan modal
function hideAddPlanModal() {
    const modal = document.getElementById('add-plan-modal');
    if (modal) {
        modal.classList.remove('show');
        document.getElementById('add-plan-form').reset();
    }
}

// Submit new plan
async function submitNewPlan(event) {
    event.preventDefault();

    const planData = {
        name: document.getElementById('plan-name').value,
        description: document.getElementById('plan-description').value,
        minimum_investment: parseFloat(document.getElementById('plan-min-investment').value),
        expected_return_percent: parseFloat(document.getElementById('plan-return').value),
        holding_period_months: parseInt(document.getElementById('plan-period').value),
        is_active: document.getElementById('plan-active').checked
    };

    try {
        const response = await adminFetch('/api/admin/plans', {
            method: 'POST',
            body: JSON.stringify(planData)
        });

        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Investment plan created successfully!', icon: 'success' });
            hideAddPlanModal();
            loadPlans();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: `Error: ${error.detail || 'Failed to create plan'}`, icon: 'error' });
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
    }
}

// Show edit plan modal
async function showEditPlanModal(planId) {
    try {
        // Fetch plan details
        const response = await adminFetch(`/api/admin/plans/${planId}`);
        const plan = await response.json();

        // Populate form fields
        document.getElementById('edit-plan-id').value = plan.id;
        document.getElementById('edit-plan-name').value = plan.name;
        document.getElementById('edit-plan-description').value = plan.description;
        document.getElementById('edit-plan-min-investment').value = plan.minimum_investment;
        document.getElementById('edit-plan-return').value = plan.expected_return_percent;
        document.getElementById('edit-plan-period').value = plan.holding_period_months;
        document.getElementById('edit-plan-active').checked = plan.is_active;

        // Show modal
        const modal = document.getElementById('edit-plan-modal');
        if (modal) {
            modal.classList.add('show');
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Error loading plan details', icon: 'error' });
        console.error(error);
    }
}

// Hide edit plan modal
function hideEditPlanModal() {
    const modal = document.getElementById('edit-plan-modal');
    if (modal) {
        modal.classList.remove('show');
        document.getElementById('edit-plan-form').reset();
    }
}

// Submit edited plan
async function submitEditedPlan(event) {
    event.preventDefault();

    const planId = document.getElementById('edit-plan-id').value;
    const planData = {
        name: document.getElementById('edit-plan-name').value,
        description: document.getElementById('edit-plan-description').value,
        minimum_investment: parseFloat(document.getElementById('edit-plan-min-investment').value),
        expected_return_percent: parseFloat(document.getElementById('edit-plan-return').value),
        holding_period_months: parseInt(document.getElementById('edit-plan-period').value),
        is_active: document.getElementById('edit-plan-active').checked
    };

    try {
        const response = await adminFetch(`/api/admin/plans/${planId}`, {
            method: 'PUT',
            body: JSON.stringify(planData)
        });

        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Investment plan updated successfully!', icon: 'success' });
            hideEditPlanModal();
            loadPlans();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: `Error: ${error.detail || 'Failed to update plan'}`, icon: 'error' });
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Delete plan
async function deletePlan(planId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Are you sure you want to delete this investment plan? This action cannot be undone.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/plans/${planId}`, { method: 'DELETE' });
        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Investment plan deleted successfully', icon: 'success' });
            loadPlans();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to delete plan'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Logout
async function logout() {
    if ((await Swal.fire({
                title: 'Confirm Action',
                text: 'Are you sure you want to logout?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) {
        localStorage.removeItem('admin_token');
        window.location.href = '/admin/login';
    }
}

// ============================================================
// DEPOSIT REQUESTS
// ============================================================

// Load deposit requests
async function loadDepositRequests(statusFilter = '') {
    const container = document.getElementById('deposits-table-container');
    container.innerHTML = 'Loading...';

    try {
        const url = statusFilter ? `/api/admin/deposit-requests?status_filter=${statusFilter}` : '/api/admin/deposit-requests';
        const response = await adminFetch(url);
        const data = await response.json();

        if (data.requests.length === 0) {
            container.innerHTML = '<p>No deposit requests found</p>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Amount</th>
                        <th>Payment Method</th>
                        <th>Status</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.requests.forEach(req => {
            const date = new Date(req.created_at).toLocaleDateString();
            const statusBadge = `badge-${req.status}`;
            html += `
                <tr>
                    <td>${req.username}<br><small style="color: #8b93a7;">${req.email}</small></td>
                    <td><strong>$${req.amount.toLocaleString()}</strong></td>
                    <td>${req.payment_method}</td>
                    <td><span class="badge ${statusBadge}">${req.status}</span></td>
                    <td>${date}</td>
                    <td>
                        ${req.status === 'pending' ? `
                            <div class="action-buttons">
                                <button class="btn btn-success" style="padding: 5px 10px;" onclick="approveDeposit('${req.id}')">Approve</button>
                                <button class="btn btn-danger" style="padding: 5px 10px;" onclick="rejectDeposit('${req.id}')">Reject</button>
                            </div>
                        ` : `<span style="color: #8b93a7;">Reviewed</span>`}
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading deposit requests</p>';
        console.error(error);
    }
}

// Filter deposit requests
function filterDepositRequests() {
    const statusFilter = document.getElementById('deposit-status-filter').value;
    loadDepositRequests(statusFilter);
}

// Approve deposit
async function approveDeposit(requestId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Approve this deposit request? This will credit the user wallet.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        TED_AUTH.showLoading('Approving deposit...');
        const response = await adminFetch(`/api/admin/deposit-requests/${requestId}/approve`, { method: 'PUT' });
        TED_AUTH.closeLoading();

        if (response.ok) {
            const data = await response.json();
            Swal.fire({ title: 'Success!', text: `Deposit approved! $${data.amount} credited to user wallet.`, icon: 'success' });
            loadDepositRequests();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: 'Error: ' + (error.detail || 'Failed to approve deposit'), icon: 'error' });
        }
    } catch (error) {
        TED_AUTH.closeLoading();
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Reject deposit
async function rejectDeposit(requestId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Reject this deposit request?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        TED_AUTH.showLoading('Rejecting deposit...');
        const response = await adminFetch(`/api/admin/deposit-requests/${requestId}/reject`, { method: 'PUT' });
        TED_AUTH.closeLoading();

        if (response.ok) {
            Swal.fire({ title: 'Notice', text: 'Deposit request rejected', icon: 'info' });
            loadDepositRequests();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: 'Error: ' + (error.detail || 'Failed to reject deposit'), icon: 'error' });
        }
    } catch (error) {
        TED_AUTH.closeLoading();
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// ============================================================
// CRYPTO WALLETS
// ============================================================

// Load crypto wallets
async function loadCryptoWallets() {
    const container = document.getElementById('crypto-wallets-container');
    container.innerHTML = 'Loading...';

    try {
        const response = await adminFetch('/api/admin/crypto-wallets');
        const wallets = await response.json();

        if (wallets.length === 0) {
            container.innerHTML = '<p>No crypto wallets found. <button class="btn btn-primary" onclick="showAddCryptoWalletModal()">Add First Wallet</button></p>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Currency</th>
                        <th>Wallet Address</th>
                        <th>Network</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        wallets.forEach(wallet => {
            const date = wallet.created_at ? new Date(wallet.created_at).toLocaleDateString() : 'N/A';
            html += `
                <tr>
                    <td><strong>${wallet.currency}</strong></td>
                    <td><code style="background: #f7fafc; padding: 4px 8px; border-radius: 4px; font-size: 12px;">${wallet.wallet_address}</code></td>
                    <td>${wallet.network || 'N/A'}</td>
                    <td><span class="badge badge-${wallet.is_active ? 'active' : 'inactive'}">${wallet.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>${date}</td>
                    <td>
                        <button class="btn btn-danger" style="padding: 5px 10px;" onclick="deleteCryptoWallet('${wallet.id}')">Delete</button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading crypto wallets</p>';
        console.error(error);
    }
}

// Show add crypto wallet modal
function showAddCryptoWalletModal() {
    const modal = document.getElementById('add-crypto-wallet-modal');
    if (modal) {
        modal.classList.add('show');
    }
}

// Hide add crypto wallet modal
function hideAddCryptoWalletModal() {
    const modal = document.getElementById('add-crypto-wallet-modal');
    if (modal) {
        modal.classList.remove('show');
        document.getElementById('add-crypto-wallet-form').reset();
    }
}

// Submit new crypto wallet
async function submitNewCryptoWallet(event) {
    event.preventDefault();

    const walletData = {
        currency: document.getElementById('crypto-currency').value,
        wallet_address: document.getElementById('crypto-wallet-address').value,
        network: document.getElementById('crypto-network').value || null,
        is_active: document.getElementById('crypto-active').checked
    };

    try {
        const response = await adminFetch('/api/admin/crypto-wallets', {
            method: 'POST',
            body: JSON.stringify(walletData)
        });

        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Crypto wallet added successfully!', icon: 'success' });
            hideAddCryptoWalletModal();
            loadCryptoWallets();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: `Error: ${error.detail || 'Failed to add wallet'}`, icon: 'error' });
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Delete crypto wallet
async function deleteCryptoWallet(walletId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Delete this crypto wallet?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/crypto-wallets/${walletId}`, { method: 'DELETE' });
        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Crypto wallet deleted successfully', icon: 'success' });
            loadCryptoWallets();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to delete wallet'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// ============================================================
// BANK ACCOUNTS
// ============================================================

// Load bank accounts
async function loadBankAccounts() {
    const container = document.getElementById('bank-accounts-container');
    container.innerHTML = 'Loading...';

    try {
        const response = await adminFetch('/api/admin/bank-accounts');
        const accounts = await response.json();

        if (accounts.length === 0) {
            container.innerHTML = '<p>No bank accounts found. <button class="btn btn-primary" onclick="showAddBankAccountModal()">Add First Account</button></p>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Bank Name</th>
                        <th>Account Name</th>
                        <th>Account Number</th>
                        <th>Routing</th>
                        <th>SWIFT</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        accounts.forEach(account => {
            html += `
                <tr>
                    <td><strong>${account.bank_name}</strong></td>
                    <td>${account.account_name}</td>
                    <td><code style="background: #f7fafc; padding: 4px 8px; border-radius: 4px;">${account.account_number}</code></td>
                    <td>${account.routing_number || 'N/A'}</td>
                    <td>${account.swift_code || 'N/A'}</td>
                    <td><span class="badge badge-${account.is_active ? 'active' : 'inactive'}">${account.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-danger" style="padding: 5px 10px;" onclick="deleteBankAccount('${account.id}')">Delete</button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading bank accounts</p>';
        console.error(error);
    }
}

// Show add bank account modal
function showAddBankAccountModal() {
    const modal = document.getElementById('add-bank-account-modal');
    if (modal) {
        modal.classList.add('show');
    }
}

// Hide add bank account modal
function hideAddBankAccountModal() {
    const modal = document.getElementById('add-bank-account-modal');
    if (modal) {
        modal.classList.remove('show');
        document.getElementById('add-bank-account-form').reset();
    }
}

// Submit new bank account
async function submitNewBankAccount(event) {
    event.preventDefault();

    const accountData = {
        bank_name: document.getElementById('bank-name').value,
        account_name: document.getElementById('account-name').value,
        account_number: document.getElementById('account-number').value,
        routing_number: document.getElementById('routing-number').value || null,
        swift_code: document.getElementById('swift-code').value || null,
        is_active: document.getElementById('bank-active').checked
    };

    try {
        const response = await adminFetch('/api/admin/bank-accounts', {
            method: 'POST',
            body: JSON.stringify(accountData)
        });

        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Bank account added successfully!', icon: 'success' });
            hideAddBankAccountModal();
            loadBankAccounts();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: `Error: ${error.detail || 'Failed to add account'}`, icon: 'error' });
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Delete bank account
async function deleteBankAccount(accountId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Delete this bank account?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/bank-accounts/${accountId}`, { method: 'DELETE' });
        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Bank account deleted successfully', icon: 'success' });
            loadBankAccounts();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to delete account'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// ============================================================
// NOTIFICATIONS
// ============================================================

// Load notifications
async function loadNotifications() {
    const container = document.getElementById('notifications-container');
    container.innerHTML = 'Loading...';

    try {
        const response = await adminFetch('/api/admin/notifications');
        const data = await response.json();

        if (data.notifications.length === 0) {
            container.innerHTML = '<p>No notifications found. <button class="btn btn-primary" onclick="showCreateNotificationModal()">Create First Notification</button></p>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Type</th>
                        <th>Target</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.notifications.forEach(notif => {
            const date = new Date(notif.created_at).toLocaleDateString();
            const typeColors = {
                'info': '#2196F3',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336'
            };
            const typeColor = typeColors[notif.notification_type] || '#8b93a7';

            html += `
                <tr>
                    <td><strong>${notif.title}</strong><br><small style="color: #8b93a7;">${notif.message.substring(0, 50)}${notif.message.length > 50 ? '...' : ''}</small></td>
                    <td><span class="badge" style="background: ${typeColor};">${notif.notification_type.toUpperCase()}</span></td>
                    <td>${notif.target_type === 'all' ? '<strong>All Users</strong>' : 'Specific User'}</td>
                    <td>${date}</td>
                    <td>
                        <button class="btn btn-danger" style="padding: 5px 10px;" onclick="deleteNotification('${notif.id}')">Delete</button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading notifications</p>';
        console.error(error);
    }
}

// Show create notification modal
function showCreateNotificationModal() {
    const modal = document.getElementById('create-notification-modal');
    if (modal) {
        modal.classList.add('show');
        document.getElementById('create-notification-form').reset();
        document.getElementById('user-selection-group').style.display = 'none';
        document.getElementById('notif-target-user').value = '';
        document.getElementById('user-search-results').style.display = 'none';
        document.getElementById('selected-user-display').style.display = 'none';
    }
}

// Hide create notification modal
function hideCreateNotificationModal() {
    const modal = document.getElementById('create-notification-modal');
    if (modal) {
        modal.classList.remove('show');
        document.getElementById('create-notification-form').reset();
    }
}

// Toggle user selection based on target type
function toggleUserSelection() {
    const targetType = document.getElementById('notif-target-type').value;
    const userSelectionGroup = document.getElementById('user-selection-group');

    if (targetType === 'specific') {
        userSelectionGroup.style.display = 'block';
    } else {
        userSelectionGroup.style.display = 'none';
        document.getElementById('notif-target-user').value = '';
    }
}

// Search users for notification
let userSearchTimeout;
async function searchUsersForNotification() {
    clearTimeout(userSearchTimeout);
    const search = document.getElementById('notif-target-user-search').value.trim();

    if (search.length < 2) {
        document.getElementById('user-search-results').style.display = 'none';
        return;
    }

    userSearchTimeout = setTimeout(async () => {
        try {
            const response = await adminFetch(`/api/admin/users?search=${encodeURIComponent(search)}&limit=10`);
            const data = await response.json();
            const resultsDiv = document.getElementById('user-search-results');

            if (data.users.length === 0) {
                resultsDiv.innerHTML = '<p style="padding: 10px; color: #8b93a7;">No users found</p>';
                resultsDiv.style.display = 'block';
                return;
            }

            let html = '';
            data.users.forEach(user => {
                html += `
                    <div style="padding: 10px; cursor: pointer; border-bottom: 1px solid #e2e8f0; hover: background-color: #f7fafc;" onclick="selectUserForNotification('${user.id}', '${user.username}', '${user.email}')">
                        <strong>${user.username}</strong><br>
                        <small style="color: #8b93a7;">${user.email}</small>
                    </div>
                `;
            });

            resultsDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        } catch (error) {
            console.error('Error searching users:', error);
        }
    }, 300);
}

// Select user for notification
function selectUserForNotification(userId, username, email) {
    document.getElementById('notif-target-user').value = userId;
    document.getElementById('user-search-results').style.display = 'none';
    document.getElementById('notif-target-user-search').value = `${username} (${email})`;
    document.getElementById('selected-user-display').textContent = `✓ Selected: ${username} (${email})`;
    document.getElementById('selected-user-display').style.display = 'block';
}

// Submit new notification
async function submitNewNotification(event) {
    event.preventDefault();

    const targetType = document.getElementById('notif-target-type').value;
    const notificationData = {
        title: document.getElementById('notif-title').value,
        message: document.getElementById('notif-message').value,
        notification_type: document.getElementById('notif-type').value,
        target_type: targetType,
        target_user_id: targetType === 'specific' ? document.getElementById('notif-target-user').value : null
    };

    // Validate specific user selection
    if (targetType === 'specific' && !notificationData.target_user_id) {
        Swal.fire({ title: 'Warning', text: 'Please select a user for specific notification', icon: 'warning' });
        return;
    }

    try {
        const response = await adminFetch('/api/admin/notifications', {
            method: 'POST',
            body: JSON.stringify(notificationData)
        });

        if (response.ok) {
            const data = await response.json();
            alert(data.message || 'Notification sent successfully!');
            hideCreateNotificationModal();
            loadNotifications();
        } else {
            const error = await response.json();
            Swal.fire({ title: 'Error!', text: `Error: ${error.detail || 'Failed to send notification'}`, icon: 'error' });
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Delete notification
async function deleteNotification(notificationId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Delete this notification? This will remove it for all users.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/notifications/${notificationId}`, { method: 'DELETE' });
        if (response.ok) {
            Swal.fire({ title: 'Success!', text: 'Notification deleted successfully', icon: 'success' });
            loadNotifications();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to delete notification'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// ============================================================
// WITHDRAWAL REQUESTS
// ============================================================

// Load withdrawal requests
async function loadWithdrawalRequests(statusFilter = '') {
    const container = document.getElementById('withdrawals-table-container');
    container.innerHTML = 'Loading...';

    try {
        const url = statusFilter ? `/api/admin/withdrawal-requests?status_filter=${statusFilter}` : '/api/admin/withdrawal-requests';
        const response = await adminFetch(url);
        const data = await response.json();

        if (data.requests.length === 0) {
            container.innerHTML = '<p>No withdrawal requests found</p>';
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Amount</th>
                        <th>Method</th>
                        <th>Status</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.requests.forEach(req => {
            const date = new Date(req.created_at).toLocaleDateString();
            const statusBadge = req.status === 'completed' ? 'badge-approved' :
                              req.status === 'rejected' ? 'badge-rejected' : 'badge-pending';
            html += `
                <tr>
                    <td>${req.username}<br><small style="color: #8b93a7;">${req.email}</small></td>
                    <td><strong>$${req.amount.toLocaleString()}</strong></td>
                    <td>${req.withdrawal_method}</td>
                    <td><span class="badge ${statusBadge}">${req.status}</span></td>
                    <td>${date}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-secondary" style="padding: 5px 10px;" onclick="viewWithdrawalDetails('${req.id}')">View</button>
                            ${req.status === 'pending' ? `
                                <button class="btn btn-success" style="padding: 5px 10px;" onclick="approveWithdrawal('${req.id}')">Approve</button>
                                <button class="btn btn-danger" style="padding: 5px 10px;" onclick="rejectWithdrawal('${req.id}')">Reject</button>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading withdrawal requests</p>';
        console.error(error);
    }
}

// Filter withdrawal requests
function filterWithdrawalRequests() {
    const statusFilter = document.getElementById('withdrawal-status-filter').value;
    loadWithdrawalRequests(statusFilter);
}

// View withdrawal details
function viewWithdrawalDetails(requestId) {
    // Fetch the full withdrawal request data
    adminFetch(`/api/admin/withdrawal-requests?offset=0&limit=1000`)
        .then(response => response.json())
        .then(data => {
            const withdrawal = data.requests.find(req => req.id === requestId);
            if (!withdrawal) {
                Swal.fire({ title: 'Notice', text: 'Withdrawal request not found', icon: 'info' });
                return;
            }

            // Populate modal with withdrawal details
            const statusBadge = withdrawal.status === 'completed' ? 'badge-approved' :
                              withdrawal.status === 'rejected' ? 'badge-rejected' : 'badge-pending';
            document.getElementById('wd-status-badge').innerHTML = `<span class="badge ${statusBadge}">${withdrawal.status.toUpperCase()}</span>`;
            document.getElementById('wd-amount').textContent = `$${withdrawal.amount.toLocaleString()}`;
            document.getElementById('wd-username').textContent = withdrawal.username || '-';
            document.getElementById('wd-email').textContent = withdrawal.email || '-';
            document.getElementById('wd-method').textContent = withdrawal.withdrawal_method;
            document.getElementById('wd-created').textContent = new Date(withdrawal.created_at).toLocaleString();
            document.getElementById('wd-reviewed').textContent = withdrawal.reviewed_at ? new Date(withdrawal.reviewed_at).toLocaleString() : 'Not reviewed';

            // Format account details as JSON for readability
            document.getElementById('wd-account-details').textContent = JSON.stringify(withdrawal.account_details, null, 2);

            // Show notes if available
            if (withdrawal.notes) {
                document.getElementById('wd-notes-container').style.display = 'block';
                document.getElementById('wd-notes').textContent = withdrawal.notes;
            } else {
                document.getElementById('wd-notes-container').style.display = 'none';
            }

            // Show modal
            document.getElementById('withdrawal-details-modal').classList.add('show');
        })
        .catch(error => {
            console.error('Error loading withdrawal details:', error);
            Swal.fire({ title: 'Error!', text: 'Error loading withdrawal details', icon: 'error' });
        });
}

// Close withdrawal details modal
function closeWithdrawalDetailsModal() {
    document.getElementById('withdrawal-details-modal').classList.remove('show');
}

// Approve withdrawal
async function approveWithdrawal(requestId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Approve this withdrawal request? This will deduct the amount from the user wallet and mark as completed.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/withdrawal-requests/${requestId}/approve`, { method: 'PUT' });
        if (response.ok) {
            const data = await response.json();
            Swal.fire({ title: 'Success!', text: `Withdrawal approved! $${data.amount} deducted from user wallet.`, icon: 'success' });
            loadWithdrawalRequests();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to approve withdrawal'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}

// Reject withdrawal
async function rejectWithdrawal(requestId) {
    if (!(await Swal.fire({
                title: 'Confirm Action',
                text: 'Reject this withdrawal request?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes',
                cancelButtonText: 'No'
            })).isConfirmed) return;

    try {
        const response = await adminFetch(`/api/admin/withdrawal-requests/${requestId}/reject`, { method: 'PUT' });
        if (response.ok) {
            Swal.fire({ title: 'Notice', text: 'Withdrawal request rejected', icon: 'info' });
            loadWithdrawalRequests();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.detail || 'Failed to reject withdrawal'));
        }
    } catch (error) {
        Swal.fire({ title: 'Error!', text: 'Network error. Please try again.', icon: 'error' });
        console.error(error);
    }
}
