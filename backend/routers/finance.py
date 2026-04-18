from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.models.finance import TransactionType
from backend.schemas.finance import (
    TransactionCreate, TransactionOut, CategoryOut,
    MonthlySummary, CategorySummary,
)
from backend.services import finance_service

router = APIRouter(prefix="/finance", tags=["finance"])


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return finance_service.get_categories(db)


@router.post("/transactions", response_model=TransactionOut, status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.create_transaction(db, current_user.id, data)


@router.get("/transactions", response_model=List[TransactionOut])
def list_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    type: Optional[TransactionType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.get_transactions(db, current_user.id, month, year, type)


@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    finance_service.delete_transaction(db, current_user.id, transaction_id)


@router.get("/summary", response_model=MonthlySummary)
def monthly_summary(
    month: int = Query(default=datetime.now().month, ge=1, le=12),
    year: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.get_monthly_summary(db, current_user.id, month, year)


@router.get("/summary/categories", response_model=List[CategorySummary])
def category_summary(
    month: int = Query(default=datetime.now().month, ge=1, le=12),
    year: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finance_service.get_expense_by_category(db, current_user.id, month, year)


@router.get("/balance")
def balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"balance": finance_service.get_all_time_balance(db, current_user.id)}
