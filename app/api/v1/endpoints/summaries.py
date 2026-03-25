from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.schemas.summary import SummaryCreate, SummaryRead, SummaryUpdate
from app.services import summary_service

router = APIRouter()


@router.post("/", response_model=SummaryRead, status_code=status.HTTP_201_CREATED)
async def create_summary(
    body: SummaryCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SummaryRead:
    """Crea un resumen asociado al usuario autenticado."""

    summary = await summary_service.create(
        session,
        body.url,
        body.title,
        current_user.id,
    )
    return SummaryRead.model_validate(summary)


@router.get("/", response_model=list[SummaryRead])
async def list_summaries(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[SummaryRead]:
    """Lista todos los resúmenes del usuario autenticado."""

    items = await summary_service.get_all(session, current_user.id)
    return [SummaryRead.model_validate(s) for s in items]


@router.get("/{summary_id}", response_model=SummaryRead)
async def get_summary(
    summary_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SummaryRead:
    """Obtiene un resumen por ID si pertenece al usuario autenticado."""

    summary = await summary_service.get_one(session, summary_id, current_user.id)
    return SummaryRead.model_validate(summary)


@router.put("/{summary_id}", response_model=SummaryRead)
async def update_summary(
    summary_id: int,
    body: SummaryUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> SummaryRead:
    """Actualiza un resumen existente (campos enviados en el body)."""

    data = body.model_dump(exclude_unset=True)
    summary = await summary_service.update(
        session,
        summary_id,
        current_user.id,
        data,
    )
    return SummaryRead.model_validate(summary)


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(
    summary_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Elimina un resumen si pertenece al usuario autenticado."""

    await summary_service.delete(session, summary_id, current_user.id)
