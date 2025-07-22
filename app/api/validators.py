from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
        updated_project_id: Optional[int] = None
) -> None:
    """Проверяет по имени наличие объекта в модели CharityProject.

    Опциональным аргyментом updated_project_id исключает из выборки
    редактируемый объект.
    """
    project_id = await charity_project_crud.get_charity_project_id_by_name(
        project_name, session, updated_project_id=updated_project_id)
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_charity_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверяет по id наличие объекта CharityProject"""
    charity_project = await charity_project_crud.get(
        project_id, session
    )
    if charity_project is None:
        if charity_project is None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Проект не найден!'
            )
    return charity_project


async def check_charity_project_before_remove(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверяет объект CharityProject на наличие и внесённые средства."""
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    if charity_project.invested_amount != 0 or (
        charity_project.fully_invested
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return charity_project


async def check_charity_project_before_update(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверяет объект CharityProject на наличие и fully_invested."""
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charity_project
