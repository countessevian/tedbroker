# Network Menu & Trader Posts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace 'traders' sidebar menu with 'network' dropdown containing Traders, Recent Trades, and Posts tabs. Implement posts data field for traders with like functionality.

**Architecture:** Backend adds posts data model to traders. Frontend creates new tab content sections for Recent Trades and Posts with 2-column grid layout.

**Tech Stack:** FastAPI/MongoDB backend, Vanilla JS frontend, SweetAlert2 for modals

---

## Task 1: Update Backend Schemas

**Files:**
- Modify: `app/schemas.py`
- Modify: `app/routes/traders.py`
- Test: Manual API test

- [ ] **Step 1: Add Post and TraderPost schemas to schemas.py**

Add after line 168 (after RecentTrade class):

```python
class PostLike(BaseModel):
    """Schema for a post like"""
    user_id: str = Field(..., description="User ID who liked the post")
    liked_at: datetime = Field(default_factory=datetime.utcnow, description="When the like was added")

class TraderPost(BaseModel):
    """Schema for a trader post"""
    id: str = Field(default_factory=lambda: str(ObjectId()), description="Unique post ID")
    trader_id: str = Field(..., description="ID of the trader who created the post")
    content: str = Field(..., description="Post content/text")
    image_url: Optional[str] = Field(None, description="Optional post image URL")
    likes: List[str] = Field(default=[], description="List of user IDs who liked this post")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Post creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Post update timestamp")
```

- [ ] **Step 2: Update ExpertTrader and ExpertTraderResponse schemas**

In `app/schemas.py` around lines 171-209:
- Add `posts: List[TraderPost] = Field(default=[], description="Trader's posts")` to both ExpertTrader and ExpertTraderResponse

- [ ] **Step 3: Update trader_helper in traders.py**

In `app/routes/traders.py` around line 13-30:
- Add `"posts": trader.get("posts", [])` to trader_helper function return dict

- [ ] **Step 4: Add API endpoints for posts**

Add to `app/routes/traders.py`:

```python
@router.get("/posts")
async def get_all_posts(current_user: dict = Depends(get_current_user_token)):
    """Get all posts from all traders"""
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        all_posts = []
        
        for trader in traders_collection.find():
            posts = trader.get("posts", [])
            for post in posts:
                all_posts.append({
                    "id": post.get("id", ""),
                    "trader_id": str(trader["_id"]),
                    "trader_name": trader["full_name"],
                    "trader_photo": trader.get("profile_photo", ""),
                    "content": post.get("content", ""),
                    "image_url": post.get("image_url"),
                    "likes": post.get("likes", []),
                    "like_count": len(post.get("likes", [])),
                    "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
                })
        
        all_posts.sort(key=lambda x: x["created_at"] or "", reverse=True)
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving posts: {str(e)}")

@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user_token)):
    """Like or unlike a post"""
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        users_collection = get_collection(USERS_COLLECTION)
        user_id = current_user["user_id"]
        
        found = False
        for trader in traders_collection.find():
            posts = trader.get("posts", [])
            for i, post in enumerate(posts):
                if post.get("id") == post_id:
                    found = True
                    likes = post.get("likes", [])
                    
                    if user_id in likes:
                        likes.remove(user_id)
                        action = "unliked"
                    else:
                        likes.append(user_id)
                        action = "liked"
                    
                    traders_collection.update_one(
                        {"_id": trader["_id"], "posts.id": post_id},
                        {"$set": {"posts.$.likes": likes}}
                    )
                    
                    return {
                        "success": True,
                        "action": action,
                        "post_id": post_id,
                        "like_count": len(likes)
                    }
        
        if not found:
            raise HTTPException(status_code=404, detail="Post not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error liking post: {str(e)}")
```

- [ ] **Step 5: Test API endpoints**

Run: Test with curl or Postman:
- `GET /api/traders/posts` - should return empty array initially
- `POST /api/traders/posts/{post_id}/like` - should toggle like

---

## Task 2: Create Seed Script for Posts

**Files:**
- Create: `seed_trader_posts.py`

- [ ] **Step 1: Create seed_trader_posts.py**

