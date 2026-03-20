@echo off
echo ==========================================
echo Iniciando Portal de Pacientes MediZen
echo ==========================================

echo Iniciando Backend (FastAPI)...
start cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Iniciando Frontend del Portal de Pacientes...
start cmd /k "cd patient-frontend && npm run dev"

echo.
echo Los servidores estan abriendo en nuevas ventanas.
echo Backend disponible en: http://localhost:8000
echo.
echo Dale unos segundos al Frontend y revisa tu navegador en:
echo http://localhost:5174 (o el puerto que indique la ventana CMD)
echo.
pause
