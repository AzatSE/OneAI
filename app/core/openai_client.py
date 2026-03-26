from openai import OpenAI
from functools import lru_cache
from app.core.config import settings

@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)