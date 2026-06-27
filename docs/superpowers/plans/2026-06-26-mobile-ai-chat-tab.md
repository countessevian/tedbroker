# Mobile AI Chat Tab + User Data Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a "TED AI" option to the mobile hamburger menu that opens a full-screen AI chat tab, and fix user data retrieval so mobile menu shows real user info.

**Architecture:** A new `tab-ai-chat` content wrapper is added to the main content area. The mobile menu gets a new "TED AI" item linking to this tab. The chat reuses the existing `sendChatMessage()` function with new element IDs to avoid conflicts. User data fix hooks `populateMobileProfile()` into the existing `populateDashboard()` flow.

**Tech Stack:** HTML (inline in dashboard.html), CSS (inline), JavaScript (inline), existing `/api/chat/ai` SSE endpoint

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `public/copytradingbroker.io/dashboard.html` | Modify | Add menu item, chat tab HTML, chat tab CSS |
| `public/copytradingbroker.io/assets/js/dashboard.js` | Modify | Call populateMobileProfile from populateDashboard |

---

### Task 1: Add "TED AI" Menu Item to Mobile Nav

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — mobile nav HTML

- [ ] **Step 1: Locate the mobile nav footer**

Find the line `<div class="mobile-nav-footer">` in the mobile nav HTML. The new TED AI item goes right BEFORE this footer div.

- [ ] **Step 2: Add the TED AI menu item**

Insert the following HTML right before `<div class="mobile-nav-footer">`:

```html
        <a class="mobile-nav-item" data-tab="ai-chat">
            <i class="fa-solid fa-robot"></i><span>TED AI</span>
        </a>
```

- [ ] **Step 3: Verify menu item is present**

Run: `grep -c "data-tab=\"ai-chat\"" public/copytradingbroker.io/dashboard.html`
Expected: 1

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-ai-chat): add TED AI menu item to mobile nav"
```

---

### Task 2: Add AI Chat Tab CSS

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — add CSS in `<style>` block

- [ ] **Step 1: Locate CSS insertion point**

Find the line `/* ======================== */` followed by `/* MOBILE SLIDE-IN NAV      */` in the `<style>` block. The AI chat tab CSS goes right BEFORE this comment.

- [ ] **Step 2: Add AI chat tab CSS**

Insert the following CSS right before the mobile slide-in nav comment:

```css
/* ======================== */
/* MOBILE AI CHAT TAB       */
/* ======================== */
.mobile-chat-tab {
    display: flex;
    flex-direction: column;
    height: calc(100vh - var(--appbar-height));
    background: #2D3748;
}
.mobile-chat-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 16px 20px;
    background: #2D3748;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}
