"""
Chat routes for MakanAI

Endpoints:
    POST /api/chat            -> send message to chatbot
    POST /api/chat/stream     -> streaming chat response (SSE)
    GET /api/chat/history     -> get chat history

Requires JWT token authentication for all routes
"""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, desc
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.meal import Meal, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.agents.orchestrator import orchestrate_chat
from app.agents.chat_agent import stream_chat_response
from app.services.context_builder import build_chat_context

router = APIRouter()

async def _get_context(
        current_user: User,
        db: AsyncSession
) -> tuple[list[dict], list[dict]]:
    """
    Helper to fetch meal history and chat history from DB

    Reused by both regular and streaming chat endpoints
    to avoid code duplication. 

    Args:
        current_user: authenticated user
        db:           async database session

    Returns: 
        tuple of (meal_history, chat_history) as list of dicts    
    """

    # Fetch the last 10 meals for context 

    meal_result = await db.execute(
        select(Meal)
        .where(Meal.user_id == current_user.id)
        .order_by(desc(Meal.logged_at))
        .limit(10)
    )

    meals = meal_result.scalars().all()

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

    # Fetch the last 6 messages for continuity 

    chat_history = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(6)
    )

    recent_chats = chat_history.scalars().all()

    chat_history = [
        {
            "role": msg.role,
            "message": msg.message
        }
        for msg in reversed(recent_chats)
    ]

    return meal_history, chat_history


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
    meal_history, chat_history = await _get_context(current_user, db)

    # Step 1 — save the user message FIRST and commit
    db.add(ChatMessage(
        user_id=current_user.id,
        role="user",
        message=request.message,
        context={}
    ))
    await db.commit()

    # Step 2 — run orchestrator (this can take 20-30s)
    result = await orchestrate_chat(
        user_id=str(current_user.id),
        message=request.message,
        meal_history=meal_history,
        chat_history=chat_history
    )

    # Step 3 — save assistant reply with its own (later) timestamp
    db.add(ChatMessage(
        user_id=current_user.id,
        role="assistant",
        message=result["reply"],
        context={"meals_used": result["context_used"]}
    ))
    await db.commit()

    return ChatResponse(
        reply=result["reply"],
        context_used=result["context_used"]
    )

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stream a chat response token by using SSE (Server Send Event)
    
    Streams the AI response word by word as it is generated
    by Ollama - provides a chatGPT like typing effect 

    The full response is saved to the database after the
    streaming is completed 

    SSE format sent to client:
        data: {"token":"hello"}
        data: {"token":" world"}
        data: [DONE]

    Args: 
        request: ChatRequest with message string 
        db: async database session 
        current_user: authenticated user from JWT

    Returns:
        StreamingResponse with text/event-stream media type
    """

    meal_history, chat_history = await _get_context(current_user, db)

    # Build context string
    context = build_chat_context(
        meal_history=meal_history, 
        chat_history=chat_history
    )

    # Save user message immediately 
    db.add(ChatMessage(
        user_id=current_user.id,
        role="user",
        message=request.message,
        context={}
    ))

    await db.commit()

    # Collect full response for saving into DB
    full_response = []

    async def generate():
        """
        Inner generator that streams tokens to the client 
        and collects the full response for DB storage
        """
        async for token in stream_chat_response(
            message=request.message,
            context=context
        ):
            full_response.append(token)

            # SSE format - each line must starts with "data: "
            yield f"data: {json.dumps({'token': token})}\n\n"

        # Signal stream is done 
        yield f"data: [DONE]\n\n"

        # Save complete response to DB after streaming 
        complete_reply = "".join(full_response)
        async with db:
            db.add(ChatMessage(
                user_id=current_user.id,
                role="assistant",
                message=complete_reply,
                context={
                    "meals_used": len(meal_history),
                    "streamed": True
                }
            ))
            await db.commit()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",  # indicator for client to know its SSE stream
        headers={
            # Disable buffering so tokens reach client immediately
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
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