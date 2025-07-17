@echo off
echo Iniciando servidor Flask...
start /b python app.py

echo Esperando que el servidor inicie...
timeout /t 3 /nobreak >nul

echo Iniciando Cloudflare Tunnel...
cloudflared tunnel --url http://192.168.1.105:5000

pause
