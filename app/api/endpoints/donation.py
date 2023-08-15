from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import CharityProject
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationRead
from app.services.investing import investing_process

router = APIRouter()


@router.get(
    "/",
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
) -> List[DonationDB]:
    """[Только для Админа] Получить список всех пожертвований"""

    return await donation_crud.get_multi(session)


@router.get(
    "/my", response_model=List[DonationRead], response_model_exclude_none=True
)
async def get_user_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[DonationRead]:
    """[Для зарегистрированных пользователей] Получить список всех пожертвований текущего пользователя."""

    return await donation_crud.get_user_donations(user, session)


@router.post(
    "/", response_model=DonationRead, response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> DonationRead:
    """[Для зарегистрированных пользователей] Создать пожертвование."""

    donation = await donation_crud.create(donation, session, user)
    await investing_process(donation, CharityProject, session)

    return donation