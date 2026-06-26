# Mobile Menu Redesign — Design Spec

**Date:** 2026-06-26
**Status:** Approved
**Scope:** Mobile menu only (≤768px). Desktop menu untouched.

## Problem

The current mobile menu reuses the desktop `<nav class="app-bar-menu">` element. CSS cascade rules at line 3719+ override the mobile `@media` rules at line 2653, causing submenu expansion to fail on mobile. Multiple attempts to fix via `!important` overrides have not resolved the issue reliably.

## Solution

Create a **dedicated mobile slide-in navigation** component (`#mobile-nav`), completely independent of the desktop menu. The desktop `<nav class="app-bar-menu">` is hidden on mobile (`display: none`), and the new mobile nav is shown as a full-screen slide-in panel from the left.

## Approach

**Approach A: Dedicated Mobile Menu Component** — approved.

| Pros | Cons |
|------|------|
| Clean separation — no CSS cascade wars | Some HTML duplication (menu items listed twice) |
| Desktop behavior impossible to break | ~150 lines of new HTML + CSS + JS |
| Easy to maintain and debug | |
| Submenu accordion is self-contained | |

## Menu Structure

| # | Item | Type | Tab Name |
|---|------|------|----------|
| 1 | Overview | Direct link | `dashboard` |
| 2 | Wallet | Direct link | `wallet` |
| 3 | Portfolio | Expandable parent | — |
|   | → Automated Calls | Submenu | `automated-calls` |
|   | → Active Copies | Submenu | `active-copies` |
|   | → Performance | Submenu | `performance` |
| 4 | Explore | Expandable parent | — |
|   | → Robo Advisor | Submenu | `subscription` |
|   | → ETF Automation | Submenu | `etf-plans` |
|   | → DeFi Automation | Submenu | `defi-earnings` |
|   | → Options Automation | Submenu | `options` |
|   | → Staking | Submenu | `staking` |
| 5 | Network | Expandable parent | — |
|   | → Traders | Submenu | `traders` |
|   | → Recent Trades | Submenu | `recent-trades` |
|   | → Posts | Submenu | `posts` |
| 6 | Referrals | Direct link | `referrals` |
| 7 | News | Direct link | `news` |

**Footer (user settings):**

| Item | Tab Name |
|------|----------|
| Personal Details | `account-personal` |
| Security | `account-security` |
| Log Out | Calls `handleLogout()` |

## HTML Structure

New `<div id="mobile-nav">` element placed right after `<header class="app-bar">` closing tag. Contains:

1. **Header** — Logo + close button (X)
2. **Profile** — Avatar, user name, user email (populated from existing DOM)
3. **Nav items** — All 7 menu items with 3 expandable submenus
4. **Footer** — Personal Details, Security, Log Out

Each expandable parent uses `data-submenu="name"`. Submenu items use `data-tab="name"` matching existing tab names.

An overlay `<div id="mobile-nav-overlay">` provides a semi-transparent backdrop.

## CSS Styling

All mobile nav CSS uses `.mobile-nav-*` class prefix. Zero conflict with desktop styles.

**Panel:**
- `position: fixed`, `top: 0`, `left: 0`
- `width: 85vw`, `max-width: 320px`
- `height: 100vh`
- Background: `#1a202c` (matches app bar dark theme)
- Transform: `translateX(-100%)` → `translateX(0)` for slide animation
- `z-index: 1060` (above overlay at `1050`)
- `overscroll-behavior: contain` prevents background scroll

**Overlay:**
- `position: fixed`, `inset: 0`
- Background: `rgba(0, 0, 0, 0.5)`
- `z-index: 1050`

**Items:**
- `padding: 14px 20px`, `gap: 14px`
- Active: left border `3px solid #D32F2F`, red text
- Submenu items indented: `padding-left: 56px`

**Accordion:**
- `max-height: 0` → `max-height: 500px` transition
- Arrow rotates 180deg when expanded

**Footer:**
- Separated by `border-top: 1px solid rgba(255,255,255,0.1)`
- Logout: red text `#ef4444`

## JavaScript Behavior

Self-contained IIFE inside existing `<script>` block. Only runs on mobile.

**Key functions:**
- `closeMobileNav()` — removes `active` class, restores body scroll
- Submenu toggles — click on `.mobile-nav-parent > .mobile-nav-item` toggles `expanded` class
- Tab switching — calls existing `switchToTab(tabName)` function (reuse, no duplication)
- Logout — calls existing `handleLogout()` function
- Profile sync — copies user data from existing DOM elements on page load
- Resize handler — closes mobile nav if window resizes above 768px

**Events handled:**
- Hamburger click → open mobile nav (only on mobile)
- Overlay click → close
- Close button click → close
- Menu item click → switch tab + close
- Submenu parent click → toggle accordion

## What Gets Removed

1. Mobile CSS rules in `@media (max-width: 768px)` block (line ~2653) that targeted `.app-bar-menu`
2. Mobile submenu toggle JS (line ~6484) that targeted `.menu-item-parent` in the desktop menu
3. The hamburger click handler's mobile branch (line ~6444) — replaced by new mobile nav handler

## What Stays Untouched

- Desktop `<nav class="app-bar-menu">` and all its CSS
- Desktop submenu dropdown JS (line ~5974)
- `switchToTab()`, `loadTabData()`, `handleLogout()` — all reused as-is
- Left panel (AI chat) behavior
- App bar layout and styling

## Verification

1. Open `/dashboard.html` on mobile or resize browser to ≤768px
2. Tap hamburger → slide-in menu opens from left
3. Tap Portfolio → expands inline showing Automated Calls, Active Copies, Performance
4. Tap any submenu item → switches to that tab, menu closes
5. Tap Explore → expands showing Robo Advisor, ETF, DeFi, Options, Staking
6. Tap Network → expands showing Traders, Recent Trades, Posts
7. Tap Referrals or News → switches tab, menu closes
8. Tap Personal Details or Security → switches tab, menu closes
9. Tap Log Out → logs out
10. Tap overlay or close button → menu closes
11. Resize to desktop → mobile nav hidden, desktop menu works normally
