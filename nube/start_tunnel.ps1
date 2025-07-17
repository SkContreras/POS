# Script para iniciar POS con Cloudflare Tunnel
Write-Host "🚀 Iniciando Sistema POS con Cloudflare Tunnel..." -ForegroundColor Green

# Verificar si cloudflared está instalado
try {
    $null = Get-Command cloudflared -ErrorAction Stop
    Write-Host "✅ cloudflared encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ cloudflared no encontrado. Instalando..." -ForegroundColor Red
    winget install --id Cloudflare.cloudflared
    Write-Host "✅ cloudflared instalado" -ForegroundColor Green
}

# Verificar si Python está disponible
try {
    $null = Get-Command python -ErrorAction Stop
    Write-Host "✅ Python encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Instala Python primero." -ForegroundColor Red
    exit 1
}

# Instalar dependencias si es necesario
if (-not (Test-Path "venv")) {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "🔄 Iniciando servidor Flask..." -ForegroundColor Yellow
$flaskProcess = Start-Process python -ArgumentList "app.py" -PassThru -WindowStyle Hidden

# Esperar a que Flask inicie
Start-Sleep -Seconds 5

# Verificar si el servidor está corriendo
try {
    $response = Invoke-WebRequest -Uri "http://192.168.1.105:5000" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✅ Servidor Flask iniciado correctamente" -ForegroundColor Green
    Write-Host "📍 Servidor local: http://192.168.1.105:5000" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error: El servidor Flask no está respondiendo" -ForegroundColor Red
    Write-Host "Verifica que la IP 192.168.1.105 sea correcta para tu máquina" -ForegroundColor Yellow
    Stop-Process -Id $flaskProcess.Id -Force
    exit 1
}

Write-Host "🌐 Iniciando túnel de Cloudflare..." -ForegroundColor Yellow
Write-Host "🔗 Una vez iniciado, obtendrás una URL pública tipo: https://xxxxxxx.trycloudflare.com" -ForegroundColor Cyan

try {
    # Iniciar túnel de Cloudflare
    cloudflared tunnel --url http://192.168.1.105:5000
} catch {
    Write-Host "❌ Error al iniciar túnel de Cloudflare" -ForegroundColor Red
} finally {
    # Limpiar al salir
    Write-Host "`n🛑 Cerrando servicios..." -ForegroundColor Yellow
    Stop-Process -Id $flaskProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Servicios cerrados" -ForegroundColor Green
}
