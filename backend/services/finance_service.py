from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime

from backend.models.finance import Transaction, Category, TransactionType
from backend.schemas.finance import TransactionCreate, MonthlySummary, CategorySummary


def get_categories(db: Session) -> List[Category]:
    return db.query(Category).all()


def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        type=data.type,
        amount=data.amount,
        description=data.description,
        category_id=data.category_id,
        date=data.date or datetime.utcnow(),
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transactions(
    db: Session,
    user_id: int,
    month: Optional[int] = None,
    year: Optional[int] = None,
    transaction_type: Optional[TransactionType] = None,
    limit: int = 100,
) -> List[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if month:
        query = query.filter(extract("month", Transaction.date) == month)
    if year:
        query = query.filter(extract("year", Transaction.date) == year)
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)

    return query.order_by(Transaction.date.desc()).limit(limit).all()


def delete_transaction(db: Session, user_id: int, transaction_id: int) -> bool:
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id,
    ).first()
    if not tx:
        return False
    db.delete(tx)
    db.commit()
    return True


def get_monthly_summary(db: Session, user_id: int, month: int, year: int) -> MonthlySummary:
    def _sum(tx_type):
        result = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == tx_type,
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year,
        ).scalar()
        return float(result or 0)

    income = _sum(TransactionType.income)
    expense = _sum(TransactionType.expense)
    return MonthlySummary(
        month=month,
        year=year,
        total_income=income,
        total_expense=expense,
        balance=income - expense,
    )


def get_expense_by_category(db: Session, user_id: int, month: int, year: int) -> List[CategorySummary]:
    rows = (
        db.query(
            Category.name,
            Category.icon,
            Category.color,
            func.sum(Transaction.amount).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.expense,
            extract("month", Transaction.date) == month,
            extract("year", Transaction.date) == year,
        )
        .group_by(Category.id)
        .all()
    )
    return [
        CategorySummary(
            category_name=r.name,
            category_icon=r.icon,
            category_color=r.color,
            total=float(r.total),
        )
        for r in rows
    ]


def get_all_time_balance(db: Session, user_id: int) -> float:
    def _sum(tx_type):
        result = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == tx_type,
        ).scalar()
        return float(result or 0)

    return _sum(TransactionType.income) - _sum(TransactionType.expense)
