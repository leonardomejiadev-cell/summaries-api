import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router

logger = logging.getLogger(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Arranque y cierre de la app; deja trazas claras en logs."""

    logger.info("Summaries API: startup completado")
    yield
    logger.info("Summaries API: apagado")


app = FastAPI(title="Summaries API", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
