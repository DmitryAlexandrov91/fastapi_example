from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_charity_project_before_remove,
                                check_charity_project_before_update,
                                check_name_duplicate)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.models import Donation
from app.schemas import (CharityProjectCreate, CharityProjectDB,
                         CharityProjectUpdate)
from app.services.investment_process import investment_process

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """Возвращает список всех проектов."""
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров.

    Создаёт благотворительный проект.
    """
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(
        charity_project, session)
    return await investment_process(
        created_obj=new_project,
        source_model=Donation,
        crud=charity_project_crud,
        session=session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров.

    Удаляет проект. Нельзя удалить проект,
    в который уже были инвестированы средства, его можно только закрыть.
    """
    charity_project = await check_charity_project_before_remove(
        project_id, session
    )
    return await charity_project_crud.remove(
        charity_project, session
    )


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров.

    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await check_charity_project_before_update(
        project_id, session
    )
    if obj_in.name is not None:
        await check_name_duplicate(
            obj_in.name,
            session,
            updated_project_id=project_id)

    return await charity_project_crud.update(
        charity_project, obj_in, session
    )
