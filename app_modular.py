#!/usr/bin/env python3
"""
Aplicación principal del sistema POS - Versión Modular
"""
from flask import Flask, request, g, redirect
from config.config import get_config
from app.models.database import DatabaseManager
from app.routes.auth import init_auth_routes
from app.routes.main import init_main_routes
from app.routes.productos import init_productos_routes
from app.utils.helpers import obtener_ip_local, iniciar_navegador_background
import os
import ssl

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
    
    # Crear directorio de certificados si no existe
    os.makedirs('certificates', exist_ok=True)
    
    # Middleware de seguridad
    @app.before_request
    def security_headers():
        """Aplicar headers de seguridad"""
        # Solo verificar HTTPS si está configurado Y tenemos certificados válidos
        if app.config.get('USE_HTTPS') and not request.is_secure:
            # Verificar que los certificados existen antes de redirigir
            cert_path = os.environ.get('SSL_CERT_PATH', 'certificates/cert.pem')
            key_path = os.environ.get('SSL_KEY_PATH', 'certificates/key.pem')
            
            # Solo redirigir si los certificados existen y no estamos en debug
            if (os.path.exists(cert_path) and os.path.exists(key_path) and 
                not app.config.get('DEBUG')):
                return redirect(request.url.replace('http://', 'https://'))
            else:
                # En desarrollo o sin certificados, solo mostrar advertencia
                from flask import g
                g.security_warning = True
    
    @app.after_request 
    def add_security_headers(response):
        """Agregar headers de seguridad a todas las respuestas"""
        security_headers = app.config.get('SECURITY_HEADERS', {})
        
        for header, value in security_headers.items():
            # Solo agregar HSTS si estamos en HTTPS
            if header == 'Strict-Transport-Security' and not request.is_secure:
                continue
            response.headers[header] = value
            
        # Ajustar cookies seguras si estamos en HTTPS
        if request.is_secure:
            app.config['SESSION_COOKIE_SECURE'] = True
        
        # Asegurar que las cookies de sesión se configuren correctamente
        if 'Set-Cookie' in response.headers:
            # Añadir configuraciones adicionales para mejorar compatibilidad
            cookie_header = response.headers.get('Set-Cookie')
            if 'session=' in cookie_header and not request.is_secure:
                # En HTTP, asegurar que la cookie no requiera HTTPS
                response.headers['Set-Cookie'] = cookie_header.replace('; Secure', '')
            
        return response
    
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
    
    # Verificar si se debe usar HTTPS desde variables de entorno
    use_https = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
    https_port = int(os.environ.get('HTTPS_PORT', '5443'))
    http_port = int(os.environ.get('PORT', app.config.get('DEFAULT_PORT', 5000)))
    
    # Configurar SSL si está habilitado
    ssl_context = None
    if use_https:
        cert_path = os.environ.get('SSL_CERT_PATH', 'certificates/cert.pem')
        key_path = os.environ.get('SSL_KEY_PATH', 'certificates/key.pem')
        
        # Verificar que existen los certificados
        if os.path.exists(cert_path) and os.path.exists(key_path):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(cert_path, key_path)
            port = https_port
            protocol = "https"
            print(f"🔐 Iniciando servidor POS en {protocol}://{host_ip}:{port}")
        else:
            print("⚠️  ADVERTENCIA: Certificados SSL no encontrados. Ejecutando en HTTP.")
            use_https = False
            port = http_port
            protocol = "http"
            print(f"🔐 Iniciando servidor POS en {protocol}://{host_ip}:{port}")
    else:
        port = http_port
        protocol = "http"
        print(f"🔐 Iniciando servidor POS en {protocol}://{host_ip}:{port}")
    
    # Mostrar advertencia de seguridad si se usa HTTP con campos de contraseña
    if not use_https:
        print("⚠️  ADVERTENCIA DE SEGURIDAD:")
        print("   El servidor está ejecutándose en HTTP (no seguro).")
        print("   Los campos de contraseña son vulnerables a interceptación.")
        print("   Para mayor seguridad, considera usar HTTPS configurando USE_HTTPS=true")
    
    # Solo abrir navegador en desarrollo local y una sola vez
    if os.environ.get('FLASK_ENV') != 'production' and not navegador_abierto:
        navegador_abierto = True
        iniciar_navegador_background()
    
    # Ejecutar aplicación
    app.run(
        debug=app.config.get('DEBUG', False), 
        host=app.config.get('DEFAULT_HOST', "0.0.0.0"), 
        port=port, 
        ssl_context=ssl_context,
        use_reloader=False
    )

if __name__ == "__main__":
    run_app()
