from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from datetime import datetime, timedelta
import secrets

from app.database import get_collection, INVESTMENT_PLANS_COLLECTION, USER_INVESTMENTS_COLLECTION, USERS_COLLECTION, TRANSACTIONS_COLLECTION, TRADERS_COLLECTION
from app.schemas import InvestInPlanRequest, UserInvestmentResponse, PortfolioSummary, TraderInfo
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/investments", tags=["investments"])


def calculate_current_value(investment: dict) -> tuple:
    """
    Calculate current value and profit/loss for an investment
    Returns: (current_value, profit_loss, profit_loss_percent, days_elapsed, days_remaining)
    """
    start_date = investment["start_date"]
    maturity_date = investment["maturity_date"]
    amount_invested = investment["amount_invested"]
    expected_return_percent = investment["expected_return_percent"]

    # Calculate days
    now = datetime.utcnow()
    total_days = (maturity_date - start_date).days
    days_elapsed = (now - start_date).days
    days_remaining = (maturity_date - now).days

    # Ensure days don't go negative
    days_elapsed = max(0, days_elapsed)
    days_remaining = max(0, days_remaining)

    # Calculate progress ratio (0 to 1)
    if total_days > 0:
        progress_ratio = min(days_elapsed / total_days, 1.0)
    else:
        progress_ratio = 0

    # Calculate expected final value
    expected_final_value = amount_invested * (1 + expected_return_percent / 100)

    # Calculate current value based on progress
    current_value = amount_invested + (expected_final_value - amount_invested) * progress_ratio

    # Calculate profit/loss
    profit_loss = current_value - amount_invested
    profit_loss_percent = (profit_loss / amount_invested * 100) if amount_invested > 0 else 0

    return current_value, profit_loss, profit_loss_percent, days_elapsed, days_remaining


