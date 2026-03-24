"""Import central de modelos para que Alembic recoja el metadata al autogenerar."""

from app.models.summary import Summary  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["User", "Summary"]
