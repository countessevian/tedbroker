# Dashboard Header App Bar + Three-Panel Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the dashboard from sidebar + content layout to header app bar + three-panel layout (AI chat | centered content | help center).

**Architecture:** Convert `<aside class="sidebar">` into a full-width `<header class="app-bar">` with the menu rendered as icon-only items (hover expands text). Repurpose the sidebar div as AI chat panel (left). Add a new right panel for help center links. Center main content between them. All tab switching, submenu toggles, and content rendering logic preserved from existing code.

**Tech Stack:** Vanilla JS, CSS, FastAPI (single AI chat endpoint), Font Awesome 6 icons

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — HTML restructure + CSS
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js` — add search, help panel, AI chat handlers
- Modify: `app/routes/chat.py` — add AI chat endpoint

---

### Task 1: Restructure HTML — header app bar + left/right panels

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html`

**Changes to HTML structure:**

Current:
```html
<header class="mobile-app-bar">...</header>
<div class="tradingview-ticker-container">...</div>
<div class="sidebar-overlay"></div>
<div class="dashboard-wrapper">
  <aside class="sidebar" id="sidebar">
    <div class="desktop-toggle-btn">...</div>
    <div class="sidebar-header"><a><img/></a></div>
    <nav class="sidebar-menu">...all menu items...</nav>
    <div class="sidebar-user-profile">...</div>
  </aside>
  <main class="main-content">...all tab content...</main>
</div>
<div class="dark-mode-toggle">...</div>
<div class="language-selector">...</div>
```

New structure:
```html
<header class="app-bar" id="app-bar">
  <div class="app-bar-left">
    <a href="/"><img src="assets/images/logoIcon/tedbrokers-logo.jpg" alt="TED Brokers" /></a>
  </div>
  <nav class="app-bar-menu" id="app-bar-menu">
    <!-- menu items moved from sidebar, icons only -->
  </nav>
  <div class="app-bar-right">
    <div class="app-bar-search" id="app-bar-search">
      <i class="fa-solid fa-search"></i>
      <input type="text" placeholder="Search..." id="search-input" />
      <div class="search-dropdown" id="search-dropdown"></div>
    </div>
    <div class="app-bar-lang" id="app-bar-lang">
      <button class="app-bar-lang-btn" onclick="toggleLanguageDropdown()">
        <span class="flag-icon" id="current-language-flag">🇺🇸</span>
      </button>
    </div>
    <div class="app-bar-darkmode" id="app-bar-darkmode" onclick="toggleDarkMode()">
      <i class="fas fa-sun sun-icon"></i>
      <i class="fas fa-moon moon-icon"></i>
    </div>
  </div>
</header>

<div class="tradingview-ticker-container">...</div>
<div class="sidebar-overlay"></div>

<div class="dashboard-wrapper">
  <!-- Left Panel: AI Chat (repurposed sidebar) -->
  <aside class="left-panel" id="left-panel">
    <div class="desktop-toggle-btn" id="desktop-toggle-btn">
      <i class="fa-solid fa-chevron-left"></i>
    </div>
    <div class="left-panel-header">
      <i class="fa-solid fa-robot"></i>
      <span>AI Assistant</span>
    </div>
    <div class="chat-messages" id="chat-messages">
      <div class="chat-welcome">
        <p>Start a conversation with your AI assistant</p>
      </div>
    </div>
    <div class="chat-input-area">
      <input type="text" id="chat-input" placeholder="Type a message..." />
      <button id="chat-send-btn"><i class="fa-solid fa-paper-plane"></i></button>
    </div>
    <div class="sidebar-user-profile" id="sidebar-user-profile">...</div>
  </aside>

  <!-- Main Content -->
  <main class="main-content">...all tab content (unchanged)...</main>

  <!-- Right Panel: Help Center -->
  <aside class="right-panel" id="right-panel">
    <div class="right-panel-header">
      <i class="fa-solid fa-circle-question"></i>
      <span>Help Center</span>
    </div>
    <div class="help-section">
      <h4 class="help-category">Getting Started</h4>
      <a class="help-link" onclick="switchToTab('how-it-works')"><i class="fa-solid fa-play"></i> How It Works</a>
      <a class="help-link" onclick="switchToTab('onboarding')"><i class="fa-solid fa-user-plus"></i> Account Setup</a>
    </div>
    <div class="help-section">
      <h4 class="help-category">Account</h4>
      <a class="help-link" onclick="switchToTab('account-personal')"><i class="fa-solid fa-user"></i> Personal Details</a>
      <a class="help-link" onclick="switchToTab('account-security')"><i class="fa-solid fa-shield-halved"></i> Security</a>
    </div>
    <div class="help-section">
      <h4 class="help-category">Trading</h4>
      <a class="help-link" onclick="switchToTab('subscription')"><i class="fa-solid fa-robot"></i> Robo Advisor</a>
      <a class="help-link" onclick="switchToTab('active-copies')"><i class="fa-solid fa-copy"></i> Active Copies</a>
      <a class="help-link" onclick="switchToTab('performance')"><i class="fa-solid fa-chart-pie"></i> Performance</a>
    </div>
    <div class="help-section">
      <h4 class="help-category">Support</h4>
      <a class="help-link" href="/faqs.html"><i class="fa-solid fa-question"></i> FAQ</a>
      <a class="help-link" href="/contact-us.html"><i class="fa-solid fa-envelope"></i> Contact Us</a>
    </div>
  </aside>
</div>
<!-- dark-mode-toggle and language-selector removed (now in app bar) -->
```

