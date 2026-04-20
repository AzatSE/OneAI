from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.core.openai_client import get_openai_client
from app.models import User
from app.schemas import TaskAdviceResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


def get_ai_service() -> AIService:
    return AIService(client=get_openai_client())


@router.get("/advice", response_model=TaskAdviceResponse)
async def get_task_advice(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
):
    return await ai.get_advice(db=db, user_id=current_user.id)

@router.get("/advice/stream")
async def get_task_advice_stream(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
):
    return StreamingResponse(
        ai.get_advice_stream(db=db, user_id=current_user.id),
        media_type="text/plain",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )