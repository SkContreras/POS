#!/usr/bin/env python3
"""
Script para depurar el manejo de sesiones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_modular import create_app

def debug_session_issue():
    """Depura específicamente el problema de sesiones"""
    print("🔍 Depurando manejo de sesiones...")
    
    # Crear aplicación
    app, db_manager = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("\n📋 Configuración de sesiones:")
            print(f"   SECRET_KEY: {app.config.get('SECRET_KEY')}")
            print(f"   SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
            print(f"   SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE')}")
            print(f"   SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")
            print(f"   PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
            
            # Test paso a paso
            print("\n🧪 Test paso a paso:")
            
            # 1. Acceso inicial a /
            print("\n1. GET / (sin login)...")
            response = client.get('/', follow_redirects=False)
            print(f"   Status: {response.status_code}")
            print(f"   Location: {response.headers.get('Location', 'N/A')}")
            
            # 2. POST login
            print("\n2. POST /login...")
            login_data = {'usuario': 'admin', 'password': 'admin123'}
            response = client.post('/login', data=login_data, follow_redirects=False)
            print(f"   Status: {response.status_code}")
            print(f"   Location: {response.headers.get('Location', 'N/A')}")
            
            # Verificar cookies y sesión
            print(f"   Set-Cookie headers: {response.headers.getlist('Set-Cookie')}")
            
            # 3. Verificar contenido de sesión después del login
            print("\n3. Verificando sesión después del login...")
            with client.session_transaction() as sess:
                print(f"   Contenido de sesión: {dict(sess)}")
                print(f"   'user_id' en sesión: {'user_id' in sess}")
                print(f"   Sesión permanente: {sess.permanent}")
            
            # 4. GET / después del login
            print("\n4. GET / (después del login)...")
            response = client.get('/', follow_redirects=False)
            print(f"   Status: {response.status_code}")
            print(f"   Location: {response.headers.get('Location', 'N/A')}")
            
            # 5. Verificar sesión después de intentar acceder a /
            print("\n5. Verificando sesión después de GET /...")
            with client.session_transaction() as sess:
                print(f"   Contenido de sesión: {dict(sess)}")
                print(f"   'user_id' en sesión: {'user_id' in sess}")

if __name__ == "__main__":
    debug_session_issue()
