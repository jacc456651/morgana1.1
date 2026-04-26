@echo off
echo [Morgana UI] Iniciando...

IF NOT EXIST "%~dp0app\dist" (
    echo [Morgana UI] Primera vez: construyendo frontend...
    cd /d "%~dp0app"
    call npm install
    call node_modules\.bin\vite build
    cd /d "%~dp0"
)

echo [Morgana UI] Servidor en http://localhost:8080
py "%~dp0server.py"
