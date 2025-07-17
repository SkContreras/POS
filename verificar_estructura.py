#!/usr/bin/env python3
"""
Script de verificación para la estructura modular del sistema POS
"""
import os
import sys
import importlib.util

def verificar_archivo(ruta, descripcion):
    """Verifica si un archivo existe"""
    existe = os.path.exists(ruta)
    status = "✅" if existe else "❌"
    print(f"{status} {descripcion}: {ruta}")
    return existe

def verificar_modulo_python(ruta, nombre_modulo):
    """Verifica si un módulo Python se puede importar"""
    try:
        spec = importlib.util.spec_from_file_location(nombre_modulo, ruta)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ Módulo importable: {nombre_modulo}")
        return True
    except Exception as e:
        print(f"❌ Error importando {nombre_modulo}: {str(e)}")
        return False

def verificar_estructura():
    """Verifica la estructura modular completa"""
    print("🔍 Verificando estructura modular del sistema POS")
    print("=" * 60)
    
    archivos_verificar = [
        # Archivos principales
        ("app.py", "Punto de entrada principal"),
        ("app_modular.py", "Aplicación Flask modular"),
        ("app_legacy.py", "Aplicación original (backup)"),
        ("migrate_to_modular.py", "Script de migración"),
        
        # Configuración
        ("config/__init__.py", "Inicializador config"),
        ("config/config.py", "Configuración global"),
        
        # Módulos principales
        ("app/__init__.py", "Inicializador app"),
        ("app/models/__init__.py", "Inicializador models"),
        ("app/models/database.py", "Modelos de base de datos"),
        ("app/routes/__init__.py", "Inicializador routes"),
        ("app/routes/auth.py", "Rutas de autenticación"),
        ("app/routes/main.py", "Rutas principales"),
        ("app/routes/productos.py", "Rutas de productos"),
        ("app/utils/__init__.py", "Inicializador utils"),
        ("app/utils/auth.py", "Utilidades de autenticación"),
        ("app/utils/helpers.py", "Utilidades generales"),
        
        # Documentación
        ("ESTRUCTURA_MODULAR.md", "Documentación de estructura"),
        
        # Archivos originales (sin cambios)
        ("database.db", "Base de datos SQLite"),
        ("requirements.txt", "Dependencias Python"),
        ("templates/", "Directorio de plantillas"),
        ("static/", "Directorio de archivos estáticos"),
    ]
    
    print("\n📁 VERIFICANDO ARCHIVOS:")
    archivos_ok = 0
    total_archivos = len(archivos_verificar)
    
    for ruta, descripcion in archivos_verificar:
        if verificar_archivo(ruta, descripcion):
            archivos_ok += 1
    
    print(f"\n📊 Archivos verificados: {archivos_ok}/{total_archivos}")
    
    # Verificar módulos Python
    print("\n🐍 VERIFICANDO MÓDULOS PYTHON:")
    modulos_verificar = [
        ("config/config.py", "config.config"),
        ("app/models/database.py", "app.models.database"),
        ("app/utils/auth.py", "app.utils.auth"),
        ("app/utils/helpers.py", "app.utils.helpers"),
    ]
    
    modulos_ok = 0
    for ruta, nombre in modulos_verificar:
        if os.path.exists(ruta) and verificar_modulo_python(ruta, nombre):
            modulos_ok += 1
    
    print(f"\n📊 Módulos importables: {modulos_ok}/{len(modulos_verificar)}")
    
    # Verificar dependencias
    print("\n📦 VERIFICANDO DEPENDENCIAS:")
    try:
        import flask
        print("✅ Flask instalado")
        dependencias_ok = True
    except ImportError:
        print("❌ Flask no instalado")
        dependencias_ok = False
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN:")
    print("=" * 60)
    
    if archivos_ok == total_archivos:
        print("✅ Estructura de archivos: COMPLETA")
    else:
        print(f"⚠️  Estructura de archivos: {archivos_ok}/{total_archivos} archivos")
    
    if modulos_ok == len(modulos_verificar):
        print("✅ Módulos Python: FUNCIONANDO")
    else:
        print(f"⚠️  Módulos Python: {modulos_ok}/{len(modulos_verificar)} funcionando")
    
    if dependencias_ok:
        print("✅ Dependencias: INSTALADAS")
    else:
        print("❌ Dependencias: FALTANTES")
    
    # Estado general
    todo_ok = (archivos_ok == total_archivos and 
               modulos_ok == len(modulos_verificar) and 
               dependencias_ok)
    
    if todo_ok:
        print("\n🎉 ¡MIGRACIÓN EXITOSA!")
        print("🚀 El sistema está listo para usar con la nueva estructura modular")
        print("\n📝 Para ejecutar:")
        print("   python app.py")
    else:
        print("\n⚠️  HAY PROBLEMAS EN LA MIGRACIÓN")
        print("🔧 Revisa los errores mostrados arriba")
        print("\n🔙 Para volver a la versión original:")
        print("   mv app_legacy.py app.py")
    
    return todo_ok

def mostrar_beneficios():
    """Muestra los beneficios de la nueva estructura"""
    print("\n" + "🌟" * 20)
    print("BENEFICIOS DE LA ESTRUCTURA MODULAR")
    print("🌟" * 20)
    
    beneficios = [
        "📦 Código organizado por responsabilidades",
        "🔍 Fácil localización y debugging de errores",
        "🚀 Escalabilidad mejorada para nuevas funciones",
        "🔄 Reutilización de código entre módulos",
        "🎯 Testing más granular y efectivo",
        "👥 Desarrollo paralelo por múltiples programadores",
        "⚙️  Configuración centralizada y por entornos",
        "📚 Mejor documentación y mantenimiento",
        "🛡️  Separación clara entre lógica y configuración",
        "🔧 Fácil modificación sin afectar otros módulos"
    ]
    
    for beneficio in beneficios:
        print(f"  {beneficio}")

if __name__ == "__main__":
    resultado = verificar_estructura()
    
    if resultado:
        mostrar_beneficios()
        
        print("\n" + "📖" * 20)
        print("PRÓXIMOS PASOS RECOMENDADOS")
        print("📖" * 20)
        print("1. 📄 Lee ESTRUCTURA_MODULAR.md para entender la nueva organización")
        print("2. 🚀 Ejecuta 'python app.py' para probar el sistema")
        print("3. 🧪 Realiza pruebas de todas las funcionalidades")
        print("4. 📝 Si todo funciona bien, puedes eliminar app_legacy.py")
        print("5. 🔄 Para futuras funciones, sigue los patrones modulares")
    
    sys.exit(0 if resultado else 1)
