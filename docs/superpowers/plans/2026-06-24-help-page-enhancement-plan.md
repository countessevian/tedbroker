# Help Page Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the existing help.html page with 4 new accordion sections documenting Dashboard, AI Assistant, Portfolio & Explore, and Network & Social features.

**Architecture:** Add new HTML category cards, sidebar links, and JavaScript data entries to the existing help page structure. No new files needed - all changes are in help.html.

**Tech Stack:** HTML, CSS (existing styles), JavaScript (existing accordion/search/scrollspy patterns)

---

### Task 1: Add New Category Cards

**Files:**
- Modify: `public/copytradingbroker.io/help.html:270-331` (category cards section)

- [ ] **Step 1: Add 4 new category cards after the existing Security card**

Insert the following HTML after the Security card div (line 330) but before the closing `</div>` of the row:

```html
<div class="col-6 col-md-4 col-lg" data-target="section-dashboard">
    <div class="help-card" onclick="scrollToSection('section-dashboard')" role="button" tabindex="0">
        <i class="fas fa-gauge-high"></i>
        <h6 data-i18n="help.card.dashboard">Dashboard</h6>
    </div>
</div>
<div class="col-6 col-md-4 col-lg" data-target="section-ai-assistant">
    <div class="help-card" onclick="scrollToSection('section-ai-assistant')" role="button" tabindex="0">
        <i class="fas fa-robot"></i>
        <h6 data-i18n="help.card.aiAssistant">AI Assistant</h6>
    </div>
</div>
<div class="col-6 col-md-4 col-lg" data-target="section-portfolio-explore">
    <div class="help-card" onclick="scrollToSection('section-portfolio-explore')" role="button" tabindex="0">
        <i class="fas fa-compass"></i>
        <h6 data-i18n="help.card.portfolio">Portfolio & Explore</h6>
    </div>
</div>
<div class="col-6 col-md-4 col-lg" data-target="section-network">
    <div class="help-card" onclick="scrollToSection('section-network')" role="button" tabindex="0">
        <i class="fas fa-network-wired"></i>
        <h6 data-i18n="help.card.network">Network & Social</h6>
    </div>
</div>
```

- [ ] **Step 2: Verify cards render correctly**

Open help.html in browser and confirm 14 category cards are visible (10 original + 4 new).

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): add category cards for Dashboard, AI Assistant, Portfolio, Network"
```

---

### Task 2: Add Sidebar Navigation Links

**Files:**
- Modify: `public/copytradingbroker.io/help.html:342-354` (sidebar scrollspy section)

- [ ] **Step 1: Add 4 new sidebar links after the Security link**

Insert the following HTML after the Security nav-link (line 352) but before the closing `</nav>` tag:

```html
<a class="nav-link" href="#section-dashboard" data-i18n="help.sidebar.dashboard">Dashboard Overview</a>
<a class="nav-link" href="#section-ai-assistant" data-i18n="help.sidebar.aiAssistant">AI Assistant</a>
<a class="nav-link" href="#section-portfolio-explore" data-i18n="help.sidebar.portfolio">Portfolio & Explore</a>
<a class="nav-link" href="#section-network" data-i18n="help.sidebar.network">Network & Social</a>
```

- [ ] **Step 2: Verify sidebar shows all 14 links**

Scroll the sidebar on desktop view and confirm all links are visible.

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): add sidebar links for new help sections"
```

---

### Task 3: Add Dashboard Overview Section Data

**Files:**
- Modify: `public/copytradingbroker.io/help.html:448-703` (helpSections JavaScript array)

- [ ] **Step 1: Add Dashboard section to helpSections array**

Insert the following JavaScript object after the Security section entry (after line 702, before the closing `];`):

