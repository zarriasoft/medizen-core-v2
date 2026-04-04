@echo off
echo ==========================================
echo Iniciando MediZen Core 2.0 (Backend, Admin, Patient)
echo ==========================================

echo Limpiando procesos anteriores...
taskkill /f /im node.exe > nul 2>&1

echo Iniciando Backend (FastAPI)...
start "Medizen Backend" cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Iniciando Frontend Administrativo (React/Vite)...
start cmd /k "cd frontend && npm run dev"

echo Iniciando Portal de Pacientes (React/Vite)...
start cmd /k "cd patient-frontend && npm run dev"

echo.
echo Los servidores estan abriendo en nuevas ventanas.
echo Admin Frontend: verifica en la consola (usualmente http://localhost:5173 o 3000)
echo Patient Frontend: verifica en la consola (usualmente http://localhost:5174)
echo Backend disponible en: http://localhost:8000
echo.
pause
