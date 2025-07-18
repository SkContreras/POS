#!/usr/bin/env python3
"""
Script de depuración para el sistema de autenticación
"""
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def debug_authentication():
    """Depura el sistema de autenticación"""
    print("🔍 Depurando sistema de autenticación...")
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        print("\n📊 Verificando estructura de la tabla usuarios...")
        c.execute("PRAGMA table_info(usuarios)")
        columns = c.fetchall()
        print("Columnas de la tabla usuarios:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\n👥 Usuarios en la base de datos:")
        c.execute("SELECT id, usuario, rol, nombre_completo, activo FROM usuarios")
        users = c.fetchall()
        
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return
        
        for user in users:
            print(f"  ID: {user[0]}, Usuario: {user[1]}, Rol: {user[2]}, Nombre: {user[3]}, Activo: {user[4]}")
        
        print("\n🔐 Verificando contraseñas...")
        
        # Verificar admin
        c.execute("SELECT password_hash FROM usuarios WHERE usuario = 'admin'")
        admin_hash = c.fetchone()
        if admin_hash:
            is_valid = check_password_hash(admin_hash[0], 'admin123')
            print(f"  Admin (admin123): {'✅ Válida' if is_valid else '❌ Inválida'}")
            print(f"  Hash almacenado: {admin_hash[0][:50]}...")
        else:
            print("  ❌ Usuario admin no encontrado")
        
        # Verificar cajero
        c.execute("SELECT password_hash FROM usuarios WHERE usuario = 'cajero'")
        cajero_hash = c.fetchone()
        if cajero_hash:
            is_valid = check_password_hash(cajero_hash[0], 'cajero123')
            print(f"  Cajero (cajero123): {'✅ Válida' if is_valid else '❌ Inválida'}")
            print(f"  Hash almacenado: {cajero_hash[0][:50]}...")
        else:
            print("  ❌ Usuario cajero no encontrado")
        
        print("\n🧪 Test de hash de contraseñas...")
        test_password = "admin123"
        new_hash = generate_password_hash(test_password)
        print(f"  Nuevo hash para '{test_password}': {new_hash}")
        is_valid = check_password_hash(new_hash, test_password)
        print(f"  Verificación: {'✅ Válida' if is_valid else '❌ Inválida'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    debug_authentication()
