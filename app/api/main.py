from fastapi import APIRouter

from app.api.routers import users,tasks,ai_router

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(ai_router.router)