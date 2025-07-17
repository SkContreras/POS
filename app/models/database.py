#!/usr/bin/env python3
"""
Modelos de base de datos para el sistema POS
"""
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

class DatabaseManager:
    """Gestor de la base de datos"""
    
    def __init__(self, db_name):
        self.db_name = db_name
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Inicializa la base de datos con todas las tablas"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Tabla de productos
        c.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        precio REAL NOT NULL,
                        imagen TEXT NOT NULL
                    )''')
        
        # Tabla de ventas
        c.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT NOT NULL,
                        total REAL NOT NULL,
                        usuario_id INTEGER,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )''')
        
        # Migración: Agregar columna usuario_id si no existe
        try:
            c.execute("SELECT usuario_id FROM ventas LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE ventas ADD COLUMN usuario_id INTEGER")
            print("✅ Migración aplicada: Columna usuario_id agregada a la tabla ventas")
        
        # Tabla de detalles de ventas
        c.execute('''CREATE TABLE IF NOT EXISTS ventas_detalle (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        venta_id INTEGER,
                        producto_id INTEGER,
                        nombre TEXT,
                        cantidad REAL,
                        precio_unitario REAL,
                        subtotal REAL,
                        FOREIGN KEY (venta_id) REFERENCES ventas(id)
                    )''')
        
        # Tabla de usuarios
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        rol TEXT NOT NULL,
                        nombre_completo TEXT NOT NULL,
                        activo INTEGER DEFAULT 1,
                        fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
                    )''')
        
        # Tabla de log de acciones
        c.execute('''CREATE TABLE IF NOT EXISTS log_acciones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER,
                        accion TEXT NOT NULL,
                        detalles TEXT,
                        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )''')
        
        # Crear usuarios por defecto si no existen
        self._create_default_users(c)
        
        conn.commit()
        conn.close()
    
    def _create_default_users(self, cursor):
        """Crea usuarios por defecto si no existen"""
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Usuario administrador por defecto
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                             VALUES (?, ?, ?, ?)''', 
                         ('admin', admin_hash, 'administrador', 'Administrador del Sistema'))
            
            # Usuario cajero por defecto
            cajero_hash = generate_password_hash('cajero123')
            cursor.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                             VALUES (?, ?, ?, ?)''', 
                         ('cajero', cajero_hash, 'cajero', 'Cajero Principal'))

class Producto:
    """Modelo para productos"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all(self):
        """Obtiene todos los productos"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM productos")
        productos = c.fetchall()
        conn.close()
        return productos
    
    def get_by_id(self, product_id):
        """Obtiene un producto por ID"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM productos WHERE id = ?", (product_id,))
        producto = c.fetchone()
        conn.close()
        return producto
    
    def create(self, nombre, precio, imagen):
        """Crea un nuevo producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO productos (nombre, precio, imagen) VALUES (?, ?, ?)",
                  (nombre, precio, imagen))
        product_id = c.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def update(self, product_id, nombre, precio, imagen):
        """Actualiza un producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE productos SET nombre = ?, precio = ?, imagen = ? WHERE id = ?",
                  (nombre, precio, imagen, product_id))
        conn.commit()
        conn.close()
    
    def delete(self, product_id):
        """Elimina un producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM productos WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

class Usuario:
    """Modelo para usuarios"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_by_username(self, username):
        """Obtiene un usuario por nombre de usuario"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, password_hash, rol, nombre_completo FROM usuarios WHERE usuario = ? AND activo = 1", 
                  (username,))
        user = c.fetchone()
        conn.close()
        return user
    
    def get_by_id(self, user_id):
        """Obtiene un usuario por ID"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    
    def get_all(self):
        """Obtiene todos los usuarios"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, usuario, rol, nombre_completo, activo, fecha_creacion FROM usuarios ORDER BY fecha_creacion DESC")
        users = c.fetchall()
        conn.close()
        return users
    
    def create(self, usuario, password_hash, rol, nombre_completo):
        """Crea un nuevo usuario"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                     VALUES (?, ?, ?, ?)''', 
                 (usuario, password_hash, rol, nombre_completo))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def update_status(self, user_id, active_status):
        """Actualiza el estado activo de un usuario"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE usuarios SET activo = ? WHERE id = ?", (active_status, user_id))
        conn.commit()
        conn.close()
    
    def get_password_hash(self, user_id):
        """Obtiene el hash de contraseña de un usuario"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT password_hash FROM usuarios WHERE id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    
    def update_credentials(self, user_id, new_username=None, new_password_hash=None):
        """Actualiza las credenciales de un usuario"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        if new_username and new_password_hash:
            c.execute("UPDATE usuarios SET usuario = ?, password_hash = ? WHERE id = ?", 
                     (new_username, new_password_hash, user_id))
        elif new_username:
            c.execute("UPDATE usuarios SET usuario = ? WHERE id = ?", (new_username, user_id))
        elif new_password_hash:
            c.execute("UPDATE usuarios SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
        
        conn.commit()
        conn.close()
    
    def username_exists(self, username, exclude_user_id=None):
        """Verifica si un nombre de usuario ya existe (excluyendo un usuario específico)"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        if exclude_user_id:
            c.execute("SELECT id FROM usuarios WHERE usuario = ? AND id != ?", (username, exclude_user_id))
        else:
            c.execute("SELECT id FROM usuarios WHERE usuario = ?", (username,))
        
        result = c.fetchone()
        conn.close()
        return result is not None

