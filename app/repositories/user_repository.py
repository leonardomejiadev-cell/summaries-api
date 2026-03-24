from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Obtiene un usuario por email o None si no existe."""

    statement = select(User).where(User.email == email)
    return (await session.exec(statement)).first()


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Obtiene un usuario por ID o None si no existe."""

    statement = select(User).where(User.id == user_id)
    return (await session.exec(statement)).first()


async def create(session: AsyncSession, email: str, hashed_password: str) -> User:
    """Inserta un usuario y devuelve la entidad persistida."""

    user = User(email=email, password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
