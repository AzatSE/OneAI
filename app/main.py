from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.core.config import settings
import os



def custom_generate_unique_id(route: APIRoute) -> str:
    tag=route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


app = FastAPI(
    generate_unique_id_function=custom_generate_unique_id,
)

origins = settings.allowed_origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
    ],
)

@app.get("/")
def root():
    return {"message": "hello"}

@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(api_router)