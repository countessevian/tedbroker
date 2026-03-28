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
        "minimum_copy_amount": trader.get("minimum_copy_amount", 100.0),
        "assets_under_management": trader.get("assets_under_management", 0.0),
        "max_drawdown": trader.get("max_drawdown", 0.0),
        "risk_score": trader.get("risk_score", 5),
        "trades": trader.get("trades", []),
        "recent_trades": trader.get("recent_trades", []),
        "posts": trader.get("posts", [])
    }


@router.get("/posts")
async def get_all_posts(current_user: dict = Depends(get_current_user_token)):
    """Get all posts from all traders - NO AUTH REQUIRED FOR TESTING"""
    import sys
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        all_posts = []
        
        print(f"=== /api/traders/posts called ===", file=sys.stderr, flush=True)
        
        for trader in traders_collection.find():
            posts = trader.get("posts", [])
            if posts:
                print(f"Trader '{trader.get('full_name')}' has {len(posts)} posts", file=sys.stderr, flush=True)
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
        
        print(f"Total posts: {len(all_posts)}", file=sys.stderr, flush=True)
        all_posts.sort(key=lambda x: x["created_at"] or "", reverse=True)
        return all_posts
    except Exception as e:
        import traceback
        print(f"ERROR: {traceback.format_exc()}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving posts: {str(e)}")


@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user_token)):
    """Like or unlike a post"""
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
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


@router.post("/posts/{post_id}/dislike")
async def dislike_post(post_id: str, current_user: dict = Depends(get_current_user_token)):
    """Dislike or undislike a post"""
    try:
        traders_collection = get_collection(TRADERS_COLLECTION)
        user_id = current_user["user_id"]
        
        found = False
        for trader in traders_collection.find():
            posts = trader.get("posts", [])
            for i, post in enumerate(posts):
                if post.get("id") == post_id:
                    found = True
                    dislikes = post.get("dislikes", [])
                    
                    if user_id in dislikes:
                        dislikes.remove(user_id)
                        action = "undisliked"
                    else:
                        dislikes.append(user_id)
                        action = "disliked"
                    
                    traders_collection.update_one(
                        {"_id": trader["_id"], "posts.id": post_id},
                        {"$set": {"posts.$.dislikes": dislikes}}
                    )
                    
                    return {
                        "success": True,
                        "action": action,
                        "post_id": post_id,
                        "dislike_count": len(dislikes)
                    }
        
        if not found:
            raise HTTPException(status_code=404, detail="Post not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disliking post: {str(e)}")


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
