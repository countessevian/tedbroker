from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId

from app.database import get_collection, TRADERS_COLLECTION
from app.schemas import ExpertTraderResponse, Trade
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/traders", tags=["traders"])


def trader_helper(trader) -> dict:
    """Helper function to format trader data from database"""
    return {
        "id": str(trader["_id"]),
        "full_name": trader["full_name"],
        "profile_photo": trader["profile_photo"],
        "description": trader["description"],
        "specialization": trader["specialization"],
        "ytd_return": trader["ytd_return"],
        "win_rate": trader["win_rate"],
        "copiers": trader["copiers"],
        "trades": trader.get("trades", [])
    }


@router.get("/", response_model=List[ExpertTraderResponse])
async def get_all_traders(current_user: dict = Depends(get_current_user_token)):
    """
    Get all expert traders
    Requires authentication
    """
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        traders = []

        for trader in traders_collection.find():
            traders.append(trader_helper(trader))

        return traders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving traders: {str(e)}")


@router.get("/{trader_id}", response_model=ExpertTraderResponse)
async def get_trader_by_id(trader_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Get a specific expert trader by ID
    Requires authentication
    """
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        trader = traders_collection.find_one({"_id": ObjectId(trader_id)})

        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")

        return trader_helper(trader)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving trader: {str(e)}")
