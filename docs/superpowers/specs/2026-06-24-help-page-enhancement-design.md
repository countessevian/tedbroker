# Help Page Enhancement Design

## Overview
Enhance the existing `help.html` page by adding 4 new accordion sections to document the dashboard features, AI assistant, portfolio/explore tools, and network/social features. The page maintains the same layout (header, footer) and accordion pattern as existing sections.

## Current State
The existing help page at `public/copytradingbroker.io/help.html` contains 10 accordion sections:
1. Getting Started
2. Account Management
3. Wallet & Deposits
4. Withdrawals
5. Copy Trading
6. Investment Plans
7. Referral Program
8. KYC & Verification
9. Support & Chat
10. Security

## New Sections to Add

### 1. Dashboard Overview (`section-dashboard`)
**Icon:** `fa-gauge-high`

**Accordion Items:**
- **What is the Dashboard?**
  - Central hub after login showing account overview, market data, and quick actions
  - Displays welcome message with user name
  - Contains stat boxes, quick action buttons, market chart, active investments, and recent activity

- **Understanding the Stat Boxes**
  - Portfolio Value: Total value of all investments and copied positions
  - Active Copies: Number of traders currently being copied
  - Total Return: Overall percentage return on investments
  - Wallet Balance: Available funds for trading or withdrawal, with "Manage Wallet" button

- **Quick Actions**
  - Start Robo Advisor: Navigate to investment plans
  - Deposit Funds: Open deposit modal
  - Browse Traders: View available Expert Traders

- **Market Overview Chart**
  - TradingView integration showing real-time market data
  - Interactive chart with symbol change capability
  - Technical indicators available (SMA, etc.)

- **Recent Activity**
  - Shows latest trading activity, deposits, withdrawals
  - Displays when no activity is available

- **Notifications**
  - Info (blue): General information
  - Success (green): Completed actions
  - Warning (orange): Attention needed
  - Error (red): Issues requiring action
  - Dismissible with X button

### 2. AI Assistant (TED AI) (`section-ai-assistant`)
**Icon:** `fa-robot`

**Accordion Items:**
- **What is TED AI?**
  - AI-powered chat assistant located in the left panel
  - Provides platform guidance, account help, and trading tips
  - Available 24/7 for instant support

- **How to Access TED AI**
  - Click the left panel toggle (chevron icon) to expand/collapse
  - The AI panel is always visible on desktop, hidden on mobile
  - Type messages in the input field at the bottom

- **What Can TED AI Help With?**
  - Platform navigation and feature explanations
  - Account setup and configuration guidance
  - Investment plan recommendations
  - Troubleshooting common issues
  - General trading education

- **Conversation Features**
  - Messages are color-coded: Red for user, dark for AI
  - Typing indicator shows when AI is processing
  - Conversation history maintained during session
  - Scroll through previous messages

- **Tips for Effective Use**
  - Be specific with questions
  - Ask follow-up questions for clarification
  - Use for quick platform guidance
  - For account issues, also contact support via chat widget

### 3. Portfolio & Explore (`section-portfolio-explore`)
**Icon:** `fa-compass`

**Accordion Items:**
- **Portfolio Overview**
  - Track all investments in one place
  - View automated calls, active copies, and performance metrics
  - Access via Portfolio menu in sidebar

- **Automated Calls**
  - AI-driven trading automation
  - View and manage automated trade signals
  - Track performance of automated strategies

- **Active Copies**
  - View all traders you're currently copying
  - See individual copy performance
  - Stop copying traders from this section

- **Performance Analytics**
  - Track profit/loss (P&L) across all investments
  - View historical performance charts
  - Analyze returns by time period

- **Robo Advisor (Investment Plans)**
  - Browse General Investment Plans
  - View plan details: minimum investment, duration, expected returns
  - Invest directly from this section
  - Track active plan progress with visual indicators

- **ETF Automation**
  - Exchange Traded Fund portfolios
  - Choose from Conservative, Moderate, or Aggressive strategies
  - View ETF market overview with TradingView integration
  - Diversified portfolio approach

- **DeFi Automation**
  - Decentralized Finance copy trading
  - Professional DeFi trader strategies
  - Conservative, Moderate, Aggressive, or Balanced options
  - Cryptocurrency market overview

- **Options Automation**
  - Options trading strategies
  - Beginner to expert level strategies
  - View available options plans

- **Staking**
  - Earn rewards by staking assets
  - View staking plans and APY rates
  - Track staking rewards

### 4. Network & Social (`section-network`)
**Icon:** `fa-network-wired`

**Accordion Items:**
- **Traders**
  - Browse available Expert Traders
  - View performance metrics: Win Rate, YTD Return, Risk Score, Copiers
  - Select traders to copy
  - View trader profiles and descriptions

- **Recent Trades**
  - View recent trading activity across the platform
  - See what other traders are doing
  - Track market movements

- **Posts**
  - Community posts from traders
  - Updates, insights, and market commentary
  - Social features for engagement

- **Search Functionality**
  - Use the search bar in the app bar
  - Find features, pages, and content quickly
  - Results appear in dropdown

- **Dark Mode**
  - Toggle between light and dark themes
  - Click the sun/moon icon in the app bar
  - Preference saved for future sessions

- **Language Selector**
  - Switch between 10 supported languages
  - Click the flag icon in the app bar
  - Available: English, Chinese, Hindi, Spanish, French, Arabic, Bengali, Russian, Portuguese, German

## Implementation Details

### Files to Modify
- `public/copytradingbroker.io/help.html`:
  - Add new category cards in the `#helpCategoryCards` section
  - Add new sidebar links in `#helpScrollspy`
  - Add new sections to the `helpSections` JavaScript array
  - Update the sidebar navigation

### Category Cards to Add
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

### Sidebar Links to Add
```html
<a class="nav-link" href="#section-dashboard" data-i18n="help.sidebar.dashboard">Dashboard Overview</a>
<a class="nav-link" href="#section-ai-assistant" data-i18n="help.sidebar.aiAssistant">AI Assistant</a>
<a class="nav-link" href="#section-portfolio-explore" data-i18n="help.sidebar.portfolio">Portfolio & Explore</a>
<a class="nav-link" href="#section-network" data-i18n="help.sidebar.network">Network & Social</a>
```

### JavaScript Data Structure
Add new entries to the `helpSections` array following the existing pattern:
```javascript
{
    id: 'section-dashboard',
    title: 'Dashboard Overview',
    icon: 'fa-gauge-high',
    items: [
        { q: 'Question', a: '<p>Answer HTML</p>' },
        // ...
    ]
}
```

## Styling
- Reuse existing accordion styles (`.accordion-button`, `.accordion-item`)
- Maintain consistent section heading styles with icons
- No new CSS required beyond existing patterns

## Responsive Behavior
- Category cards: 2 columns on mobile, 3 on tablet, 5+ on desktop
- Sidebar: Hidden on mobile, visible on desktop (lg+)
- Accordion: Full-width on all devices

## Accessibility
- Keyboard navigation for accordion items
- ARIA attributes on accordion buttons and panels
- Focus states for interactive elements
- Screen reader friendly content structure

## Testing
- Verify all accordion items open/close correctly
- Test search functionality with new content
- Check sidebar scrollspy updates for new sections
- Validate responsive layout on mobile/tablet/desktop
- Test keyboard navigation
- Verify i18n data attributes are present (even if translations pending)

## Success Criteria
- All 4 new sections added with detailed content
- Category cards visible and clickable
- Sidebar navigation includes new sections
- Search functionality works with new content
- Page maintains same layout as other main pages
- No JavaScript errors
- Responsive on all screen sizes
