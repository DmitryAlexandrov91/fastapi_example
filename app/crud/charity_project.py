from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas import CharityProjectUpdate


class CRUDCharityProject(CRUDBase):
    """CRUD класс модели CharityProject."""

    async def get_charity_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
            updated_project_id: Optional[int] = None
    ) -> Optional[int]:
        select_expr = select(CharityProject.id).where(
            CharityProject.name == project_name
        )
        if updated_project_id is not None:
            select_expr = select_expr.where(
                CharityProject.id != updated_project_id
            )
        charity_poject_id = await session.execute(select_expr)
        return charity_poject_id.scalars().first()

    async def update(
        self,
        db_obj: CharityProject,
        obj_in: CharityProjectUpdate,
        session: AsyncSession
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if db_obj.full_amount < db_obj.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Запрещено устанавливать '
                'требуемую сумму меньше внесённой'
            )

        return await self.check_obj_after_update(obj=db_obj, session=session)

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> list[dict]:
        """Возвращает список словарей с закрытыми проектами."""

        select_expr = select(
            self.model).where(
            self.model.fully_invested
        ).order_by(
            extract('year', self.model.close_date) - func.extract(
                'year', self.model.create_date),
            extract('month', self.model.close_date) - func.extract(
                'month', self.model.create_date),
            extract('day', self.model.close_date) - func.extract(
                'day', self.model.create_date)
        )
        result = (
            await session.execute(select_expr)
        ).scalars().all()

        return [jsonable_encoder(project) for project in result]


charity_project_crud = CRUDCharityProject(CharityProject)
