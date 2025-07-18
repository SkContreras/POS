#!/usr/bin/env python3
"""
Script para depurar el error 308 en detail
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_modular import create_app

def debug_308_error():
    """Depura específicamente el error 308"""
    print("🔍 Depurando error 308...")
    
    # Crear aplicación
    app, db_manager = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("\n📋 Configuración de la aplicación:")
            print(f"   DEBUG: {app.config.get('DEBUG')}")
            print(f"   USE_HTTPS: {app.config.get('USE_HTTPS')}")
            print(f"   SECRET_KEY: {app.config.get('SECRET_KEY')[:10]}...")
            
            print("\n🌐 Variables de entorno relevantes:")
            print(f"   USE_HTTPS: {os.environ.get('USE_HTTPS', 'No configurada')}")
            print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV', 'No configurada')}")
            
            print("\n📍 Rutas registradas:")
            for rule in app.url_map.iter_rules():
                print(f"   {rule.rule} -> {rule.endpoint} ({rule.methods})")
            
            print("\n🧪 Test detallado del flujo:")
            
            # Primero login
            login_data = {
                'usuario': 'admin',
                'password': 'admin123'
            }
            
            print("1. POST /login...")
            response = client.post('/login', data=login_data, follow_redirects=False)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 302:
                # Ahora acceder a la ruta principal directamente
                print("\n2. GET / directamente...")
                response = client.get('/', follow_redirects=False)
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 308:
                    print("❌ Error 308 confirmado en GET /")
                    # Verificar si hay cookies de sesión
                    print(f"   Cookies: {[c for c in client.cookie_jar]}")
                
                # Probar con diferentes headers
                print("\n3. GET / con headers HTTPS...")
                response = client.get('/', headers={'X-Forwarded-Proto': 'https'}, follow_redirects=False)
                print(f"   Status: {response.status_code}")
                
                print("\n4. GET / con host HTTPS...")
                response = client.get('/', base_url='https://localhost', follow_redirects=False)
                print(f"   Status: {response.status_code}")

if __name__ == "__main__":
    debug_308_error()
