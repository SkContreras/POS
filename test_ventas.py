#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de ventas
"""
import urllib.request
import urllib.parse
import json
import http.cookiejar

# Configuración del servidor
BASE_URL = "http://192.168.1.82:5000"

def test_simple_connection():
    """Probar conexión simple al servidor"""
    print("🌐 Probando conexión al servidor...")
    
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/ping", timeout=10)
        if response.status == 200:
            print("✅ Servidor respondiendo correctamente")
            return True
        else:
            print(f"⚠️ Servidor respondió con código: {response.status}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_database_access():
    """Probar acceso a la base de datos"""
    print("🗄️ Probando acceso a la base de datos...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('database.db', timeout=10)
        cursor = conn.cursor()
        
        # Probar consulta simple
        cursor.execute("SELECT COUNT(*) FROM productos")
        productos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM usuarios") 
        usuarios = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Base de datos accesible: {productos} productos, {usuarios} usuarios")
        return True
        
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
        return False

def simulate_manual_sale():
    """Simular una venta manual con la función directa"""
    print("🛒 Simulando venta manual...")
    
    try:
        # Importar los modelos directamente
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.models.database import DatabaseManager, Producto, Venta
        
        # Crear conexión a base de datos
        db_manager = DatabaseManager('database.db')
        producto_model = Producto(db_manager)
        venta_model = Venta(db_manager)
        
        # Datos de venta de prueba
        carrito = [
            {
                "id": 1,
                "nombre": "Pescado empanizado",
                "precio": 100.0,
                "cantidad": 1
            }
        ]
        total = 100.0
        usuario_id = 1  # Admin
        
        # Intentar crear venta
        venta_id, error = venta_model.create(total, usuario_id, carrito, producto_model)
        
        if venta_id and not error:
            print(f"✅ Venta simulada exitosa - ID: {venta_id}")
            return True
        else:
            print(f"❌ Venta simulada falló: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        return False

def main():
    print("🏪 Sistema POS - Diagnóstico Completo")
    print("=" * 50)
    
    # Prueba 1: Conexión al servidor
    server_ok = test_simple_connection()
    
    # Prueba 2: Acceso a base de datos
    db_ok = test_database_access()
    
    # Prueba 3: Venta simulada
    sale_ok = simulate_manual_sale()
    
    print("\n📊 Resumen de Diagnóstico:")
    print(f"🌐 Servidor: {'✅ OK' if server_ok else '❌ FALLO'}")
    print(f"🗄️ Base de datos: {'✅ OK' if db_ok else '❌ FALLO'}")
    print(f"🛒 Sistema de ventas: {'✅ OK' if sale_ok else '❌ FALLO'}")
    
    if server_ok and db_ok and sale_ok:
        print("\n🎉 ¡Todos los sistemas funcionan correctamente!")
        print("💡 Puedes proceder a vender desde la interfaz web.")
    else:
        print("\n⚠️ Hay problemas en el sistema.")
        if not server_ok:
            print("   - Verifica que el servidor esté ejecutándose")
        if not db_ok:
            print("   - Verifica permisos de la base de datos")
        if not sale_ok:
            print("   - Verifica la lógica de ventas")

if __name__ == "__main__":
    main()
