# Help Center Page Design

## Overview

Create a comprehensive single-page Help Center at `/help` for TED Brokers platform. The page follows the same layout as all other public pages (same header/navbar + footer), uses Bootstrap 5 accordion components, and covers all platform features inferred from the dashboard and API endpoints.

## Layout

```
+----------------------------------------------------------+
|                    Header / Navbar                         |
| [Logo] | Home | Company | Resources | Legal | Account     |
+----------------------------------------------------------+
|                                                            |
|  +------------------------------------------------------+ |
|  |           Hero Section (bg-primary-dark #D32F2F)      | |
|  |           "Help Center" title                         | |
|  |           Search bar (JS filter)                      | |
|  +------------------------------------------------------+ |
|                                                            |
|  +----------+  +----------------------------------------+ |
|  | Sidebar  |  | Content Area                           | |
|  | (sticky) |  |                                         | |
|  |          |  | Section 1: Getting Started             | |
|  | 1. Get.. |  |   +-- accordion items (Q&A)           | |
|  | 2. Acc.. |  | Section 2: Account Management         | |
|  | 3. Wal.. |  |   +-- accordion items (Q&A)           | |
|  | 4. With. |  | Section 3: Wallet & Deposits           | |
|  | 5. Copy. |  |   +-- accordion items (Q&A)           | |
|  | 6. Inve. |  | ...                                    | |
|  | 7. Refe. |  |                                         | |
|  | 8. KYC.. |  |                                         | |
|  | 9. Supp. |  |                                         | |
|  | 10. Sec. |  |                                         | |
|  +----------+  +----------------------------------------+ |
|                                                            |
+----------------------------------------------------------+
|                        Footer                              |
+----------------------------------------------------------+
```

### Approach: Category Tab Cards + Accordion Subsections

- **Hero banner**: Red background (#D32F2F), white "Help Center" heading, subtitle, and a search input
- **Category card grid**: Row of 10 icon cards below hero (3-5 per row responsive). Each card shows an icon + category name. Clicking smooth-scrolls to the section.
- **Content below cards**: Two-column layout on desktop (sidebar + content), single column on mobile
- **Sticky sidebar** (desktop only): 10 category links with Bootstrap scrollspy — highlights current section
- **Each section**: Horizontal rule divider + section heading with icon + accordion group of Q&A items

## Content Sections

### 1. Getting Started
- What is TED Brokers?
- How do I create an account?
- How do I log in?
- What is Google OAuth and how do I use it?
- I didn't receive my verification email — what now?
- How does 2FA work during login?

### 2. Account Management
- How do I update my profile?
- How do I change my password?
- How do I change my email address?
- How do I delete my account?
- Viewing my login history

### 3. Wallet & Deposits
- How do I check my wallet balance?
- How do I make a deposit? (Bank transfer, crypto, PayPal)
- What are the minimum/maximum deposit amounts?
- How long do deposits take to process?
- Viewing my transaction history

### 4. Withdrawals
- How do I add a bank account for withdrawal?
- How do I add a crypto address for withdrawal?
- How do I request a withdrawal?
- What is the 2-step verification for withdrawals?
- How long do withdrawals take?

### 5. Copy Trading
- What is copy trading?
- How do I select an expert trader?
- How do I unselect a trader?
- Understanding trader metrics (win rate, YTD return, risk score, drawdown)
- How are trades generated?

### 6. Investment Plans
- What investment plans are available?
- General Investment Plans
- ETF Plans
- DeFi Plans
- Options Plans
- How do I invest in a plan?
- How do I track my portfolio performance?

### 7. Referral Program
- How does the referral program work?
- How do I get my referral link?
- How do I submit a referral code?
- What are the referral bonuses?

### 8. KYC & Verification
- What is KYC and why is it required?
- How do I complete the onboarding wizard?
- What documents do I need to upload?
- Investment questionnaire — what is it?
- How long does KYC verification take?

### 9. Support & Chat
- How do I contact support?
- How does the in-app chat work?
- Checking my message history
- Response times and availability

### 10. Security
- How does 2FA protect my account?
- How are my withdrawals secured?
- Suspicious activity detection
- Tips for keeping my account safe

## Visual Design

### Color Scheme
- Brand red: `#D32F2F` (primary-dark)
- Dark hover: `#B71C1C`
- White backgrounds for content
- Dark footer (existing pattern)

### Typography
- Same as rest of site (using the theme's style.css)

### Icons
- Font Awesome 6 (already loaded site-wide)
- Each category card gets a relevant icon:
  - Getting Started: `fa-rocket`
  - Account Management: `fa-user-cog`
  - Wallet & Deposits: `fa-wallet`
  - Withdrawals: `fa-money-bill-transfer`
  - Copy Trading: `fa-copy`
  - Investment Plans: `fa-chart-line`
  - Referral Program: `fa-share-nodes`
  - KYC & Verification: `fa-id-card`
  - Support & Chat: `fa-headset`
  - Security: `fa-shield-halved`

### Search Bar
- Simple text input in the hero area
- On keyup, filter visible accordion sections by matching text in question/answer
- Uses JavaScript to show/hide accordion items and their parent sections

## Implementation

### File to create
- `public/copytradingbroker.io/help.html` — standalone HTML page

### Route to add (in main.py)
- `GET /help` and `GET /help.html` serving `help.html`

### Dependencies
- Same CSS/JS as all other pages (plugins.css, style.css, custom-theme.css)
- Bootstrap 5 accordion component (already loaded via plugins.js)
- No new external dependencies

### Navigation structure
- 3-column card grid at top for category overview
- Left sidebar with scrollspy (desktop, sticky)
- 10 sections, each with accordion items
- Responsive: sidebar hidden on mobile, replaced by card navigation at top

## Content Writing Approach

Each Q&A answer will be:
- 2-4 sentences for simple topics
- Step-by-step instructions for procedural topics (deposits, withdrawals, KYC)
- Clear, helpful tone — no jargon without explanation
- Consistent with the platform's actual behavior (matches API endpoints and dashboard UI)
