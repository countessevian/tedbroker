# Mobile Menu Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broken mobile hamburger menu with a dedicated full-screen slide-in navigation panel that works independently of the desktop menu.

**Architecture:** A new `<div id="mobile-nav">` element is added to `dashboard.html` with its own CSS and JS, completely separate from the desktop `<nav class="app-bar-menu">`. The desktop menu is hidden on mobile. All tab switching reuses the existing `switchToTab()` function.

**Tech Stack:** HTML, CSS (inline in `<style>`), JavaScript (inline in `<script>`), Font Awesome icons

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `public/copytradingbroker.io/dashboard.html` | Modify | Add mobile nav HTML, CSS, JS; remove old broken mobile rules |

All changes are in a single file. No backend changes. No new files.

---

### Task 1: Add Mobile Nav CSS

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — add CSS block inside `<style>` section

- [ ] **Step 1: Locate the CSS insertion point**

Find the line `/* Mobile submenu overrides — must come AFTER base .app-bar-menu rules */` in the `<style>` block. The new mobile nav CSS goes right BEFORE this comment.

- [ ] **Step 2: Add the mobile nav CSS**

Insert the following CSS block right before the `/* Mobile submenu overrides` comment:

```css
/* ======================== */
/* MOBILE SLIDE-IN NAV      */
/* ======================== */
.mobile-nav-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1050;
    transition: opacity 0.3s ease;
}
.mobile-nav-overlay.active {
    display: block;
}

.mobile-nav {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 85vw;
    max-width: 320px;
    height: 100vh;
    height: 100dvh;
    background: #1a202c;
    z-index: 1060;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    flex-direction: column;
    overflow-y: auto;
    overscroll-behavior: contain;
}
.mobile-nav.active {
    display: flex;
    transform: translateX(0);
}

.mobile-nav-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}
.mobile-nav-logo {
    height: 30px;
    border-radius: 6px;
}
.mobile-nav-close {
    background: none;
    border: none;
    color: #a0aec0;
    font-size: 20px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 6px;
    transition: background 0.2s;
}
.mobile-nav-close:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
}

.mobile-nav-profile {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}
.mobile-nav-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #D32F2F, #5a9abf);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 18px;
    flex-shrink: 0;
}
.mobile-nav-user-name {
    color: #fff;
    font-weight: 600;
    font-size: 15px;
}
.mobile-nav-user-email {
    color: #a0aec0;
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 200px;
}

.mobile-nav-items {
    flex: 1;
    padding: 8px 0;
    overflow-y: auto;
}
.mobile-nav-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 20px;
    color: #cbd5e0;
    text-decoration: none;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    font-size: 15px;
    position: relative;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
}
.mobile-nav-item i:first-child {
    width: 22px;
    text-align: center;
    font-size: 16px;
    flex-shrink: 0;
}
.mobile-nav-item:hover,
.mobile-nav-item.active {
    background: rgba(255, 255, 255, 0.08);
    color: #fff;
}
.mobile-nav-item.active {
    border-left: 3px solid #D32F2F;
    color: #D32F2F;
}

.mobile-nav-submenu {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    background: rgba(0, 0, 0, 0.15);
}
.mobile-nav-parent.expanded .mobile-nav-submenu {
    max-height: 500px;
}
.mobile-nav-arrow {
    margin-left: auto;
    font-size: 12px;
    transition: transform 0.3s ease;
}
.mobile-nav-parent.expanded .mobile-nav-arrow {
    transform: rotate(180deg);
}
.mobile-nav-subitem {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 20px 12px 56px;
    color: #a0aec0;
    text-decoration: none;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    font-size: 14px;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
}
.mobile-nav-subitem i:first-child {
    width: 18px;
    text-align: center;
    font-size: 14px;
    flex-shrink: 0;
}
.mobile-nav-subitem:hover,
.mobile-nav-subitem.active {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
}
.mobile-nav-subitem.active {
    color: #D32F2F;
}

.mobile-nav-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px 0;
    flex-shrink: 0;
}
.mobile-nav-logout {
    color: #ef4444 !important;
}
.mobile-nav-logout:hover {
    background: rgba(239, 68, 68, 0.1) !important;
}
```

- [ ] **Step 3: Verify CSS is valid**

Run: `grep -c "mobile-nav" public/copytradingbroker.io/dashboard.html`
Expected: output >= 40 (confirms CSS was added)

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-nav): add slide-in navigation CSS styles"
```

---

### Task 2: Add Mobile Nav HTML

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — add HTML after `<header class="app-bar">` closing tag

- [ ] **Step 1: Locate the HTML insertion point**

Find the closing `</header>` tag for the app bar (line ~4358). The new mobile nav HTML goes right AFTER this tag.

- [ ] **Step 2: Add the mobile nav HTML**

Insert the following HTML right after `</header>`:

```html
<!-- Mobile Slide-In Navigation -->
<div id="mobile-nav-overlay" class="mobile-nav-overlay"></div>
<div id="mobile-nav" class="mobile-nav">
    <div class="mobile-nav-header">
        <img src="assets/images/logoIcon/tedbrokers-logo.jpg" alt="TED Brokers" class="mobile-nav-logo" />
        <button class="mobile-nav-close" id="mobile-nav-close">
            <i class="fa-solid fa-xmark"></i>
        </button>
    </div>

    <div class="mobile-nav-profile">
        <div class="mobile-nav-avatar" id="mobile-nav-avatar">U</div>
        <div class="mobile-nav-user-info">
            <div class="mobile-nav-user-name" id="mobile-nav-user-name">User</div>
            <div class="mobile-nav-user-email" id="mobile-nav-user-email">user@email.com</div>
        </div>
    </div>

    <div class="mobile-nav-items">
        <a class="mobile-nav-item active" data-tab="dashboard">
            <i class="fa-solid fa-gauge-high"></i><span>Overview</span>
        </a>
        <a class="mobile-nav-item" data-tab="wallet">
            <i class="fa-solid fa-wallet"></i><span>Wallet</span>
        </a>

        <div class="mobile-nav-parent" data-submenu="portfolio">
            <a class="mobile-nav-item">
                <i class="fa-solid fa-chart-line"></i><span>Portfolio</span>
                <i class="fa-solid fa-chevron-down mobile-nav-arrow"></i>
            </a>
            <div class="mobile-nav-submenu">
                <a class="mobile-nav-subitem" data-tab="automated-calls">
                    <i class="fa-solid fa-robot"></i><span>Automated Calls</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="active-copies">
                    <i class="fa-solid fa-copy"></i><span>Active Copies</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="performance">
                    <i class="fa-solid fa-chart-pie"></i><span>Performance</span>
                </a>
            </div>
        </div>

        <div class="mobile-nav-parent" data-submenu="explore">
            <a class="mobile-nav-item">
                <i class="fa-solid fa-compass"></i><span>Explore</span>
                <i class="fa-solid fa-chevron-down mobile-nav-arrow"></i>
            </a>
            <div class="mobile-nav-submenu">
                <a class="mobile-nav-subitem" data-tab="subscription">
                    <i class="fa-solid fa-robot"></i><span>Robo Advisor</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="etf-plans">
                    <i class="fa-solid fa-chart-pie"></i><span>ETF Automation</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="defi-earnings">
                    <i class="fa-solid fa-coins"></i><span>DeFi Automation</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="options">
                    <i class="fa-solid fa-file-alt"></i><span>Options Automation</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="staking">
                    <i class="fa-solid fa-layer-group"></i><span>Staking</span>
                </a>
            </div>
        </div>

        <div class="mobile-nav-parent" data-submenu="network">
            <a class="mobile-nav-item">
                <i class="fa-solid fa-network-wired"></i><span>Network</span>
                <i class="fa-solid fa-chevron-down mobile-nav-arrow"></i>
            </a>
            <div class="mobile-nav-submenu">
                <a class="mobile-nav-subitem" data-tab="traders">
                    <i class="fa-solid fa-users-line"></i><span>Traders</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="recent-trades">
                    <i class="fa-solid fa-clock-rotate-left"></i><span>Recent Trades</span>
                </a>
                <a class="mobile-nav-subitem" data-tab="posts">
                    <i class="fa-solid fa-newspaper"></i><span>Posts</span>
                </a>
            </div>
        </div>

        <a class="mobile-nav-item" data-tab="referrals">
            <i class="fa-solid fa-share-nodes"></i><span>Referrals</span>
        </a>
        <a class="mobile-nav-item" data-tab="news">
            <i class="fa-solid fa-newspaper"></i><span>News</span>
        </a>
    </div>

    <div class="mobile-nav-footer">
        <a class="mobile-nav-item" data-tab="account-personal">
            <i class="fa-solid fa-user"></i><span>Personal Details</span>
        </a>
        <a class="mobile-nav-item" data-tab="account-security">
            <i class="fa-solid fa-shield-halved"></i><span>Security</span>
        </a>
        <a class="mobile-nav-item mobile-nav-logout" id="mobile-nav-logout">
            <i class="fa-solid fa-right-from-bracket"></i><span>Log Out</span>
        </a>
    </div>
