from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.summary import Summary


class User(SQLModel, table=True):
    """Usuario persistido; `password` almacena el hash (no texto plano)."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=320, unique=True, index=True)
    password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )

    summaries: Mapped[List["Summary"]] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
