from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.summary import Summary


async def get_by_id(session: AsyncSession, summary_id: int) -> Summary | None:
    """Obtiene un summary por ID o None si no existe."""

    statement = select(Summary).where(Summary.id == summary_id)
    return (await session.exec(statement)).first()


async def get_all_by_owner(session: AsyncSession, owner_id: int) -> list[Summary]:
    """Lista todos los summaries de un owner."""

    statement = select(Summary).where(Summary.owner_id == owner_id)
    return list((await session.exec(statement)).all())


async def create(
    session: AsyncSession,
    url: str,
    title: str | None,
    owner_id: int,
) -> Summary:
    """Inserta un summary y devuelve la entidad persistida."""

    summary = Summary(url=url, title=title, owner_id=owner_id)
    session.add(summary)
    await session.commit()
    await session.refresh(summary)
    return summary


async def update(session: AsyncSession, summary: Summary, data: dict) -> Summary:
    """Actualiza campos de un summary existente y retorna la versión persistida."""

    for key, value in data.items():
        setattr(summary, key, value)
    session.add(summary)
    await session.commit()
    await session.refresh(summary)
    return summary


async def delete(session: AsyncSession, summary: Summary) -> None:
    """Elimina un summary existente."""

    await session.delete(summary)
    await session.commit()
