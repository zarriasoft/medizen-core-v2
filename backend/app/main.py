import os
import time
import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .limiter import limiter
import socketio

from .database import engine, Base
from .routers import patients, memberships, membership_plans, programs, dashboard, appointments, auth, capture, ai, settings, patient_portal, payments
from .alerts import run_daily_alerts
from .notifications import check_upcoming_appointments, sio

# --- LOGGING ESTRUCTURADO ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "app.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger("medizen")

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MediZen Core 2.0 API iniciando...")
    scheduler.add_job(run_daily_alerts, "interval", hours=24, id="daily_alerts")
    scheduler.add_job(check_upcoming_appointments, "interval", hours=1, id="appointment_reminders")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    logger.info("MediZen Core 2.0 API detenida.")

app = FastAPI(title="MediZen Core 2.0 API", lifespan=lifespan)

# --- RATE LIMITING (compartido via app/limiter.py) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
_default_local_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]
_allow_origins_env = os.getenv("ALLOWED_ORIGINS")
if _allow_origins_env:
    allow_origins = [origin.strip() for origin in _allow_origins_env.split(",") if origin.strip()]
else:
    allow_origins = _default_local_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app" if not _allow_origins_env else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HTTP REQUEST LOGGING MIDDLEWARE ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "%s %s %d %.3fs",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(memberships.router)
app.include_router(membership_plans.router)
app.include_router(programs.router)
app.include_router(dashboard.router)
app.include_router(appointments.router)
app.include_router(capture.router)
app.include_router(settings.router)
app.include_router(ai.router)
app.include_router(patient_portal.router)
app.include_router(payments.router)

# --- WEBSOCKET (Socket.IO) ---
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@app.get("/")
def read_root():
    return {"message": "Welcome to MediZen Core 2.0 API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0"}
