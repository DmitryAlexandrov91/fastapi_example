from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

from .constants import (CHAR_PRJ_DESCRIPTION_MIN_LENGTH,
                        CHAR_PRJ_NAME_MAX_LENGTH, CHAR_PRJ_NAME_MIN_LENGTH)


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=CHAR_PRJ_NAME_MIN_LENGTH,
        max_length=CHAR_PRJ_NAME_MAX_LENGTH)
    description: Optional[str] = Field(
        None,
        min_length=CHAR_PRJ_DESCRIPTION_MIN_LENGTH)
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(
        ...,
        min_length=CHAR_PRJ_NAME_MIN_LENGTH,
        max_length=CHAR_PRJ_NAME_MAX_LENGTH)
    description: str = Field(
        ...,
        min_length=CHAR_PRJ_NAME_MIN_LENGTH)
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):
    pass


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True