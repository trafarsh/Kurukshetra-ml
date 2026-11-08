"""API route routers package."""
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes.drivers import router as drivers_router
from app.api.routes.tracks import router as tracks_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.telemetry import router as telemetry_router
from app.api.routes.ml import router as ml_router

__all__ = [
    "health_router",
    "auth_router",
    "vehicles_router",
    "drivers_router",
    "tracks_router",
    "sessions_router",
    "telemetry_router",
    "ml_router",
]
