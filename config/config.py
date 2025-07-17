#!/usr/bin/env python3
"""
Configuración global del sistema POS
"""
import os
from datetime import timedelta

class Config:
    """Configuración base"""
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', '14/Oct/14')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Base de datos
    DB_NAME = 'database.db'
    
    # Configuración de archivos
    UPLOAD_FOLDER = 'static/img'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Configuración del servidor
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 5000
    
    # Configuración de desarrollo
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

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
