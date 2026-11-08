"""
Kurukshetra Kart Telemetry & Digital Twin Platform — Main Application Entrypoint.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.core.exceptions import KartException
from app.core.logging_config import get_logger
from app.core.security import hash_password
from app.models.user import Role, User
from app.telemetry.websocket_manager import ws_manager
from app.api.routes import (
    health_router,
    auth_router,
    vehicles_router,
    drivers_router,
    tracks_router,
    sessions_router,
    telemetry_router,
    ml_router,
    phase7_router,
)

logger = get_logger("main")


def seed_initial_data():
    """Seed initial master roles and default admin user if database is fresh."""
    db = SessionLocal()
    try:
        roles = [
            ("ADMIN", "System administrator with full privileges"),
            ("TELEMETRY_ENGINEER", "Pit-wall real-time sensor monitor"),
            ("DATA_ENGINEER", "Pipeline, dataset cleaning and quality engineer"),
            ("ML_ENGINEER", "Predictive modeling and training engineer"),
            ("DYNAMICS_ENGINEER", "Vehicle dynamics, simulation and digital twin specialist"),
            ("DRIVER", "Kart driver performance analytics access"),
            ("TEAM_MANAGER", "Executive performance and reporting access"),
        ]
        role_map = {}
        for r_name, r_desc in roles:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=r_desc)
                db.add(role)
                db.flush()
            role_map[r_name] = role

        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@kurukshetraracing.skcet.ac.in",
                hashed_password=hash_password("admin123"),
                role_id=role_map["ADMIN"].id,
                is_active=True,
            )
            db.add(admin)
            logger.info("Created default administrator account: admin / admin123")

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed initial master data: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    logger.info("Initializing database schemas...")
    init_db()
    seed_initial_data()
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} online.")
    yield
    logger.info("Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Motorsport Telemetry, Machine Learning & Calibrated Physics Digital Twin Platform.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(KartException)
async def kart_exception_handler(request: Request, exc: KartException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


# WebSocket live streaming endpoint
@app.websocket("/ws/v1/telemetry/{session_id}")
async def websocket_telemetry_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or client commands
            if "ping" in data:
                await websocket.send_json({"type": "pong", "session_id": session_id})
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)


# Include API v1 Routers
app.include_router(health_router, prefix="")
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(vehicles_router, prefix=settings.API_V1_STR)
app.include_router(drivers_router, prefix=settings.API_V1_STR)
app.include_router(tracks_router, prefix=settings.API_V1_STR)
app.include_router(sessions_router, prefix=settings.API_V1_STR)
app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(ml_router, prefix=settings.API_V1_STR)
app.include_router(phase7_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "team": "Kurukshetra Racing, SKCET",
        "competition": "EKVC Season 4 — Innovation Round",
        "documentation": "/docs",
        "health": "/health",
        "websocket": "/ws/v1/telemetry/{session_id}",
    }
