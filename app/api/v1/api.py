from fastapi import APIRouter

from app.api.v1.endpoints import auth, summaries

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
