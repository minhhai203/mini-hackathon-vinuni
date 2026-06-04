"""HTTP API routes."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.logger import get_logger
from src.models.chat import ChatRequest, ChatResponse
from src.models.health import HealthResponse
from src.services.chatbot import AIChatbotService

log = get_logger("chatbot.api")
router = APIRouter()
chatbot_service = AIChatbotService()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    log.info("REQUEST  | message=%r | history_len=%d", request.message, len(request.history or []))
    try:
        result = chatbot_service.reply(
            request.message,
            profile=request.profile,
            history=request.history,
        )
        reply_preview = (result.get("reply") or "")[:200].replace("\n", " ")
        log.info(
            "RESPONSE | tools=%s | reply_preview=%r",
            result.get("used_tools", []),
            reply_preview,
        )
        return ChatResponse(**result)
    except Exception as exc:
        log.exception("ERROR    | message=%r | error=%s", request.message, exc)
        raise