@router.post("/invest")
async def invest_in_plan(
    request: InvestInPlanRequest,
    current_user: dict = Depends(get_current_user_token)
):
    """
    User invests in an investment plan
    Deducts amount from wallet and creates investment record
    """
    try:
        users_collection = get_collection(USERS_COLLECTION)
        plans_collection = get_collection(INVESTMENT_PLANS_COLLECTION)
        investments_collection = get_collection(USER_INVESTMENTS_COLLECTION)
        transactions_collection = get_collection(TRANSACTIONS_COLLECTION)

        user_id = current_user["user_id"]

        # Get user
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get investment plan
        try:
            plan = plans_collection.find_one({"_id": ObjectId(request.plan_id)})
        except:
            raise HTTPException(status_code=400, detail="Invalid plan ID")

        if not plan:
            raise HTTPException(status_code=404, detail="Investment plan not found")

        if not plan.get("is_active", True):
            raise HTTPException(status_code=400, detail="This investment plan is not currently active")

        # Validate investment amount
        if request.amount < plan["minimum_investment"]:
            raise HTTPException(
                status_code=400,
                detail=f"Investment amount must be at least ${plan['minimum_investment']}"
            )

        # Check if user has selected at least 1 trader for copy trading
        selected_traders = user.get("selected_traders", [])
        if not selected_traders or len(selected_traders) < 1:
            raise HTTPException(
                status_code=400,
                detail="You must select at least 1 trader before activating a copy trading plan"
            )

        # Check wallet balance
        wallet_balance = user.get("wallet_balance", 0.0)
        if wallet_balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient wallet balance. You have ${wallet_balance}, but need ${request.amount}"
            )

        # Calculate dates
        start_date = datetime.utcnow()
        maturity_date = start_date + timedelta(days=plan["holding_period_months"] * 30)  # Approximate months to days

        # Create investment record
        investment_doc = {
            "user_id": user_id,
            "plan_id": str(plan["_id"]),
            "plan_name": plan["name"],
            "amount_invested": request.amount,
            "expected_return_percent": plan["expected_return_percent"],
            "holding_period_months": plan["holding_period_months"],
            "start_date": start_date,
            "maturity_date": maturity_date,
            "status": "active",
            "created_at": start_date,
            "updated_at": start_date
        }

        result = investments_collection.insert_one(investment_doc)

        # Deduct from wallet balance
        new_balance = wallet_balance - request.amount
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"wallet_balance": new_balance}}
        )

        # Create transaction record
        transaction_doc = {
            "user_id": user_id,
            "transaction_type": "investment",
            "amount": request.amount,
            "status": "completed",
            "payment_method": "wallet",
            "reference_number": secrets.token_hex(16),
            "description": f"Investment in {plan['name']}",
            "investment_id": str(result.inserted_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        transactions_collection.insert_one(transaction_doc)

        # Increment plan subscribers count
        plans_collection.update_one(
            {"_id": ObjectId(request.plan_id)},
            {"$inc": {"current_subscribers": 1}}
        )

        return {
            "message": "Investment successful",
            "investment_id": str(result.inserted_id),
            "amount_invested": request.amount,
            "plan_name": plan["name"],
            "new_wallet_balance": new_balance,
            "maturity_date": maturity_date.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investment failed: {str(e)}")


@router.get("/portfolio", response_model=PortfolioSummary)
async def get_user_portfolio(current_user: dict = Depends(get_current_user_token)):
    """
    Get user's investment portfolio with current performance
    """
    try:
        investments_collection = get_collection(USER_INVESTMENTS_COLLECTION)
        users_collection = get_collection(USERS_COLLECTION)
        traders_collection = get_collection(TRADERS_COLLECTION)
        user_id = current_user["user_id"]

        # Get user to access selected traders
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        selected_trader_ids = user.get("selected_traders", []) if user else []

        # Get trader details for selected traders
        traders_info = []
        for trader_id in selected_trader_ids:
            try:
                trader = traders_collection.find_one({"_id": ObjectId(trader_id)})
                if trader:
                    traders_info.append({
                        "id": str(trader["_id"]),
                        "full_name": trader["full_name"],
                        "profile_photo": trader.get("profile_photo", "")
                    })
            except:
                continue

        # Get all user investments
        investments = list(investments_collection.find({"user_id": user_id}))

        if not investments:
            return PortfolioSummary(
                total_invested=0.0,
                current_value=0.0,
                total_profit_loss=0.0,
                total_profit_loss_percent=0.0,
                active_investments=0,
                investments=[]
            )

        # Calculate current values and build response
        investment_responses = []
        total_invested = 0.0
        total_current_value = 0.0
        active_count = 0

        for inv in investments:
            current_value, profit_loss, profit_loss_percent, days_elapsed, days_remaining = calculate_current_value(inv)

            # Update status if matured
            if days_remaining <= 0 and inv["status"] == "active":
                investments_collection.update_one(
                    {"_id": inv["_id"]},
                    {"$set": {"status": "matured"}}
                )
                inv["status"] = "matured"

            # Convert trader info to TraderInfo objects
            trader_info_list = []
            for trader_dict in traders_info:
                trader_info_list.append(TraderInfo(
                    id=trader_dict["id"],
                    full_name=trader_dict["full_name"],
                    profile_photo=trader_dict["profile_photo"]
                ))

            investment_response = UserInvestmentResponse(
                id=str(inv["_id"]),
                plan_id=inv["plan_id"],
                plan_name=inv["plan_name"],
                amount_invested=inv["amount_invested"],
                expected_return_percent=inv["expected_return_percent"],
                holding_period_months=inv["holding_period_months"],
                start_date=inv["start_date"],
                maturity_date=inv["maturity_date"],
                current_value=round(current_value, 2),
                profit_loss=round(profit_loss, 2),
                profit_loss_percent=round(profit_loss_percent, 2),
                days_elapsed=days_elapsed,
                days_remaining=days_remaining,
                status=inv["status"],
                selected_traders=trader_info_list
            )

            investment_responses.append(investment_response)
            total_invested += inv["amount_invested"]
            total_current_value += current_value

            if inv["status"] == "active":
                active_count += 1

        # Calculate totals
        total_profit_loss = total_current_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0

        return PortfolioSummary(
            total_invested=round(total_invested, 2),
            current_value=round(total_current_value, 2),
            total_profit_loss=round(total_profit_loss, 2),
            total_profit_loss_percent=round(total_profit_loss_percent, 2),
            active_investments=active_count,
            investments=investment_responses
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch portfolio: {str(e)}")


@router.get("/portfolio/{investment_id}")
async def get_investment_details(
    investment_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get detailed information about a specific investment
    """
    try:
        investments_collection = get_collection(USER_INVESTMENTS_COLLECTION)
        user_id = current_user["user_id"]

        # Get investment
        try:
            investment = investments_collection.find_one({
                "_id": ObjectId(investment_id),
                "user_id": user_id
            })
        except:
            raise HTTPException(status_code=400, detail="Invalid investment ID")

        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")

        # Calculate current values
        current_value, profit_loss, profit_loss_percent, days_elapsed, days_remaining = calculate_current_value(investment)

        return {
            "id": str(investment["_id"]),
            "plan_id": investment["plan_id"],
            "plan_name": investment["plan_name"],
            "amount_invested": investment["amount_invested"],
            "expected_return_percent": investment["expected_return_percent"],
            "holding_period_months": investment["holding_period_months"],
            "start_date": investment["start_date"].isoformat(),
            "maturity_date": investment["maturity_date"].isoformat(),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_percent": round(profit_loss_percent, 2),
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "status": investment["status"],
            "created_at": investment["created_at"].isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch investment details: {str(e)}")


@router.get("/active-plans")
async def get_active_plans_with_progress(current_user: dict = Depends(get_current_user_token)):
    """
    Get active investment plans with progress, selected traders, and performance metrics
    Organized by plan type (ETF, DeFi, Options)
    """
    try:
        investments_collection = get_collection(USER_INVESTMENTS_COLLECTION)
        users_collection = get_collection(USERS_COLLECTION)
        traders_collection = get_collection(TRADERS_COLLECTION)
        user_id = current_user["user_id"]

        # Get user to access selected traders
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        selected_trader_ids = user.get("selected_traders", [])

        # Get trader details for selected traders
        traders_info = []
        for trader_id in selected_trader_ids:
            try:
                trader = traders_collection.find_one({"_id": ObjectId(trader_id)})
                if trader:
                    traders_info.append({
                        "id": str(trader["_id"]),
                        "full_name": trader["full_name"],
                        "profile_photo": trader.get("profile_photo", "")
                    })
            except:
                continue

        # Get all active investments for this user
        active_investments = list(investments_collection.find({
            "user_id": user_id,
            "status": "active"
        }))

        # Group investments by plan type
        etf_plans = []
        defi_plans = []
        options_plans = []
        general_plans = []

        for inv in active_investments:
            current_value, profit_loss, profit_loss_percent, days_elapsed, days_remaining = calculate_current_value(inv)

            # Calculate progress percentage
            total_days = (inv["maturity_date"] - inv["start_date"]).days
            progress_percent = (days_elapsed / total_days * 100) if total_days > 0 else 0
            progress_percent = min(100, max(0, progress_percent))

            # Calculate time remaining in human-readable format
            if days_remaining > 30:
                months_remaining = days_remaining // 30
                days_rem = days_remaining % 30
                time_remaining = f"{months_remaining}mo {days_rem}d" if days_rem > 0 else f"{months_remaining}mo"
            else:
                time_remaining = f"{days_remaining}d"

            plan_data = {
                "id": str(inv["_id"]),
                "plan_id": inv["plan_id"],
                "plan_name": inv["plan_name"],
                "amount_invested": inv["amount_invested"],
                "current_value": round(current_value, 2),
                "profit_loss_percent": round(profit_loss_percent, 2),
                "progress_percent": round(progress_percent, 2),
                "time_remaining": time_remaining,
                "days_remaining": days_remaining,
                "start_date": inv["start_date"].isoformat(),
                "maturity_date": inv["maturity_date"].isoformat(),
                "selected_traders": traders_info
            }

            # Categorize by plan type based on plan name
            plan_name_lower = inv["plan_name"].lower()
            if "etf" in plan_name_lower:
                etf_plans.append(plan_data)
            elif "defi" in plan_name_lower:
                defi_plans.append(plan_data)
            elif "option" in plan_name_lower:
                options_plans.append(plan_data)
            else:
                general_plans.append(plan_data)

        return {
            "etf_plans": etf_plans,
            "defi_plans": defi_plans,
            "options_plans": options_plans,
            "general_plans": general_plans,
            "total_active": len(active_investments)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active plans: {str(e)}")
