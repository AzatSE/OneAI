from openai import OpenAI, RateLimitError, APITimeoutError
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
import json

from app.models import Task
from app.schemas import TaskAdviceResponse

SYSTEM_PROMPT = """You are a personal productivity coach — direct, sharp, no fluff.
The user will give you their incomplete tasks.

Your job:
1. Summary — 1-2 sentences max. React like a coach who just glanced at their list.
2. Suggestions — 3 max. One sentence each. Tell them exactly what to do first and why.

Rules:
- Write in first person as a coach ("I'd start with...", "Looking at your list...")
- Sound human, not corporate
- Short. Every word must earn its place.
- respond in users language

Return strictly JSON:
{
  "summary": "...",
  "suggestions": ["...", "...", "..."]
}"""

class AIService:
    def __init__(self, client: OpenAI):
        self.client = client

    def get_advice(self, db: Session, user_id: int) -> TaskAdviceResponse:
        tasks = db.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.comlite == False)
            .order_by(Task.created_at.asc())
            .limit(30)
        ).scalars().all()

        if not tasks:
            return TaskAdviceResponse(
                summary="You have no incomplete tasks. Great job!",
                suggestions=["Add some tasks so I can help you plan."],
            )

        task_list = "\n".join(f"- ID {t.id}: {t.task}" for t in tasks)

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"My tasks:\n{task_list}"},
                ],
                response_format={"type": "json_object"},
                timeout=30.0,
            )
        except RateLimitError:
            raise HTTPException(429, "Too many requests to AI, try again in a minute")
        except APITimeoutError:
            raise HTTPException(504, "AI did not respond in time, please try again")

        data = json.loads(response.choices[0].message.content)

        return TaskAdviceResponse(
            summary=data["summary"],
            suggestions=data["suggestions"],
        )