- [ ] **Step 1: Replace the sidebar HTML with the new header + three-panel structure**

Replace the `<header class="mobile-app-bar">` through `</aside>` (sidebar close) with the new app bar + left panel HTML. Keep the sidebar-menu nav contents exactly as-is (same classes, data-tab attributes, icons, spans) — they move inside `<nav class="app-bar-menu">`.

Move the dark-mode-toggle and language-selector divs inside the app-bar-right area (remove their fixed-position originals).

Keep the `<div class="sidebar-user-profile">` inside the left-panel (below chat input).

- [ ] **Step 2: Add the right panel HTML**

After the `</main>` tag and before `</div>` (dashboard-wrapper close), add the `<aside class="right-panel">` HTML.

---

### Task 2: Add CSS for app bar, hover expansion, submenu dropdowns, three-column layout

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` (add to existing `<style>` block)

**New CSS variables needed in `:root`:**
```css
--appbar-height: 60px;
--left-panel-width: 280px;
--left-panel-collapsed: 50px;
--right-panel-width: 260px;
```

- [ ] **Step 1: Add app bar CSS**

```css
.app-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--appbar-height);
  background: #2D3748;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 1001;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}

.app-bar-left {
  flex-shrink: 0;
  width: 180px;
}

.app-bar-left img {
  max-width: 140px;
  height: auto;
}

.app-bar-menu {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.app-bar-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #cbd5e0;
  text-decoration: none;
  transition: all 0.25s ease;
  white-space: nowrap;
  overflow: hidden;
  max-width: 40px;
  position: relative;
}

.app-bar-menu .menu-item i {
  font-size: 18px;
  min-width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.app-bar-menu .menu-item span {
  max-width: 0;
  overflow: hidden;
  transition: max-width 0.25s ease, margin-left 0.25s ease;
  font-size: 13px;
  font-weight: 500;
}

.app-bar-menu .menu-item:hover {
  background: rgba(255,255,255,0.1);
  max-width: 200px;
  gap: 8px;
}

.app-bar-menu .menu-item:hover span {
  max-width: 150px;
  margin-left: 8px;
}

.app-bar-menu .menu-item.active {
  color: #D32F2F;
  background: rgba(211,47,47,0.1);
}

.app-bar-menu .menu-item.logout-btn:hover {
  background: rgba(211,47,47,0.2);
  color: #ff6b6b;
}

/* Hide submenu arrows and parent indicators in app bar */
.app-bar-menu .submenu-arrow,
.app-bar-menu .menu-item-parent {
  display: none;
}

/* Submenu dropdown */
.menu-dropdown {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #2D3748;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 8px 0;
  min-width: 200px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  display: none;
  z-index: 1002;
}

.menu-dropdown.open {
  display: block;
}

.menu-dropdown .submenu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #cbd5e0;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 13px;
}

