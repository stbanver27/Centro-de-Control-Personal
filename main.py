from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.core.database import engine, Base, SessionLocal
from backend.models import user, finance, project  # register models
from backend.routers import auth, finance as finance_router, projects, dashboard
from backend.services.seed import seed_database

# Create tables + seed
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_database(db)

app = FastAPI(title="ControlOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router,           prefix="/api")
app.include_router(finance_router.router, prefix="/api")
app.include_router(projects.router,       prefix="/api")
app.include_router(dashboard.router,      prefix="/api")

# Paths
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CSS_DIR      = os.path.join(FRONTEND_DIR, "css")
JS_DIR       = os.path.join(FRONTEND_DIR, "js")

# Static assets
app.mount("/static", StaticFiles(directory=CSS_DIR), name="static")
app.mount("/js",     StaticFiles(directory=JS_DIR),  name="js")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/{page_name}", include_in_schema=False)
def serve_page(page_name: str):
    path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
    if os.path.isfile(path):
        return FileResponse(path)
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))