```javascript
{
    id: 'section-dashboard',
    title: 'Dashboard Overview',
    icon: 'fa-gauge-high',
    items: [
        {
            q: 'What is the Dashboard?',
            a: '<p>The Dashboard is your central hub after logging into TED Brokers. It provides a comprehensive overview of your account, market data, and quick access to all platform features. The dashboard displays a welcome message with your name, stat boxes showing key metrics, quick action buttons, a real-time market chart, your active investments, and recent activity.</p>'
        },
        {
            q: 'Understanding the Stat Boxes',
            a: '<p>The dashboard displays four key metric boxes at the top:<br><br><strong>Portfolio Value</strong> — The total current value of all your investments and copied trading positions.<br><strong>Active Copies</strong> — The number of Expert Traders you are currently copying.<br><strong>Total Return</strong> — Your overall percentage return on all investments.<br><strong>Wallet Balance</strong> — Your available funds ready for trading or withdrawal. Click "Manage Wallet" to go directly to the Wallet section.</p>'
        },
        {
            q: 'What are Quick Actions?',
            a: '<p>Quick Actions provide one-click access to common tasks:<br><br><strong>Start Robo Advisor</strong> — Navigate directly to Investment Plans to browse and invest in automated strategies.<br><strong>Deposit Funds</strong> — Open the deposit modal to add funds via bank transfer, cryptocurrency, or PayPal.<br><strong>Browse Traders</strong> — View available Expert Traders and their performance metrics to find traders to copy.</p>'
        },
        {
            q: 'How does the Market Overview Chart work?',
            a: '<p>The Market Overview Chart is powered by TradingView and displays real-time market data. You can interact with the chart to view different timeframes, add technical indicators (such as SMA), and change the trading symbol. The chart updates automatically to show current market conditions, helping you make informed decisions about your investments.</p>'
        },
        {
            q: 'What is Recent Activity?',
            a: '<p>The Recent Activity section displays your latest trading actions, including copy trades executed, deposits made, withdrawals processed, and investment changes. This helps you track what has happened with your account. When there is no activity, a message will indicate that you can start copy trading to see activity here.</p>'
        },
        {
            q: 'How do Notifications work?',
            a: '<p>Notifications appear at the top of the dashboard to alert you about important account events. There are four types:<br><br><strong>Info (blue)</strong> — General information about your account or platform updates.<br><strong>Success (green)</strong> — Confirmation of completed actions like successful deposits.<br><strong>Warning (orange)</strong> — Attention needed, such as pending verifications.<br><strong>Error (red)</strong> — Issues requiring immediate action, like failed transactions.<br><br>Each notification can be dismissed by clicking the X button.</p>'
        }
    ]
},
```

- [ ] **Step 2: Verify Dashboard section renders**

Open help.html, click the Dashboard category card, and confirm the accordion section appears with 6 questions.

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): add Dashboard Overview section content"
```

---

### Task 4: Add AI Assistant Section Data

**Files:**
- Modify: `public/copytradingbroker.io/help.html` (helpSections JavaScript array)

- [ ] **Step 1: Add AI Assistant section to helpSections array**

Insert the following JavaScript object after the Dashboard section entry:

```javascript
{
    id: 'section-ai-assistant',
    title: 'AI Assistant (TED AI)',
    icon: 'fa-robot',
    items: [
        {
            q: 'What is TED AI?',
            a: '<p>TED AI is an AI-powered chat assistant built into the TED Brokers dashboard. Located in the left panel, it provides instant platform guidance, account help, and trading tips. TED AI is available 24/7 and can answer questions about features, help you navigate the platform, and provide general trading education.</p>'
        },
        {
            q: 'How do I access TED AI?',
            a: '<p>TED AI is located in the left panel of the dashboard. On desktop, the panel is always visible. To expand or collapse it, click the chevron toggle button at the top of the panel. On mobile devices, the panel is hidden by default — tap the menu icon to access it. Type your message in the input field at the bottom of the panel and press Enter or click the send button.</p>'
        },
        {
            q: 'What can TED AI help with?',
            a: '<p>TED AI can assist with:<br><br><strong>Platform Navigation</strong> — Explaining where to find features and how to use them.<br><strong>Account Setup</strong> — Guidance on profile configuration, security settings, and verification.<br><strong>Investment Guidance</strong> — Helping you understand different investment plans and strategies.<br><strong>Troubleshooting</strong> — Solving common issues with deposits, withdrawals, or account access.<br><strong>Trading Education</strong> — General explanations of copy trading, market concepts, and risk management.</p>'
        },
        {
            q: 'What are the conversation features?',
            a: '<p>TED AI provides a seamless chat experience:<br><br><strong>Color-coded Messages</strong> — Your messages appear in red, AI responses in dark gray for easy distinction.<br><strong>Typing Indicator</strong> — Animated dots show when TED AI is processing your request.<br><strong>Session History</strong> — Your conversation is maintained during the session, so you can scroll back through previous messages.<br><strong>Real-time Responses</strong> — Get instant answers without leaving the dashboard.</p>'
        },
        {
            q: 'Tips for using TED AI effectively',
            a: '<p>For the best experience with TED AI:<br><br><strong>Be Specific</strong> — Ask direct questions like "How do I deposit funds?" rather than vague queries.<br><strong>Follow Up</strong> — If an answer needs clarification, ask follow-up questions.<br><strong>Quick Guidance</strong> — Use TED AI for platform navigation and feature explanations.<br><strong>Account Issues</strong> — For sensitive account matters, also contact human support via the chat widget for additional security.<br><strong>Learning</strong> — Ask TED AI to explain trading concepts you encounter on the platform.</p>'
        }
    ]
},
```

- [ ] **Step 2: Verify AI Assistant section renders**

Click the AI Assistant category card and confirm the accordion section appears with 5 questions.

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): add AI Assistant (TED AI) section content"
```