class Venta:
    """Modelo para ventas"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, total, usuario_id, carrito):
        """Crea una nueva venta con sus detalles"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO ventas (fecha, total, usuario_id) VALUES (?, ?, ?)", 
                  (fecha, total, usuario_id))
        venta_id = c.lastrowid
        
        # Agregar detalles de la venta
        for item in carrito:
            c.execute(
                "INSERT INTO ventas_detalle (venta_id, producto_id, nombre, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    venta_id,
                    item["id"],
                    item["nombre"],
                    item["cantidad"],
                    item["precio"],
                    item["precio"] * item["cantidad"],
                ),
            )
        
        conn.commit()
        conn.close()
        return venta_id
    
    def get_all_with_details(self):
        """Obtiene todas las ventas con detalles y información del usuario"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Obtener ventas con información del usuario
        c.execute('''SELECT v.id, v.fecha, v.total, v.usuario_id, u.usuario, u.nombre_completo, u.rol
                     FROM ventas v 
                     LEFT JOIN usuarios u ON v.usuario_id = u.id 
                     ORDER BY v.fecha DESC''')
        ventas = c.fetchall()
        
        # Obtener detalles de cada venta
        ventas_con_detalle = []
        for venta in ventas:
            c.execute("SELECT nombre, cantidad, precio_unitario, subtotal FROM ventas_detalle WHERE venta_id = ?", 
                      (venta[0],))
            detalles = c.fetchall()
            ventas_con_detalle.append({
                "id": venta[0],
                "fecha": venta[1],
                "total": venta[2],
                "usuario_id": venta[3],
                "usuario": venta[4] if venta[4] else "Usuario eliminado",
                "nombre_completo": venta[5] if venta[5] else "Usuario eliminado",
                "rol": venta[6] if venta[6] else "unknown",
                "detalles": detalles
            })
        
        conn.close()
        return ventas_con_detalle

class LogAccion:
    """Modelo para log de acciones"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, user_id, action, details=None):
        """Registra una acción en el log"""
        conn = self.db.get_connection()
        c = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO log_acciones (usuario_id, accion, detalles, fecha) VALUES (?, ?, ?, ?)",
                  (user_id, action, details, fecha))
        conn.commit()
        conn.close()
    
    def get_filtered(self, usuario_filtro=None, fecha_desde=None, fecha_hasta=None):
        """Obtiene logs filtrados"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Construir consulta base
        query = '''SELECT l.id, l.usuario_id, l.accion, l.detalles, l.fecha, u.usuario, u.rol
                   FROM log_acciones l 
                   JOIN usuarios u ON l.usuario_id = u.id
                   WHERE 1=1'''
        params = []
        
        # Aplicar filtros
        if usuario_filtro:
            query += ' AND l.usuario_id = ?'
            params.append(usuario_filtro)
        
        if fecha_desde:
            query += ' AND DATE(l.fecha) >= ?'
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += ' AND DATE(l.fecha) <= ?'
            params.append(fecha_hasta)
        
        query += ' ORDER BY l.fecha DESC LIMIT 500'
        
        c.execute(query, params)
        logs = c.fetchall()
        conn.close()
        return logs
    
    def get_stats(self):
        """Obtiene estadísticas del sistema"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Usuarios activos
        c.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
        usuarios_activos = c.fetchone()[0]
        
        # Ventas de hoy
        hoy = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
        ventas_hoy = c.fetchone()[0]
        
        conn.close()
        return {
            'usuarios_activos': usuarios_activos,
            'ventas_hoy': ventas_hoy
        }
