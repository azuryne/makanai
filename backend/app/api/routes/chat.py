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
    Send a message chat to MakanAI nutrition chatbot
    """
