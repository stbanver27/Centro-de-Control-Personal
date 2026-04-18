from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.models.project import Task, TaskStatus, Project
from backend.services import finance_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now()
    month, year = now.month, now.year

    # Financial
    summary = finance_service.get_monthly_summary(db, current_user.id, month, year)
    balance = finance_service.get_all_time_balance(db, current_user.id)
    recent_transactions = finance_service.get_transactions(db, current_user.id, limit=5)

    # Projects & Tasks
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    all_tasks = db.query(Task).join(Project).filter(Project.user_id == current_user.id).all()

    pending_tasks = [t for t in all_tasks if t.status == TaskStatus.pending]
    in_progress_tasks = [t for t in all_tasks if t.status == TaskStatus.in_progress]

    # Alerts
    alerts = []
    if len(pending_tasks) > 10:
        alerts.append({"type": "warning", "message": f"Tienes {len(pending_tasks)} tareas pendientes acumuladas."})
    if summary.total_expense > summary.total_income and summary.total_income > 0:
        alerts.append({"type": "danger", "message": "Tus gastos este mes superan tus ingresos."})
    if balance < 0:
        alerts.append({"type": "danger", "message": "Tu balance general es negativo."})
    if summary.total_expense > 500000 and summary.total_income == 0:
        alerts.append({"type": "info", "message": "No has registrado ingresos este mes."})

    return {
        "user": {"name": current_user.name},
        "finance": {
            "balance": balance,
            "monthly_income": summary.total_income,
            "monthly_expense": summary.total_expense,
            "monthly_balance": summary.balance,
            "recent_transactions": [
                {
                    "id": t.id,
                    "type": t.type,
                    "amount": t.amount,
                    "description": t.description,
                    "date": t.date.isoformat(),
                    "category": {"name": t.category.name, "icon": t.category.icon} if t.category else None,
                }
                for t in recent_transactions
            ],
        },
        "projects": {
            "total": len(projects),
            "active": len([p for p in projects if any(t.status != TaskStatus.done for t in p.tasks)]),
        },
        "tasks": {
            "total": len(all_tasks),
            "pending": len(pending_tasks),
            "in_progress": len(in_progress_tasks),
            "done": len([t for t in all_tasks if t.status == TaskStatus.done]),
            "pending_list": [
                {
                    "id": t.id,
                    "title": t.title,
                    "priority": t.priority,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "project": t.project.name,
                }
                for t in sorted(pending_tasks, key=lambda x: (x.priority != "high", x.due_date or datetime.max))[:5]
            ],
        },
        "alerts": alerts,
    }
