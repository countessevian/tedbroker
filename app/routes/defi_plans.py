from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId

from app.database import get_collection, DEFI_PLANS_COLLECTION
from app.schemas import DeFiPlanResponse
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/defi-plans", tags=["defi_plans"])


def defi_plan_helper(plan) -> dict:
    """Helper function to format DeFi plan data from database"""
    return {
        "id": str(plan["_id"]),
        "name": plan["name"],
        "portfolio_type": plan["portfolio_type"],
        "expected_return_percent": plan["expected_return_percent"],
        "duration_months": plan["duration_months"],
        "minimum_investment": plan.get("minimum_investment", 0.0),
        "description": plan.get("description"),
        "is_active": plan.get("is_active", True)
    }


@router.get("/", response_model=List[DeFiPlanResponse])
async def get_all_defi_plans(current_user: dict = Depends(get_current_user_token)):
    """
    Get all active DeFi plans
    Requires authentication
    """
    try:
        plans_collection = get_collection(DEFI_PLANS_COLLECTION)
        plans = []

        # Only get active plans
        for plan in plans_collection.find({"is_active": True}):
            plans.append(defi_plan_helper(plan))

        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving DeFi plans: {str(e)}")


@router.get("/{plan_id}", response_model=DeFiPlanResponse)
async def get_defi_plan_by_id(plan_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Get a specific DeFi plan by ID
    Requires authentication
    """
    try:
        plans_collection = get_collection(DEFI_PLANS_COLLECTION)
        plan = plans_collection.find_one({"_id": ObjectId(plan_id)})

        if not plan:
            raise HTTPException(status_code=404, detail="DeFi plan not found")

        return defi_plan_helper(plan)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving DeFi plan: {str(e)}")
