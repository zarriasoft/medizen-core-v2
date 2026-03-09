@echo off
title Iniciador de Medizen
color 0b

echo =======================================================
echo          MEDIZEN CORE 2.0 - ENTORNO DE DESARROLLO
echo =======================================================
echo.

echo Iniciando el servidor Backend (FastAPI)...
start "Medizen Backend" cmd /k "cd backend & if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) & uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo Iniciando el servidor Frontend (React)...
start "Medizen Frontend" cmd /k "cd frontend & npm run dev"

echo.
echo =======================================================
echo POR FAVOR REVISA LA VENTANA "Medizen Frontend"
echo Ahi dira exactamente el enlace para entrar (ej. http://localhost:3000)
echo Copia ese enlace y pegalo en Chrome.
echo =======================================================
echo.
pause
