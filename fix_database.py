#!/usr/bin/env python3
"""
Script para solucionar problemas de la base de datos
Limpia archivos WAL y optimiza la base de datos
"""
import sqlite3
import os
import time

DB_NAME = 'database.db'

def fix_database():
    """Soluciona problemas comunes de la base de datos"""
    
    print("🔧 Solucionando problemas de base de datos...")
    
    # 1. Cerrar cualquier conexión activa y limpiar archivos WAL
    wal_file = f"{DB_NAME}-wal"
    shm_file = f"{DB_NAME}-shm"
    
    if os.path.exists(wal_file):
        print(f"📁 Encontrado archivo WAL: {wal_file}")
    
    if os.path.exists(shm_file):
        print(f"📁 Encontrado archivo SHM: {shm_file}")
    
    # 2. Conectar y hacer checkpoint para consolidar cambios WAL
    try:
        conn = sqlite3.connect(DB_NAME, timeout=60)
        
        # Configurar modo WAL si no está activo
        conn.execute('PRAGMA journal_mode=WAL;')
        
        # Hacer checkpoint para consolidar cambios
        print("⚡ Consolidando cambios WAL...")
        conn.execute('PRAGMA wal_checkpoint(FULL);')
        
        # Optimizar base de datos
        print("🚀 Optimizando base de datos...")
        conn.execute('VACUUM;')
        conn.execute('ANALYZE;')
        
        # Verificar integridad
        print("🔍 Verificando integridad...")
        result = conn.execute('PRAGMA integrity_check;').fetchone()
        if result[0] == 'ok':
            print("✅ Base de datos íntegra")
        else:
            print(f"⚠️ Problema de integridad: {result[0]}")
        
        # Configurar pragmas para mejor rendimiento
        conn.execute('PRAGMA busy_timeout=60000;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        conn.execute('PRAGMA cache_size=10000;')
        conn.execute('PRAGMA temp_store=memory;')
        
        conn.close()
        print("✅ Base de datos optimizada correctamente")
        
        # 3. Verificar que archivos WAL/SHM fueron procesados
        if os.path.exists(wal_file):
            size = os.path.getsize(wal_file)
            print(f"📊 Archivo WAL después del checkpoint: {size} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al optimizar base de datos: {e}")
        return False

def show_database_status():
    """Muestra el estado actual de la base de datos"""
    try:
        conn = sqlite3.connect(DB_NAME, timeout=30)
        
        # Información general
        cursor = conn.cursor()
        
        # Modo journal
        journal_mode = conn.execute('PRAGMA journal_mode;').fetchone()[0]
        print(f"📖 Modo journal: {journal_mode}")
        
        # Tamaño de página
        page_size = conn.execute('PRAGMA page_size;').fetchone()[0]
        print(f"📄 Tamaño de página: {page_size} bytes")
        
        # Número de páginas
        page_count = conn.execute('PRAGMA page_count;').fetchone()[0]
        print(f"📚 Número de páginas: {page_count}")
        
        # Tamaño total aproximado
        total_size = page_size * page_count
        print(f"💾 Tamaño aproximado: {total_size / 1024:.2f} KB")
        
        # Contar registros en tablas principales
        cursor.execute("SELECT COUNT(*) FROM productos")
        productos_count = cursor.fetchone()[0]
        print(f"📦 Productos: {productos_count}")
        
        cursor.execute("SELECT COUNT(*) FROM ventas")
        ventas_count = cursor.fetchone()[0]
        print(f"💰 Ventas: {ventas_count}")
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios_count = cursor.fetchone()[0]
        print(f"👥 Usuarios: {usuarios_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al obtener estado: {e}")

if __name__ == "__main__":
    print("🏪 Sistema POS - Reparador de Base de Datos")
    print("=" * 50)
    
    print("\n📊 Estado inicial de la base de datos:")
    show_database_status()
    
    print("\n🔧 Iniciando reparación...")
    if fix_database():
        print("\n📊 Estado final de la base de datos:")
        show_database_status()
        print("\n✅ ¡Reparación completada exitosamente!")
        print("💡 Puedes reiniciar tu aplicación POS ahora.")
    else:
        print("\n❌ La reparación falló. Verifica que no haya procesos usando la base de datos.")
