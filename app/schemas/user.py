from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload para registrar un usuario (contraseña en claro; se hashea en el servicio)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    """Usuario expuesto por la API (sin contraseña)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Actualización parcial; solo se aplican campos enviados."""

    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
