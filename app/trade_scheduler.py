import random
import asyncio
from datetime import datetime, timedelta
from typing import List
from app.database import get_collection, TRADERS_COLLECTION

SYMBOLS = [
    "BTC/USD", "ETH/USD", "SOL/USD", "XRP/USD", "ADA/USD",
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
    "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META",
    "SPY", "QQQ", "IWM", "DIA",
    "GOLD", "SILVER", "OIL", "NAT GAS"
]

EXCHANGES = [
    "Binance", "Coinbase", "Kraken", "Forex.com", "IG Markets",
    "TD Ameritrade", "Interactive Brokers", "Robinhood", "eToro",
    "OANDA", "FXCM", "ThinkMarkets"
]

ORDER_TYPES = ["market", "limit", "stop_loss", "take_profit"]

def generate_random_trade() -> dict:
    """Generate a single random trade with realistic values"""
    symbol = random.choice(SYMBOLS)
    exchange = random.choice(EXCHANGES)
    side = random.choice(["long", "short"])
    order_type = random.choice(ORDER_TYPES)
    
    if "BTC" in symbol or "ETH" in symbol or "SOL" in symbol:
        entry_price = round(random.uniform(100, 50000), 2)
    elif "XRP" in symbol or "ADA" in symbol:
        entry_price = round(random.uniform(0.1, 10), 4)
    elif "/" in symbol:
        entry_price = round(random.uniform(0.5, 200), 5)
    elif symbol in ["GOLD", "SILVER", "OIL", "NAT GAS"]:
        entry_price = round(random.uniform(10, 5000), 2)
    else:
        entry_price = round(random.uniform(10, 1000), 2)
    
    quantity = round(random.uniform(0.01, 100), 4)
    notional_value = round(entry_price * quantity, 2)
    
    leverage = round(random.choice([1, 1, 2, 3, 5, 10, 20, 50]), 1)
    
    hours_ago = random.uniform(0, 168)
    timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
    
    return {
        "symbol": symbol,
        "exchange": exchange,
        "side": side,
        "order_type": order_type,
        "entry_price": entry_price,
        "notional_value": notional_value,
        "leverage": leverage,
        "timestamp": timestamp.isoformat()
    }

def generate_recent_trades(count: int = 10) -> List[dict]:
    """Generate a list of recent trades sorted by timestamp (newest first)"""
    trades = [generate_random_trade() for _ in range(count)]
    trades.sort(key=lambda x: x["timestamp"], reverse=True)
    return trades

async def update_all_traders_trades():
    """Update recent trades for all traders in the database"""
    traders = get_collection(TRADERS_COLLECTION)
    
    all_traders = list(traders.find())
    
    for trader in all_traders:
        new_trades = generate_recent_trades(10)
        
        traders.update_one(
            {"_id": trader["_id"]},
            {"$set": {"recent_trades": new_trades, "updated_at": datetime.utcnow()}}
        )
    
    print(f"Updated recent trades for {len(all_traders)} traders at {datetime.utcnow()}")

async def run_trade_scheduler():
    """Run the trade scheduler loop"""
    while True:
        hours_until_next = random.randint(1, 5)
        print(f"Next trade update in {hours_until_next} hours")
        
        await asyncio.sleep(hours_until_next * 3600)
        
        await update_all_traders_trades()

async def initialize_traders_trades():
    """Initialize recent trades for traders that don't have them"""
    traders = get_collection(TRADERS_COLLECTION)
    
    traders_without_trades = traders.find({
        "$or": [
            {"recent_trades": {"$exists": False}},
            {"recent_trades": None},
            {"recent_trades": {"$size": 0}}
        ]
    })
    
    count = 0
    for trader in traders_without_trades:
        new_trades = generate_recent_trades(10)
        
        traders.update_one(
            {"_id": trader["_id"]},
            {"$set": {"recent_trades": new_trades}}
        )
        count += 1
    
    print(f"Initialized recent trades for {count} traders")
    return count
