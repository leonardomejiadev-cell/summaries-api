from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, Index, Text, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class Summary(SQLModel, table=True):
    """Resumen asociado a una URL y a un usuario propietario."""

    __tablename__ = "summaries"
    __table_args__ = (Index("ix_summaries_owner_id_url", "owner_id", "url"),)

    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(max_length=2048, index=True)
    title: str | None = Field(default=None, max_length=500)
    summary_text: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    owner_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    owner: Optional["User"] = Relationship(back_populates="summaries")
