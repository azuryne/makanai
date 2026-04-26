"""
Pydantic schemas for chat request and response 

Used by:
    POST /api/chat 

"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ChatRequest(BaseModel):
    """
    Incoming chat message from the user.

    Fields:
        message: the user's message text
    """
    message: str


class ChatMessageResponse(BaseModel):
    """
    Single chat message returned in history

    Fields:
        id -> unique message ID
        role -> 'user' or 'assistant'
        message -> message content
        created_at -> timestamp
    
    """

    id: UUID
    role: str
    message: str
    created_at: datetime

    class Config: 
        from_attributes = True

class ChatResponse(BaseModel):
    """
    Response returned after processing a chat message 

    Fields:
        reply -> AI generated response
        context_used -> number of meals used as context
    """

    reply: str
    context_used: int 