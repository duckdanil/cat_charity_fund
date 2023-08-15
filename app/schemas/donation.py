from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DonationCreate(BaseModel):
    """Базовая схема для работы с пожертвованиями."""

    full_amount: int = Field(..., gt=0)
    comment: Optional[str]


class DonationRead(DonationCreate):
    """Схема для просмотра пожертвования."""

    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationRead):
    """Схема для работы с проектом в БД."""

    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
