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
