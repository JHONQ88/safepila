@echo off
echo ==========================================
echo  SafePILA - Iniciando servicios...
echo ==========================================
echo.

echo [1/2] Iniciando Backend (puerto 8000)...
start "SafePILA Backend" cmd /c "cd /d "%~dp0backend" && call venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Frontend (puerto 3000)...
start "SafePILA Frontend" cmd /c "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ==========================================
echo  Servicios iniciados:
echo  - Backend:  http://localhost:8000
echo  - Frontend: http://localhost:3000
echo  - API Docs: http://localhost:8000/docs
echo ==========================================
echo.
echo Presiona cualquier tecla para salir...
pause >nul