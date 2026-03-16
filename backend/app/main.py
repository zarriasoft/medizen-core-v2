from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import patients, memberships, programs, dashboard, appointments, auth, capture
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(memberships.router)
app.include_router(programs.router)
app.include_router(dashboard.router)
app.include_router(appointments.router)
app.include_router(capture.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to MediZen Core 2.0 API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0"}
