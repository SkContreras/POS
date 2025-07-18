#!/usr/bin/env python3
"""
Generador y almacenamiento de SECRET_KEY para el sistema POS
Este archivo almacena la clave secreta utilizada por Flask para firmar sesiones y cookies.

IMPORTANTE: 
- NO compartas este archivo en repositorios públicos
- Mantén este archivo seguro y con permisos restringidos
- La SECRET_KEY es crítica para la seguridad de las sesiones
"""

import secrets
import os
from datetime import datetime

# SECRET_KEY actual del sistema POS
# Generada el: 2025-07-17 18:05:35
CURRENT_SECRET_KEY = "pos-secret-key-2024-development"

# Historial de claves (para referencia)
SECRET_KEY_HISTORY = [
    {
        "key": "14/Oct/14",
        "created": "2024-01-01",
        "description": "Clave original simple (insegura)",
        "status": "deprecated"
    },
    {
        "key": "pos-secret-key-2024-development", 
        "created": "2025-07-17",
        "description": "Clave mejorada para desarrollo",
        "status": "active"
    }
]

def generate_new_secret_key():
    """Genera una nueva SECRET_KEY segura"""
    return secrets.token_urlsafe(32)

def generate_production_key():
    """Genera una clave específica para producción"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_part = secrets.token_urlsafe(24)
    return f"pos_prod_{timestamp}_{random_part}"

def get_secret_key():
    """Obtiene la SECRET_KEY actual"""
    # Prioridad: Variable de entorno > Clave actual > Generar nueva
    return os.environ.get('SECRET_KEY', CURRENT_SECRET_KEY)

def save_new_key_to_history(new_key, description="Nueva clave generada"):
    """Añade una nueva clave al historial"""
    new_entry = {
        "key": new_key,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": description,
        "status": "active"
    }
    
    # Marcar las anteriores como inactivas
    for entry in SECRET_KEY_HISTORY:
        if entry["status"] == "active":
            entry["status"] = "inactive"
    
    SECRET_KEY_HISTORY.append(new_entry)
    return new_entry

if __name__ == "__main__":
    print("🔐 Generador de SECRET_KEY para Sistema POS")
    print("=" * 50)
    
    print(f"\n📋 Clave actual: {CURRENT_SECRET_KEY}")
    
    print(f"\n🔄 Nueva clave aleatoria: {generate_new_secret_key()}")
    
    print(f"\n🏭 Clave para producción: {generate_production_key()}")
    
    print(f"\n📚 Historial de claves:")
    for i, entry in enumerate(SECRET_KEY_HISTORY, 1):
        status_icon = "✅" if entry["status"] == "active" else "🔒"
        print(f"   {i}. {status_icon} {entry['created']} - {entry['description']}")
        print(f"      {entry['key'][:20]}...")
    
    print(f"\n💡 Para usar una clave específica:")
    print(f"   export SECRET_KEY='tu_clave_aquí'")
    print(f"   python app_modular.py")
