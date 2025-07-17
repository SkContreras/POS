#!/usr/bin/env python3
"""
Aplicación principal del sistema POS - Versión Modular
"""
from flask import Flask
from config.config import get_config
from app.models.database import DatabaseManager
from app.routes.auth import init_auth_routes
from app.routes.main import init_main_routes
from app.routes.productos import init_productos_routes
from app.utils.helpers import obtener_ip_local, iniciar_navegador_background
import os

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Cargar configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar base de datos
    db_manager = DatabaseManager(app.config['DB_NAME'])
    db_manager.init_db()
    
    # Registrar blueprints
    init_auth_routes(app, db_manager)
    init_main_routes(app, db_manager)
    init_productos_routes(app, db_manager)
    
    return app, db_manager

def run_app():
    """Ejecuta la aplicación"""
    # Crear aplicación
    app, db_manager = create_app()
    
    # Variable para controlar si ya se abrió el navegador
    navegador_abierto = False
    
    # Obtener configuración del servidor
    host_ip = obtener_ip_local()
    port = int(os.environ.get('PORT', app.config.get('DEFAULT_PORT', 5000)))
    
    print(f"Iniciando servidor POS en http://{host_ip}:{port}")
    
    # Solo abrir navegador en desarrollo local y una sola vez
    if os.environ.get('FLASK_ENV') != 'production' and not navegador_abierto:
        navegador_abierto = True
        iniciar_navegador_background()
    
    # Ejecutar aplicación
    app.run(
        debug=app.config.get('DEBUG', False), 
        host=app.config.get('DEFAULT_HOST', "0.0.0.0"), 
        port=port, 
        use_reloader=False
    )

if __name__ == "__main__":
    run_app()