```python
"""
Seed script to populate traders with sample posts
"""
from datetime import datetime, timedelta
import random
from pymongo import MongoClient
import os
from bson import ObjectId

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tedbroker")

SAMPLE_POSTS = [
    {
        "content": "Just closed a profitable position on BTC! Strong support at $42k holding. Looking bullish for the week ahead.",
        "image_url": None
    },
    {
        "content": "Market analysis: USD/JPY approaching key resistance at 150. Watch for rejection or breakout.",
        "image_url": None
    },
    {
        "content": "Great day for tech stocks! NVDA and AMD leading the rally. Position sizing is key to managing risk.",
        "image_url": None
    },
    {
        "content": "Remember: Risk management is everything. Never risk more than 2% on a single trade!",
        "image_url": None
    },
    {
        "content": "New trade signal incoming: Going long on GOLD as safe haven asset. Stop loss set at $2020.",
        "image_url": None
    },
    {
        "content": "Earnings season is here! Added positions in AAPL and MSFT. Blue chips for the win.",
        "image_url": None
    },
    {
        "content": "Patience pays off. Wait for your setup, don't chase price. The market will always present another opportunity.",
        "image_url": None
    },
    {
        "content": "Updated my trading journal today. Reflection is crucial for improvement. What's your review process?",
        "image_url": None
    },
    {
        "content": "Volatility is opportunity. Embrace it, don't fear it. Smart money moves when others panic.",
        "image_url": None
    },
    {
        "content": "Just hit 100 consecutive winning days on my copy trading signals! Thank you to all my followers.",
        "image_url": None
    }
]

def seed_posts():
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    traders = db["expert_traders"]
    
    for trader in traders.find():
        num_posts = random.randint(3, 6)
        selected_posts = random.sample(SAMPLE_POSTS, num_posts)
        
        posts = []
        for i, post_data in enumerate(selected_posts):
            days_ago = i * random.randint(1, 3)
            post = {
                "id": str(ObjectId()),
                "content": post_data["content"],
                "image_url": post_data["image_url"],
                "likes": random.sample([f"user_{j}" for j in range(20)], random.randint(0, 10)),
                "created_at": datetime.utcnow() - timedelta(days=days_ago)
            }
            posts.append(post)
        
        traders.update_one(
            {"_id": trader["_id"]},
            {"$set": {"posts": posts}}
        )
        print(f"Added {len(posts)} posts to {trader['full_name']}")
    
    client.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_posts()
```

- [ ] **Step 2: Run seed script**

Run: `python seed_trader_posts.py`

---

## Task 3: Update Frontend Sidebar

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html:2895-2898`
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js`
- Test: Visual check in browser

- [ ] **Step 1: Replace traders menu item with Network dropdown**

In dashboard.html around line 2895, replace:
```html
<a class="menu-item" data-tab="traders">
    <i class="fa-solid fa-users-line"></i>
    <span data-i18n="nav.traders">Traders</span>
</a>
```

With:
```html
<!-- Network Parent with Submenu -->
<div class="menu-item-parent">
    <a class="menu-item" id="network-menu">
        <i class="fa-solid fa-network-wired"></i>
        <span>Network</span>
        <i class="fa-solid fa-chevron-right submenu-arrow"></i>
    </a>
    <div class="submenu" id="network-submenu">
        <a class="submenu-item" data-tab="traders">
            <i class="fa-solid fa-users-line"></i>
            <span data-i18n="nav.traders">Traders</span>
        </a>
        <a class="submenu-item" data-tab="recent-trades">
            <i class="fa-solid fa-clock-rotate-left"></i>
            <span>Recent Trades</span>
        </a>
        <a class="submenu-item" data-tab="posts">
            <i class="fa-solid fa-newspaper"></i>
            <span>Posts</span>
        </a>
    </div>
</div>
```

- [ ] **Step 2: Add JavaScript for Network dropdown toggle**

In dashboard.html around line 4192 (after accountMenu handler), add:

```javascript
// Network submenu dropdown toggle
const networkMenu = document.getElementById('network-menu');
const networkSubmenu = document.getElementById('network-submenu');
const networkParent = networkMenu.closest('.menu-item-parent');

networkMenu.addEventListener('click', function(e) {
    e.preventDefault();
    networkParent.classList.toggle('expanded');
    networkSubmenu.classList.toggle('expanded');
});
```

- [ ] **Step 3: Add CSS for network dropdown if needed**

In dashboard.html around line 540 (in styles), ensure submenu styling works:
- Verify `.menu-item-parent.expanded .submenu` shows properly
- Add any missing styles

