from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from backend.models.finance import TransactionType


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    type: TransactionType

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float
    description: str
    category_id: Optional[int] = None
    date: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransactionOut(BaseModel):
    id: int
    type: TransactionType
    amount: float
    description: str
    date: datetime
    created_at: datetime
    category: Optional[CategoryOut] = None

    model_config = {"from_attributes": True}


class MonthlySummary(BaseModel):
    month: int
    year: int
    total_income: float
    total_expense: float
    balance: float


class CategorySummary(BaseModel):
    category_name: str
    category_icon: str
    category_color: str
    total: float