.menu-dropdown .submenu-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.menu-dropdown .submenu-item i {
  width: 18px;
  text-align: center;
  font-size: 14px;
}
```

- [ ] **Step 2: Add app bar right section CSS**

```css
.app-bar-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-bar-search {
  position: relative;
  display: flex;
  align-items: center;
}

.app-bar-search input {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 6px 14px 6px 32px;
  color: #fff;
  font-size: 13px;
  width: 180px;
  outline: none;
  transition: all 0.3s ease;
}

.app-bar-search input:focus {
  width: 240px;
  background: rgba(255,255,255,0.15);
  border-color: #D32F2F;
}

.app-bar-search input::placeholder {
  color: #8b93a7;
}

.app-bar-search > i {
  position: absolute;
  left: 10px;
  color: #8b93a7;
  font-size: 13px;
  pointer-events: none;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: #2D3748;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  display: none;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1002;
}

.search-dropdown.open {
  display: block;
}

.search-result-category {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: #8b93a7;
  letter-spacing: 0.5px;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  color: #cbd5e0;
  font-size: 13px;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.search-result-item i {
  width: 16px;
  text-align: center;
  font-size: 13px;
}

.app-bar-lang-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  font-size: 18px;
  line-height: 1;
  transition: background 0.2s;
}

.app-bar-lang-btn:hover {
  background: rgba(255,255,255,0.1);
}

/* Language dropdown inside app bar */
.app-bar-lang .language-dropdown {
  right: auto;
  left: 0;
}

.app-bar-darkmode {
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
  font-size: 16px;
}

.app-bar-darkmode:hover {
  background: rgba(255,255,255,0.1);
}

