from datetime import datetime
from typing import List, Type, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_available_objects(
    obj_in: Union[CharityProject, Donation],
    session: AsyncSession,
) -> List[Union[CharityProject, Donation]]:
    """
    Ф-я для получения проектов, в которые можно инвестировать, и
    пожертвований, который доступны для инвестирования.
    """

    objects = await session.execute(
        select(obj_in)
        .where(obj_in.fully_invested == 0)
        .order_by(obj_in.create_date)
    )
    return objects.scalars().all()


async def close_donation_for_obj(
    obj_in: Union[CharityProject, Donation]
) -> Union[CharityProject, Donation]:
    """Ф-я закрытия для объекта (проекта или пожертвования)."""

    obj_in.invested_amount = obj_in.full_amount
    obj_in.fully_invested = True
    obj_in.close_date = datetime.now()

    return obj_in


async def investing_process(
    object_in: Union[CharityProject, Donation],
    model_class: Type[Union[CharityProject, Donation]],
    session: AsyncSession,
) -> Union[CharityProject, Donation]:
    """Ф-я, реализующая логику инвестирования в проекты."""

    available_objects = await get_available_objects(model_class, session)
    available_amount = object_in.full_amount

    if not available_objects:
        return object_in

    for not_invested_obj in available_objects:
        need_to_invest = (
            not_invested_obj.full_amount - not_invested_obj.invested_amount
        )

        to_invest = min(need_to_invest, available_amount)

        not_invested_obj.invested_amount += to_invest
        object_in.invested_amount += to_invest
        available_amount -= to_invest

        if not_invested_obj.full_amount == not_invested_obj.invested_amount:
            await close_donation_for_obj(not_invested_obj)

        if not available_amount:
            await close_donation_for_obj(object_in)
            break

    await session.commit()
    await session.refresh(object_in)

    return object_in
