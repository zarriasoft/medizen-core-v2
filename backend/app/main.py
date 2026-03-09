import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import patients, memberships, programs, dashboard, appointments, auth
from .alerts import run_alerts_check_job

# Crear las tablas en la BD (En prod se usa Alembic)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar cuando inicie FastAPI
    task = asyncio.create_task(run_alerts_check_job())
    yield
    # Limpiar cuando se apague
    task.cancel()

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

@app.get("/")
def read_root():
    return {"message": "Welcome to MediZen Core 2.0 API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "2.0"}
