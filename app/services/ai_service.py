from openai import AsyncOpenAI, RateLimitError, APITimeoutError
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
import json

from app.models import Task
from app.schemas import TaskAdviceResponse

from typing import AsyncGenerator


SYSTEM_PROMPT = """You are a personal productivity coach — sharp, focused, motivating.

The user will give you a list of tasks.

Your job:
1. Summary — 1-2 sentences max. React like a coach who instantly sees what's going on.
2. Suggestions — up to 5 short actions. 
   - Cover ALL tasks (group small ones if needed)
   - Prioritize clearly (what first, what next)
   - Be specific and actionable
   - Add motivation (push them forward, no fluff)

Rules:
- Write in first person ("I'd start with...", "Looking at this...")
- Be concise but powerful
- Do NOT ignore tasks — group them if there are many
- No generic advice
- Respond in user's language

Format your response EXACTLY like this (no markdown, no extra text):
SUMMARY: <your summary here>
SUGGESTIONS:
- <suggestion 1>
- <suggestion 2>
- <suggestion 3>"""

class AIService:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def get_advice(self, db: Session, user_id: int) -> TaskAdviceResponse:
        tasks = db.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.comlite.is_(False))
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
            response = await self.client.chat.completions.create(
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

        try:
            data = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, KeyError):
            raise HTTPException(502, "AI returned an unexpected response format")

        return TaskAdviceResponse(
            summary=data["summary"],
            suggestions=data["suggestions"],
        )

    async def get_advice_stream(self, db: Session, user_id: int) -> AsyncGenerator[str, None]:
        tasks = db.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.comlite.is_(False))
            .order_by(Task.created_at.asc())
            .limit(30)
        ).scalars().all()

        if not tasks:
            yield json.dumps({
                "summary": "You have no incomplete tasks. Great job!",
                "suggestions": ["Add some tasks so I can help you plan."]
            })
            return

        task_list = "\n".join(f"- ID {t.id}: {t.task}" for t in tasks)

        stream = await self.client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"My tasks:\n{task_list}"},
            ],
            stream=True,
            timeout=30.0,
        )

        yield " " * 1024 + "\n"

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta