from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from backend.core.security import hash_password
from backend.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME
from backend.models.user import User
from backend.models.finance import Category, Transaction, TransactionType
from backend.models.project import Project, Task, TaskStatus, Priority


EXPENSE_CATEGORIES = [
    ("Alimentación", "🍔", "#ef4444"),
    ("Transporte", "🚗", "#f97316"),
    ("Vivienda", "🏠", "#8b5cf6"),
    ("Salud", "💊", "#06b6d4"),
    ("Entretenimiento", "🎮", "#ec4899"),
    ("Educación", "📚", "#10b981"),
    ("Ropa", "👕", "#f59e0b"),
    ("Servicios", "💡", "#6366f1"),
]

INCOME_CATEGORIES = [
    ("Salario", "💼", "#22c55e"),
    ("Freelance", "💻", "#3b82f6"),
    ("Inversiones", "📈", "#a855f7"),
]


def seed_database(db: Session):
    # Admin user
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        return  # Already seeded

    user = User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        hashed_password=hash_password(ADMIN_PASSWORD),
    )
    db.add(user)
    db.flush()

    # Categories
    cat_objects = {}
    for name, icon, color in EXPENSE_CATEGORIES:
        c = Category(name=name, icon=icon, color=color, type=TransactionType.expense)
        db.add(c)
        db.flush()
        cat_objects[name] = c

    for name, icon, color in INCOME_CATEGORIES:
        c = Category(name=name, icon=icon, color=color, type=TransactionType.income)
        db.add(c)
        db.flush()
        cat_objects[name] = c

    # Transactions — last 3 months
    now = datetime.utcnow()
    expense_cats = [cat_objects[n] for n, _, _ in EXPENSE_CATEGORIES]
    income_cats = [cat_objects[n] for n, _, _ in INCOME_CATEGORIES]

    for days_back in range(90):
        date = now - timedelta(days=days_back)

        # ~2 expenses/day
        for _ in range(random.randint(1, 3)):
            cat = random.choice(expense_cats)
            amount = round(random.uniform(1000, 80000), 0)
            db.add(Transaction(
                user_id=user.id,
                type=TransactionType.expense,
                amount=amount,
                description=f"Gasto en {cat.name}",
                category_id=cat.id,
                date=date,
            ))

        # Income ~monthly
        if days_back % 30 == 0:
            cat = cat_objects["Salario"]
            db.add(Transaction(
                user_id=user.id,
                type=TransactionType.income,
                amount=1_800_000,
                description="Salario mensual",
                category_id=cat.id,
                date=date,
            ))

    # Projects
    projects_data = [
        {
            "name": "Portfolio Web",
            "description": "Sitio web personal con proyectos y CV",
            "color": "#6366f1",
            "tasks": [
                ("Diseñar wireframes", TaskStatus.done, Priority.high),
                ("Desarrollar landing page", TaskStatus.done, Priority.high),
                ("Integrar proyectos", TaskStatus.in_progress, Priority.medium),
                ("SEO y optimización", TaskStatus.pending, Priority.low),
                ("Deploy en Vercel", TaskStatus.pending, Priority.medium),
            ],
        },
        {
            "name": "App ControlOS",
            "description": "Segunda mente personal: dinero + proyectos",
            "color": "#10b981",
            "tasks": [
                ("Backend FastAPI", TaskStatus.done, Priority.high),
                ("Modelos y migraciones", TaskStatus.done, Priority.high),
                ("Frontend dashboard", TaskStatus.in_progress, Priority.high),
                ("Módulo de finanzas", TaskStatus.in_progress, Priority.medium),
                ("Módulo kanban", TaskStatus.pending, Priority.medium),
                ("Testing e2e", TaskStatus.pending, Priority.low),
            ],
        },
        {
            "name": "Aprendizaje 2024",
            "description": "Track de cursos y certificaciones",
            "color": "#f59e0b",
            "tasks": [
                ("FastAPI avanzado", TaskStatus.done, Priority.high),
                ("React + TypeScript", TaskStatus.in_progress, Priority.medium),
                ("Docker & DevOps", TaskStatus.pending, Priority.medium),
                ("AWS Cloud Practitioner", TaskStatus.pending, Priority.low),
            ],
        },
    ]

    for p_data in projects_data:
        project = Project(
            user_id=user.id,
            name=p_data["name"],
            description=p_data["description"],
            color=p_data["color"],
        )
        db.add(project)
        db.flush()

        for title, status, priority in p_data["tasks"]:
            due = now + timedelta(days=random.randint(5, 60)) if status != TaskStatus.done else None
            db.add(Task(
                project_id=project.id,
                title=title,
                status=status,
                priority=priority,
                due_date=due,
            ))

    db.commit()
    print("✅ Database seeded successfully")
    print(f"   Email: {ADMIN_EMAIL}")
    print(f"   Password: {ADMIN_PASSWORD}")
