from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_name_duplicate(project_name: str, session: AsyncSession) -> None:
    """Проверка отсутствия проекта с таким именем."""
    project_id = await charity_project_crud.get_project_id_by_name(project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Проект с таким именем уже существует!"
        )


async def check_charity_project_exists(project_id: int, session: AsyncSession) -> CharityProject:
    """Проверка существования проекта по его id."""
    project = await charity_project_crud.get_charity_project_by_id(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден!"
        )
    return project


def check_charity_project_invested_sum(project: CharityProject, new_amount: int):
    """Проверка доступности целевой суммы в рамках уже существующих пожертвований."""
    if project.invested_amount > new_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Целевая сумма должна быть больше уже пожертвованной!"
        )


def check_charity_project_already_invested(charity_project: CharityProject):
    """Проверка наличия пожертвований в проект."""
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="В проект были внесены средства, не подлежит удалению!"
        )


def check_charity_project_closed(charity_project: CharityProject):
    """Проверка того, закрыт ли проект."""
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Закрытый проект нельзя редактировать!"
        )
