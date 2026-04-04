@echo off
title Iniciador de Medizen Completo
color 0b

echo =======================================================
echo          MEDIZEN CORE 2.0 - ENTORNO DE DESARROLLO
echo =======================================================
echo.

echo Limpiando procesos anteriores...
taskkill /f /im node.exe > nul 2>&1

echo Iniciando el servidor Backend (FastAPI)...
start "Medizen Backend" cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo Iniciando el Portal Administrativo (React)...
start "Medizen Admin" cmd /k "cd frontend & npm run dev"

echo Iniciando el Portal de Pacientes (React)...
start "Medizen Patient Portal" cmd /k "cd patient-frontend & npm run dev"

echo.
echo =======================================================
echo POR FAVOR REVISA LAS CONSOLAS PARA LOS ENLACES.
echo Backend: http://localhost:8000
echo =======================================================
echo.
pause
