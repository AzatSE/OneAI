from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import model_validator
from typing import List, Optional



class Settings(BaseSettings):

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXP_DAYS: int
    SECRET_KEY: str

    OPENAI_API_KEY: str

    ENV: str = "development"

    allowed_origins: Optional[List[str]] = None

    @model_validator(mode="before")
    @classmethod
    def parse_origins(cls, values):
        origins = values.get("allowed_origins")
        if isinstance(origins, str):
            values["allowed_origins"] = [o.strip() for o in origins.split(",")]
        return values

    @model_validator(mode="after")
    def set_default_origins(self):
        if self.allowed_origins is None:
            self.allowed_origins = [
                "http://localhost:5173",
                "http://localhost",
                "http://127.0.0.1:5173",
                "http://127.0.0.1",
            ]
        return self



    @property
    def URL_DB(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = str(Path(__file__).parents[2] / ".env")
        env_file_encoding = "utf-8"

settings = Settings()

@lru_cache
def get_settings(self):
    return Settings()