# Dashboard Header App Bar + Three-Panel Layout Design

## Overview

Redesign the user dashboard layout from a sidebar + content layout to a header app bar + three-panel layout. The existing sidebar menu moves into the header as icon-only items with hover-to-expand text. The old sidebar space becomes an AI chat panel. A new right panel holds help center links. Main content is centered between the two panels.

## Layout

```
+----------------------------------------------------------+
|                    Header App Bar                          |
| [Logo] | [Menu Icons centered] | [Search] [Lang] [Dark]  |
+---------+----------------------------+--------------------+
| AI Chat |      Main Content          | Help Center        |
| Panel   |      (centered, max-width) | Panel              |
| 280px   |      flex: 1               | 260px              |
+---------+----------------------------+--------------------+
```

## Component 1: Header App Bar

### Structure
- Fixed top bar, full viewport width, ~60px height
- `display: flex` row layout
- Left: logo image (180px max-width, same as current)
- Center: menu items, flex-grow, centered via `justify-content: center`
- Right: search bar, language toggle, dark mode toggle, user avatar

### Menu Items
- Rendered as `<a>` tags with icons only (24px), no text labels
- On hover: item smoothly expands horizontally, text label slides in next to icon (CSS `max-width` + `overflow` transition or `transform: scaleX`)
- Active tab has a red bottom-border indicator (#D32F2F)
- Click (no hover needed): opens the tab via existing `data-tab` mechanism
- Parent items (Portfolio, Explore, Network, Account): clicking toggles a dropdown panel below the bar containing the submenu items vertically listed
- Submenu items in dropdown: clicking opens the tab and closes the dropdown
- Logout: stays as a menu item, icon only, red highlight on hover

### DOM Migration
- Menu `<nav class="sidebar-menu">` moves from `<aside class="sidebar">` into `<header class="app-bar">`
- All `data-tab`, `menu-item`, `menu-item-parent`, `submenu-item` classes and attributes preserved
- Existing tab-switching JS keeps working unchanged (selectors still match)
- Submenu dropdown toggles are replaced: instead of expanding inline in sidebar, they open a positioned dropdown below the bar

### Search Bar
- Text input with search icon, placeholder "Search dashboard..."
- On input: queries against tab names, trader names (from loaded data), and visible content
- Results shown in a dropdown below the input, categorized as "Tabs", "Traders", "Content"
- Selecting a result navigates to the relevant tab or loads the trader/content view
- Uses existing `loadExpertTraders()`, `loadPosts()` etc. data when available

### Language & Dark Mode Toggle
- Moved from fixed-position floating elements into the header bar
- Same visual styling, just re-parented into the flex row
- Dark mode toggle: icon-only in the bar (no text label)
- Language selector: compact flag + abbreviation only

## Component 2: Left Panel — AI Chat

### Structure
- Former sidebar div repurposed: `<aside class="sidebar" id="sidebar">` becomes the AI chat panel
- Width: 280px expanded, ~50px collapsed
- Collapsible via existing toggle button — collapsed shows only a chat icon, expanded shows full chat
- On mobile (< 768px): slides in/out via hamburger button (same as current mobile sidebar behavior)

### AI Chat Interface (New — separate spec)
- Chat message area (scrollable, flex-grow)
- Input bar at bottom with text input + send button
- Initially empty with a welcome message
- Connected to an AI chat backend endpoint (separate spec for backend + API contract)

### States
- Empty: "Start a conversation with your AI assistant"
- Loading: typing indicator dots
- Messages: user messages (right-aligned) + AI responses (left-aligned)
- Error: retry button on failed messages

## Component 3: Main Content (Centered)

### Structure
- `<main class="main-content">` remains, positioned between left and right panels
- Margin-left: 280px (when left panel expanded), 50px (when collapsed)
- Margin-right: 260px (when right panel visible)
- Max-width: 900px for readability
- On mobile: full width, no margins

### Tab Content
- All existing `tab-content-wrapper` elements preserved
- Tab switching logic unchanged
- Content renders the same way — only the container sizing changes

## Component 4: Right Panel — Help Center

### Structure
- New `<aside class="help-panel">` element, fixed right side
- Width: 260px
- Contains: help links organized by category
- Hidden on mobile entirely

### Content
- "Getting Started" — onboarding guide, how-it-works links
- "Account" — password reset, 2FA setup, profile management
- "Trading" — copy trading guide, portfolio management
- "Support" — contact form link, FAQ link
- Each link opens the relevant dashboard tab or an external page

## Responsive Behavior

### Desktop (> 1024px)
- Full three-panel layout
- App bar visible
- TradingView ticker below app bar

### Tablet (768px - 1024px)
- Three-panel layout, slightly smaller margins
- Main content max-width adjusts

### Mobile (< 768px)
- App bar: compact (logo + menu hamburger + search icon + lang + dark mode)
- Menu items: hidden behind hamburger, sidebar-style slide-out (same as current mobile menu)
- Left panel (AI chat): hidden, opened via hamburger or a chat FAB
- Right panel (Help Center): completely omitted
- Main content: full width

## Files Changed

| File | Change |
|------|--------|
| `public/.../dashboard.html` | Restructure `<aside>` to `<header>` + left/right panels, new CSS, updated JS handlers |
| `public/.../assets/js/dashboard.js` | Add search logic, AI chat handlers, help panel rendering |
| `app/routes/chat.py` or new | AI chat backend endpoint |

## Implementation Order

1. Restructure HTML: create header app bar, move menu into it, repurpose sidebar as AI chat panel, add help panel
2. Add CSS for app bar, icon hover expansion, submenu dropdowns, three-column layout, responsive
3. Update JS: fix menu click selectors for new DOM locations, add search, add help panel click handlers, add AI chat send/receive
4. Build AI chat backend endpoint
5. Test all menu items still navigate to correct tabs
6. Test responsive breakpoints

## Future Considerations

- AI chat history persistence in MongoDB
- Typing indicators, file attachments in chat
- Search indexing for full-text search across platform
