@echo off
echo ==============================================
echo  Iniciando el sistema Punto de Venta Mega-Mas
echo ==============================================
cd %~dp0

:: Crea entorno virtual si no existe
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activa el entorno
call venv\Scripts\activate.bat

:: Instala las dependencias si es necesario
echo Instalando dependencias...
pip install -r requirements.txt

:: Corre la app
echo Iniciando servidor...
python app.py

pause
