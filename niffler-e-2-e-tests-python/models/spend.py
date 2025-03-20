from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    __tablename__ = 'category'
    id: Optional[str] = Field(default=None, primary_key=True)
    category: str = Field(alias="name")
    username: str


class Spend(SQLModel, table=True):
    __tablename__ = 'spend'
    id: Optional[str] = Field(default=None, primary_key=True)
    amount: float
    description: str
    category_id: Optional[str] = Field(default=None, foreign_key="category.id")
    spend_date: Optional[datetime] = Field(default=None, alias="spendDate")
    currency: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)


class SpendAdd(BaseModel):
    amount: float
    description: str
    category: str
    spendDate: str
    currency: str