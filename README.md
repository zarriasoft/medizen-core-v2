# MediZen Core v2

Plataforma de gestión clínica de bienestar integral con índice IEIM (Índice de Equilibrio Integral Medicen).

**Stack:** FastAPI + React + PostgreSQL | **Lenguaje:** Python 3.12 + TypeScript

## Arquitectura

```
v2/
├── backend/             # API REST FastAPI
│   └── app/
│       ├── routers/     # auth, patients, memberships, dashboard, appointments, capture, ai, settings, patient_portal
│       ├── models.py    # SQLAlchemy ORM (13 tablas)
│       ├── schemas.py   # Pydantic validators
│       └── crud.py      # Operaciones CRUD reutilizables
├── frontend/            # Portal administrativo (React + Vite + TypeScript)
└── patient-frontend/    # Portal de pacientes (React + Vite + TypeScript)
```

## Requisitos previos

- Python 3.12+
- Node.js 22+
- PostgreSQL 15 (opcional, también funciona con SQLite local)

## Instalación

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configurar variables de entorno
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (Portal Administrativo)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev  # http://localhost:5173
```

### 3. Patient Frontend (Portal de Pacientes)

```bash
cd patient-frontend
npm install
cp .env.example .env
npm run dev  # http://localhost:5174
```

## Docker

```bash
cp .env.docker.example .env.docker
docker compose up --build
```

Servicios: PostgreSQL (5432), Backend (8000), Frontend (5173), Patient Frontend (5174)

## Scripts disponibles

| Comando | Descripción |
|---|---|
| `pytest -v` | Ejecutar tests backend |
| `npm test` | Ejecutar tests frontend |
| `npm run lint` | Verificar tipos TypeScript |
| `python backup_all.py` | Respaldo completo (DB local + cloud + app) |
| `python backup_all.py --db` | Solo base de datos local |
| `python backup_all.py --cloud` | Solo base de datos cloud (Neon) |
| `python backup_all.py --files` | Solo archivos de la app |

## API

Swagger UI disponible en `http://localhost:8000/docs` (OpenAPI).

Endpoints principales:
- `POST /auth/login` — Login admin/staff
- `POST /auth/login/patient` — Login paciente
- `GET/POST /patients/` — CRUD pacientes
- `POST /patients/{id}/ieim/` — Registrar evaluación IEIM
- `GET /dashboard/metrics` — Métricas del dashboard
- `POST /public/capture` — Captación pública (test IEIM)
- `POST /public/enroll` — Inscripción de paciente

## Pruebas

```bash
# Backend (31 tests)
cd backend && pytest -v

# Frontend (10 tests)
cd frontend && npm test

# Patient Frontend (11 tests)
cd patient-frontend && npm test
```

## CI/CD

GitHub Actions configurado en `.github/workflows/ci.yml`:
- Backend tests (pytest)
- Frontend tests (vitest)
- Patient frontend tests (vitest)
- Type check (tsc --noEmit)

## Variables de entorno

Ver `.env.example` en cada subproyecto para la lista completa de variables requeridas.
