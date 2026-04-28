"""
Chat Agent for MAKANAI 

Generates contextual chatbot responses using Ollama.
Agent receives user's message and a pre-built context 
string containing meal history and chat history.

Called by:
    orchestrator.orchestrate_chat()
"""

from app.services.ollama import ollama_service
from app.constant import CHAT_HUMAN_PROMPT, CHAT_SYSTEM_PROMPT

async def generate_chat_response(
        message: str,
        context: str
) -> str:
    """
    Generates a chatbot response using Ollama.

    Inject user's meal history and chat message history
    as context into the prompt, so Ollama can give 
    personalized and relevant response

    Args:
        message: the user's current message
        context: the formatted string with meal and chat history
                 built by context_builder.build_chat_context()

    Returns:
        AI generated response string
    """
    prompt = CHAT_HUMAN_PROMPT.format(
        meal_context=context,
        chat_history="",      # already included in context
        message=message
    )

    try:
        response = await ollama_service.generate(
            prompt=prompt,
            system=CHAT_SYSTEM_PROMPT
        )
        return response.strip()
    
    except Exception as e:
        print(f"Chat agent error: {e}")
        return (
            "Sorry, I am having trouble responding right now"
            "Please ensure that Ollama is running"
        )
    
async def stream_chat_response(
        message: str,
        context: str
): 
    """
    Stream chat response tokens from Ollama one by one

    Used by streaming POST /api/chat/stream endpoint
    Yields tokens as they arrive for a typing effect. 

    Args:
        message: the user's current message
        context: formatted string with meal + chat history

    Yields:
        individual token strings as they arrive 
    """

    prompt = CHAT_HUMAN_PROMPT.format(
        meal_context=context,
        chat_history="",
        message=message
    )

    try:
        async for token in ollama_service.stream(
            prompt=prompt,
            system=CHAT_SYSTEM_PROMPT
        ):
            yield token

    except Exception as e:
        print(f"Chat stream agent error: {e}")
        yield "Sorry, I am having trouble responding right now"


