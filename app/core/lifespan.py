import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Arranque y cierre de la app; deja trazas claras en logs."""

    logger.info("Summaries API: startup completado")
    yield
    logger.info("Summaries API: apagado")
