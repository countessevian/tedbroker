# Mobile AI Chat Tab + User Data Fix — Design Spec

**Date:** 2026-06-26
**Status:** Approved
**Scope:** Mobile menu AI chat tab + user data retrieval fix

## Problems

1. **No TED AI in mobile menu** — Desktop has a "TED AI" chat panel in the left sidebar, but mobile has no way to access it.
2. **User data shows placeholders** — The `populateMobileProfile()` function runs immediately on page load, before `populateDashboard(userData)` fetches real user data from the API. So mobile menu shows "User" and "user@email.com" instead of actual values.

## Solution: 3 Changes

### Change 1: Add "TED AI" menu item

Insert a new menu item in the mobile nav HTML, after the News item and before the footer:

```html
<a class="mobile-nav-item" data-tab="ai-chat">
    <i class="fa-solid fa-robot"></i><span>TED AI</span>
</a>
```

### Change 2: Create AI chat tab content

Add a new `<div class="tab-content-wrapper" id="tab-ai-chat">` inside `<main class="main-content">`. This tab contains:

- **Header**: "TED AI" styled as in desktop (`<span style="color:#D32F2F">TED</span> <span style="color:#ffffff">AI</span>`)
- **Welcome text**: "Start your conversation with TED AI and get the most out of your TED Brokers experience" (italic, muted)
- **Chat messages area**: Same structure as desktop left panel
- **Input area**: Text input + send button

The chat functionality reuses the existing `sendChatMessage()` function — no duplication. The mobile tab creates its own `chat-messages` and `chat-input` elements with different IDs to avoid conflicts with the desktop left panel.

### Change 3: Fix user data retrieval

Update `populateMobileProfile()` to accept a `userData` parameter and be called from `populateDashboard(userData)` in `dashboard.js`. This ensures mobile menu shows real name and email after the API response.

## Files Modified

| File | Change |
|------|--------|
| `dashboard.html` | Add mobile nav menu item, add AI chat tab content, update populateMobileProfile() |
| `dashboard.js` | Call populateMobileProfile(userData) from populateDashboard() |

## Verification

1. Open mobile menu → "TED AI" option visible with robot icon
2. Tap "TED AI" → switches to AI chat tab
3. Chat tab shows "TED AI" header styled as desktop
4. Chat tab shows welcome text
5. Can type message and send → streaming response works
6. Mobile menu shows actual user name and email (not placeholders)
7. Desktop left panel AI chat still works unchanged