.mobile-chat-header i {
    font-size: 20px;
    color: #cbd5e0;
}
.mobile-chat-header-text {
    font-size: 18px;
    font-weight: 700;
}
.mobile-chat-welcome {
    padding: 20px;
    text-align: center;
}
.mobile-chat-welcome p {
    color: #a0aec0;
    font-size: 13px;
    font-style: italic;
    line-height: 1.5;
}
.mobile-chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.mobile-chat-messages .chat-message {
    max-width: 85%;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
}
.mobile-chat-messages .chat-message.user {
    align-self: flex-end;
    background: linear-gradient(135deg, #D32F2F, #b71c1c);
    color: #fff;
    border-bottom-right-radius: 4px;
}
.mobile-chat-messages .chat-message.ai {
    align-self: flex-start;
    background: rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
    border-bottom-left-radius: 4px;
}
.mobile-chat-messages .chat-message.ai h1,
.mobile-chat-messages .chat-message.ai h2,
.mobile-chat-messages .chat-message.ai h3 {
    color: #fff;
    margin: 8px 0 4px 0;
}
.mobile-chat-messages .chat-message.ai p {
    margin: 4px 0;
}
.mobile-chat-messages .chat-message.ai ul,
.mobile-chat-messages .chat-message.ai ol {
    padding-left: 20px;
    margin: 6px 0;
}
.mobile-chat-messages .chat-message.ai code {
    background: rgba(255, 255, 255, 0.15);
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 12px;
}
.mobile-chat-messages .chat-message.ai pre {
    background: rgba(0, 0, 0, 0.3);
    padding: 8px;
    border-radius: 6px;
    overflow-x: auto;
}
.mobile-chat-messages .chat-message.ai blockquote {
    border-left: 3px solid #D32F2F;
    padding-left: 10px;
    color: #a0aec0;
}
.mobile-chat-messages .streaming-cursor {
    display: inline-block;
    width: 6px;
    height: 14px;
    background: #D32F2F;
    border-radius: 2px;
    margin-left: 2px;
    vertical-align: text-bottom;
    animation: cursorBlink 0.8s step-end infinite;
}
.mobile-chat-input-area {
    display: flex;
    gap: 8px;
    padding: 12px 16px;
    background: #2D3748;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}
.mobile-chat-input-area input {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
    color: #fff;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}
.mobile-chat-input-area input:focus {
    border-color: #D32F2F;
}
.mobile-chat-input-area input::placeholder {
    color: #718096;
}
.mobile-chat-input-area button {
    background: #D32F2F;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    color: #fff;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 16px;
}
.mobile-chat-input-area button:hover {
    background: #b71c1c;
}
```

- [ ] **Step 3: Verify CSS is present**

Run: `grep -c "mobile-chat-tab" public/copytradingbroker.io/dashboard.html`
Expected: >= 5

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-ai-chat): add AI chat tab CSS styles"
```

---

### Task 3: Add AI Chat Tab HTML

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — add tab content wrapper

- [ ] **Step 1: Locate insertion point**

Find the last `</div>` closing the `tab-news` tab content wrapper, right before the closing `</main>` tag. The new AI chat tab goes right AFTER the last tab wrapper and BEFORE `</main>`.

- [ ] **Step 2: Add the AI chat tab HTML**

Insert the following HTML right before `</main>`:

```html
            <!-- AI Chat Tab (Mobile) -->
            <div class="tab-content-wrapper" id="tab-ai-chat">
                <div class="mobile-chat-tab">
                    <div class="mobile-chat-header">
                        <i class="fa-solid fa-robot"></i>
                        <span class="mobile-chat-header-text"><span style="color: #D32F2F; font-family: 'Helvetica Neue', Helvetica, sans-serif; font-weight: 900;">TED</span> <span style="color: #ffffff;">AI</span></span>
                    </div>
                    <div class="mobile-chat-messages" id="mobile-chat-messages">
                        <div class="mobile-chat-welcome">
                            <p>Start your conversation with TED AI and get the most out of your TED Brokers experience</p>
                        </div>
                    </div>
                    <div class="mobile-chat-input-area">
                        <input type="text" id="mobile-chat-input" placeholder="Type a message..." />
                        <button id="mobile-chat-send-btn"><i class="fa-solid fa-paper-plane"></i></button>
                    </div>
                </div>
            </div>
```

- [ ] **Step 3: Verify tab is present**

Run: `grep -c "tab-ai-chat" public/copytradingbroker.io/dashboard.html`
Expected: >= 2 (one for the wrapper, one for the ID)

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-ai-chat): add AI chat tab HTML structure"
```

---

### Task 4: Add AI Chat Tab JavaScript

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — add JS in `<script>` block

- [ ] **Step 1: Locate JS insertion point**

Find the line `// === MOBILE SLIDE-IN NAVIGATION ===` in the `<script>` block. The AI chat tab JS goes right AFTER the closing `})();` of the mobile nav IIFE.

- [ ] **Step 2: Add the AI chat tab JavaScript**

Insert the following JS right after the `})();` that closes the mobile nav IIFE:

```javascript
// === MOBILE AI CHAT TAB ===
(function() {
    var mobileChatInput = document.getElementById('mobile-chat-input');
    var mobileChatSendBtn = document.getElementById('mobile-chat-send-btn');
    var mobileChatMessages = document.getElementById('mobile-chat-messages');
    var mobileChatConversationHistory = [];
    var mobileIsStreaming = false;

    if (!mobileChatInput || !mobileChatSendBtn || !mobileChatMessages) return;

    function addMobileChatMessage(text, sender) {
        if (!mobileChatMessages) return;
        var welcome = mobileChatMessages.querySelector('.mobile-chat-welcome');
        if (welcome) welcome.remove();

        var msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ' + sender;

        if (sender === 'ai') {
            msgDiv.innerHTML = renderMarkdown(text);
        } else {
            msgDiv.textContent = text;
        }

        mobileChatMessages.appendChild(msgDiv);
        mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
        return msgDiv;
    }

    function createMobileStreamingMessage() {
        if (!mobileChatMessages) return null;
        var welcome = mobileChatMessages.querySelector('.mobile-chat-welcome');
        if (welcome) welcome.remove();

        var msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message ai streaming';
        msgDiv.innerHTML = '<span class="streaming-cursor"></span>';
        mobileChatMessages.appendChild(msgDiv);
        mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
        return msgDiv;
    }

    function updateMobileStreamingMessage(msgDiv, rawText) {
        if (!msgDiv) return;
        msgDiv.innerHTML = renderMarkdown(rawText) + '<span class="streaming-cursor"></span>';
        mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
    }

    function finalizeMobileStreamingMessage(msgDiv, rawText) {
        if (!msgDiv) return;
        msgDiv.innerHTML = renderMarkdown(rawText);
        msgDiv.classList.remove('streaming');
    }

    function showMobileTypingIndicator() {
        if (!mobileChatMessages) return;
        var typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message ai typing-indicator';
        typingDiv.id = 'mobile-chat-loading';
        typingDiv.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
        mobileChatMessages.appendChild(typingDiv);
        mobileChatMessages.scrollTop = mobileChatMessages.scrollHeight;
    }

    function removeMobileTypingIndicator() {
        var el = document.getElementById('mobile-chat-loading');
        if (el) el.remove();
    }

    async function sendMobileChatMessage(text) {
        if (!text.trim() || mobileIsStreaming) return;
        mobileIsStreaming = true;

        addMobileChatMessage(text, 'user');
        mobileChatInput.value = '';

        mobileChatConversationHistory.push({ role: 'user', content: text });
        if (mobileChatConversationHistory.length > 10) {
            mobileChatConversationHistory = mobileChatConversationHistory.slice(-10);
        }

        showMobileTypingIndicator();

        try {
            var token = TED_AUTH.getToken();
            var resp = await fetch('/api/chat/ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: JSON.stringify({
                    message: text,
                    conversation_history: mobileChatConversationHistory
                })
            });

            if (!resp.ok) {
                throw new Error('API returned ' + resp.status);
            }

            removeMobileTypingIndicator();
            var streamMsg = createMobileStreamingMessage();
            var fullText = '';

            var reader = resp.body.getReader();
            var decoder = new TextDecoder();
            var buffer = '';

            while (true) {
                var result = await reader.read();
                if (result.done) break;

                buffer += decoder.decode(result.value, { stream: true });
                var lines = buffer.split('\n');
                buffer = lines.pop();

                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (!line.trim()) continue;
                    try {
                        var data = JSON.parse(line);
                        if (data.token) {
                            fullText += data.token;
                            await new Promise(function(r) { requestAnimationFrame(r); });
                            updateMobileStreamingMessage(streamMsg, fullText);
                        }
                        if (data.done) {
                            finalizeMobileStreamingMessage(streamMsg, fullText);
                        }
                    } catch (e) {
                        // skip malformed lines
                    }
                }
            }

            if (fullText) {
                finalizeMobileStreamingMessage(streamMsg, fullText);
                mobileChatConversationHistory.push({ role: 'assistant', content: fullText });
            } else {
                finalizeMobileStreamingMessage(streamMsg, 'I received your message. How can I help?');
            }

        } catch (e) {
            removeMobileTypingIndicator();
            addMobileChatMessage('Sorry, I had trouble responding. Please try again.', 'ai');
        }

        mobileIsStreaming = false;
    }

    mobileChatSendBtn.addEventListener('click', function() {
        var text = mobileChatInput.value.trim();
        if (text) sendMobileChatMessage(text);
    });

    mobileChatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            var text = this.value.trim();
            if (text) sendMobileChatMessage(text);
        }
    });
})();
```

- [ ] **Step 3: Verify JS is present**

Run: `grep -c "MOBILE AI CHAT TAB" public/copytradingbroker.io/dashboard.html`
Expected: 1

- [ ] **Step 4: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html
git commit -m "feat(mobile-ai-chat): add AI chat tab JavaScript with streaming"
```

---

### Task 5: Fix User Data Retrieval in Mobile Menu

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html` — update populateMobileProfile()
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js` — call populateMobileProfile from populateDashboard

- [ ] **Step 1: Update populateMobileProfile() in dashboard.html**

Find the existing `populateMobileProfile()` function inside the mobile nav IIFE. Replace the entire function with this version that accepts userData:

```javascript
    // Populate user profile from existing DOM or userData parameter
    function populateMobileProfile(userData) {
        var mobileName = document.getElementById('mobile-nav-user-name');
        var mobileEmail = document.getElementById('mobile-nav-user-email');
        var mobileAvatar = document.getElementById('mobile-nav-avatar');

        if (userData) {
            // Use fresh API data
            var displayName = userData.full_name || userData.username || 'User';
            if (mobileName) mobileName.textContent = displayName;
            if (mobileEmail) mobileEmail.textContent = userData.email || '';
            if (mobileAvatar) {
                mobileAvatar.textContent = displayName.charAt(0).toUpperCase() || 'U';
            }
        } else {
            // Fallback: read from DOM elements (may have defaults)
            var userName = document.getElementById('user-display-name');
            var userEmail = document.getElementById('user-email');
            if (userName && mobileName) mobileName.textContent = userName.textContent;
            if (userEmail && mobileEmail) mobileEmail.textContent = userEmail.textContent;
            if (userName && mobileAvatar) {
                var initials = userName.textContent.trim().charAt(0).toUpperCase();
                mobileAvatar.textContent = initials || 'U';
            }
        }
    }
    populateMobileProfile();
```

- [ ] **Step 2: Expose populateMobileProfile globally**

Find the line `window.closeMobileNav = closeMobileNav;` inside the mobile nav IIFE. Add this line right after it:

```javascript
    window.populateMobileProfile = populateMobileProfile;
```

- [ ] **Step 3: Update dashboard.js to call populateMobileProfile**

Open `public/copytradingbroker.io/assets/js/dashboard.js`. Find the `populateDashboard(userData)` function (around line 663). Add the following line right after the line that sets `user-email` (around line 696):

```javascript
    // Update mobile nav profile with real user data
    if (typeof window.populateMobileProfile === 'function') {
        window.populateMobileProfile(userData);
    }
```

- [ ] **Step 4: Verify changes**

Run: `grep -c "populateMobileProfile(userData)" public/copytradingbroker.io/assets/js/dashboard.js`
Expected: 1

Run: `grep -c "window.populateMobileProfile" public/copytradingbroker.io/dashboard.html`
Expected: 1

- [ ] **Step 5: Commit**

```bash
git add public/copytradingbroker.io/dashboard.html public/copytradingbroker.io/assets/js/dashboard.js
git commit -m "fix(mobile-nav): populate mobile menu with real user data from API"
```

---

### Task 6: End-to-End Verification

**Files:**
- Verify: `public/copytradingbroker.io/dashboard.html` served at `http://localhost:8071/dashboard.html`

- [ ] **Step 1: Server is running**

Run: `curl -s http://localhost:8071/dashboard.html | head -5`
Expected: HTML output

- [ ] **Step 2: AI chat menu item present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "data-tab=\"ai-chat\""`
Expected: >= 1

- [ ] **Step 3: AI chat tab present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "tab-ai-chat"`
Expected: >= 2

- [ ] **Step 4: AI chat CSS present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "mobile-chat-tab"`
Expected: >= 5

- [ ] **Step 5: AI chat JS present**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "MOBILE AI CHAT TAB"`
Expected: 1

- [ ] **Step 6: populateMobileProfile accepts userData**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "populateMobileProfile(userData)"`
Expected: 1

- [ ] **Step 7: dashboard.js calls populateMobileProfile**

Run: `grep -c "populateMobileProfile" public/copytradingbroker.io/assets/js/dashboard.js`
Expected: 1

- [ ] **Step 8: Desktop AI chat still exists**

Run: `curl -s http://localhost:8071/dashboard.html | grep -c "left-panel-header"`
Expected: >= 1

- [ ] **Step 9: Final commit (if any remaining changes)**

```bash
git add public/copytradingbroker.io/dashboard.html public/copytradingbroker.io/assets/js/dashboard.js
git commit -m "feat(mobile-ai-chat): complete mobile AI chat tab implementation"
```
