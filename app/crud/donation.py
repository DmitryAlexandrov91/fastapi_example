from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    """CRUD класс модели Donation."""

    async def get_current_user_donations(
            self,
            session: AsyncSession,
            user: User
    ):
        """Возвращает список пожертвований пользователя."""
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id,
            )
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
