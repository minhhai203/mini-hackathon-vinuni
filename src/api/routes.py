"""HTTP API routes."""

from fastapi import APIRouter

from src.models.chat import ChatRequest, ChatResponse
from src.models.health import HealthResponse
from src.services.chatbot import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = chatbot_service.reply(
        request.message,
        profile=request.profile,
        history=request.history,
    )
    return ChatResponse(**result)
