from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import patients, memberships, membership_plans, programs, dashboard, appointments, auth, capture, ai, settings, patient_portal
from .alerts import run_daily_alerts

import logging
logging.basicConfig(level=logging.INFO)

# Crear las tablas en la BD (En prod se usa Alembic)
Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ejecutar chequeo al arrancar y luego cada 24 horas
    scheduler.add_job(run_daily_alerts, "interval", hours=24, id="daily_alerts")
    scheduler.start()
    run_daily_alerts()  # Primera ejecucion al arrancar
    yield
    scheduler.shutdown(wait=False)

app = FastAPI(title="MediZen Core 2.0 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "https://medizen-frontend.vercel.app",
        "https://patient-frontend-iota.vercel.app",
        "https://patient-frontend-nbieonvsf-zarriasofts-projects.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to MediZen Core 2.0 API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0"}
