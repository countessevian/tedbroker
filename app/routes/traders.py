from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from datetime import datetime

from app.database import get_collection, TRADERS_COLLECTION, USERS_COLLECTION
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


@router.post("/select/{trader_id}")
async def select_trader(trader_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Select a trader for copy trading
    Adds the trader to the user's selected_traders list
    """
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        users_collection = get_collection(USERS_COLLECTION)
        user_id = current_user["user_id"]

        # Verify trader exists
        try:
            trader = traders_collection.find_one({"_id": ObjectId(trader_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid trader ID")

        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")

        # Get user
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if trader is already selected
        selected_traders = user.get("selected_traders", [])
        if trader_id in selected_traders:
            raise HTTPException(status_code=400, detail="Trader is already selected")

        # Add trader to selected list
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$push": {"selected_traders": trader_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Increment copiers count for the trader
        traders_collection.update_one(
            {"_id": ObjectId(trader_id)},
            {"$inc": {"copiers": 1}}
        )

        # Get updated selected traders list
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
        selected_count = len(updated_user.get("selected_traders", []))

        return {
            "message": f"Successfully selected {trader['full_name']} for copy trading",
            "trader_id": trader_id,
            "trader_name": trader["full_name"],
            "selected_traders_count": selected_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selecting trader: {str(e)}")


@router.delete("/unselect/{trader_id}")
async def unselect_trader(trader_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Unselect a trader from copy trading
    Removes the trader from the user's selected_traders list
    """
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        users_collection = get_collection(USERS_COLLECTION)
        user_id = current_user["user_id"]

        # Get user
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if trader is selected
        selected_traders = user.get("selected_traders", [])
        if trader_id not in selected_traders:
            raise HTTPException(status_code=400, detail="Trader is not selected")

        # Remove trader from selected list
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$pull": {"selected_traders": trader_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Decrement copiers count for the trader
        try:
            trader = traders_collection.find_one({"_id": ObjectId(trader_id)})
            if trader:
                traders_collection.update_one(
                    {"_id": ObjectId(trader_id)},
                    {"$inc": {"copiers": -1}}
                )
        except:
            pass  # If trader doesn't exist, just continue

        # Get updated selected traders list
        updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
        selected_count = len(updated_user.get("selected_traders", []))

        trader_name = trader["full_name"] if trader else "Unknown Trader"

        return {
            "message": f"Successfully unselected {trader_name}",
            "trader_id": trader_id,
            "selected_traders_count": selected_count
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unselecting trader: {str(e)}")


@router.get("/selected/list")
async def get_selected_traders(current_user: dict = Depends(get_current_user_token)):
    """
    Get list of traders selected by the current user
    """
    try:
        users_collection = get_collection(USERS_COLLECTION)
        traders_collection = get_collection(TRADERS_COLLECTION)
        user_id = current_user["user_id"]

        # Get user
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        selected_trader_ids = user.get("selected_traders", [])

        # Get full trader details
        selected_traders = []
        for trader_id in selected_trader_ids:
            try:
                trader = traders_collection.find_one({"_id": ObjectId(trader_id)})
                if trader:
                    selected_traders.append(trader_helper(trader))
            except:
                # Skip invalid trader IDs
                continue

        return {
            "selected_traders": selected_traders,
            "count": len(selected_traders)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving selected traders: {str(e)}")
