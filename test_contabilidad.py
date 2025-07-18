#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de contabilidad
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Agregar el directorio del proyecto al path
sys.path.append('/home/ayase/Documentos/code/POS')

from app.models.database import DatabaseManager, Venta

def test_contabilidad():
    """Prueba las funciones de contabilidad"""
    print("🔍 Probando funciones de contabilidad...")
    
    # Inicializar base de datos
    db_manager = DatabaseManager('database.db')
    venta_model = Venta(db_manager)
    
    # Fechas de prueba
    fecha_fin = datetime.now().strftime('%Y-%m-%d')
    fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período de prueba: {fecha_inicio} a {fecha_fin}")
    
    try:
        # Probar estadísticas
        print("\n📊 Probando estadísticas...")
        estadisticas = venta_model.get_estadisticas_periodo(fecha_inicio, fecha_fin)
        print(f"✅ Estadísticas: {estadisticas}")
        
        # Probar ventas por día
        print("\n📈 Probando ventas por día...")
        ventas_dia = venta_model.get_ventas_por_dia(fecha_inicio, fecha_fin)
        print(f"✅ Ventas por día: {len(ventas_dia)} registros")
        if ventas_dia:
            print(f"   Ejemplo: {ventas_dia[0]}")
        
        # Probar ventas por hora
        print("\n🕐 Probando ventas por hora...")
        ventas_hora = venta_model.get_ventas_por_hora(fecha_inicio, fecha_fin)
        print(f"✅ Ventas por hora: {len(ventas_hora)} registros")
        if ventas_hora:
            print(f"   Ejemplo: {ventas_hora[0]}")
        
        # Probar productos más vendidos
        print("\n🏆 Probando productos más vendidos...")
        productos_top = venta_model.get_productos_mas_vendidos(fecha_inicio, fecha_fin)
        print(f"✅ Productos top: {len(productos_top)} registros")
        if productos_top:
            print(f"   Ejemplo: {productos_top[0]}")
        
        # Probar ingresos por categoría
        print("\n📂 Probando ingresos por categoría...")
        ingresos_cat = venta_model.get_ingresos_por_categoria(fecha_inicio, fecha_fin)
        print(f"✅ Ingresos por categoría: {len(ingresos_cat)} registros")
        if ingresos_cat:
            print(f"   Ejemplo: {ingresos_cat[0]}")
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """Verifica el estado de la base de datos"""
    print("🔍 Verificando estado de la base de datos...")
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Verificar tabla de ventas
        c.execute("SELECT COUNT(*) FROM ventas")
        total_ventas = c.fetchone()[0]
        print(f"📊 Total de ventas: {total_ventas}")
        
        # Verificar tabla de ventas_detalle
        c.execute("SELECT COUNT(*) FROM ventas_detalle")
        total_detalles = c.fetchone()[0]
        print(f"📋 Total de detalles: {total_detalles}")
        
        # Verificar tabla de productos
        c.execute("SELECT COUNT(*) FROM productos")
        total_productos = c.fetchone()[0]
        print(f"📦 Total de productos: {total_productos}")
        
        # Mostrar últimas ventas
        c.execute("SELECT id, fecha, total FROM ventas ORDER BY fecha DESC LIMIT 5")
        ultimas_ventas = c.fetchall()
        print(f"🔄 Últimas 5 ventas:")
        for venta in ultimas_ventas:
            print(f"   ID: {venta[0]}, Fecha: {venta[1]}, Total: ${venta[2]}")
        
        conn.close()
        
        if total_ventas > 0:
            print("✅ Base de datos tiene datos para probar")
            return True
        else:
            print("⚠️ Base de datos vacía - no hay ventas para mostrar")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de contabilidad...")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    os.chdir('/home/ayase/Documentos/code/POS')
    
    # Verificar base de datos
    db_ok = check_database()
    
    print("\n" + "=" * 50)
    
    if db_ok:
        # Probar funciones
        test_ok = test_contabilidad()
        
        if test_ok:
            print("\n🎉 ¡Sistema de contabilidad funcionando correctamente!")
        else:
            print("\n❌ Hay problemas con el sistema de contabilidad")
    else:
        print("\n⚠️ No se pueden ejecutar pruebas - base de datos sin datos")
    
    print("=" * 50)
