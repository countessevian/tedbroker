# Smartsupp Integration Design

## Overview

Integrate Smartsupp with TED Broker for:
1. **Visitor tracking** — invisible Smartsupp chat widget on all pages notifies the mobile app when someone visits the website
2. **Login alerts** — server-side Smartsupp API sends a notification to a persistent conversation after every successful login, with IP, time, location, browser, and device details

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Browser     │────▶│  Hidden Smartsupp │────▶│  Smartsupp       │
│  (any page)  │     │  JS Widget        │     │  Visitor Tracking │
└─────────────┘     └──────────────────┘     │  (mobile push)    │
                                             └─────────────────┘
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Login flow  │────▶│  smartsupp_      │────▶│  Smartsupp API   │
│  (FastAPI)   │     │  service.py      │     │  → conversation  │
└─────────────┘     └──────────────────┘     │  → mobile push    │
                                             └─────────────────┘
```

## Component 1: Hidden Chat Widget (Visitor Tracking)

### Embed Strategy
- Add Smartsupp loader script to `chat-events.js` (included on every page)
- The widget loads invisibly — no chat button, no bubble, no UI
- Visitor tracking works automatically; Smartsupp mobile app pushes "visitor online" notifications

### Implementation
```javascript
// Added to chat-events.js (loaded on all pages)
(function(w,d,s,o,f,js,fjs){
  w['Smartsupp']=o; w[o]=w[o]||function(){(w[o].q=w[o].q||[]).push(arguments)};
  js=d.createElement(s); fjs=d.getElementsByTagName(s)[0];
  js.id=o; js.src=f; js.async=1; fjs.parentNode.insertBefore(js,fjs);
})(window,document,'script','smartsupp','https://www.smartsuppchat.com/loader.js?key=046eb16e4fcdd1c4985f1a6f93910d3484a02f05');

smartsupp('widget', 'hide'); // Hide the chat UI entirely
```

### Hiding the Widget
- Use `smartsupp('widget', 'hide')` API call to hide the chat button and bubble
- This keeps the visitor tracking active while making the widget invisible

## Component 2: Login Notification Service

### File: `app/smartsupp_service.py`

A Python service that:
1. Creates/manages a persistent "System Alert" contact in Smartsupp
2. Creates a single persistent conversation for login alerts (looked up via `ext_id`)
3. Sends each login notification as a message in this conversation
4. Reopens the conversation if it was closed (conversation is the "contact" sub_type so messages trigger push notifications)

### API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /contacts/find?email=...` | Find existing alert contact |
| `POST /contacts` | Create alert contact (once) |
| `POST /conversations/search` | Find existing alert conversation by `ext_id` |
| `POST /conversations` | Create conversation (once) with `contact_id` and `ext_id` |
| `POST /conversations/{id}/messages` | Send login alert message with `sub_type: "contact"` |
| `PATCH /conversations/{id}/open` | Reopen conversation if closed |

### Message Format (sent as `sub_type: "contact"`)
```
🔐 New Login — Ted Broker
User: user@example.com
Time: 2026-06-20 12:30 UTC
IP: 192.168.1.100
Location: Lagos, Nigeria
Device: Chrome 120 / Windows 10
```

### Data Source
- Uses `LoginHistoryService` methods that already extract: `get_ip_address()`, `get_device_info()`, `get_location_from_ip()`
- Called from the same code blocks that already call `email_service.send_login_notification()`

## Component 3: Integration Points in Auth Flow

### Hook 1 — Login without 2FA (`app/routes/auth.py:204`)
After the successful login record and email notification, add:
```python
try:
    smartsupp_service.send_login_alert(
        email=user["email"],
        username=username,
        ip_address=ip_address,
        device_info=device_info,
        location=location
    )
except Exception as e:
    print(f"Failed to send Smartsupp login alert: {e}")
```

### Hook 2 — Login with 2FA (`app/routes/auth.py:531`)
After 2FA verification, after the email notification (around line 554), add the same call.

## Configuration

### `.env` additions
```
SMARTSUPP_API_KEY=046eb16e4fcdd1c4985f1a6f93910d3484a02f05
SMARTSUPP_ALERT_EMAIL=login-alerts@tedbroker.com
```

The API key is used both as the widget key and the Bearer token for REST API calls.

## Files Changed

| File | Change |
|------|--------|
| `app/smartsupp_service.py` | **New** — Smartsupp API client for login notifications |
| `app/routes/auth.py` | Add smartsupp_service call after successful login (2 locations) |
| `public/.../assets/js/chat-events.js` | Add hidden Smartsupp widget loader |
| `.env.example` | Add SMARTSUPP_API_KEY and SMARTSUPP_ALERT_EMAIL |
| `.env` | Add SMARTSUPP_API_KEY (user's existing env) |

## Error Handling

- All Smartsupp API failures are caught and logged (non-blocking)
- Initial contact/conversation creation failures print warnings but don't crash the app
- If the persistent conversation is not found, a new one is created
- HTTP errors from Smartsupp API are caught with try/except

## Testing

1. Load any page on the site — verify Smartsupp widget loads but is invisible (check DevTools Network tab for `loader.js`)
2. Check Smartsupp mobile app — verify "visitor online" notification appears
3. Log in without 2FA — verify Smartsupp conversation receives the login message
4. Log in with 2FA — verify same
5. Verify login details (IP, location, browser, device) are accurate in the message

## Future Considerations

- If the persistent conversation grows too long, implement periodic archival + fresh conversation creation
- Smartsupp API rate limit is 1000 requests/hour — this integration uses ~1 request per login (message send), well within limits
- Contact and conversation IDs could be cached in a config file to avoid API lookups on every startup
