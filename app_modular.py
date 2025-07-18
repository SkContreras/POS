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
import sys

# Variable global para controlar la apertura del navegador
navegador_abierto = False

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
        # Detectar si es una página con campos de contraseña
        password_endpoints = ['/login', '/gestionar_usuarios', '/auth/login', '/users']
        is_password_page = any(endpoint in request.path for endpoint in password_endpoints)
        
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
                # En desarrollo o sin certificados, mostrar advertencia de seguridad
                from flask import g
                g.security_warning = True
                if is_password_page:
                    g.password_security_warning = True
        elif not request.is_secure and is_password_page:
            # Advertencia específica para páginas con contraseñas en HTTP
            from flask import g
            g.password_security_warning = True
    
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
    
    # Almacenar información del servidor para uso en rutas (como QR)
    app.config['SERVER_INFO'] = {
        'host': '127.0.0.1',  # Se actualizará en run_app()
        'port': 5000,         # Se actualizará en run_app()
        'protocol': 'http'    # Se actualizará en run_app()
    }
    
    # Registrar blueprints
    init_auth_routes(app, db_manager)
    init_main_routes(app, db_manager)
    init_productos_routes(app, db_manager)
    
    # Registrar rutas de gastos
    from app.routes.gastos import init_gastos_routes
    init_gastos_routes(app, db_manager)
    
    return app

def run_app():
    """Ejecuta la aplicación con configuraciones de red y SSL"""
    app = create_app()
    
    # Obtener puerto de argumentos de línea de comandos o usar el por defecto
    port_override = None
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '--port' and i + 1 < len(sys.argv):
                try:
                    port_override = int(sys.argv[i + 1])
                except ValueError:
                    print("⚠️  Puerto inválido, usando puerto por defecto")
    
    # Configuración de red
    host_ip = obtener_ip_local()
    use_https = app.config.get('USE_HTTPS', False)
    http_port = port_override or app.config.get('HTTP_PORT', 5000)
    https_port = port_override or app.config.get('HTTPS_PORT', 5443)
    
    # Variable global para controlar la apertura del navegador
    global navegador_abierto
    navegador_abierto = False
    
    # Configuración SSL
    ssl_context = None
    
    if use_https:
        # Configuración HTTPS
        cert_path = os.environ.get('SSL_CERT_PATH', 'certificates/cert.pem')
        key_path = os.environ.get('SSL_KEY_PATH', 'certificates/key.pem')
        
        try:
            # Verificar si los certificados existen
            if os.path.exists(cert_path) and os.path.exists(key_path):
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(cert_path, key_path)
                port = https_port
                protocol = "https"
                print(f"🔒 Iniciando servidor POS seguro en {protocol}://{host_ip}:{port}")
            else:
                print("⚠️  Certificados SSL no encontrados, usando HTTP")
                port = http_port
                protocol = "http"
                print(f"🔐 Iniciando servidor POS en {protocol}://{host_ip}:{port}")
        except Exception as e:
            print(f"⚠️  Error configurando SSL: {e}, usando HTTP")
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
    
    # Actualizar información del servidor en la configuración para uso en rutas
    app.config['SERVER_INFO'].update({
        'host': host_ip,
        'port': port,
        'protocol': protocol
    })
    
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
