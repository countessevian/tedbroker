# Network Search & Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add search and filtering functionality to Traders, Recent Trades, and Posts tabs in the Network menu.

**Architecture:** Client-side filtering using JavaScript. Add search input and filter dropdowns to each tab's header. Filter data in memory after loading from API.

**Tech Stack:** Vanilla JavaScript, HTML, CSS (existing)

---

## Task 1: Add Search/Filter UI to Traders Tab

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` (add filter HTML)
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js` (add filter functions)
- Modify: `public/copytradingbroker.io/dashboard.html` (add filter CSS)

- [ ] **Step 1: Add search and filter HTML above traders-container**

In `dashboard.html` around line 3436 (after content-header), add:

```html
<div class="traders-filter-bar">
    <div class="search-wrapper">
        <i class="fa-solid fa-search"></i>
        <input type="text" id="traders-search" placeholder="Search traders..." oninput="filterTraders()">
    </div>
    <select id="traders-specialization-filter" onchange="filterTraders()">
        <option value="">All Specializations</option>
        <option value="Crypto">Crypto</option>
        <option value="Forex">Forex</option>
        <option value="Stocks">Stocks</option>
        <option value="Options">Options</option>
        <option value="Commodities">Commodities</option>
    </select>
    <select id="traders-risk-filter" onchange="filterTraders()">
        <option value="">All Risk Levels</option>
        <option value="1-3">Low (1-3)</option>
        <option value="4-6">Medium (4-6)</option>
        <option value="7-10">High (7-10)</option>
    </select>
    <select id="traders-winrate-filter" onchange="filterTraders()">
        <option value="">All Win Rates</option>
        <option value="70+">70%+</option>
        <option value="50-70">50-70%</option>
        <option value="<50">Under 50%</option>
    </select>
</div>
```

- [ ] **Step 2: Add filterTraders function to dashboard.js**

Add after loadExpertTraders function:

```javascript
function filterTraders() {
    const searchTerm = document.getElementById('traders-search')?.value.toLowerCase() || '';
    const specialization = document.getElementById('traders-specialization-filter')?.value || '';
    const riskFilter = document.getElementById('traders-risk-filter')?.value || '';
    const winrateFilter = document.getElementById('traders-winrate-filter')?.value || '';
    
    if (!tradersCache) return;
    
    let filtered = tradersCache.filter(trader => {
        // Search by name
        if (searchTerm && !trader.full_name.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        // Filter by specialization
        if (specialization && !trader.specialization.toLowerCase().includes(specialization.toLowerCase())) {
            return false;
        }
        
        // Filter by risk score
        if (riskFilter) {
            const risk = trader.risk_score || 5;
            if (riskFilter === '1-3' && (risk < 1 || risk > 3)) return false;
            if (riskFilter === '4-6' && (risk < 4 || risk > 6)) return false;
            if (riskFilter === '7-10' && (risk < 7 || risk > 10)) return false;
        }
        
        // Filter by win rate
        if (winrateFilter) {
            const winRate = trader.win_rate || 0;
            if (winrateFilter === '70+' && winRate < 70) return false;
            if (winrateFilter === '50-70' && (winRate < 50 || winRate > 70)) return false;
            if (winrateFilter === '<50' && winRate >= 50) return false;
        }
        
        return true;
    });
    
    displayTraders(filtered);
}
```

- [ ] **Step 3: Add traders-filter-bar CSS**

Add to dashboard.html styles:

```css
.traders-filter-bar {
    display: flex;
    gap: 12px;
    padding: 16px 20px;
    background: var(--card-bg, #fff);
    border-radius: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.search-wrapper {
    flex: 1;
    min-width: 200px;
    position: relative;
}

.search-wrapper i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #8b93a7;
}

.search-wrapper input {
    width: 100%;
    padding: 10px 10px 10px 36px;
    border: 1px solid var(--border-color, #e5e7eb);
    border-radius: 8px;
    font-size: 14px;
}

.traders-filter-bar select {
    padding: 10px 12px;
    border: 1px solid var(--border-color, #e5e7eb);
    border-radius: 8px;
    font-size: 14px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #1f2937);
    min-width: 150px;
}
```

---

## Task 2: Add Search/Filter UI to Recent Trades Tab

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` (add filter HTML)
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js` (add filter functions)

- [ ] **Step 1: Add search and filter HTML above recent-trades-container**

In dashboard.html around line 3680 (after content-header), add:

```html
<div class="recent-trades-filter-bar">
    <div class="search-wrapper">
        <i class="fa-solid fa-search"></i>
        <input type="text" id="recent-trades-search" placeholder="Search by symbol or trader..." oninput="filterRecentTrades()">
    </div>
    <select id="trades-side-filter" onchange="filterRecentTrades()">
        <option value="">All Sides</option>
        <option value="long">Long</option>
        <option value="short">Short</option>
    </select>
    <select id="trades-exchange-filter" onchange="filterRecentTrades()">
        <option value="">All Exchanges</option>
        <option value="Binance">Binance</option>
        <option value="Coinbase">Coinbase</option>
        <option value="Kraken">Kraken</option>
        <option value="eToro">eToro</option>
        <option value="OANDA">OANDA</option>
    </select>
    <select id="trades-ordertype-filter" onchange="filterRecentTrades()">
        <option value="">All Order Types</option>
        <option value="market">Market</option>
        <option value="limit">Limit</option>
        <option value="stop_loss">Stop Loss</option>
        <option value="take_profit">Take Profit</option>
    </select>
</div>
```

- [ ] **Step 2: Add filterRecentTrades function to dashboard.js**

Add after loadRecentTrades function:

