#!/usr/bin/env python3
"""
Script de migración para la base de datos del sistema POS
Verifica y corrige la estructura de la base de datos
"""

import sqlite3
import os
from datetime import datetime

DB_NAME = 'database.db'

def verificar_estructura_db():
    """Verifica y corrige la estructura de la base de datos"""
    print("🔍 Verificando estructura de la base de datos...")
    
    if not os.path.exists(DB_NAME):
        print("❌ Base de datos no encontrada")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    migraciones_aplicadas = 0
    
    try:
        # Verificar tabla ventas
        print("\n📋 Verificando tabla 'ventas'...")
        c.execute("PRAGMA table_info(ventas)")
        columnas_ventas = [col[1] for col in c.fetchall()]
        print(f"   Columnas actuales: {columnas_ventas}")
        
        if 'usuario_id' not in columnas_ventas:
            print("   ⚠️  Falta columna 'usuario_id', agregando...")
            c.execute("ALTER TABLE ventas ADD COLUMN usuario_id INTEGER")
            migraciones_aplicadas += 1
            print("   ✅ Columna 'usuario_id' agregada")
        else:
            print("   ✅ Columna 'usuario_id' ya existe")
        
        # Verificar tabla usuarios
        print("\n👥 Verificando tabla 'usuarios'...")
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not c.fetchone():
            print("   ⚠️  Tabla 'usuarios' no existe, creando...")
            c.execute('''CREATE TABLE usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            usuario TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL,
                            rol TEXT NOT NULL,
                            nombre_completo TEXT NOT NULL,
                            activo INTEGER DEFAULT 1,
                            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
                        )''')
            migraciones_aplicadas += 1
            print("   ✅ Tabla 'usuarios' creada")
        else:
            print("   ✅ Tabla 'usuarios' ya existe")
        
        # Verificar tabla log_acciones
        print("\n📝 Verificando tabla 'log_acciones'...")
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_acciones'")
        if not c.fetchone():
            print("   ⚠️  Tabla 'log_acciones' no existe, creando...")
            c.execute('''CREATE TABLE log_acciones (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            usuario_id INTEGER,
                            accion TEXT NOT NULL,
                            detalles TEXT,
                            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                        )''')
            migraciones_aplicadas += 1
            print("   ✅ Tabla 'log_acciones' creada")
        else:
            print("   ✅ Tabla 'log_acciones' ya existe")
        
        # Verificar usuarios por defecto
        print("\n🔐 Verificando usuarios por defecto...")
        c.execute("SELECT COUNT(*) FROM usuarios")
        count = c.fetchone()[0]
        
        if count == 0:
            print("   ⚠️  No hay usuarios, creando usuarios por defecto...")
            from werkzeug.security import generate_password_hash
            
            # Usuario administrador por defecto
            admin_hash = generate_password_hash('admin123')
            c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                         VALUES (?, ?, ?, ?)''', 
                     ('admin', admin_hash, 'administrador', 'Administrador del Sistema'))
            
            # Usuario cajero por defecto
            cajero_hash = generate_password_hash('cajero123')
            c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                         VALUES (?, ?, ?, ?)''', 
                     ('cajero', cajero_hash, 'cajero', 'Cajero Principal'))
            
            migraciones_aplicadas += 1
            print("   ✅ Usuarios por defecto creados")
            print("      - admin / admin123 (administrador)")
            print("      - cajero / cajero123 (cajero)")
        else:
            print(f"   ✅ Ya existen {count} usuarios en el sistema")
        
        conn.commit()
        
        print(f"\n✅ Verificación completada")
        if migraciones_aplicadas > 0:
            print(f"🔄 Se aplicaron {migraciones_aplicadas} migraciones")
        else:
            print("📋 No se necesitaron migraciones")
        
        # Mostrar estadísticas
        print("\n📊 Estadísticas de la base de datos:")
        c.execute("SELECT COUNT(*) FROM productos")
        productos = c.fetchone()[0]
        print(f"   - Productos: {productos}")
        
        c.execute("SELECT COUNT(*) FROM ventas")
        ventas = c.fetchone()[0]
        print(f"   - Ventas: {ventas}")
        
        c.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
        usuarios_activos = c.fetchone()[0]
        print(f"   - Usuarios activos: {usuarios_activos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False
    finally:
        conn.close()

def mostrar_tablas():
    """Muestra todas las tablas de la base de datos"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("\n📋 Tablas en la base de datos:")
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = c.fetchall()
    
    for tabla in tablas:
        nombre_tabla = tabla[0]
        print(f"\n🗂️  Tabla: {nombre_tabla}")
        c.execute(f"PRAGMA table_info({nombre_tabla})")
        columnas = c.fetchall()
        
        for col in columnas:
            tipo = col[2]
            pk = " (PK)" if col[5] else ""
            not_null = " NOT NULL" if col[3] else ""
            print(f"   - {col[1]}: {tipo}{not_null}{pk}")
    
    conn.close()

def main():
    print("🏪 SISTEMA POS - Migración de Base de Datos")
    print("=" * 50)
    
    if verificar_estructura_db():
        print("\n¿Deseas ver el detalle de todas las tablas? (s/n): ", end="")
        respuesta = input().lower()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            mostrar_tablas()
    
    print("\n🎉 Proceso completado")

if __name__ == "__main__":
    main()
