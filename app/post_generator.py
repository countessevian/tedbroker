import random
from datetime import datetime, timedelta
from bson import ObjectId


class PostGenerator:
    def __init__(self):
        self.sentiments = {
            "bullish": {
                "templates": [
                    "Just closed a profitable position on {asset}! {detail}",
                    "Strong {asset} momentum today. {detail}",
                    "Great entry point on {asset}. {detail}",
                    "{asset} breaking out! {detail}",
                    "Bullish signal on {asset}. {detail}",
                    "Just added more {asset} to my portfolio. {detail}",
                    "{asset} showing incredible strength. {detail}",
                    "Excellent results from my {asset} position today. {detail}",
                    "{asset} to the moon! {detail}",
                    "My {asset} play is paying off big time. {detail}",
                ],
                "details": [
                    "Looking at further upside potential.",
                    "Patience always pays off.",
                    "This is just the beginning.",
                    "Trust the process.",
                    "Another win for the strategy.",
                    "Consistency is key to success.",
                    "Stay focused, stay profitable.",
                    "The trend is your friend.",
                    "Momentum is on our side.",
                    "Great risk-reward opportunity here.",
                ]
            },
            "bearish": {
                "templates": [
                    "Taking profits on {asset} before the correction. {detail}",
                    "Warning sign on {asset}. {detail}",
                    "Scaling out of {asset} position. {detail}",
                    "{asset} looking weak today. {detail}",
                    "Protecting gains on {asset}. {detail}",
                    "Short opportunity on {asset}. {detail}",
                    "Red flag on {asset}. {detail}",
                    "Exiting {asset} before it drops further. {detail}",
                    "{asset} losing steam. {detail}",
                    "Time to be cautious with {asset}. {detail}",
                ],
                "details": [
                    "Better safe than sorry.",
                    "Lock in profits and move on.",
                    "Risk management first.",
                    "Don't let gains turn into losses.",
                    "Taking a step back to reassess.",
                    "Preserving capital matters.",
                    "Wait for better entry points.",
                    "The market will provide another chance.",
                    "Stay disciplined.",
                    "Smart traders know when to exit.",
                ]
            },
            "neutral": {
                "templates": [
                    "Watching {asset} closely today. {detail}",
                    "Waiting for confirmation on {asset}. {detail}",
                    "{asset} in consolidation phase. {detail}",
                    "Analyzing {asset} for next move. {detail}",
                    "Holding {asset} for now. {detail}",
                    "No immediate action on {asset}. {detail}",
                    "Keeping an eye on {asset}. {detail}",
                    "{asset} in a holding pattern. {detail}",
                    "Monitoring {asset} support levels. {detail}",
                    "Standing by on {asset} decisions. {detail}",
                ],
                "details": [
                    "Patience is my greatest asset.",
                    "The market will show me the way.",
                    "Trading is a waiting game.",
                    "Don't force trades, wait for setup.",
                    "Clarity comes with time.",
                    "Stay observant, stay ready.",
                    "Good things come to those who wait.",
                    "Sometimes doing nothing is the move.",
                    "A watched pot never boils, but it doesn't burn either.",
                    "The best trade is the one you don't take.",
                ]
            },
            "excited": {
                "templates": [
                    "Huge breakout on {asset}! {detail}",
                    "Incredible move on {asset} today! {detail}",
                    "Just caught an amazing {asset} signal! {detail}",
                    "{asset} is on fire! {detail}",
                    "Couldn't ask for better {asset} action! {detail}",
                    "Insane {asset} momentum right now! {detail}",
                    "What a day for {asset}! {detail}",
                    "Explosive {asset} move! {detail}",
                    "Riding the {asset} wave today! {detail}",
                    "{asset} making new highs! {detail}",
                ],
                "details": [
                    "This is what trading is all about!",
                    "Always trust your analysis!",
                    "The setup worked perfectly!",
                    "Capitalizing on the opportunity!",
                    "Making moves while others watch!",
                    "Living for these moments!",
                    "Sticking to the plan pays off!",
                    "When opportunity knocks, answer!",
                    "This is why I love trading!",
                    "Momentum trading at its finest!",
                ]
            },
            "cautious": {
                "templates": [
                    "Taking it slow with {asset}. {detail}",
                    "Being careful with {asset} position. {detail}",
                    "Want to see more confirmation on {asset}. {detail}",
                    "Not rushing into {asset} yet. {detail}",
                    "Small position on {asset} for now. {detail}",
                    "Waiting for better timing on {asset}. {detail}",
                    "Stay cautious with {asset}. {detail}",
                    "Managing risk on {asset}. {detail}",
                    "Measuring my steps with {asset}. {detail}",
                    "Keeping {asset} position size small. {detail}",
                ],
                "details": [
                    "Slow and steady wins the race.",
                    "Never bet more than you can afford to lose.",
                    "The market will always have opportunities.",
                    "Preserve capital for better days.",
                    "Better to be early than wrong.",
                    "Size matters more than direction.",
                    "Risk management above all else.",
                    "Stay humble, stay careful.",
                    "Don't rush perfection.",
                    "Quality over quantity in trades.",
                ]
            },
            "reflective": {
                "templates": [
                    "Another day of learning with {asset}. {detail}",
                    "Reflecting on my {asset} trade today. {detail}",
                    "What I learned from {asset} today. {detail}",
                    "Journaling my {asset} positions. {detail}",
                    "Reviewing the {asset} setup. {detail}",
                    "Lessons from today's {asset} action. {detail}",
                    "Thinking about my {asset} strategy. {detail}",
                    "Self-reflection improves trading. {detail}",
                    "Analyzing what worked with {asset}. {detail}",
                    "成长的代价是交易的一部分。",
                ],
                "details": [
                    "Every trade is a learning opportunity.",
                    "Improvement is a continuous journey.",
                    "Trading is 90% mental.",
                    "Keep a trading journal, it helps.",
                    "Reflect to perfect.",
                    "Knowledge compounds over time.",
                    "Yesterday's mistake is tomorrow's lesson.",
                    "Stay student, stay humble.",
                    "The market teaches if you listen.",
                    "Self-awareness is key to success.",
                ]
            },
            "motivational": {
                "templates": [
                    "Remember: {detail}",
                    "Trading tip: {detail}",
                    "Always remember: {detail}",
                    "My trading philosophy: {detail}",
                    "Key lesson: {detail}",
                    "Don't forget: {detail}",
                    "Wisdom for the day: {detail}",
                    "Keep this in mind: {detail}",
                    "Reminder to myself: {detail}",
                    "Core belief: {detail}",
                ],
                "details": [
                    "Risk management is everything.",
                    "Never risk more than 2% on a single trade.",
                    "Plan your trade, trade your plan.",
                    "The trend is your friend until it bends.",
                    "Trade the signal, not the opinion.",
                    "Patience is a trader's best weapon.",
                    "Cut losses short, let profits run.",
                    "Consistency beats intensity.",
                    "Respect the market, it knows more than you.",
                    "Emotions are the enemy of profit.",
                ]
            },
            "humorous": {
                "templates": [
                    "My {asset} trade: {detail}",
                    "When you YOLO on {asset}... {detail}",
                    "{asset} has entered the chat. {detail}",
                    "Plot twist: {detail}",
                    "Me trying to time {asset}: {detail}",
                    "Trading {asset} be like: {detail}",
                    "Lowkey obsessed with {asset}. {detail}",
                    "If {asset} was a person... {detail}",
                    "That moment when {asset}: {detail}",
                    "Unpopular opinion about {asset}: {detail}",
                ],
                "details": [
                    "I'm in, we're going to the moon!",
                    "It seemed like a good idea at the time.",
                    "WCGW? (What Could Go Wrong?)",
                    "To the moon! Wait, wrong direction...",
                    "FOMO is a dangerous game.",
                    "HODL! Oh wait, I meant SELL!",
                    "Why did I do that? Oh right, greed.",
                    "Moon emoji. That's my analysis.",
                    "YOLO turned into OYLO (Own Your Loss).",
                    "The more you learn, the more you realize you know nothing.",
                ]
            },
            "news_related": {
                "templates": [
                    "Just heard the news on {asset}. {detail}",
                    "Market moving on {asset} news. {detail}",
                    "Interesting development with {asset}. {detail}",
                    "Reacting to {asset} headlines. {detail}",
                    "{asset} making headlines today. {detail}",
                    "Breaking: {asset} update. {detail}",
                    "What the {asset} news means for traders. {detail}",
                    "Market sentiment shifting on {asset}. {detail}",
                    "{asset} in the spotlight. {detail}",
                    "Latest on {asset}: {detail}",
                ],
                "details": [
                    "News moves markets.",
                    "Trade the news, not the rumor.",
                    "Stay informed, stay ahead.",
                    "Information is power in trading.",
                    "The market reacts faster than you think.",
                    "Buy the rumor, sell the news.",
                    "Knowledge is your edge.",
                    "Read between the lines.",
                    "Not all news is good news.",
                    "Trust but verify.",
                ]
            },
            "community": {
                "templates": [
                    "Thanks for the support on my {asset} call! {detail}",
                    "Community trade idea: {asset}. {detail}",
                    "What's everyone's take on {asset}? {detail}",
                    "Sharing my {asset} analysis with you all. {detail}",
                    "Grateful for this trading community! {detail}",
                    "Let's discuss {asset}. {detail}",
                    "Your thoughts on {asset}? {detail}",
                    "Together we grow: {detail}",
                    "Thank you for following my {asset} signals! {detail}",
                    "This community makes trading better. {detail}",
                ],
                "details": [
                    "Trading is better together.",
                    "Community wins beat individual wins.",
                    "Sharing knowledge multiplies it.",
                    "We all win when we learn together.",
                    "Your support means everything.",
                    "Together we can achieve more.",
                    "Strength in numbers.",
                    "The community is the secret weapon.",
                    "Learn from everyone, teach everyone.",
                    "Collaboration over competition.",
                ]
            }
        }

        self.assets = [
            "BTC", "BTC/USD", "Bitcoin", "Ethereum", "ETH", "Solana", "SOL",
            "Apple", "AAPL", "Tesla", "TSLA", "NVIDIA", "NVDA", "Microsoft", "MSFT",
            "Gold", "XAU/USD", "Silver", "XAG/USD", "EUR/USD", "GBP/USD",
            "USD/JPY", "AUD/USD", "US30", "NAS100", "SPX500",
            "Dogecoin", "DOGE", "Shiba", "Polygon", "MATIC", "Cardano", "ADA",
            "Ripple", "XRP", "Avalanche", "AVAX", "Chainlink", "LINK",
            "Pound", "GBP", "Euro", "EUR", "Oil", "WTI", "天然氣", "天然气的价格"
        ]

        self.trader_names = [
            "Alex", "Jordan", "Casey", "Morgan", "Taylor", "Sam", "Jamie",
            "Riley", "Quinn", "Avery", "Blake", "Cameron", "Drew", "Ellis",
            "Finley", "Harper", "Hayden", "Kai", "Logan", "Parker",
            "Reese", "Rowan", "Skyler", "Spencer", "Sydney"
        ]

    def generate_posts_for_trader(self, trader_name: str, trader_id: str, num_posts: int = 5) -> list:
        """Generate a unique set of posts for a trader"""
        random.seed(f"{trader_id}_{datetime.utcnow().date()}")
        
        posts = []
        used_templates = set()
        
        sentiments = list(self.sentiments.keys())
        random.shuffle(sentiments)
        
        for i in range(num_posts):
            sentiment = sentiments[i % len(sentiments)]
            templates_list = self.sentiments[sentiment]["templates"]
            details_list = self.sentiments[sentiment]["details"]
            
            template_idx = random.randint(0, len(templates_list) - 1)
            while f"{sentiment}_{template_idx}" in used_templates:
                template_idx = (template_idx + 1) % len(templates_list)
            used_templates.add(f"{sentiment}_{template_idx}")
            
            template = templates_list[template_idx]
            detail = random.choice(details_list)
            asset = random.choice(self.assets)
            
            content = template.format(asset=asset, detail=detail)
            
            hours_ago = random.randint(1, 72)
            created_at = datetime.utcnow() - timedelta(hours=hours_ago)
            
            like_users = random.sample(
                [f"user_{j}" for j in range(1, 50)],
                random.randint(0, 15)
            )
            
            posts.append({
                "id": str(ObjectId()),
                "trader_id": trader_id,
                "trader_name": trader_name,
                "content": content,
                "image_url": None,
                "likes": like_users,
                "like_count": len(like_users),
                "created_at": created_at
            })
        
        posts.sort(key=lambda x: x["created_at"], reverse=True)
        return posts

    def generate_all_posts(self) -> list:
        """Generate fresh posts for all traders - call this on each API request"""
        from app.database import get_collection, TRADERS_COLLECTION
        
        traders_collection = get_collection(TRADERS_COLLECTION)
        all_posts = []
        
        today = datetime.utcnow().date()
        
        for trader in traders_collection.find():
            trader_id = str(trader["_id"])
            trader_name = trader.get("full_name", "Unknown Trader")
            
            random.seed(f"{trader_id}_{today}")
            num_posts = random.randint(4, 7)
            
            posts = self.generate_posts_for_trader(
                trader_name=trader_name,
                trader_id=trader_id,
                num_posts=num_posts
            )
            
            all_posts.extend(posts)
        
        all_posts.sort(key=lambda x: x["created_at"], reverse=True)
        return all_posts


post_generator = PostGenerator()