---

## Task 4: Create Recent Trades Tab Content

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html`
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js`

- [ ] **Step 1: Add Recent Trades tab content HTML**

After the traders tab content (around line 3425), add:

```html
<!-- Recent Trades Tab -->
<div class="tab-content-wrapper" id="tab-recent-trades">
    <div class="content-header">
        <h1>Recent Trades</h1>
        <p>Latest trades from all traders in the network</p>
    </div>
    
    <div id="recent-trades-container">
        <p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading recent trades...</p>
    </div>
</div>
```

- [ ] **Step 2: Add loadRecentTrades function to dashboard.js**

Add after loadExpertTraders function (around line 900):

```javascript
let recentTradesCache = null;

async function loadRecentTrades(forceReload = false) {
    if (recentTradesCache && !forceReload) {
        displayRecentTrades(recentTradesCache);
        return;
    }
    
    const container = document.getElementById('recent-trades-container');
    container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading recent trades...</p>';
    
    try {
        const response = await TED_AUTH.apiCall('/api/traders/', {
            method: 'GET'
        });
        
        if (!response.ok) throw new Error('Failed to fetch traders');
        
        const traders = await response.json();
        
        let allTrades = [];
        traders.forEach(trader => {
            const trades = trader.recent_trades || [];
            trades.forEach(trade => {
                allTrades.push({
                    ...trade,
                    trader_id: trader.id,
                    trader_name: trader.full_name,
                    trader_photo: trader.profile_photo
                });
            });
        });
        
        allTrades.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        recentTradesCache = allTrades;
        displayRecentTrades(allTrades);
        
    } catch (error) {
        console.error('Error loading recent trades:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load recent trades.</p>';
    }
}

function displayRecentTrades(trades) {
    const container = document.getElementById('recent-trades-container');
    
    if (trades.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No recent trades available.</p>';
        return;
    }
    
    const tradesHTML = trades.slice(0, 50).map(trade => {
        const sideClass = trade.side === 'long' ? 'long' : 'short';
        const returnColor = trade.side === 'long' ? '#4caf50' : '#f44336';
        
        return `
            <div class="recent-trade-card">
                <div class="recent-trade-header">
                    <div class="recent-trade-trader">
                        ${trade.trader_photo 
                            ? `<img src="${trade.trader_photo}" class="recent-trade-avatar" />`
                            : `<div class="recent-trade-avatar">${trade.trader_name.charAt(0)}</div>`
                        }
                        <span class="recent-trade-trader-name">${trade.trader_name}</span>
                    </div>
                    <span class="recent-trade-time">${formatTimestamp(trade.timestamp)}</span>
                </div>
                <div class="recent-trade-body">
                    <div class="recent-trade-main">
                        <span class="recent-trade-symbol">${trade.symbol}</span>
                        <span class="recent-trade-exchange">${trade.exchange}</span>
                        <span class="recent-trade-side ${sideClass}">${trade.side.toUpperCase()}</span>
                    </div>
                    <div class="recent-trade-details">
                        <div class="recent-trade-detail">
                            <span class="label">Order Type</span>
                            <span class="value">${formatOrderType(trade.order_type)}</span>
                        </div>
                        <div class="recent-trade-detail">
                            <span class="label">Entry</span>
                            <span class="value">$${trade.entry_price?.toLocaleString()}</span>
                        </div>
                        <div class="recent-trade-detail">
                            <span class="label">Notional</span>
                            <span class="value">$${trade.notional_value?.toLocaleString()}</span>
                        </div>
                        <div class="recent-trade-detail">
                            <span class="label">Leverage</span>
                            <span class="value">${trade.leverage}x</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `<div class="recent-trades-grid">${tradesHTML}</div>`;
}

function formatOrderType(orderType) {
    const types = {
        'market': 'Market',
        'limit': 'Limit',
        'stop_loss': 'Stop Loss',
        'take_profit': 'Take Profit'
    };
    return types[orderType] || orderType;
}
```

- [ ] **Step 3: Add CSS for recent trades cards**

Add to dashboard.html styles (around line 750):

```css
.recent-trades-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    padding: 20px;
}

.recent-trade-card {
    background: var(--card-bg, #fff);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.recent-trade-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.recent-trade-trader {
    display: flex;
    align-items: center;
    gap: 8px;
}

.recent-trade-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
}

