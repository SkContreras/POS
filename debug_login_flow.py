#!/usr/bin/env python3
"""
Script para depurar el flujo de login con Flask
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_modular import create_app
from flask import url_for

def test_login_flow():
    """Test del flujo completo de login"""
    print("🧪 Iniciando test del flujo de login...")
    
    # Crear aplicación
    app, db_manager = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("\n1️⃣ Probando acceso a la página de login...")
            
            # Test GET login
            response = client.get('/login')
            print(f"   GET /login - Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error al acceder al login: {response.data.decode()}")
                return
            
            print("✅ Página de login cargada correctamente")
            
            print("\n2️⃣ Probando login con credenciales correctas...")
            
            # Test POST login con credenciales correctas
            login_data = {
                'usuario': 'admin',
                'password': 'admin123'
            }
            
            response = client.post('/login', data=login_data, follow_redirects=False)
            print(f"   POST /login - Status: {response.status_code}")
            print(f"   Location header: {response.headers.get('Location', 'No hay redirección')}")
            
            if response.status_code == 302:
                print("✅ Redirección exitosa después del login")
                
                # Verificar si la redirección es al index
                location = response.headers.get('Location', '')
                if '/login' in location:
                    print("❌ PROBLEMA: Redirigiendo de vuelta al login")
                else:
                    print(f"✅ Redirigiendo correctamente a: {location}")
                
                # Seguir la redirección
                print("\n3️⃣ Siguiendo la redirección...")
                # En lugar de extraer solo la parte final, usar la URL completa
                redirect_url = response.headers.get('Location', '/')
                print(f"   Redirigiendo a: {redirect_url}")
                response = client.get(redirect_url, follow_redirects=False)
                print(f"   GET después de login - Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    print("✅ Acceso exitoso después del login")
                elif response.status_code == 302:
                    print("⚠️ Otra redirección después del login")
                    print(f"   Nueva location: {response.headers.get('Location')}")
                elif response.status_code == 308:
                    print("❌ Error 308 - Permanent Redirect")
                    print("   Esto indica un problema con las rutas o middleware")
                else:
                    print(f"❌ Error después del login: {response.status_code}")
                    
            elif response.status_code == 200:
                print("⚠️ Login devolvió 200 (debería ser redirección)")
                # Verificar si hay mensajes de error en la respuesta
                response_text = response.data.decode()
                if 'Usuario o contraseña incorrectos' in response_text:
                    print("❌ PROBLEMA: Credenciales rechazadas")
                elif 'Bienvenido' in response_text:
                    print("✅ Login exitoso pero sin redirección")
                else:
                    print("⚠️ Respuesta inesperada")
            else:
                print(f"❌ Error en login: {response.status_code}")
                print(response.data.decode()[:200])
            
            print("\n4️⃣ Probando login con credenciales incorrectas...")
            
            # Test POST login con credenciales incorrectas
            login_data_bad = {
                'usuario': 'admin',
                'password': 'wrongpassword'
            }
            
            response = client.post('/login', data=login_data_bad, follow_redirects=False)
            print(f"   POST /login (mal password) - Status: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.data.decode()
                if 'Usuario o contraseña incorrectos' in response_text:
                    print("✅ Credenciales incorrectas rechazadas correctamente")
                else:
                    print("⚠️ No se muestra mensaje de error esperado")
            else:
                print(f"⚠️ Status inesperado para credenciales incorrectas: {response.status_code}")

if __name__ == "__main__":
    test_login_flow()
