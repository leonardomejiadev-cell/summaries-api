from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.lifespan import lifespan
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="Summaries API", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
