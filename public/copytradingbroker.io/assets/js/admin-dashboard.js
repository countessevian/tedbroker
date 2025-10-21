const API_BASE = '';
let currentTab = 'dashboard';

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

// Load users
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
        
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Wallet</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.users.forEach(user => {
            const date = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A';
            html += `
                <tr>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>$${user.wallet_balance.toLocaleString()}</td>
                    <td><span class="badge badge-${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>${date}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 5px 10px; margin: 2px;" onclick="viewUser('${user.id}')">View</button>
                        ${user.is_active ? 
                            `<button class="btn btn-secondary" style="padding: 5px 10px; margin: 2px; background: #f44336;" onclick="deactivateUser('${user.id}')">Deactivate</button>` :
                            `<button class="btn btn-secondary" style="padding: 5px 10px; margin: 2px; background: #4caf50;" onclick="activateUser('${user.id}')">Activate</button>`
                        }
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="color: red;">Error loading users</p>';
    }
}

// Search users
function searchUsers() {
    const search = document.getElementById('user-search').value;
    loadUsers(search);
}

// View user details
async function viewUser(userId) {
    try {
        const response = await adminFetch(`/api/admin/users/${userId}`);
        const user = await response.json();
        
        alert(`User Details:\n\nUsername: ${user.username}\nEmail: ${user.email}\nFull Name: ${user.full_name || 'N/A'}\nWallet: $${user.wallet_balance}\nStatus: ${user.is_active ? 'Active' : 'Inactive'}\nReferral Code: ${user.referral_code || 'N/A'}`);
    } catch (error) {
        alert('Error loading user details');
    }
}

// Activate user
async function activateUser(userId) {
    if (!confirm('Activate this user?')) return;
    
    try {
        await adminFetch(`/api/admin/users/${userId}/activate`, { method: 'PUT' });
        alert('User activated');
        loadUsers();
    } catch (error) {
        alert('Error activating user');
    }
}

// Deactivate user
async function deactivateUser(userId) {
    if (!confirm('Deactivate this user?')) return;
    
    try {
        await adminFetch(`/api/admin/users/${userId}/deactivate`, { method: 'PUT' });
        alert('User deactivated');
        loadUsers();
    } catch (error) {
        alert('Error deactivating user');
    }
}

// Load traders
async function loadTraders() {
    const container = document.getElementById('traders-container');
    container.innerHTML = 'Loading...';
    
    try {
        const response = await adminFetch('/api/traders/');
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
                    <button class="btn btn-secondary" onclick="deleteTrader('${trader.id}')">Delete</button>
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
    alert('Add Trader feature - Please use the API directly at /api/traders/ (POST) or contact support for full implementation');
}

// Delete trader
async function deleteTrader(traderId) {
    if (!confirm('Delete this trader?')) return;
    
    try {
        await adminFetch(`/api/traders/${traderId}`, { method: 'DELETE' });
        alert('Trader deleted');
        loadTraders();
    } catch (error) {
        alert('Error deleting trader');
    }
}

// Load plans
async function loadPlans() {
    const container = document.getElementById('plans-container');
    container.innerHTML = 'Loading...';
    
    try {
        const response = await adminFetch('/api/plans/');
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
                    <p><span class="badge badge-${plan.is_active ? 'active' : 'inactive'}">${plan.is_active ? 'Active' : 'Inactive'}</span></p>
                    <button class="btn btn-secondary" onclick="deletePlan('${plan.id}')">Delete</button>
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
    alert('Add Plan feature - Please use the API directly at /api/plans/ (POST) or contact support for full implementation');
}

// Delete plan
async function deletePlan(planId) {
    if (!confirm('Delete this plan?')) return;
    
    try {
        await adminFetch(`/api/plans/${planId}`, { method: 'DELETE' });
        alert('Plan deleted');
        loadPlans();
    } catch (error) {
        alert('Error deleting plan');
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('admin_token');
        window.location.href = '/admin/login';
    }
}