</div>
```

- [ ] **Step 3: Verify HTML is present**

Run: `grep -c "mobile-nav-overlay\|mobile-nav\"" public/copytradingbroker.io/dashboard.html`
Expected: output >= 2

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-nav): add slide-in navigation HTML structure"
```

---

### Task 3: Add Mobile Nav JavaScript

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — add JS inside existing `<script>` block

- [ ] **Step 1: Locate the JS insertion point**

Find the line `// Mobile: expand submenus inline instead of dropdown` in the `<script>` block. The new mobile nav JS goes right BEFORE this comment (replacing the old mobile submenu toggle logic).

- [ ] **Step 2: Add the mobile nav JavaScript**

Insert the following JS right before the `// Mobile: expand submenus inline` comment:

```javascript
// === MOBILE SLIDE-IN NAVIGATION ===
(function() {
    const mobileNav = document.getElementById('mobile-nav');
    const mobileOverlay = document.getElementById('mobile-nav-overlay');
    const mobileCloseBtn = document.getElementById('mobile-nav-close');
    const hamburgerBtn = document.getElementById('hamburger-btn');

    if (!mobileNav || !hamburgerBtn) return;

    function openMobileNav() {
        if (window.innerWidth > 768) return;
        mobileNav.classList.add('active');
        mobileOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileNav() {
        mobileNav.classList.remove('active');
        mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Expose closeMobileNav globally for switchToTab to call
    window.closeMobileNav = closeMobileNav;

    hamburgerBtn.addEventListener('click', function() {
        if (mobileNav.classList.contains('active')) {
            closeMobileNav();
        } else {
            openMobileNav();
        }
    });

    mobileCloseBtn.addEventListener('click', closeMobileNav);
    mobileOverlay.addEventListener('click', closeMobileNav);

    // Submenu accordion toggles
    document.querySelectorAll('.mobile-nav-parent').forEach(function(parent) {
        var item = parent.querySelector('.mobile-nav-item');
        if (item) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                parent.classList.toggle('expanded');
            });
        }
    });

    // Tab switching — reuse existing switchToTab()
    document.querySelectorAll('.mobile-nav-item[data-tab], .mobile-nav-subitem[data-tab]').forEach(function(item) {
        item.addEventListener('click', function() {
            var tabName = this.getAttribute('data-tab');
            if (tabName && typeof switchToTab === 'function') {
                switchToTab(tabName);
            }
            closeMobileNav();
            updateMobileNavActive(tabName);
        });
    });

    // Footer items (Personal Details, Security)
    document.querySelectorAll('.mobile-nav-footer .mobile-nav-item[data-tab]').forEach(function(item) {
        item.addEventListener('click', function() {
            var tabName = this.getAttribute('data-tab');
            if (tabName && typeof switchToTab === 'function') {
                switchToTab(tabName);
            }
            closeMobileNav();
            updateMobileNavActive(tabName);
        });
    });

    // Logout
    var logoutBtn = document.getElementById('mobile-nav-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            closeMobileNav();
            if (typeof handleLogout === 'function') handleLogout();
        });
    }

    // Update active states in mobile nav
    function updateMobileNavActive(tabName) {
        document.querySelectorAll('.mobile-nav-item, .mobile-nav-subitem').forEach(function(el) {
            el.classList.remove('active');
        });
        var targetItem = document.querySelector('.mobile-nav-item[data-tab="' + tabName + '"], .mobile-nav-subitem[data-tab="' + tabName + '"]');
        if (targetItem) {
            targetItem.classList.add('active');
            var parent = targetItem.closest('.mobile-nav-parent');
            if (parent) {
                parent.querySelector('.mobile-nav-item').classList.add('active');
                parent.classList.add('expanded');
            }
        }
    }

    // Close on resize to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileNav();
        }
    });

    // Populate user profile from existing DOM
    function populateMobileProfile() {
        var userName = document.getElementById('user-display-name');
        var userEmail = document.getElementById('user-email');
        var mobileName = document.getElementById('mobile-nav-user-name');
        var mobileEmail = document.getElementById('mobile-nav-user-email');
        var mobileAvatar = document.getElementById('mobile-nav-avatar');

        if (userName && mobileName) mobileName.textContent = userName.textContent;
        if (userEmail && mobileEmail) mobileEmail.textContent = userEmail.textContent;
        if (userName && mobileAvatar) {
            var initials = userName.textContent.trim().charAt(0).toUpperCase();
            mobileAvatar.textContent = initials || 'U';
        }
    }
    populateMobileProfile();
})();
```

