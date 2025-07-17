#!/usr/bin/env python3
"""
Script para cambiar credenciales de usuarios en el sistema POS
sin necesidad de reinstalar la base de datos
"""

import sqlite3
import getpass
from werkzeug.security import generate_password_hash

DB_NAME = 'database.db'

def mostrar_usuarios():
    """Muestra todos los usuarios del sistema"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, usuario, rol, nombre_completo, activo FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    
    print("\n=== USUARIOS ACTUALES ===")
    print("ID | Usuario | Rol | Nombre Completo | Activo")
    print("-" * 50)
    for user in usuarios:
        activo = "Sí" if user[4] else "No"
        print(f"{user[0]:2} | {user[1]:8} | {user[2]:13} | {user[3]:15} | {activo}")

def cambiar_password():
    """Cambia la contraseña de un usuario"""
    mostrar_usuarios()
    
    try:
        user_id = int(input("\nIngresa el ID del usuario: "))
        nueva_password = getpass.getpass("Nueva contraseña: ")
        confirmar_password = getpass.getpass("Confirmar contraseña: ")
        
        if nueva_password != confirmar_password:
            print("❌ Las contraseñas no coinciden")
            return
        
        if len(nueva_password) < 4:
            print("❌ La contraseña debe tener al menos 4 caracteres")
            return
        
        # Actualizar en la base de datos
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Verificar que el usuario existe
        c.execute("SELECT usuario FROM usuarios WHERE id = ?", (user_id,))
        user_data = c.fetchone()
        
        if not user_data:
            print("❌ Usuario no encontrado")
            return
        
        # Actualizar contraseña
        password_hash = generate_password_hash(nueva_password)
        c.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        conn.commit()
        conn.close()
        
        print(f"✅ Contraseña cambiada exitosamente para: {user_data[0]}")
        
    except ValueError:
        print("❌ ID debe ser un número")
    except Exception as e:
        print(f"❌ Error: {e}")

def crear_usuario():
    """Crea un nuevo usuario"""
    print("\n=== CREAR NUEVO USUARIO ===")
    
    usuario = input("Nombre de usuario: ").strip()
    if not usuario:
        print("❌ El nombre de usuario no puede estar vacío")
        return
    
    password = getpass.getpass("Contraseña: ")
    if len(password) < 4:
        print("❌ La contraseña debe tener al menos 4 caracteres")
        return
    
    print("Roles disponibles:")
    print("1. administrador")
    print("2. cajero")
    rol_opcion = input("Selecciona rol (1 o 2): ")
    
    if rol_opcion == "1":
        rol = "administrador"
    elif rol_opcion == "2":
        rol = "cajero"
    else:
        print("❌ Opción inválida")
        return
    
    nombre_completo = input("Nombre completo: ").strip()
    if not nombre_completo:
        print("❌ El nombre completo no puede estar vacío")
        return
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        password_hash = generate_password_hash(password)
        c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                     VALUES (?, ?, ?, ?)''', 
                 (usuario, password_hash, rol, nombre_completo))
        conn.commit()
        conn.close()
        
        print(f"✅ Usuario '{usuario}' creado exitosamente")
        
    except sqlite3.IntegrityError:
        print("❌ El nombre de usuario ya existe")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🏪 SISTEMA POS - Gestión de Credenciales")
    print("=" * 40)
    
    while True:
        print("\nOpciones:")
        print("1. Ver usuarios")
        print("2. Cambiar contraseña")
        print("3. Crear nuevo usuario")
        print("4. Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ")
        
        if opcion == "1":
            mostrar_usuarios()
        elif opcion == "2":
            cambiar_password()
        elif opcion == "3":
            crear_usuario()
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
