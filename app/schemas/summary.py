from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SummaryCreate(BaseModel):
    """Datos para crear un resumen asociado a una URL."""

    url: str = Field(min_length=1, pattern=r'^https?://')
    title: str | None = None


class SummaryRead(BaseModel):
    """Resumen completo tal como se expone en la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    title: str | None
    summary_text: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime


class SummaryUpdate(BaseModel):
    """Actualización parcial de metadatos del resumen."""

    url: str | None = Field(default=None, min_length=1, pattern=r'^https?://')
    title: str | None = None
