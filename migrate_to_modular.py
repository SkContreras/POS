#!/usr/bin/env python3
"""
Script para migrar de app.py monolítico a la estructura modular
"""
import os
import shutil
from datetime import datetime

def backup_original():
    """Hace backup del app.py original"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"app_original_{timestamp}.py"
    
    if os.path.exists("app.py"):
        shutil.copy2("app.py", backup_name)
        print(f"✅ Backup creado: {backup_name}")
        return backup_name
    return None

def migrate_to_modular():
    """Migra la aplicación a la estructura modular"""
    print("🔄 Iniciando migración a estructura modular...")
    
    # Hacer backup
    backup_file = backup_original()
    
    if backup_file:
        # Renombrar app.py actual
        if os.path.exists("app.py"):
            os.rename("app.py", "app_legacy.py")
            print("📦 app.py renombrado a app_legacy.py")
        
        # Crear nuevo app.py que use la estructura modular
        create_new_app_py()
        
        print("\n✅ Migración completada!")
        print("\n📁 Nueva estructura:")
        print("├── app.py (nuevo - usa estructura modular)")
        print("├── app_legacy.py (original)")
        print("├── app_modular.py (aplicación modular)")
        print("├── config/")
        print("│   └── config.py")
        print("└── app/")
        print("    ├── models/")
        print("    │   └── database.py")
        print("    ├── routes/")
        print("    │   ├── auth.py")
        print("    │   ├── main.py")
        print("    │   └── productos.py")
        print("    └── utils/")
        print("        ├── auth.py")
        print("        └── helpers.py")
        
        print(f"\n💾 Backup disponible en: {backup_file}")
        print("\n🚀 Para usar la nueva estructura modular:")
        print("   python app.py")
        print("\n🔙 Para volver a la versión original:")
        print("   mv app_legacy.py app.py")
        
    else:
        print("❌ No se encontró app.py para migrar")

def create_new_app_py():
    """Crea nuevo app.py que usa la estructura modular"""
    content = '''#!/usr/bin/env python3
"""
Sistema POS - Punto de Venta
Versión modular mejorada para mejor mantenimiento
"""

# Importar la aplicación modular
from app_modular import run_app

if __name__ == "__main__":
    print("🏪 Sistema POS - Versión Modular")
    print("=" * 50)
    print("✨ Estructura modular mejorada")
    print("📁 Código organizado en módulos especializados")
    print("🔧 Mejor mantenimiento y escalabilidad")
    print("=" * 50)
    
    # Ejecutar aplicación
    run_app()
'''
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Nuevo app.py creado")

def show_usage_instructions():
    """Muestra instrucciones de uso"""
    print("\n" + "="*60)
    print("📚 INSTRUCCIONES DE USO - ESTRUCTURA MODULAR")
    print("="*60)
    print("\n🏗️  ESTRUCTURA DE ARCHIVOS:")
    print("   app.py                 - Punto de entrada principal")
    print("   app_modular.py         - Aplicación modular")
    print("   config/config.py       - Configuración global")
    print("   app/models/database.py - Modelos de base de datos")
    print("   app/routes/auth.py     - Rutas de autenticación")
    print("   app/routes/main.py     - Rutas principales")
    print("   app/routes/productos.py- Rutas de productos")
    print("   app/utils/auth.py      - Utilidades de autenticación")
    print("   app/utils/helpers.py   - Utilidades generales")
    
    print("\n🔧 VENTAJAS DE LA NUEVA ESTRUCTURA:")
    print("   ✅ Código organizado por responsabilidades")
    print("   ✅ Fácil mantenimiento y debugging")
    print("   ✅ Escalabilidad mejorada")
    print("   ✅ Reutilización de código")
    print("   ✅ Separación clara de configuración y lógica")
    
    print("\n🚀 PARA EJECUTAR:")
    print("   python app.py")
    
    print("\n🔄 PARA VOLVER A LA VERSIÓN ORIGINAL:")
    print("   mv app_legacy.py app.py")
    
    print("\n📝 PARA AGREGAR NUEVAS FUNCIONALIDADES:")
    print("   1. Crear nuevos blueprints en app/routes/")
    print("   2. Agregar modelos en app/models/")
    print("   3. Registrar blueprints en app_modular.py")

if __name__ == "__main__":
    migrate_to_modular()
    show_usage_instructions()
