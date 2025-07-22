from typing import Union

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import CharityProject, Donation


async def invest_amount(
    source_obj: Union[CharityProject, Donation],
    target_obj: Union[CharityProject, Donation]
):
    """Инвестирует средства из одного объекта в другой."""
    source_remaining = source_obj.full_amount - source_obj.invested_amount
    target_remaining = target_obj.full_amount - target_obj.invested_amount

    if source_remaining <= target_remaining:
        source_obj.invested_amount += source_remaining
        target_obj.invested_amount += source_remaining
    else:
        source_obj.invested_amount += target_remaining
        target_obj.invested_amount += target_remaining


async def investment_process(
    created_obj: Union[CharityProject, Donation],
    source_model: Union[CharityProject, Donation],
    crud,
    session: AsyncSession = Depends(get_async_session),
):
    """Запускает процесс инвестирования.

    created_obj - созданный объект (новый проект или пожертвование)
    source_model - проверяемая модель на наличие открытых объектов
    (проектов или пожертвований).

    Возвращает обновлённый созданный объект.
    """
    open_objs = await crud.get_open_objs(source_model, session)
    if not open_objs:
        return created_obj

    is_donation = isinstance(created_obj, Donation)

    for obj in open_objs:
        if is_donation:
            await invest_amount(created_obj, obj)
        else:
            await invest_amount(obj, created_obj)
        await crud.try_to_close_obj(obj)

    return await crud.check_obj_after_update(created_obj, session)