---

### Task 5: Add Portfolio & Explore Section Data

**Files:**
- Modify: `public/copytradingbroker.io/help.html` (helpSections JavaScript array)

- [ ] **Step 1: Add Portfolio & Explore section to helpSections array**

Insert the following JavaScript object after the AI Assistant section entry:

```javascript
{
    id: 'section-portfolio-explore',
    title: 'Portfolio & Explore',
    icon: 'fa-compass',
    items: [
        {
            q: 'What is the Portfolio section?',
            a: '<p>The Portfolio section allows you to track all your investments in one place. Access it via the Portfolio menu in the sidebar. It contains three subsections: Automated Calls (AI-driven trading), Active Copies (traders you\'re copying), and Performance (analytics and returns). This gives you a complete view of your investment activity.</p>'
        },
        {
            q: 'What are Automated Calls?',
            a: '<p>Automated Calls is an AI-driven trading feature that generates trade signals based on market conditions. You can view and manage your automated trade signals, track their performance, and adjust your strategy. This feature helps you participate in markets without manual trading.</p>'
        },
        {
            q: 'How do I view Active Copies?',
            a: '<p>The Active Copies section shows all the Expert Traders you are currently copying. For each trader, you can see individual copy performance, including profit/loss and return percentage. You can stop copying a trader directly from this section by clicking the "Stop Copying" button.</p>'
        },
        {
            q: 'How does Performance Analytics work?',
            a: '<p>Performance Analytics tracks your profit/loss (P&L) across all investments. You can view historical performance charts showing returns over time, analyze returns by different time periods (daily, weekly, monthly), and identify which investments are performing best. This helps you make data-driven decisions about your portfolio.</p>'
        },
        {
            q: 'What is the Robo Advisor?',
            a: '<p>The Robo Advisor (Investment Plans) section displays General Investment Plans available on the platform. Browse plans to view details including minimum investment amount, holding duration, expected returns, and risk level. You can invest directly from this section by selecting a plan and entering your investment amount. Active plan progress is shown with visual indicators tracking your returns.</p>'
        },
        {
            q: 'What is ETF Automation?',
            a: '<p>ETF Automation offers Exchange Traded Fund portfolios for diversified investing. Choose from three strategy types based on your risk tolerance:<br><br><strong>Conservative</strong> — Lower risk, steady returns<br><strong>Moderate</strong> — Balanced risk and growth<br><strong>Aggressive</strong> — Higher risk, higher potential returns<br><br>The section includes a TradingView market overview widget showing real-time ETF data.</p>'
        },
        {
            q: 'What is DeFi Automation?',
            a: '<p>DeFi Automation provides Decentralized Finance copy trading strategies. You can copy trades from professional DeFi traders with various risk profiles:<br><br><strong>Conservative</strong> — Lower risk DeFi strategies<br><strong>Moderate</strong> — Balanced DeFi approach<br><strong>Aggressive</strong> — Higher risk, higher reward<br><strong>Balanced</strong> — Mix of strategies<br><br>A cryptocurrency market overview shows current crypto prices and trends.</p>'
        },
        {
            q: 'What is Options Automation?',
            a: '<p>Options Automation offers options trading strategies for different skill levels. Whether you\'re a beginner or expert, you can find suitable options plans. Browse available strategies, view their risk-return profiles, and invest in options that match your goals and experience level.</p>'
        },
        {
            q: 'What is Staking?',
            a: '<p>Staking allows you to earn rewards by locking up your assets for a period of time. View available staking plans with their Annual Percentage Yield (APY) rates. Track your staking rewards as they accumulate. Staking is a way to earn passive income on assets you plan to hold long-term.</p>'
        }
    ]
},
```

