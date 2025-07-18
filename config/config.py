#!/usr/bin/env python3
"""
Configuración global del sistema POS
"""
import os
import sys
from datetime import timedelta

# Añadir el directorio padre al path para importar secret_keys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from secret_keys import get_secret_key
except ImportError:
    # Fallback si no existe el archivo
    def get_secret_key():
        return os.environ.get('SECRET_KEY', 'pos-secret-key-2024-development')

class Config:
    """Configuración base"""
    # Configuración de Flask
    SECRET_KEY = get_secret_key()
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Se activará automáticamente con HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'pos_session'
    
    # Base de datos
    DB_NAME = 'database.db'
    
    # Configuración de archivos
    UPLOAD_FOLDER = 'static/img'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Configuración del servidor
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 5000
    
    # Configuración de seguridad
    USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
    HTTPS_PORT = int(os.environ.get('HTTPS_PORT', '5443'))
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', 'certificates/cert.pem')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', 'certificates/key.pem')
    
    # Headers de seguridad
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Configuración de desarrollo
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    # En desarrollo, permitir HTTP para facilidad de uso
    USE_HTTPS = False
    
class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    # En producción, forzar HTTPS
    USE_HTTPS = True

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DB_NAME = 'test_database.db'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
