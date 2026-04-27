"""
Chat routes for MakanAI

Endpoints:
    POST /api/chat            -> send message to chatbot
    GET /api/chat/history     -> get chat history

Requires JWT token authentication for all routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, desc
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.meal import Meal, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.agents.orchestrator import orchestrate_chat

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message chat to MakanAI nutrition chatbot.

    Fetches the user's rcent meal history and chat history
    from the database, passes them to the orchestrator as
    context, and returns an AI generated response 

    Args:
        request: Chat Request with message string 
        db:      async database session
        current_user: authenticated user from JWT

    Returns:
        ChatResponse with reply and context_used count
    """

    # Fetch last 10 meals for context
    meal_result = await db.execute(
        select(Meal)
        .where(Meal.user_id == current_user.id)
        .order_by(desc(Meal.logged_at))
        .limit(10)
    )
    meals = meal_result.scalars().all()

    # Convert meals to dict 
    meal_history = [
        {
            "raw_text": meal.raw_text,
            "parsed_foods": meal.parsed_foods or [],
            "nutrition": meal.nutrition or {},
            "meal_time": meal.meal_time,
            "logged_at": meal.logged_at.isoformat() if meal.logged_at else None
        }
        for meal in meals
    ]

    # Fetch last 6 messages for conversation continuity
    chat_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(6)
    )
    recent_chats = chat_result.scalars().all()

    # Reverse so oldest message is first
    chat_history = [
        {
            "role": msg.role,
            "message": msg.message
        }
        for msg in reversed(recent_chats)
    ]

    # Run orchestrator 
    result = await orchestrate_chat(
        user_id=str(current_user.id),
        message=request.message,
        meal_history=meal_history,
        chat_history=chat_history
    )

    # Save user message to DB 
    user_message = ChatMessage(
        user_id=current_user.id,
        role="user",
        message=request.message,
        context={}
    )
    db.add(user_message)

    # Save assistant response to DB 
    assistant_message = ChatMessage(
        user_id=current_user.id,
        role="assistant",
    
        message=result["reply"],
        context={"meal_used": result['context_used']}
    )
    db.add(assistant_message)

    await db.commit()

    return ChatResponse(
        reply=result["reply"],
        context_used=result["context_used"]
    )

@router.get("/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    limit: int = 20, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the user's chat history

    Returns the most recent chat message ordered 
    from the oldest to newest so the frontend can render 
    the conversation in the correct order
    
    Args:
        limit: max number of messages to return
        db: async database session
        current_user: authenticated user from JWT
    
    Returns:
        list of ChatMessageResponse ordered from oldest first
    """

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse so oldest is first
    return list(reversed(messages))