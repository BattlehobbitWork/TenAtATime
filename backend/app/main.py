"""Ten at a Time -- FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB, start scheduler."""
    await init_db()
    logger.info("Database initialized and seeded.")

    # Start reminder scheduler
    try:
        from app.services.scheduler import start_scheduler
        start_scheduler()
        logger.info("Reminder scheduler started.")
    except Exception as e:
        logger.warning(f"Scheduler failed to start (non-critical): {e}")

    yield

    # Shutdown
    try:
        from app.services.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
from app.routes import tasks, settings as settings_routes, push, auth  # noqa: E402

app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")
app.include_router(push.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


# Auth middleware -- protect all /api routes except auth and health
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for login, verify, and health endpoints
    path = request.url.path
    if (path in ["/api/health", "/api/auth/login", "/api/auth/verify", "/api/auth/logout"]
            or not path.startswith("/api")):
        return await call_next(request)

    # If no password configured, allow all
    if not settings.auth_password:
        return await call_next(request)

    # Check for valid token
    from app.routes.auth import _active_tokens
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        if token in _active_tokens:
            return await call_next(request)

    return JSONResponse(status_code=401, content={"detail": "Please sign in."})


# Serve frontend static files (in production, nginx handles this)
import os  # noqa: E402
dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")
