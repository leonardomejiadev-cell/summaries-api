from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera hash bcrypt para almacenar contraseñas de forma segura."""

    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Compara contraseña en claro con un hash bcrypt almacenado."""

    return _pwd_context.verify(plain, hashed)


def create_access_token(data: dict[str, Any]) -> str:
    """Crea un JWT HS256 con expiración configurada en settings."""

    to_encode = dict(data)
    expire_ts = int(
        (
            datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ).timestamp()
    )
    to_encode.update({"exp": expire_ts})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodifica y valida el JWT; retorna payload o `None` si es inválido."""

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