.recent-trade-trader-name {
    font-weight: 600;
    color: var(--text-primary, #1f2937);
    font-size: 14px;
}

.recent-trade-time {
    color: var(--text-secondary, #6b7280);
    font-size: 12px;
}

.recent-trade-main {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.recent-trade-symbol {
    font-weight: 700;
    font-size: 16px;
    color: var(--text-primary, #1f2937);
}

.recent-trade-exchange {
    color: var(--text-secondary, #6b7280);
    font-size: 12px;
    padding: 2px 8px;
    background: var(--bg-secondary, #f3f4f6);
    border-radius: 4px;
}

.recent-trade-side {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.recent-trade-side.long {
    background: rgba(76, 175, 80, 0.1);
    color: #4caf50;
}

.recent-trade-side.short {
    background: rgba(244, 67, 54, 0.1);
    color: #f44336;
}

.recent-trade-details {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

.recent-trade-detail {
    text-align: center;
}

.recent-trade-detail .label {
    display: block;
    font-size: 10px;
    color: var(--text-secondary, #6b7280);
    text-transform: uppercase;
    margin-bottom: 2px;
}

.recent-trade-detail .value {
    font-weight: 600;
    font-size: 13px;
    color: var(--text-primary, #1f2937);
}
```

- [ ] **Step 4: Hook up Recent Trades tab loading**

In dashboard.html around line 4227, update the submenu click handler to also load data:

```javascript
document.querySelectorAll('.submenu-item[data-tab]').forEach(item => {
    item.addEventListener('click', function() {
        const tabName = this.getAttribute('data-tab');
        
        // ... existing code ...
        
        // Load data for specific tabs
        if (tabName === 'traders') {
            loadExpertTraders(true);
        } else if (tabName === 'recent-trades') {
            loadRecentTrades(true);
        } else if (tabName === 'posts') {
            loadPosts(true);
        }
    });
});
```

---

## Task 5: Create Posts Tab Content

**Files:**
- Modify: `public/copytradingbroker.io/dashboard.html`
- Modify: `public/copytradingbroker.io/assets/js/dashboard.js`

- [ ] **Step 1: Add Posts tab content HTML**

After the recent-trades tab content, add:

```html
<!-- Posts Tab -->
<div class="tab-content-wrapper" id="tab-posts">
    <div class="content-header">
        <h1>Network Posts</h1>
        <p>Latest updates from traders in the network</p>
    </div>
    
    <div id="posts-container">
        <p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading posts...</p>
    </div>
</div>
```

- [ ] **Step 2: Add loadPosts and renderPosts functions to dashboard.js**

Add after loadRecentTrades:

```javascript
let postsCache = null;
let currentUserId = null;

async function loadPosts(forceReload = false) {
    if (postsCache && !forceReload) {
        renderPosts(postsCache);
        return;
    }
    
    const container = document.getElementById('posts-container');
    container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">Loading posts...</p>';
    
    try {
        const [postsResponse, userResponse] = await Promise.all([
            TED_AUTH.apiCall('/api/traders/posts', { method: 'GET' }),
            TED_AUTH.apiCall('/api/auth/me', { method: 'GET' })
        ]);
        
        if (!postsResponse.ok) throw new Error('Failed to fetch posts');
        
        const posts = await postsResponse.json();
        const userData = await userResponse.json();
        currentUserId = userData.id;
        
        postsCache = posts;
        renderPosts(posts);
        
    } catch (error) {
        console.error('Error loading posts:', error);
        container.innerHTML = '<p style="text-align: center; color: #ff6b6b; padding: 40px 0;">Failed to load posts.</p>';
    }
}

function renderPosts(posts) {
    const container = document.getElementById('posts-container');
    
    if (posts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #8b93a7; padding: 40px 0;">No posts available yet.</p>';
        return;
    }
    
    const postsHTML = posts.map(post => {
        const isLiked = currentUserId && post.likes.includes(currentUserId);
        const likeClass = isLiked ? 'liked' : '';
        
        return `
            <div class="post-card">
                <div class="post-header">
                    <div class="post-trader">
                        ${post.trader_photo 
                            ? `<img src="${post.trader_photo}" class="post-avatar" />`
                            : `<div class="post-avatar">${post.trader_name.charAt(0)}</div>`
                        }
                        <div class="post-trader-info">
                            <span class="post-trader-name">${post.trader_name}</span>
                            <span class="post-time">${formatTimestamp(post.created_at)}</span>
                        </div>
                    </div>
                </div>
                <div class="post-content">
                    <p>${post.content}</p>
                    ${post.image_url ? `<img src="${post.image_url}" class="post-image" />` : ''}
                </div>
                <div class="post-actions">
                    <button class="post-like-btn ${likeClass}" onclick="likePost('${post.id}')">
                        <i class="fa-${isLiked ? 'solid' : 'regular'} fa-heart"></i>
                        <span class="like-count">${post.like_count || 0}</span>
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `<div class="posts-grid">${postsHTML}</div>`;
}

async function likePost(postId) {
    try {
        const response = await TED_AUTH.apiCall(`/api/traders/posts/${postId}/like`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to like post');
        }
        
        const result = await response.json();
        
        // Update cache
        if (postsCache) {
            const post = postsCache.find(p => p.id === postId);
            if (post) {
                if (result.action === 'liked') {
                    post.likes.push(currentUserId);
                } else {
                    post.likes = post.likes.filter(id => id !== currentUserId);
                }
                post.like_count = result.like_count;
            }
        }
        
        // Re-render posts
        renderPosts(postsCache);
        
    } catch (error) {
        console.error('Error liking post:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    }
}
```

- [ ] **Step 3: Add CSS for posts grid**

Add to dashboard.html styles:

```css
.posts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    padding: 20px;
}

@media (max-width: 768px) {
    .posts-grid {
        grid-template-columns: 1fr;
    }
}

.post-card {
    background: var(--card-bg, #fff);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.post-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.post-trader {
    display: flex;
    align-items: center;
    gap: 12px;
}

.post-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
    background: linear-gradient(135deg, #D32F2F, #5a9abf);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 18px;
}

.post-trader-info {
    display: flex;
    flex-direction: column;
}

.post-trader-name {
    font-weight: 600;
    color: var(--text-primary, #1f2937);
    font-size: 15px;
}

.post-time {
    color: var(--text-secondary, #6b7280);
    font-size: 12px;
}

.post-content {
    flex: 1;
}

.post-content p {
    margin: 0;
    color: var(--text-primary, #1f2937);
    line-height: 1.6;
    font-size: 14px;
}

.post-image {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
    border-radius: 8px;
    margin-top: 12px;
}

.post-actions {
    display: flex;
    gap: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color, #e5e7eb);
}

.post-like-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-secondary, #6b7280);
    font-size: 14px;
    padding: 8px 12px;
    border-radius: 20px;
    transition: all 0.2s;
}

.post-like-btn:hover {
    background: rgba(244, 67, 54, 0.1);
}

.post-like-btn.liked {
    color: #f44336;
}

.post-like-btn.liked .fa-heart {
    animation: heartPop 0.3s ease;
}

@keyframes heartPop {
    0% { transform: scale(1); }
    50% { transform: scale(1.3); }
    100% { transform: scale(1); }
}
```

- [ ] **Step 4: Export functions to window**

Add to end of dashboard.js:

```javascript
window.loadRecentTrades = loadRecentTrades;
window.loadPosts = loadPosts;
window.likePost = likePost;
```

---

## Task 6: Testing & Verification

- [ ] **Step 1: Verify server is running and restart if needed**

Run: `curl http://localhost:8000/` should return 200

- [ ] **Step 2: Test API endpoints**

- GET /api/traders/posts - should return posts array
- POST /api/traders/posts/{id}/like - should toggle like

- [ ] **Step 3: Visual verification in browser**

1. Login to dashboard
2. Click "Network" in sidebar - dropdown should expand
3. Click "Traders" - should show traders list
4. Click "Recent Trades" - should show all recent trades in card grid
5. Click "Posts" - should show posts in 2-column grid with like buttons
6. Click like button - should toggle like and update count

---

## Summary of Files Modified

1. `app/schemas.py` - Add PostLike, TraderPost schemas, update ExpertTrader
2. `app/routes/traders.py` - Add posts API endpoints, update trader_helper
3. `seed_trader_posts.py` - Create seed script for posts
4. `public/copytradingbroker.io/dashboard.html` - Update sidebar, add tab content, add CSS
5. `public/copytradingbroker.io/assets/js/dashboard.js` - Add loadRecentTrades, loadPosts, likePost functions