- [ ] **Step 3: Verify JS is present**

Run: `grep -c "MOBILE SLIDE-IN NAVIGATION" public/copytradingbroker.io/dashboard.html`
Expected: 1

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-nav): add slide-in navigation JavaScript"
```

---

### Task 4: Remove Old Broken Mobile CSS Rules

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — remove old mobile menu CSS rules

- [ ] **Step 1: Locate the old mobile CSS block**

Find the `@media (max-width: 768px)` block that contains the old `.app-bar-menu` mobile rules. It starts around line 2653 with `.hamburger-btn { display: flex; }` and the comment about mobile submenu overrides.

- [ ] **Step 2: Remove old mobile menu CSS rules**

Delete the following lines from the `@media (max-width: 768px)` block:

```css
            /* Mobile .app-bar-menu overrides are AFTER base .app-bar-menu rules (line ~3828) */
```

Replace with just the hamburger button rule and the non-menu items:

Find this section and remove the comment line only (keep `.hamburger-btn` and everything after it that isn't `.app-bar-menu` related):

```css
        @media (max-width: 768px) {
            .hamburger-btn { display: flex; }

            /* Mobile .app-bar-menu overrides are AFTER base .app-bar-menu rules (line ~3828) */

            .app-bar-search input { width: 120px; }
```

Change to:

```css
        @media (max-width: 768px) {
            .hamburger-btn { display: flex; }

            .app-bar-search input { width: 120px; }
```

- [ ] **Step 3: Also remove the mobile submenu overrides block**

Find the block that starts with `/* Mobile submenu overrides — must come AFTER base .app-bar-menu rules */` (around line 3748). Delete the ENTIRE `@media (max-width: 768px)` block that follows it — all the `.app-bar-menu` mobile rules. This block is no longer needed since we have the dedicated mobile nav.

Remove everything from:
```css
        /* Mobile submenu overrides — must come AFTER base .app-bar-menu rules */
        @media (max-width: 768px) {
            .app-bar-menu {
```

Through to the closing `}` of that media block (ends with the `.app-bar-menu .submenu-item` rule).

- [ ] **Step 4: Verify old rules are removed**

Run: `grep -c "Mobile submenu overrides" public/copytradingbroker.io/dashboard.html`
Expected: 0

Run: `grep -c "app-bar-menu.*mobile-open" public/copytradingbroker.io/dashboard.html`
Expected: 0

- [ ] **Step 5: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "refactor(mobile-nav): remove old broken mobile menu CSS rules"
```

---

### Task 5: Remove Old Broken Mobile JS Handlers

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — remove old mobile submenu toggle JS and old hamburger mobile branch

- [ ] **Step 1: Remove old mobile submenu toggle JS**

Find and delete the entire block:
```javascript
        // Mobile: expand submenus inline instead of dropdown
        document.querySelectorAll('#app-bar-menu .menu-item-parent > .menu-item').forEach(item => {
            item.addEventListener('click', function(e) {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    const parent = this.closest('.menu-item-parent');
                    const submenu = parent.querySelector('.submenu');
                    parent.classList.toggle('expanded');
                    if (submenu) submenu.classList.toggle('expanded');
                }
            });
        });
```

- [ ] **Step 2: Update the hamburger click handler**

Find the existing hamburger click handler:
```javascript
        hamburgerBtn.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                const appBarMenu = document.getElementById('app-bar-menu');
                appBarMenu.classList.toggle('mobile-open');
                hamburgerBtn.classList.toggle('active');
                sidebarOverlay.classList.toggle('active');
                leftPanel.classList.remove('mobile-open');
            } else {
```

Replace the mobile branch with a no-op (the new mobile nav JS handles mobile):
```javascript
        hamburgerBtn.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                // Mobile hamburger is handled by the mobile-nav IIFE
                return;
            } else {
```

- [ ] **Step 3: Verify old handlers are removed**

Run: `grep -c "expand submenus inline" public/copytradingbroker.io/dashboard.html`
Expected: 0

Run: `grep -c "app-bar-menu.*mobile-open" public/copytradingbroker.io/dashboard.html`
Expected: 0

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "refactor(mobile-nav): remove old broken mobile JS handlers"
```

---

### Task 6: Verify Desktop Menu Is Unchanged

**Files:**
- Verify: `public/copytradingbroker.io/dashboard.html`

- [ ] **Step 1: Verify desktop CSS is untouched**

Run: `grep -n "app-bar-menu {" public/copytradingbroker.io/dashboard.html`
Expected: Only the base `.app-bar-menu` rule at line ~3644 (no mobile overrides)

- [ ] **Step 2: Verify desktop submenu dropdown JS is untouched**

Run: `grep -n "Submenu dropdowns in the app bar" public/copytradingbroker.io/dashboard.html`
Expected: Found at line ~5974

- [ ] **Step 3: Verify switchToTab is untouched**

Run: `grep -n "function switchToTab" public/copytradingbroker.io/dashboard.html`
Expected: Found, unchanged

- [ ] **Step 4: Verify loadTabData is untouched**

Run: `grep -n "function loadTabData" public/copytradingbroker.io/dashboard.html`
Expected: Found, unchanged

- [ ] **Step 5: No commit needed — verification only**

---

### Task 7: End-to-End Verification

**Files:**
- Verify: `public/copytradingbroker.io/dashboard.html` served at `http://localhost:8071/dashboard.html`

- [ ] **Step 1: Server is running**

Run: `curl -s http://localhost:8071/dashboard.html | head -5`
Expected: HTML output (confirms server is serving the file)

- [ ] **Step 2: Mobile nav HTML is present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "mobile-nav-overlay"`
Expected: >= 1

- [ ] **Step 3: Mobile nav CSS is present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "MOBILE SLIDE-IN NAV"`
Expected: 1

- [ ] **Step 4: Mobile nav JS is present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "MOBILE SLIDE-IN NAVIGATION"`
Expected: 1

- [ ] **Step 5: No old mobile CSS conflicts**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "Mobile submenu overrides"`
Expected: 0

- [ ] **Step 6: Desktop menu CSS still exists**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "\.app-bar-menu {"`
Expected: 1 (base rule only)

- [ ] **Step 7: All tab names are present in mobile nav**

Run: `curl -s http://localhost:8071/dashboard.html | grep -o 'data-tab="[^"]*"' | sort -u`
Expected: All 17 tab names present:
`account-personal`, `account-security`, `active-copies`, `automated-calls`, `dashboard`, `defi-earnings`, `etf-plans`, `news`, `options`, `performance`, `posts`, `recent-trades`, `referrals`, `staking`, `subscription`, `traders`, `wallet`

- [ ] **Step 8: Final commit (if any remaining changes)**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-nav): complete mobile slide-in navigation implementation"
```
