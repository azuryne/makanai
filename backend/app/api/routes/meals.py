from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.meal import Meal
from app.schemas.meal import MealLogRequest, MealLogResponse, MealHistoryResponse
from app.api.deps import get_current_user
# from app.agents.orchestrator import orchestrator
from app.agents.orchestrator import orchestrate_meal_log 

router = APIRouter()

@router.post("/log", response_model=MealLogResponse)
async def log_meal(
    request: MealLogRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
): 
    """Log meal using natural language"""

    # Process the text with AI 
    result = await orchestrate_meal_log(request.text)

    # Create the meal record 
    meal =  Meal(
        user_id=current_user.id,
        raw_text=request.text,
        parsed_foods=result["parsed_foods"],
        nutrition=result["nutrition"],
        meal_time=request.meal_time
    )

    db.add(meal)
    await db.commit()
    await db.refresh(meal)            # get meal.id without commiting 

    return MealLogResponse(
        meal_id=meal.id,
        raw_text=meal.raw_text,
        parsed_food=meal.parsed_foods,
        nutrition=meal.nutrition,
        meal_time=meal.meal_time,
        logged_at=meal.logged_at
    )


@router.get("/history", response_model=MealHistoryResponse)
async def get_meal_history(
    limit: int = 50,
    offset: int = 0, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    """Get user's meal history"""
    result = await db.execute(
        select(Meal)
        .where(Meal.user_id == current_user.id)
        .order_by(Meal.logged_at)
        .limit(limit)
        .offset(offset)
    )
    meals = result.scalar().all()
    return MealHistoryResponse(
        meals=[
            MealLogResponse(
                meal_id=meal.id,
                raw_text=meal.raw_text,
                parsed_food=meal.parsed_foods or [],
                nutrition=meal.nutrition or {},
                meal_time=meal.meal_time,
                logged_at=meal.logged_at
            )
            for meal in meals
        ],
        total=len(meals)  
    )

