from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health() -> dict[str, str]:
    """Verifica que la API está activa."""

    return {"status": "ok"}
