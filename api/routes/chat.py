"""
Chat API Routes - Conversational interface for price comparison.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.chatbot_service import get_chatbot_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str
    user_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response from bot."""
    response: str
    intent: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    timestamp: str


@router.post("", response_model=ChatResponse)
async def send_message(chat: ChatMessage):
    """
    Send a message to the chatbot and get a response.
    
    The chatbot understands natural language queries like:
    - "Find milk prices"
    - "Compare bread across platforms"
    - "Show today's best deals"
    - "Which platform has cheapest rice?"
    - "Tell me about Blinkit"
    
    Returns a response with:
    - text response
    - detected intent
    - suggested action (search, compare, deals, etc.)
    - data for the action
    - follow-up suggestions
    """
    chatbot = get_chatbot_service()
    
    try:
        result = await chatbot.process_message(
            message=chat.message,
            user_id=chat.user_id,
            location=chat.location
        )
        
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            action=result.get("action"),
            data=result.get("data"),
            suggestions=result.get("suggestions", []),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/history")
async def get_history():
    """Get conversation history."""
    chatbot = get_chatbot_service()
    return {
        "history": chatbot.get_conversation_history(),
        "count": len(chatbot.get_conversation_history())
    }


@router.delete("/history")
async def clear_history():
    """Clear conversation history."""
    chatbot = get_chatbot_service()
    chatbot.clear_history()
    return {"status": "cleared", "message": "Conversation history cleared"}


@router.get("/suggestions")
async def get_suggestions():
    """Get suggested queries for new users."""
    return {
        "suggestions": [
            {
                "category": "Search",
                "queries": [
                    "Find milk prices",
                    "Search for Amul butter",
                    "Show me bread options"
                ]
            },
            {
                "category": "Compare",
                "queries": [
                    "Compare rice prices",
                    "Which platform has cheapest eggs?",
                    "Best price for maggi"
                ]
            },
            {
                "category": "Deals",
                "queries": [
                    "Show today's best deals",
                    "Discounts on snacks",
                    "What's on sale?"
                ]
            },
            {
                "category": "Platforms",
                "queries": [
                    "Tell me about Zepto",
                    "Which platform delivers fastest?",
                    "Compare all platforms"
                ]
            }
        ]
    }

