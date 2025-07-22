from datetime import datetime
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation, User


class CRUDBase:

    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_by_attribute(
            self,
            attr_name: str,
            attr_value: str,
            session: AsyncSession,
    ):
        attr = getattr(self.model, attr_name)
        db_obj = await session.execute(
            select(self.model).where(attr == attr_value)
        )
        return db_obj.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession,
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            user: Optional[User] = None
    ):
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def try_to_close_obj(
        self,
        obj: Union[CharityProject, Donation]
    ):
        """Закрывает проект или пожертвование."""
        if obj.full_amount == obj.invested_amount:
            obj.fully_invested = True
            obj.close_date = datetime.now()

    async def check_obj_after_update(
        self,
        obj: Union[CharityProject, Donation],
        session: AsyncSession
    ) -> Union[CharityProject, Donation]:
        """Закрывает проект или пожертвование. Сохраняет в бд."""
        await self.try_to_close_obj(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_open_objs(
        self,
        source_model: Union[CharityProject, Donation],
        session: AsyncSession
    ):
        """Возвращает список открытых объектов (проектов или пожертвований)."""
        select_open_objs = select(source_model).where(
            source_model.fully_invested == 0
        ).order_by(source_model.id)
        return (await session.execute(select_open_objs)).scalars().all()

    async def remove(
            self,
            db_obj,
            session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj
