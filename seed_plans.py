"""
Seed script to populate the database with investment plans mock data
Run this script to add sample investment plans to the database
"""
from datetime import datetime
import sys
from pymongo import MongoClient
import os

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tedbroker")

# Mock investment plans data
INVESTMENT_PLANS_DATA = [
    {
        "name": "Starter Plan",
        "description": "Perfect for beginners looking to start their investment journey. Low-risk portfolio with steady returns and full liquidity after 6 months.",
        "minimum_investment": 500.0,
        "holding_period_months": 6,
        "expected_return_percent": 8.5,
        "current_subscribers": 1247,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Growth Plan",
        "description": "Balanced risk-reward ratio ideal for intermediate investors. Diversified portfolio across stocks, forex, and commodities with quarterly rebalancing.",
        "minimum_investment": 2000.0,
        "holding_period_months": 12,
        "expected_return_percent": 15.2,
        "current_subscribers": 892,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Premium Plan",
        "description": "High-growth potential for experienced investors. Access to exclusive trading strategies and cryptocurrency portfolios with professional management.",
        "minimum_investment": 5000.0,
        "holding_period_months": 18,
        "expected_return_percent": 24.7,
        "current_subscribers": 534,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Elite Plan",
        "description": "Maximum returns for serious investors. Aggressive trading strategies, leveraged positions, and direct access to expert traders. Priority customer support included.",
        "minimum_investment": 10000.0,
        "holding_period_months": 24,
        "expected_return_percent": 35.3,
        "current_subscribers": 267,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Conservative Plan",
        "description": "Safety-first approach with capital preservation focus. Ideal for risk-averse investors seeking stable returns through bonds and blue-chip stocks.",
        "minimum_investment": 1000.0,
        "holding_period_months": 9,
        "expected_return_percent": 6.8,
        "current_subscribers": 1589,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Crypto Accelerator",
        "description": "Specialized cryptocurrency investment plan. High volatility with potential for exceptional returns. Includes Bitcoin, Ethereum, and altcoin exposure.",
        "minimum_investment": 3000.0,
        "holding_period_months": 15,
        "expected_return_percent": 42.5,
        "current_subscribers": 423,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]


def seed_investment_plans():
    """Seed the database with investment plans data"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        plans_collection = db["investment_plans"]

        # Check if collection already has data
        existing_count = plans_collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️  Collection already contains {existing_count} investment plans.")
            response = input("Do you want to clear existing data and reseed? (yes/no): ")
            if response.lower() == 'yes':
                plans_collection.delete_many({})
                print("✓ Cleared existing investment plans data")
            else:
                print("❌ Seeding cancelled")
                return

        # Insert investment plans data
        result = plans_collection.insert_many(INVESTMENT_PLANS_DATA)
        print(f"✓ Successfully inserted {len(result.inserted_ids)} investment plans")

        # Display inserted plans
        print("\n💰 Investment Plans Added:")
        print("-" * 100)
        for plan in INVESTMENT_PLANS_DATA:
            print(f"• {plan['name']}")
            print(f"  Min Investment: ${plan['minimum_investment']:,.2f} | Holding Period: {plan['holding_period_months']} months")
            print(f"  Expected Return: {plan['expected_return_percent']}% | Subscribers: {plan['current_subscribers']}")
            print(f"  {plan['description'][:80]}...")
            print()

        print("✓ Database seeding completed successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 100)
    print("TED BROKER - Investment Plans Database Seeding")
    print("=" * 100)
    print()
    seed_investment_plans()
