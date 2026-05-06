"""
Insights routes for MAKANAI 

Endpoints: 
    GET /api/insights/weekly -> returns weekly insight summary

Requires JWT authentication on all routes 
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select 
from datetime import datetime, timedelta, timezone
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.meal import Meal
from app.schemas.insight import WeeklyInsightResponse, NutritionAverage
from app.agents.orchestrator import orchestrate_weekly_insights
from datetime import date

router = APIRouter()

@router.get("/weekly", response_model=WeeklyInsightResponse)
async def get_weekly_insight(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a weekly insight summary for the current user 

    Fetches the last 7 days of meal logs from the database,
    passes them to the insight agent via the orchestrator,
    and returns an AI-generated summary with nutrition averages

    Returns:
        WeeklyInsightResponse with summary, highlights, 
        suggestions and average nutrition values

    Raises:
        HTTPException 404 if no meals found for the week 
    """

    # Calculate date range - last 7 days 
    week_end = datetime.now(timezone.utc)
    week_start = week_end - timedelta(days=7)

    # Fetch meals from the last 7 days 
    result = await db.execute(
        select(Meal)
        .where(Meal.user_id == current_user.id)
        .where(Meal.logged_at >= week_start)
        .where(Meal.logged_at <= week_end)
        .order_by(Meal.logged_at.desc())
    )
    meals = result.scalars().all()

    # Convert to list of dicts for the agent 
    meals_data = [
        {
            "raw_text" : meal.raw_text,
            "parsed_foods" : meal.parsed_foods or [],
            "nutrition" : meal.nutrition or {},
            "meal_time" : meal.meal_time,
            "logged_at" : meal.logged_at,
        } for meal in meals
    ]

    # Run orchestrator
    insight = await orchestrate_weekly_insights(
        user_id=str(current_user.id),
        meals=meals_data
    )

    return WeeklyInsightResponse(
        week_start=week_start.date(),
        week_end=week_end.date(),
        total_meals=len(meals),
        average_nutrition=NutritionAverage(
            **insight["average_nutrition"]
        ),
        summary=insight["summary"],
        highlights=insight["highlights"],
        suggestions=insight["suggestions"]
    )
    