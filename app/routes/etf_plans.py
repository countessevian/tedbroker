from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId

from app.database import get_collection, ETF_PLANS_COLLECTION
from app.schemas import ETFPlanResponse
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/etf-plans", tags=["etf_plans"])


def etf_plan_helper(plan) -> dict:
    """Helper function to format ETF plan data from database"""
    return {
        "id": str(plan["_id"]),
        "name": plan["name"],
        "plan_type": plan["plan_type"],
        "expected_return_percent": plan["expected_return_percent"],
        "duration_months": plan["duration_months"],
        "minimum_investment": plan.get("minimum_investment", 0.0),
        "description": plan.get("description"),
        "is_active": plan.get("is_active", True)
    }


@router.get("/", response_model=List[ETFPlanResponse])
async def get_all_etf_plans(current_user: dict = Depends(get_current_user_token)):
    """
    Get all active ETF plans
    Requires authentication
    """
    try:
        plans_collection = get_collection(ETF_PLANS_COLLECTION)
        plans = []

        # Only get active plans
        for plan in plans_collection.find({"is_active": True}):
            plans.append(etf_plan_helper(plan))

        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ETF plans: {str(e)}")


@router.get("/{plan_id}", response_model=ETFPlanResponse)
async def get_etf_plan_by_id(plan_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Get a specific ETF plan by ID
    Requires authentication
    """
    try:
        plans_collection = get_collection(ETF_PLANS_COLLECTION)
        plan = plans_collection.find_one({"_id": ObjectId(plan_id)})

        if not plan:
            raise HTTPException(status_code=404, detail="ETF plan not found")

        return etf_plan_helper(plan)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving ETF plan: {str(e)}")
