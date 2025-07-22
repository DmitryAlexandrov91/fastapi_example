from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import donation_crud
from app.models import CharityProject, User
from app.schemas import DonationCreate, DonationDB, DonationMultiDB
from app.services.investment_process import investment_process

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationMultiDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров.

    Возвращает список всех пожертвований.
    """
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=list[DonationDB],
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Вернуть список пожертвований пользователя, выполняющего запрос."""
    return await donation_crud.get_current_user_donations(
        session=session,
        user=user
    )


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """Сделать пожертвование.."""
    new_donation = await donation_crud.create(
        donation, session, user=user)
    return await investment_process(
        created_obj=new_donation,
        source_model=CharityProject,
        crud=donation_crud,
        session=session
    )
