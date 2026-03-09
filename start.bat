@echo off
echo ==========================================
echo Iniciando MediZen Core 2.0 (Backend y Frontend)
echo ==========================================

echo Iniciando Backend (FastAPI)...
start cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Iniciando Frontend (React/Vite)...
start cmd /k "cd frontend && npm run dev"

echo.
echo Los servidores estan abriendo en nuevas ventanas.
echo Frontend disponible en: http://localhost:3000 o http://localhost:5173 (mira la consola web)
echo Backend disponible en: http://localhost:8000
echo.
pause