.app-bar-darkmode .sun-icon { color: #FDB813; }
.app-bar-darkmode .moon-icon { color: #a0aec0; }
[data-theme="dark"] .app-bar-darkmode .sun-icon { display: none; }
[data-theme="light"] .app-bar-darkmode .moon-icon { display: none; }
```

- [ ] **Step 3: Update layout CSS — left panel, right panel, centered main content**

Replace the existing `.sidebar` CSS block with `.left-panel`:

```css
.left-panel {
  width: var(--left-panel-width);
  background: #2D3748;
  border-right: 1px solid rgba(255,255,255,0.1);
  position: fixed;
  height: calc(100vh - var(--appbar-height));
  left: 0;
  top: var(--appbar-height);
  overflow-y: hidden;
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.left-panel.collapsed {
  width: var(--left-panel-collapsed);
}

.left-panel.collapsed .left-panel-header span,
.left-panel.collapsed .chat-messages,
.left-panel.collapsed .chat-input-area,
.left-panel.collapsed .sidebar-user-profile .user-info {
  display: none;
}

.left-panel.collapsed .sidebar-user-profile {
  justify-content: center;
}

.left-panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.left-panel-header i {
  font-size: 20px;
  color: #D32F2F;
}

/* Chat area */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-welcome {
  text-align: center;
  color: #8b93a7;
  padding: 20px;
  font-size: 13px;
}

.chat-message {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  animation: fadeInUp 0.2s ease;
}

.chat-message.user {
  align-self: flex-end;
  background: #D32F2F;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chat-message.ai {
  align-self: flex-start;
  background: rgba(255,255,255,0.1);
  color: #e2e8f0;
  border-bottom-left-radius: 4px;
}

.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.chat-input-area input {
  flex: 1;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 8px 14px;
  color: #fff;
  font-size: 13px;
  outline: none;
}

.chat-input-area input:focus {
  border-color: #D32F2F;
}

.chat-input-area input::placeholder {
  color: #8b93a7;
}

.chat-input-area button {
  background: #D32F2F;
  border: none;
  border-radius: 50%;
  width: 34px;
  height: 34px;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-input-area button:hover {
  background: #b71c1c;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
```

Update `.main-content`:
```css
.main-content {
  margin-left: var(--left-panel-width);
  margin-right: var(--right-panel-width);
  margin-top: calc(var(--appbar-height) + 50px);
  flex: 1;
  padding: 30px;
  max-width: 900px;
  width: auto;
  transition: all 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: var(--left-panel-collapsed);
}
```

Add right panel CSS:
```css
.right-panel {
  width: var(--right-panel-width);
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  position: fixed;
  height: calc(100vh - var(--appbar-height) - 50px);
  right: 0;
  top: calc(var(--appbar-height) + 50px);
  overflow-y: auto;
  z-index: 999;
  transition: all 0.3s ease;
  padding: 16px;
}

.right-panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.right-panel-header i {
  color: #D32F2F;
  font-size: 18px;
}

.help-section {
  margin-bottom: 20px;
}

.help-category {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.help-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}

.help-link:hover {
  color: #D32F2F;
}

.help-link i {
  width: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}
```

Update `.tradingview-ticker-container`:
```css
.tradingview-ticker-container {
  top: var(--appbar-height);
  left: var(--left-panel-width);
  right: var(--right-panel-width);
}

.tradingview-ticker-container.sidebar-collapsed {
  left: var(--left-panel-collapsed);
}
```

- [ ] **Step 4: Update mobile responsive CSS**

In the `@media (max-width: 768px)` block, update:

```css
@media (max-width: 768px) {
  .app-bar-menu { display: none; }  /* Hidden on mobile, use hamburger */
  
  .app-bar-search input { width: 120px; }
  .app-bar-search input:focus { width: 160px; }
  
  .left-panel {
    transform: translateX(-100%);
    top: var(--appbar-height);
    height: calc(100vh - var(--appbar-height));
  }
  .left-panel.mobile-open { transform: translateX(0); }
  
  .right-panel { display: none; }  /* Hidden on mobile */
  
  .main-content {
    margin-left: 0;
    margin-right: 0;
    margin-top: calc(var(--appbar-height) + 50px);
    max-width: 100%;
    padding: 16px;
  }
  
  .tradingview-ticker-container {
    left: 0;
    right: 0;
  }
  
  .sidebar-overlay {
    top: var(--appbar-height);
    height: calc(100% - var(--appbar-height));
  }
}
```

Add hamburger button to the app bar for mobile (inside `.app-bar-left`):
```html
<button class="hamburger-btn" id="hamburger-btn">
  <span></span><span></span><span></span>
</button>
```

Remove the old `<header class="mobile-app-bar">`.

- [ ] **Step 5: Add desktop toggle button style update**

```css
.left-panel.collapsed + * .desktop-toggle-btn,
.left-panel.collapsed .desktop-toggle-btn {
  left: calc(var(--left-panel-collapsed) - 18px);
}
.desktop-toggle-btn {
  top: calc(var(--appbar-height) + 10px);
  left: calc(var(--left-panel-width) - 18px);
}
```

---

### Task 3: Update JavaScript — menu positioning, dropdowns, search, help panel, AI chat

**Files:**
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js`

- [ ] **Step 1: Add helper function for tab switching**

Add at the beginning of dashboard.js:
```javascript
/**
 * Switch to a dashboard tab programmatically
 */
function switchToTab(tabName) {
  // Remove active from all menu/submenu items
  document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
  document.querySelectorAll('.submenu-item').forEach(si => si.classList.remove('active'));
  
  // Activate the corresponding menu item
  const menuItem = document.querySelector(`.menu-item[data-tab="${tabName}"]`);
  if (menuItem) menuItem.classList.add('active');
  
  const submenuItem = document.querySelector(`.submenu-item[data-tab="${tabName}"]`);
  if (submenuItem) submenuItem.classList.add('active');
  
  // Show tab content
  document.querySelectorAll('.tab-content-wrapper').forEach(tc => tc.classList.remove('active'));
  const tabContent = document.getElementById('tab-' + tabName);
  if (tabContent) tabContent.classList.add('active');
  
  window.scrollTo(0, 0);
}
```

- [ ] **Step 2: Replace submenu toggle handlers**

Replace the existing per-parent submenu toggle code (lines ~5081-5123) with a universal dropdown approach:

```javascript
// Submenu dropdowns in the app bar
const menuItemsWithSubmenu = document.querySelectorAll('#app-bar-menu .menu-item-parent > .menu-item');
menuItemsWithSubmenu.forEach(item => {
  const parent = item.closest('.menu-item-parent');
  const submenu = parent.querySelector('.submenu');
  const dropdownId = parent.id + '-dropdown';
  
  // Create dropdown element
  const dropdown = document.createElement('div');
  dropdown.className = 'menu-dropdown';
  dropdown.id = dropdownId;
  dropdown.innerHTML = submenu.innerHTML;
  item.parentNode.appendChild(dropdown);
  
  // Position the dropdown
  item.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    // Close other open dropdowns
    document.querySelectorAll('.menu-dropdown.open').forEach(d => {
      if (d.id !== dropdownId) d.classList.remove('open');
    });
    
    dropdown.classList.toggle('open');
  });
  
  // Handle submenu item clicks
  dropdown.querySelectorAll('.submenu-item').forEach(subItem => {
    subItem.addEventListener('click', function(e) {
      e.stopPropagation();
      const tabName = this.getAttribute('data-tab');
      if (tabName) {
        switchToTab(tabName);
        dropdown.classList.remove('open');
      }
    });
  });
});

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
  if (!e.target.closest('.menu-item-parent')) {
    document.querySelectorAll('.menu-dropdown.open').forEach(d => d.classList.remove('open'));
  }
});
```

Keep the existing tab switching handlers for `.menu-item[data-tab]` and `.submenu-item[data-tab]` — they still work unchanged since the DOM classes/attributes are preserved.

- [ ] **Step 3: Add search functionality**

Add at the end of dashboard.js:

```javascript
// Search functionality
const searchInput = document.getElementById('search-input');
const searchDropdown = document.getElementById('search-dropdown');

// Known tab names and their icons for search
const SEARCH_ITEMS = [
  { type: 'Tab', name: 'Dashboard', tab: 'dashboard', icon: 'fa-gauge-high' },
  { type: 'Tab', name: 'Wallet', tab: 'wallet', icon: 'fa-wallet' },
  { type: 'Tab', name: 'Automated Calls', tab: 'automated-calls', icon: 'fa-robot' },
  { type: 'Tab', name: 'Active Copies', tab: 'active-copies', icon: 'fa-copy' },
  { type: 'Tab', name: 'Performance', tab: 'performance', icon: 'fa-chart-pie' },
  { type: 'Tab', name: 'Robo Advisor', tab: 'subscription', icon: 'fa-robot' },
  { type: 'Tab', name: 'ETF Automation', tab: 'etf-plans', icon: 'fa-chart-pie' },
  { type: 'Tab', name: 'DeFi Automation', tab: 'defi-earnings', icon: 'fa-coins' },
  { type: 'Tab', name: 'Options', tab: 'options', icon: 'fa-file-alt' },
  { type: 'Tab', name: 'Staking', tab: 'staking', icon: 'fa-layer-group' },
  { type: 'Tab', name: 'Traders', tab: 'traders', icon: 'fa-users-line' },
  { type: 'Tab', name: 'Recent Trades', tab: 'recent-trades', icon: 'fa-clock-rotate-left' },
  { type: 'Tab', name: 'Posts', tab: 'posts', icon: 'fa-newspaper' },
  { type: 'Tab', name: 'Referrals', tab: 'referrals', icon: 'fa-share-nodes' },
  { type: 'Tab', name: 'News', tab: 'news', icon: 'fa-newspaper' },
  { type: 'Tab', name: 'Personal Details', tab: 'account-personal', icon: 'fa-user' },
  { type: 'Tab', name: 'Security', tab: 'account-security', icon: 'fa-shield-halved' },
];

let searchTraderCache = [];

// Load trader names for search
async function loadSearchTraders() {
  try {
    const resp = await TED_AUTH.apiCall('/api/traders');
    const data = await resp.json();
    if (data.traders) {
      searchTraderCache = data.traders.map(t => ({
        type: 'Trader',
        name: t.full_name || t.name || 'Unknown',
        tab: 'traders',
        icon: 'fa-user'
      }));
    }
  } catch(e) { /* silent */ }
}

if (searchInput) {
  searchInput.addEventListener('input', function() {
    const query = this.value.trim().toLowerCase();
    if (query.length < 1) {
      searchDropdown.classList.remove('open');
      return;
    }
    
    // Search tabs
    const tabResults = SEARCH_ITEMS.filter(item =>
      item.name.toLowerCase().includes(query)
    );
    
    // Search traders
    const traderResults = searchTraderCache.filter(item =>
      item.name.toLowerCase().includes(query)
    );
    
    // Build dropdown
    let html = '';
    if (tabResults.length) {
      html += '<div class="search-result-category">Tabs</div>';
      tabResults.forEach(item => {
        html += `<div class="search-result-item" data-tab="${item.tab}"><i class="fa-solid ${item.icon}"></i> ${item.name}</div>`;
      });
    }
    if (traderResults.length) {
      html += '<div class="search-result-category">Traders</div>';
      traderResults.forEach(item => {
        html += `<div class="search-result-item" data-tab="${item.tab}"><i class="fa-solid ${item.icon}"></i> ${item.name}</div>`;
      });
    }
    
    if (html) {
      searchDropdown.innerHTML = html;
      searchDropdown.classList.add('open');
      
      // Add click handlers
      searchDropdown.querySelectorAll('.search-result-item').forEach(el => {
        el.addEventListener('click', function() {
          const tab = this.dataset.tab;
          switchToTab(tab);
          searchDropdown.classList.remove('open');
          searchInput.value = '';
          
          // Load traders tab data if needed
          if (tab === 'traders') loadExpertTraders(true);
        });
      });
    } else {
      searchDropdown.innerHTML = '<div class="search-result-item" style="color:#8b93a7;cursor:default;">No results found</div>';
      searchDropdown.classList.add('open');
    }
  });
  
  // Close search on blur
  searchInput.addEventListener('blur', function() {
    setTimeout(() => searchDropdown.classList.remove('open'), 200);
  });
  
  // Load traders for search
  loadSearchTraders();
}
```

- [ ] **Step 4: Add AI chat handlers**

Add at the end of dashboard.js:

```javascript
// AI Chat
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const chatMessages = document.getElementById('chat-messages');

function addChatMessage(text, sender) {
  if (!chatMessages) return;
  // Remove welcome message
  const welcome = chatMessages.querySelector('.chat-welcome');
  if (welcome) welcome.remove();
  
  const msgDiv = document.createElement('div');
  msgDiv.className = 'chat-message ' + sender;
  msgDiv.textContent = text;
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendChatMessage(text) {
  addChatMessage(text, 'user');
  chatInput.value = '';
  
  // Show loading indicator
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'chat-message ai';
  loadingDiv.textContent = 'Thinking...';
  loadingDiv.id = 'chat-loading';
  chatMessages.appendChild(loadingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  try {
    const resp = await TED_AUTH.apiCall('/api/chat/ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await resp.json();
    
    document.getElementById('chat-loading')?.remove();
    addChatMessage(data.response || data.message, 'ai');
  } catch(e) {
    document.getElementById('chat-loading')?.remove();
    addChatMessage('Sorry, I had trouble responding. Please try again.', 'ai');
  }
}

if (chatSendBtn && chatInput) {
  chatSendBtn.addEventListener('click', function() {
    const text = chatInput.value.trim();
    if (text) sendChatMessage(text);
  });
  
  chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      const text = this.value.trim();
      if (text) sendChatMessage(text);
    }
  });
}
```

- [ ] **Step 5: Update sidebar toggle to left-panel toggle**

Update the existing sidebar toggle JS (around line 5205-5257) to work with `.left-panel`:

```javascript
// Left panel toggle
const leftPanel = document.getElementById('left-panel');
const mainContent = document.querySelector('.main-content');
const hamburgerBtn = document.getElementById('hamburger-btn');
const desktopToggleBtn = document.getElementById('desktop-toggle-btn');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const tickerContainer = document.getElementById('tradingview-ticker');

// Mobile hamburger
if (hamburgerBtn) {
  hamburgerBtn.addEventListener('click', function() {
    leftPanel.classList.toggle('mobile-open');
    hamburgerBtn.classList.toggle('active');
    if (sidebarOverlay) sidebarOverlay.classList.toggle('active');
  });
}

// Desktop collapse
if (desktopToggleBtn) {
  const desktopToggleIcon = desktopToggleBtn.querySelector('i');
  desktopToggleBtn.addEventListener('click', function() {
    leftPanel.classList.toggle('collapsed');
    mainContent.classList.toggle('sidebar-collapsed');
    if (tickerContainer) tickerContainer.classList.toggle('sidebar-collapsed');
    
    if (leftPanel.classList.contains('collapsed')) {
      desktopToggleIcon.classList.remove('fa-chevron-left');
      desktopToggleIcon.classList.add('fa-chevron-right');
    } else {
      desktopToggleIcon.classList.remove('fa-chevron-right');
      desktopToggleIcon.classList.add('fa-chevron-left');
    }
  });
}

// Overlay click to close
if (sidebarOverlay) {
  sidebarOverlay.addEventListener('click', function() {
    leftPanel.classList.remove('mobile-open');
    if (hamburgerBtn) hamburgerBtn.classList.remove('active');
    sidebarOverlay.classList.remove('active');
  });
}
```

---

### Task 4: Add AI chat backend endpoint

**Files:**
- Modify: `app/routes/chat.py`

- [ ] **Step 1: Add AI chat endpoint**

Add to the bottom of `app/routes/chat.py`:

```python
from pydantic import BaseModel


class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str


@router.post("/ai", response_model=AIChatResponse)
async def ai_chat(
    chat_request: AIChatRequest,
    current_user: dict = Depends(get_current_user_token)
):
    """
    AI assistant chat endpoint.
    Returns a helpful response about the TED Brokers platform.
    """
    message = chat_request.message.lower()
    
    # Simple intent-based responses
    if any(word in message for word in ["hello", "hi", "hey", "help"]):
        response = "Hi there! I'm your TED Brokers AI assistant. I can help you with navigating the dashboard, understanding your portfolio, finding trading plans, or managing your account. What would you like to know?"
    elif any(word in message for word in ["deposit", "fund", "add money", "wallet"]):
        response = "To deposit funds, go to the Wallet tab and click 'Deposit'. You can fund your account via cryptocurrency (BTC, ETH, USDT) or bank transfer. Minimum deposit is $50."
    elif any(word in message for word in ["withdraw", "withdrawal", "cash out"]):
        response = "To withdraw funds, go to the Wallet tab and click 'Withdraw'. Withdrawals are processed within 24 hours. Minimum withdrawal is $10."
    elif any(word in message for word in ["portfolio", "investment", "copy", "trader"]):
        response = "You can view your portfolio in the Portfolio section. To copy a trader, go to Network > Traders, browse expert traders, and click 'Copy' on any trader whose strategy matches your goals."
    elif any(word in message for word in ["plan", "subscription", "robo", "etf", "defi", "staking"]):
        response = "We offer several investment plans: Robo Advisor (automated AI trading), ETF Automation, DeFi Earnings, Options Automation, and Staking. You can explore all of them in the Explore menu."
    elif any(word in message for word in ["refer", "referral", "share", "invite"]):
        response = "Our referral program rewards you for inviting friends! Go to the Referrals tab to get your unique referral link. You'll earn a commission on your referrals' trading fees."
    elif any(word in message for word in ["security", "password", "2fa", "two factor"]):
        response = "To manage your security settings, go to Account > Security. You can enable 2FA, change your password, and view your login history there."
    elif any(word in message for word in ["news", "market", "price", "bitcoin", "crypto"]):
        response = "You can stay updated with the latest market news in the News tab. We aggregate news from multiple sources including CryptoCompare and NewsAPI."
    elif any(word in message for word in ["account", "profile", "setting"]):
        response = "Your account settings are in the Account menu. You can update your personal details, manage security, and view your profile information."
    elif any(word in message for word in ["trade", "recent", "history"]):
        response = "Your recent trades are displayed in Network > Recent Trades. You can see all your copy trading activities there."
    else:
        response = "I'm not sure I understand. I can help with: deposits, withdrawals, portfolio management, investment plans, referrals, security settings, account info, and market news. Just ask me anything about the platform!"
    
    return AIChatResponse(response=response)
```

---

### Task 5: Update main.py to include existing chat router (verify)

**Files:**
- Read: `main.py`

- [ ] **Step 1: Verify chat router is included**

Check that `main.py` line 62 includes `chat` in the import and has `app.include_router(chat.router)`.

Current import at line 11:
```python
from app.routes import auth, traders, plans, etf_plans, defi_plans, options_plans, wallet, referrals, admin, deposits, investments, news, crypto_wallets, withdrawals, chat, onboarding, notifications, language
```

The `chat` router is already imported and included — no changes needed.

---

### Task 6: Test and verify

- [ ] **Step 1: Verify the page loads without errors**

Restart the server and load the dashboard page. Check browser console for any JS errors.

Run: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8071/dashboard.html`
Expected: 200

- [ ] **Step 2: Verify all menu items switch tabs correctly**

Click each menu item and verify the correct tab content appears. Test both top-level items and submenu items.

- [ ] **Step 3: Verify hover expansion on menu items**

Hover over each icon-only menu item in the app bar. Verify the text label slides in smoothly.

- [ ] **Step 4: Verify submenu dropdowns**

Click a parent menu item (Portfolio, Explore, Network, Account). Verify a dropdown appears below with sub-items. Click a sub-item — verify it opens the tab and closes the dropdown.

- [ ] **Step 5: Verify search functionality**

Type in the search bar. Verify results appear categorized. Click a result — verify it navigates to the correct tab.

- [ ] **Step 6: Verify AI chat**

Type a message in the AI chat panel. Verify it sends to the backend and receives a response.

- [ ] **Step 7: Verify responsive behavior**

Resize the browser to mobile width (< 768px). Verify: app bar is compact, left panel slides in/out via hamburger, right panel is hidden, main content is full-width.

- [ ] **Step 8: Verify dark mode and language toggle**

Toggle dark mode from the app bar icon. Verify the theme switches correctly. Open the language dropdown from the app bar. Switch language — verify translation works.
