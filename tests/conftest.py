import os
from collections.abc import AsyncGenerator, Generator

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.main import app


def pytest_configure(config: pytest.Config) -> None:
    # Requerido por el enunciado: pytest-asyncio con asyncio_mode="auto".
    # pytest-asyncio expone esta opción como `config.option.asyncio_mode`.
    if hasattr(config.option, "asyncio_mode"):
        config.option.asyncio_mode = "auto"


@pytest.fixture(scope="session")
def _apply_migrations() -> None:
    """
    Prepara el schema de la DB de test una sola vez, aplicando Alembic `upgrade head`.
    """

    settings = get_settings()
    if not settings.TEST_DATABASE_URL:
        raise RuntimeError("TEST_DATABASE_URL is required to run tests.")

    # Alembic env.py lee DATABASE_URL desde settings. Para tests, lo apuntamos al TEST_DATABASE_URL.
    os.environ["DATABASE_URL"] = settings.TEST_DATABASE_URL
    get_settings.cache_clear()

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function")
async def session(_apply_migrations: None) -> AsyncGenerator[AsyncSession, None]:
    """
    Para cada test:
    - abre una transacción
    - entrega una AsyncSession unida a esa conexión
    - hace rollback al finalizar (DB limpia)
    """

    settings = get_settings()
    if not settings.TEST_DATABASE_URL:
        raise RuntimeError("TEST_DATABASE_URL is required to run tests.")

    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True)

    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            async with AsyncSession(bind=conn, expire_on_commit=False) as db:
                yield db
        finally:
            await trans.rollback()

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Cliente HTTP async contra la app ASGI, usando override de get_session.
    """

    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
