from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.summary import Summary
from app.repositories import summary_repository


async def create(
    session: AsyncSession,
    url: str,
    title: str | None,
    owner_id: int,
) -> Summary:
    """Crea un resumen para el owner indicado."""

    return await summary_repository.create(session, url, title, owner_id)


async def get_all(session: AsyncSession, owner_id: int) -> list[Summary]:
    """Lista todos los resúmenes del owner."""

    return await summary_repository.get_all_by_owner(session, owner_id)


async def get_one(
    session: AsyncSession,
    summary_id: int,
    owner_id: int,
) -> Summary:
    """
    Obtiene un resumen por ID; 404 si no existe, 403 si el owner no coincide.
    """

    summary = await summary_repository.get_by_id(session, summary_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )
    if summary.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this summary",
        )
    return summary


async def update(
    session: AsyncSession,
    summary_id: int,
    owner_id: int,
    data: dict,
) -> Summary:
    """Actualiza un resumen existente solo si el caller es el dueño."""

    summary = await get_one(session, summary_id, owner_id)
    return await summary_repository.update(session, summary, data)


async def delete(
    session: AsyncSession,
    summary_id: int,
    owner_id: int,
) -> None:
    """Elimina un resumen solo si el caller es el dueño."""

    summary = await get_one(session, summary_id, owner_id)
    await summary_repository.delete(session, summary)
