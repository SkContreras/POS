#!/usr/bin/env python3
"""
Script de prueba completa para la estructura modular del sistema POS
"""
import time
import sys
import os
from threading import Thread
from app_modular import create_app

def test_app_creation():
    """Prueba la creación de la aplicación"""
    print("🧪 Probando creación de aplicación...")
    try:
        app, db_manager = create_app()
        print("✅ Aplicación creada exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        return False

def test_routes_exist():
    """Prueba que todas las rutas estén registradas"""
    print("\n🧪 Probando registro de rutas...")
    try:
        app, db_manager = create_app()
        
        # Obtener todas las rutas registradas
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': rule.rule
            })
        
        # Rutas esperadas por blueprint
        expected_routes = {
            'auth': ['login', 'logout', 'verificar_admin', 'gestionar_usuarios', 'crear_usuario', 'cambiar_estado_usuario', 'log_acciones'],
            'main': ['index', 'shutdown', 'qr_code', 'historial', 'finalizar_venta'],
            'productos': ['agregar_producto', 'editar_producto', 'editar_lista', 'eliminar_producto']
        }
        
        print("📋 Rutas registradas:")
        routes_found = {}
        
        for route in routes:
            endpoint = route['endpoint']
            if '.' in endpoint:
                blueprint, route_name = endpoint.split('.', 1)
                if blueprint not in routes_found:
                    routes_found[blueprint] = []
                routes_found[blueprint].append(route_name)
                print(f"  ✅ {endpoint} - {route['rule']} - {route['methods']}")
            elif endpoint not in ['static']:
                print(f"  📝 {endpoint} - {route['rule']} - {route['methods']}")
        
        # Verificar que todas las rutas esperadas estén presentes
        missing_routes = []
        for blueprint, expected in expected_routes.items():
            for route_name in expected:
                if blueprint not in routes_found or route_name not in routes_found[blueprint]:
                    missing_routes.append(f"{blueprint}.{route_name}")
        
        if missing_routes:
            print(f"⚠️  Rutas faltantes: {missing_routes}")
            return False
        else:
            print("✅ Todas las rutas esperadas están registradas")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando rutas: {e}")
        return False

def test_config_loading():
    """Prueba la carga de configuración"""
    print("\n🧪 Probando carga de configuración...")
    try:
        from config.config import get_config
        config_class = get_config()
        
        # Verificar que las configuraciones importantes estén presentes
        required_configs = ['SECRET_KEY', 'DB_NAME', 'UPLOAD_FOLDER', 'DEFAULT_HOST', 'DEFAULT_PORT']
        
        for config_name in required_configs:
            if hasattr(config_class, config_name):
                print(f"  ✅ {config_name}: {getattr(config_class, config_name)}")
            else:
                print(f"  ❌ Configuración faltante: {config_name}")
                return False
        
        print("✅ Configuración cargada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

def test_database_models():
    """Prueba los modelos de base de datos"""
    print("\n🧪 Probando modelos de base de datos...")
    try:
        from app.models.database import DatabaseManager, Producto, Usuario, Venta, LogAccion
        
        # Crear instancia de DatabaseManager
        db_manager = DatabaseManager('test_database.db')
        
        # Probar creación de modelos
        models = {
            'Producto': Producto(db_manager),
            'Usuario': Usuario(db_manager),
            'Venta': Venta(db_manager),
            'LogAccion': LogAccion(db_manager)
        }
        
        for model_name, model_instance in models.items():
            print(f"  ✅ {model_name}: Instancia creada")
        
        print("✅ Todos los modelos funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en modelos de base de datos: {e}")
        return False

def test_utils():
    """Prueba las utilidades"""
    print("\n🧪 Probando utilidades...")
    try:
        # Probar utilidades de autenticación
        from app.utils.auth import login_required, admin_required, get_current_user
        print("  ✅ Utilidades de autenticación importadas")
        
        # Probar utilidades generales
        from app.utils.helpers import obtener_ip_local, generar_qr_code, allowed_file
        print("  ✅ Utilidades generales importadas")
        
        # Probar función de IP local
        ip = obtener_ip_local()
        print(f"  ✅ IP local obtenida: {ip}")
        
        print("✅ Todas las utilidades funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en utilidades: {e}")
        return False

def run_comprehensive_test():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPREHENSIVAS DE LA ESTRUCTURA MODULAR")
    print("=" * 70)
    
    tests = [
        ("Creación de aplicación", test_app_creation),
        ("Registro de rutas", test_routes_exist),
        ("Carga de configuración", test_config_loading),
        ("Modelos de base de datos", test_database_models),
        ("Utilidades", test_utils)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 EJECUTANDO: {test_name}")
        print('='*50)
        
        result = test_func()
        results.append((test_name, result))
        
        if result:
            print(f"✅ PASSED: {test_name}")
        else:
            print(f"❌ FAILED: {test_name}")
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n📈 RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("🚀 La estructura modular está funcionando perfectamente")
        print("\n🎯 PRÓXIMOS PASOS:")
        print("  1. Ejecutar 'python app.py' para usar el sistema")
        print("  2. Probar todas las funcionalidades manualmente")
        print("  3. Si todo funciona, eliminar app_legacy.py")
        return True
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa los errores mostrados arriba")
        print("🔙 Si es necesario, vuelve a la versión original con:")
        print("     mv app_legacy.py app.py")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
