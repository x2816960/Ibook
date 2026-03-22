from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models import User, TokenBlacklist, Task, Attachment, SystemConfig  # noqa: F401
from app.routers import auth, tasks, attachments, admin, backup

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.services.auth_service import init_admin
        from app.models.system_config import init_system_config
        init_admin(db)
        init_system_config(db)
    finally:
        db.close()

    from app.utils.cleanup import cleanup_trash, cleanup_token_blacklist
    scheduler.add_job(cleanup_trash, "interval", hours=1, id="cleanup_trash")
    scheduler.add_job(cleanup_token_blacklist, "interval", hours=1, id="cleanup_blacklist")
    scheduler.start()

    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Ibook", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(attachments.router)
app.include_router(admin.router)
app.include_router(backup.router)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """SPA catch-all: 非 API 路径返回 index.html"""
        file_path = static_dir / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(static_dir / "index.html"))
