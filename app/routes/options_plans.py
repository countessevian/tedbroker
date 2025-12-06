from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId

from app.database import get_collection, OPTIONS_PLANS_COLLECTION
from app.schemas import OptionsPlanResponse
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/options-plans", tags=["options_plans"])


def options_plan_helper(plan) -> dict:
    """Helper function to format Options plan data from database"""
    return {
        "id": str(plan["_id"]),
        "name": plan["name"],
        "plan_type": plan["plan_type"],
        "expected_return_percent": plan["expected_return_percent"],
        "duration_months": plan.get("duration_months", 0),
        "minimum_investment": plan.get("minimum_investment", 0.0),
        "description": plan.get("description"),
        "is_active": plan.get("is_active", True)
    }


@router.get("/", response_model=List[OptionsPlanResponse])
async def get_all_options_plans(current_user: dict = Depends(get_current_user_token)):
    """
    Get all active Options plans
    Requires authentication
    """
    try:
        plans_collection = get_collection(OPTIONS_PLANS_COLLECTION)
        plans = []

        # Only get active plans
        for plan in plans_collection.find({"is_active": True}):
            plans.append(options_plan_helper(plan))

        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Options plans: {str(e)}")


@router.get("/{plan_id}", response_model=OptionsPlanResponse)
async def get_options_plan_by_id(plan_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Get a specific Options plan by ID
    Requires authentication
    """
    try:
        plans_collection = get_collection(OPTIONS_PLANS_COLLECTION)
        plan = plans_collection.find_one({"_id": ObjectId(plan_id)})

        if not plan:
            raise HTTPException(status_code=404, detail="Options plan not found")

        return options_plan_helper(plan)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving Options plan: {str(e)}")
