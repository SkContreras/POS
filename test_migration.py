#!/usr/bin/env python3
"""
Script de prueba para verificar la migración de precios
"""

import sqlite3
import os

def test_migration():
    """Prueba la migración de la base de datos"""
    
    # Verificar que existe la base de datos
    if not os.path.exists('database.db'):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Verificar estructura de la tabla productos
    c.execute("PRAGMA table_info(productos)")
    columns = c.fetchall()
    
    print("📋 Estructura actual de la tabla productos:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Verificar que existen las nuevas columnas
    column_names = [col[1] for col in columns]
    
    if 'precio_compra' in column_names and 'precio_venta' in column_names:
        print("✅ Migración exitosa: Columnas precio_compra y precio_venta encontradas")
        
        # Mostrar algunos productos de ejemplo
        c.execute("SELECT id, nombre, precio_compra, precio_venta FROM productos LIMIT 5")
        productos = c.fetchall()
        
        if productos:
            print("\n📦 Productos de ejemplo:")
            for p in productos:
                margen = ((p[3] - p[2]) / p[2] * 100) if p[2] > 0 else 0
                print(f"  - {p[1]}: Compra ${p[2]:.2f}, Venta ${p[3]:.2f} (Margen: {margen:.1f}%)")
        else:
            print("📦 No hay productos en la base de datos")
            
    elif 'precio' in column_names:
        print("⚠️  Migración pendiente: Aún se usa la estructura antigua")
    else:
        print("❌ Error: No se encontraron columnas de precio")
    
    conn.close()

if __name__ == "__main__":
    test_migration()
