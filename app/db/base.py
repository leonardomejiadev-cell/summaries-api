"""Import central de modelos para que Alembic recoja el metadata al autogenerar."""

from sqlmodel import SQLModel

from app.models.summary import Summary  # noqa: F401
from app.models.user import User  # noqa: F401

# Metadata único de SQLModel una vez registrados los modelos anteriores.
metadata = SQLModel.metadata

__all__ = ["User", "Summary", "metadata"]