```javascript
function filterRecentTrades() {
    const searchTerm = document.getElementById('recent-trades-search')?.value.toLowerCase() || '';
    const sideFilter = document.getElementById('trades-side-filter')?.value || '';
    const exchangeFilter = document.getElementById('trades-exchange-filter')?.value || '';
    const orderTypeFilter = document.getElementById('trades-ordertype-filter')?.value || '';
    
    if (!recentTradesCache) return;
    
    let filtered = recentTradesCache.filter(trade => {
        // Search by symbol or trader name
        if (searchTerm) {
            const symbolMatch = trade.symbol?.toLowerCase().includes(searchTerm);
            const traderMatch = trade.trader_name?.toLowerCase().includes(searchTerm);
            if (!symbolMatch && !traderMatch) return false;
        }
        
        // Filter by side
        if (sideFilter && trade.side !== sideFilter) return false;
        
        // Filter by exchange
        if (exchangeFilter && !trade.exchange?.toLowerCase().includes(exchangeFilter.toLowerCase())) return false;
        
        // Filter by order type
        if (orderTypeFilter && trade.order_type !== orderTypeFilter) return false;
        
        return true;
    });
    
    displayRecentTrades(filtered);
}
```

- [ ] **Step 3: Add recent-trades-filter-bar CSS**

Add to dashboard.html styles:

```css
.recent-trades-filter-bar {
    display: flex;
    gap: 12px;
    padding: 16px 20px;
    background: var(--card-bg, #fff);
    border-radius: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.recent-trades-filter-bar .search-wrapper {
    flex: 1;
    min-width: 200px;
    position: relative;
}

.recent-trades-filter-bar .search-wrapper i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #8b93a7;
}

.recent-trades-filter-bar input {
    width: 100%;
    padding: 10px 10px 10px 36px;
    border: 1px solid var(--border-color, #e5e7eb);
    border-radius: 8px;
    font-size: 14px;
}

.recent-trades-filter-bar select {
    padding: 10px 12px;
    border: 1px solid var(--border-color, #e5e7eb);
    border-radius: 8px;
    font-size: 14px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #1f2937);
    min-width: 140px;
}
```

---

## Task 3: Add Search/Filter UI to Posts Tab

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` (add filter HTML)
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js` (add filter functions)

- [ ] **Step 1: Add search and filter HTML above posts-container**

In dashboard.html around line 3708 (after content-header), add:

```html
<div class="posts-filter-bar">
    <div class="search-wrapper">
        <i class="fa-solid fa-search"></i>
        <input type="text" id="posts-search" placeholder="Search posts..." oninput="filterPosts()">
    </div>
    <select id="posts-trader-filter" onchange="filterPosts()">
        <option value="">All Traders</option>
        <!-- Trader options populated dynamically -->
    </select>
    <select id="posts-sort-filter" onchange="filterPosts()">
        <option value="newest">Newest First</option>
        <option value="oldest">Oldest First</option>
        <option value="most-liked">Most Liked</option>
    </select>
</div>
```

- [ ] **Step 2: Add filterPosts function to dashboard.js**

Add after loadPosts function:

```javascript
function filterPosts() {
    const searchTerm = document.getElementById('posts-search')?.value.toLowerCase() || '';
    const traderFilter = document.getElementById('posts-trader-filter')?.value || '';
    const sortFilter = document.getElementById('posts-sort-filter')?.value || 'newest';
    
    if (!postsCache) return;
    
    let filtered = postsCache.filter(post => {
        // Search by content
        if (searchTerm && !post.content?.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        // Filter by trader
        if (traderFilter && post.trader_name !== traderFilter) return false;
        
        return true;
    });
    
    // Sort
    if (sortFilter === 'newest') {
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (sortFilter === 'oldest') {
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    } else if (sortFilter === 'most-liked') {
        filtered.sort((a, b) => (b.like_count || 0) - (a.like_count || 0));
    }
    
    renderPosts(filtered);
}

function populateTraderFilter() {
    const select = document.getElementById('posts-trader-filter');
    if (!select || !tradersCache) return;
    
    const traders = [...new Set(tradersCache.map(p => p.trader_name))].sort();
    select.innerHTML = '<option value="">All Traders</option>' + 
        traders.map(t => `<option value="${t}">${t}</option>`).join('');
}
```

- [ ] **Step 3: Add posts-filter-bar CSS**

Add to dashboard.html styles:

```css
.posts-filter-bar {
    display: flex;
    gap: 12px;
    padding: 16px 20px;
    background: var(--card-bg, #fff);
    border-radius: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.posts-filter-bar .search-wrapper {
    flex: 1;
    min-width: 200px;
    position: relative;
}

.posts-filter-bar .search-wrapper i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #8b93a7;
}

.posts-filter-bar input {
    width: 100%;
    padding: 10px 10px 10px 36px;
    border: 1px solid var(--border-color, #e5e7eb);
    border-radius: 8px;
    font-size: 14px;
}

.posts-filter-bar select {
    padding: 10px 12px;
    border: 1px solid var(--border-color, #e5e7eb);
    border-radius: 8px;
    font-size: 14px;
    background: var(--bg-primary, #fff);
    color: var(--text-primary, #1f2937);
    min-width: 150px;
}
```

---

## Task 4: Update load Functions to Cache Data

**Files:**
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js`

- [ ] **Step 1: Update loadExpertTraders to cache data**

Ensure tradersCache is set after loading:

```javascript
// After fetching traders, add:
tradersCache = traders;
displayTraders(traders);

// Also call populateTraderFilter after traders load
populateTraderFilter();
```

---

## Summary

This implementation adds:
1. **Traders Tab**: Search by name, filter by specialization, risk score, win rate
2. **Recent Trades Tab**: Search by symbol/trader, filter by side, exchange, order type
3. **Posts Tab**: Search by content, filter by trader, sort by date/likes
