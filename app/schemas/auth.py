from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credenciales para obtener un JWT."""

    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Respuesta estándar OAuth2-style (Bearer)."""

    access_token: str
    token_type: str = "bearer"