- [ ] **Step 2: Verify Portfolio & Explore section renders**

Click the Portfolio & Explore category card and confirm the accordion section appears with 9 questions.

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): add Portfolio & Explore section content"
```

---

### Task 6: Add Network & Social Section Data

**Files:**
- Modify: `public/copytradingbroker.io/help.html` (helpSections JavaScript array)

- [ ] **Step 1: Add Network & Social section to helpSections array**

Insert the following JavaScript object after the Portfolio & Explore section entry (before the closing `];`):

```javascript
{
    id: 'section-network',
    title: 'Network & Social',
    icon: 'fa-network-wired',
    items: [
        {
            q: 'How do I browse Traders?',
            a: '<p>The Traders section displays all available Expert Traders on the platform. For each trader, you can view key performance metrics including Win Rate (percentage of profitable trades), YTD Return (year-to-date returns), Risk Score (1-10 risk rating), and number of Copiers. Click on a trader to view their full profile, strategy description, and recent trades. Select "Copy" to start mirroring their trades.</p>'
        },
        {
            q: 'What are Recent Trades?',
            a: '<p>The Recent Trades section shows the latest trading activity across the platform. You can see what other traders are doing in real-time, including which assets they\'re trading, their position sizes, and whether they\'re going long or short. This helps you identify market trends and discover new trading opportunities.</p>'
        },
        {
            q: 'What are Posts?',
            a: '<p>Posts are community updates shared by Expert Traders and the TED Brokers team. Traders can share market insights, trading strategies, and commentary on current market conditions. This social feature helps you stay informed about market trends and learn from experienced traders\' perspectives.</p>'
        },
        {
            q: 'How do I use Search?',
            a: '<p>The Search bar is located in the top app bar. Click on it and type to find features, pages, and content quickly. Results appear in a dropdown as you type. You can search for specific features like "deposit", "traders", or "settings" to navigate directly to the relevant section. This saves time when looking for specific functionality.</p>'
        },
        {
            q: 'How do I enable Dark Mode?',
            a: '<p>Dark Mode reduces eye strain and provides a sleek alternative interface. To toggle Dark Mode, click the sun/moon icon in the app bar. Your preference is saved automatically and will be remembered for future sessions. The dark theme changes the dashboard background, cards, and text colors while maintaining readability.</p>'
        },
        {
            q: 'How do I change the language?',
            a: '<p>TED Brokers supports 10 languages. To switch languages, click the flag icon in the app bar to open the language selector. Choose from:<br><br>English, Chinese (中文), Hindi (हिन्दी), Spanish (Español), French (Français), Arabic (العربية), Bengali (বাংলা), Russian (Русский), Portuguese (Português), German (Deutsch)<br><br>Your language preference is saved and applies across the entire platform.</p>'
        }
    ]
}
```

- [ ] **Step 2: Verify Network & Social section renders**

Click the Network & Social category card and confirm the accordion section appears with 6 questions.

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): add Network & Social section content"
```

---

### Task 7: Final Verification and Testing

**Files:**
- Verify: `public/copytradingbroker.io/help.html`

- [ ] **Step 1: Test all accordion sections**

Open help.html in a browser and verify:
- All 14 category cards are visible and clickable
- Each card scrolls to the correct section
- All accordion items open and close correctly
- Search functionality works with new content

- [ ] **Step 2: Test sidebar navigation**

On desktop view:
- All 14 sidebar links are visible
- Clicking a link scrolls to the correct section
- Scrollspy highlights the correct section as you scroll

- [ ] **Step 3: Test responsive layout**

- Mobile: Category cards display in 2-column grid
- Tablet: Category cards display in 3-column grid
- Desktop: Sidebar is visible, category cards in 4+ columns
- All accordion items work on mobile

- [ ] **Step 4: Test search functionality**

Type in the search box and verify:
- "Dashboard" shows Dashboard section results
- "AI" shows AI Assistant results
- "Portfolio" shows Portfolio & Explore results
- "Traders" shows Network & Social results

- [ ] **Step 5: Final commit**

```bash
git add public/copytradingbroker.io/help.html
git commit -m "feat(help): complete help page enhancement with 4 new sections"
```
