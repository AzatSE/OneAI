from openai import AsyncOpenAI
from functools import lru_cache
from app.core.config import settings


@lru_cache(maxsize=1)
def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
