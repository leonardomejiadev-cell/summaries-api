from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import TokenResponse


async def register(session: AsyncSession, email: str, password: str) -> User:
    """
    Registra un usuario: exige email único, hashea la contraseña y persiste vía repositorio.
    La verificación previa actúa como fast-path; el IntegrityError cubre la race condition.
    """

    existing = await user_repository.get_by_email(session, email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    hashed = hash_password(password)
    try:
        return await user_repository.create(session, email, hashed)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


async def login(session: AsyncSession, email: str, password: str) -> TokenResponse:
    """
    Valida credenciales y emite JWT; ante cualquier fallo coherente con autenticación, responde 401.
    """

    user = await user_repository.get_by_email(session, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)
