from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tedbroker")

# Global MongoDB client
client = None
db = None


def connect_to_mongo():
    """Connect to MongoDB and return database instance"""
    global client, db
    try:
        client = MongoClient(MONGODB_URL)
        # Test the connection
        client.admin.command('ping')
        db = client[DATABASE_NAME]
        print(f"✓ Successfully connected to MongoDB: {DATABASE_NAME}")
        return db
    except ConnectionFailure as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        raise


def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("✓ MongoDB connection closed")


def get_database():
    """Get database instance"""
    global db
    if db is None:
        db = connect_to_mongo()
    return db


def get_collection(collection_name: str):
    """Get a specific collection from the database"""
    database = get_database()
    return database[collection_name]


# Collection names
USERS_COLLECTION = "users"
TRADERS_COLLECTION = "expert_traders"
INVESTMENT_PLANS_COLLECTION = "investment_plans"
TRANSACTIONS_COLLECTION = "transactions"
DEPOSIT_REQUESTS_COLLECTION = "deposit_requests"
