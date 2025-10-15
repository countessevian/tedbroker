"""
Seed script to populate the database with expert traders mock data
Run this script to add sample expert traders to the database
"""
from datetime import datetime
import sys
from pymongo import MongoClient
import os

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tedbroker")

# Mock expert traders data
EXPERT_TRADERS_DATA = [
    {
        "full_name": "John Crypto Expert",
        "profile_photo": "https://i.pravatar.cc/150?img=12",
        "description": "Veteran cryptocurrency trader with over 8 years of experience in digital assets. Specializes in swing trading and technical analysis of major cryptocurrencies.",
        "specialization": "Cryptocurrency Trading",
        "ytd_return": 156.5,
        "win_rate": 89.2,
        "copiers": 432,
        "trades": [
            {
                "ticker": "BTCUSD",
                "current_price": 43250.50,
                "position": "bought"
            },
            {
                "ticker": "ETHUSD",
                "current_price": 2280.75,
                "position": "bought"
            },
            {
                "ticker": "BNBUSD",
                "current_price": 315.20,
                "position": "sold"
            },
            {
                "ticker": "SOLUSD",
                "current_price": 98.45,
                "position": "bought"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "full_name": "Sarah Forex Pro",
        "profile_photo": "https://i.pravatar.cc/150?img=45",
        "description": "Professional forex day trader focused on major currency pairs. Uses a combination of fundamental and technical analysis to identify high-probability trades.",
        "specialization": "Forex Day Trading",
        "ytd_return": 98.3,
        "win_rate": 76.5,
        "copiers": 289,
        "trades": [
            {
                "ticker": "EURUSD",
                "current_price": 1.0875,
                "position": "bought"
            },
            {
                "ticker": "GBPUSD",
                "current_price": 1.2650,
                "position": "sold"
            },
            {
                "ticker": "USDJPY",
                "current_price": 148.25,
                "position": "bought"
            },
            {
                "ticker": "AUDUSD",
                "current_price": 0.6580,
                "position": "bought"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "full_name": "Mike Stock Trader",
        "profile_photo": "https://i.pravatar.cc/150?img=33",
        "description": "Long-term stock market investor with a focus on value investing and dividend growth stocks. Strong track record in technology and healthcare sectors.",
        "specialization": "Long-term Stock Market Investor",
        "ytd_return": 67.8,
        "win_rate": 82.1,
        "copiers": 567,
        "trades": [
            {
                "ticker": "AAPL",
                "current_price": 178.50,
                "position": "bought"
            },
            {
                "ticker": "MSFT",
                "current_price": 368.25,
                "position": "bought"
            },
            {
                "ticker": "NVDA",
                "current_price": 495.80,
                "position": "bought"
            },
            {
                "ticker": "TSLA",
                "current_price": 242.15,
                "position": "sold"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "full_name": "Lisa Dividend Queen",
        "profile_photo": "https://i.pravatar.cc/150?img=47",
        "description": "Dividend growth investing specialist with 12+ years experience. Focuses on building sustainable income portfolios with consistent dividend growth.",
        "specialization": "Dividend Growth Investing",
        "ytd_return": 45.2,
        "win_rate": 91.7,
        "copiers": 721,
        "trades": [
            {
                "ticker": "JNJ",
                "current_price": 162.35,
                "position": "bought"
            },
            {
                "ticker": "PG",
                "current_price": 151.90,
                "position": "bought"
            },
            {
                "ticker": "KO",
                "current_price": 58.75,
                "position": "bought"
            },
            {
                "ticker": "PEP",
                "current_price": 169.40,
                "position": "bought"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "full_name": "David Options Master",
        "profile_photo": "https://i.pravatar.cc/150?img=56",
        "description": "Options trading specialist focusing on spreads and volatility strategies. Expert in risk management and theta decay strategies.",
        "specialization": "Options Trading",
        "ytd_return": 112.6,
        "win_rate": 73.8,
        "copiers": 358,
        "trades": [
            {
                "ticker": "SPY",
                "current_price": 445.30,
                "position": "bought"
            },
            {
                "ticker": "QQQ",
                "current_price": 378.65,
                "position": "bought"
            },
            {
                "ticker": "IWM",
                "current_price": 192.80,
                "position": "sold"
            },
            {
                "ticker": "DIA",
                "current_price": 368.90,
                "position": "bought"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "full_name": "Emma Tech Investor",
        "profile_photo": "https://i.pravatar.cc/150?img=48",
        "description": "Technology sector specialist with deep knowledge of software, semiconductors, and cloud computing. Focus on growth stocks with strong fundamentals.",
        "specialization": "Technology Stocks",
        "ytd_return": 134.7,
        "win_rate": 85.3,
        "copiers": 612,
        "trades": [
            {
                "ticker": "GOOGL",
                "current_price": 138.25,
                "position": "bought"
            },
            {
                "ticker": "META",
                "current_price": 352.80,
                "position": "bought"
            },
            {
                "ticker": "AMD",
                "current_price": 118.45,
                "position": "bought"
            },
            {
                "ticker": "INTC",
                "current_price": 42.60,
                "position": "sold"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]


def seed_expert_traders():
    """Seed the database with expert traders data"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        traders_collection = db["expert_traders"]

        # Check if collection already has data
        existing_count = traders_collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️  Collection already contains {existing_count} traders.")
            response = input("Do you want to clear existing data and reseed? (yes/no): ")
            if response.lower() == 'yes':
                traders_collection.delete_many({})
                print("✓ Cleared existing traders data")
            else:
                print("❌ Seeding cancelled")
                return

        # Insert expert traders data
        result = traders_collection.insert_many(EXPERT_TRADERS_DATA)
        print(f"✓ Successfully inserted {len(result.inserted_ids)} expert traders")

        # Display inserted traders
        print("\n📊 Expert Traders Added:")
        print("-" * 80)
        for trader in EXPERT_TRADERS_DATA:
            print(f"• {trader['full_name']} - {trader['specialization']}")
            print(f"  YTD Return: {trader['ytd_return']}% | Win Rate: {trader['win_rate']}% | Copiers: {trader['copiers']}")
            print(f"  Active Trades: {len(trader['trades'])}")
            print()

        print("✓ Database seeding completed successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 80)
    print("TED BROKER - Expert Traders Database Seeding")
    print("=" * 80)
    print()
    seed_expert_traders()
