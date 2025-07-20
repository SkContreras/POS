#!/usr/bin/env python3
"""
Modelos de base de datos para el sistema POS
"""
import sqlite3
import time
from datetime import datetime
from werkzeug.security import generate_password_hash

class DatabaseManager:
    """Gestor de la base de datos"""
    
    def __init__(self, db_name):
        self.db_name = db_name
    
    def get_connection(self, timeout=30):
        """Obtiene una conexión a la base de datos con manejo de reintentos"""
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(self.db_name, timeout=timeout)
                # Configurar WAL mode para mejor concurrencia
                conn.execute('PRAGMA journal_mode=WAL;')
                # Configurar timeout para transacciones más largo
                conn.execute('PRAGMA busy_timeout=60000;')
                # Configurar opciones adicionales para mejor rendimiento
                conn.execute('PRAGMA synchronous=NORMAL;')
                conn.execute('PRAGMA cache_size=10000;')
                conn.execute('PRAGMA temp_store=memory;')
                return conn
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"DEBUG: Base de datos bloqueada, reintentando en {retry_delay}s (intento {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponencial
                else:
                    raise e
    
    def init_db(self):
        """Inicializa la base de datos con todas las tablas"""
        conn = self.get_connection()
        if conn is None:
            raise RuntimeError("No se pudo obtener una conexión a la base de datos.")
        c = conn.cursor()
        
        # Tabla de productos
        c.execute('''CREATE TABLE IF NOT EXISTS productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        precio_compra REAL DEFAULT 0,
                        precio_venta REAL NOT NULL,
                        imagen TEXT NOT NULL,
                        categoria TEXT DEFAULT 'Platillos de cocina',
                        fecha_agregado TEXT DEFAULT CURRENT_TIMESTAMP,
                        veces_vendido INTEGER DEFAULT 0,
                        stock INTEGER DEFAULT 0
                    )''')
        
        # Migración: Agregar columna categoria si no existe
        try:
            c.execute("SELECT categoria FROM productos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE productos ADD COLUMN categoria TEXT DEFAULT 'Platillos de cocina'")
            # Actualizar productos existentes que no tengan categoría
            c.execute("UPDATE productos SET categoria = 'Platillos de cocina' WHERE categoria IS NULL")
            conn.commit()
            print("✅ Migración aplicada: Columna categoria agregada a la tabla productos")
        
        # Migración: Agregar columna fecha_agregado si no existe
        try:
            c.execute("SELECT fecha_agregado FROM productos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE productos ADD COLUMN fecha_agregado TEXT")
            # Actualizar productos existentes con fecha actual
            c.execute("UPDATE productos SET fecha_agregado = datetime('now') WHERE fecha_agregado IS NULL")
            conn.commit()
            print("✅ Migración aplicada: Columna fecha_agregado agregada a la tabla productos")
        
        # Migración: Agregar columna veces_vendido si no existe
        try:
            c.execute("SELECT veces_vendido FROM productos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE productos ADD COLUMN veces_vendido INTEGER DEFAULT 0")
            # Actualizar productos existentes con contador en 0
            c.execute("UPDATE productos SET veces_vendido = 0 WHERE veces_vendido IS NULL")
            conn.commit()
            print("✅ Migración aplicada: Columna veces_vendido agregada a la tabla productos")
        
        # Migración: Agregar columna stock si no existe
        try:
            c.execute("SELECT stock FROM productos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
            # Para productos de pescadería, establecer stock inicial
            c.execute("UPDATE productos SET stock = 10 WHERE categoria = 'Pescadería'")
            # Para platillos de cocina, establecer stock alto (productos no perecederos)
            c.execute("UPDATE productos SET stock = 999 WHERE categoria = 'Platillos de cocina'")
            conn.commit()
            print("✅ Migración aplicada: Columna stock agregada a la tabla productos")

        # Migración: Agregar columna precio_compra si no existe
        try:
            c.execute("SELECT precio_compra FROM productos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE productos ADD COLUMN precio_compra REAL DEFAULT 0")
            # Actualizar productos existentes - por defecto el precio de compra será 70% del precio de venta
            c.execute("UPDATE productos SET precio_compra = precio * 0.7 WHERE precio_compra IS NULL OR precio_compra = 0")
            if conn:
                conn.commit()
            print("✅ Migración aplicada: Columna precio_compra agregada a la tabla productos")

        # Migración: Renombrar columna precio a precio_venta para mayor claridad
        try:
            c.execute("SELECT precio_venta FROM productos LIMIT 1")
        except sqlite3.OperationalError:
            # Crear nueva tabla temporal con la estructura correcta
            c.execute('''CREATE TABLE productos_temp (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            precio_compra REAL DEFAULT 0,
                            precio_venta REAL NOT NULL,
                            imagen TEXT NOT NULL,
                            categoria TEXT DEFAULT 'Platillos de cocina',
                            fecha_agregado TEXT DEFAULT CURRENT_TIMESTAMP,
                            veces_vendido INTEGER DEFAULT 0,
                            stock INTEGER DEFAULT 0
                        )''')
            
            # Copiar datos existentes, renombrando precio a precio_venta
            c.execute('''INSERT INTO productos_temp 
                        (id, nombre, precio_compra, precio_venta, imagen, categoria, fecha_agregado, veces_vendido, stock)
                        SELECT id, nombre, 
                               COALESCE(precio_compra, precio * 0.7) as precio_compra,
                               precio as precio_venta, 
                               imagen, categoria, fecha_agregado, veces_vendido, stock 
                        FROM productos''')
            
            # Eliminar tabla original y renombrar la temporal
            c.execute('DROP TABLE productos')
            c.execute('ALTER TABLE productos_temp RENAME TO productos')
            conn.commit()
            print("✅ Migración aplicada: Estructura de precios actualizada (precio_compra, precio_venta)")
        
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
        
        # Tabla de gastos operativos
        c.execute('''CREATE TABLE IF NOT EXISTS gastos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        categoria TEXT NOT NULL,
                        subcategoria TEXT,
                        descripcion TEXT NOT NULL,
                        monto REAL NOT NULL,
                        fecha TEXT NOT NULL,
                        fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                        usuario_id INTEGER,
                        comprobante TEXT,
                        recurrente INTEGER DEFAULT 0,
                        frecuencia_dias INTEGER DEFAULT 0,
                        activo INTEGER DEFAULT 1,
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
    
    def create(self, nombre, precio_venta, imagen, categoria='Platillos de cocina', stock=None, precio_compra=None):
        """Crea un nuevo producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Determinar stock inicial según categoría si no se especifica
        if stock is None:
            stock = 10 if categoria == 'Pescadería' else 999
        
        # Si no se especifica precio de compra, usar 70% del precio de venta como default
        if precio_compra is None:
            precio_compra = float(precio_venta) * 0.7
        
        c.execute("""INSERT INTO productos 
                     (nombre, precio_compra, precio_venta, imagen, categoria, fecha_agregado, veces_vendido, stock) 
                     VALUES (?, ?, ?, ?, ?, datetime('now'), 0, ?)""",
                  (nombre, precio_compra, precio_venta, imagen, categoria, stock))
        product_id = c.lastrowid
        conn.commit()
        conn.close()
        return product_id
    
    def update(self, product_id, nombre, precio_venta, imagen, categoria='Platillos de cocina', stock=None, precio_compra=None):
        """Actualiza un producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Si no se especifica precio de compra, mantener el actual o calcular 70% del precio de venta
        if precio_compra is None:
            # Obtener precio de compra actual
            producto_actual = self.get_by_id(product_id)
            if producto_actual and len(producto_actual) > 2:
                precio_compra = producto_actual[2] if producto_actual[2] > 0 else float(precio_venta) * 0.7
            else:
                precio_compra = float(precio_venta) * 0.7
        
        if stock is not None:
            c.execute("""UPDATE productos SET 
                         nombre = ?, precio_compra = ?, precio_venta = ?, imagen = ?, categoria = ?, stock = ? 
                         WHERE id = ?""",
                      (nombre, precio_compra, precio_venta, imagen, categoria, stock, product_id))
        else:
            c.execute("""UPDATE productos SET 
                         nombre = ?, precio_compra = ?, precio_venta = ?, imagen = ?, categoria = ? 
                         WHERE id = ?""",
                      (nombre, precio_compra, precio_venta, imagen, categoria, product_id))
        conn.commit()
        conn.close()
    
    def delete(self, product_id):
        """Elimina un producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM productos WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
    
    def get_all_filtered(self, order_by='fecha_agregado', categoria=None, busqueda=None):
        """Obtiene productos con filtros y ordenamiento"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Construir consulta base
        query = "SELECT * FROM productos WHERE 1=1"
        params = []
        
        # Filtro por categoría
        if categoria and categoria != 'todas':
            query += " AND categoria = ?"
            params.append(categoria)
        
        # Filtro por búsqueda
        if busqueda:
            query += " AND nombre LIKE ?"
            params.append(f"%{busqueda}%")
        
        # Ordenamiento
        if order_by == 'alfabetico':
            query += " ORDER BY nombre ASC"
        elif order_by == 'precio_asc':
            query += " ORDER BY precio_venta ASC"
        elif order_by == 'precio_desc':
            query += " ORDER BY precio_venta DESC"
        elif order_by == 'mas_vendido':
            query += " ORDER BY veces_vendido DESC"
        elif order_by == 'menos_vendido':
            query += " ORDER BY veces_vendido ASC"
        elif order_by == 'recientes':
            query += " ORDER BY fecha_agregado DESC"
        elif order_by == 'antiguos':
            query += " ORDER BY fecha_agregado ASC"
        else:  # por defecto fecha de agregado desc
            query += " ORDER BY fecha_agregado DESC"
        
        c.execute(query, params)
        productos = c.fetchall()
        conn.close()
        return productos
    
    def increment_sales_count(self, product_id):
        """Incrementa el contador de ventas de un producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE productos SET veces_vendido = veces_vendido + 1 WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
    
    def get_categories(self):
        """Obtiene todas las categorías disponibles"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria")
        categorias = [row[0] for row in c.fetchall()]
        conn.close()
        return categorias
    
    def reduce_stock(self, product_id, cantidad):
        """Reduce el stock de un producto con manejo de reintentos mejorado"""
        max_retries = 5
        
        for attempt in range(max_retries):
            conn = None
            try:
                conn = self.db.get_connection()
                c = conn.cursor()
                
                # Iniciar transacción inmediata para evitar bloqueos
                c.execute('BEGIN IMMEDIATE;')
                
                # Verificar stock actual
                c.execute("SELECT stock FROM productos WHERE id = ?", (product_id,))
                stock_actual = c.fetchone()
                
                if stock_actual and stock_actual[0] >= cantidad:
                    # Actualizar stock
                    c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, product_id))
                    conn.commit()
                    conn.close()
                    print(f"DEBUG: Stock reducido exitosamente para producto {product_id}")
                    return True
                else:
                    conn.rollback()
                    conn.close()
                    print(f"DEBUG: Stock insuficiente para producto {product_id}: disponible {stock_actual[0] if stock_actual else 0}, requerido {cantidad}")
                    return False
                    
            except sqlite3.OperationalError as e:
                if conn:
                    try:
                        conn.rollback()
                        conn.close()
                    except:
                        pass
                    
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    delay = 0.5 * (2 ** attempt)  # Backoff exponencial más agresivo
                    print(f"DEBUG: Base de datos bloqueada en reduce_stock, reintentando en {delay}s (intento {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"DEBUG: Error en reduce_stock después de {attempt + 1} intentos: {str(e)}")
                    return False
                    
            except Exception as e:
                if conn:
                    try:
                        conn.rollback()
                        conn.close()
                    except:
                        pass
                print(f"DEBUG: Error inesperado en reduce_stock: {str(e)}")
                return False
        
        print(f"DEBUG: reduce_stock falló después de {max_retries} intentos")
        return False
    
    def update_stock(self, product_id, nuevo_stock):
        """Actualiza el stock de un producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, product_id))
        conn.commit()
        conn.close()
    
    def get_low_stock_products(self, umbral=5):
        """Obtiene productos con stock bajo"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM productos WHERE stock <= ? AND categoria = 'Pescadería' ORDER BY stock ASC", (umbral,))
        productos = c.fetchall()
        conn.close()
        return productos
    
    def check_stock(self, product_id):
        """Verifica el stock de un producto con manejo de reintentos"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                conn = self.db.get_connection()
                c = conn.cursor()
                c.execute("SELECT stock FROM productos WHERE id = ?", (product_id,))
                stock = c.fetchone()
                conn.close()
                return stock[0] if stock else 0
                
            except sqlite3.OperationalError as e:
                if conn:
                    conn.close()
                    
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"DEBUG: Base de datos bloqueada en check_stock, reintentando (intento {attempt + 1}/{max_retries})")
                    time.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    print(f"DEBUG: Error en check_stock: {str(e)}")
                    return 0
                    
            except Exception as e:
                if conn:
                    conn.close()
                print(f"DEBUG: Error inesperado en check_stock: {str(e)}")
                return 0
        
        return 0

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
    
    def create(self, total, usuario_id, carrito, producto_model=None):
        """Crea una nueva venta con sus detalles y maneja el stock"""
        conn = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                conn = self.db.get_connection()
                c = conn.cursor()
                
                # Iniciar transacción explícita
                c.execute('BEGIN IMMEDIATE;')
                
                # Verificar stock disponible antes de procesar la venta
                if producto_model:
                    for item in carrito:
                        stock_actual = producto_model.check_stock(item["id"])
                        if stock_actual < item["cantidad"]:
                            # Si no hay suficiente stock, cancelar la venta
                            conn.rollback()
                            conn.close()
                            return None, f"Stock insuficiente para {item['nombre']}. Stock disponible: {stock_actual}"
                
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO ventas (fecha, total, usuario_id) VALUES (?, ?, ?)", 
                          (fecha, total, usuario_id))
                venta_id = c.lastrowid
                
                # Agregar detalles de la venta y reducir stock
                for item in carrito:
                    c.execute(
                        "INSERT INTO ventas_detalle (venta_id, producto_id, nombre, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            venta_id,
                            item["id"],
                            item["nombre"],
                            item["cantidad"],
                            item["precio"],  # Este precio viene del frontend, corresponde al precio_venta
                            item["precio"] * item["cantidad"],
                        ),
                    )
                    
                    # Reducir stock directamente en esta transacción
                    if producto_model:
                        # Verificar stock actual antes de reducir
                        c.execute("SELECT stock FROM productos WHERE id = ?", (item["id"],))
                        stock_actual = c.fetchone()
                        
                        if stock_actual and stock_actual[0] >= item["cantidad"]:
                            # Reducir stock
                            c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", 
                                    (item["cantidad"], item["id"]))
                        else:
                            # Si no hay suficiente stock, hacer rollback
                            conn.rollback()
                            conn.close()
                            return None, f"Stock insuficiente para {item['nombre']}. Disponible: {stock_actual[0] if stock_actual else 0}"
                
                conn.commit()
                conn.close()
                print(f"DEBUG: Venta creada exitosamente - ID: {venta_id}")
                return venta_id, None
                
            except sqlite3.OperationalError as e:
                if conn:
                    conn.rollback()
                    conn.close()
                
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"DEBUG: Base de datos bloqueada en venta, reintentando (intento {attempt + 1}/{max_retries})")
                    time.sleep(0.5 * (attempt + 1))  # Delay progresivo
                    continue
                else:
                    print(f"DEBUG: Error de base de datos en venta: {str(e)}")
                    return None, f"Error de base de datos: {str(e)}"
                    
            except Exception as e:
                if conn:
                    conn.rollback()
                    conn.close()
                print(f"DEBUG: Error inesperado en venta: {str(e)}")
                return None, str(e)
        
        return None, "Error: No se pudo completar la venta después de varios intentos"
    
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
    
    def get_estadisticas_periodo(self, fecha_inicio, fecha_fin):
        """Obtiene estadísticas generales para un período"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Estadísticas básicas
        c.execute("""
            SELECT 
                COUNT(*) as total_ventas,
                COALESCE(SUM(total), 0) as ingresos_totales,
                COALESCE(AVG(total), 0) as venta_promedio,
                COALESCE(MAX(total), 0) as venta_maxima,
                COALESCE(MIN(total), 0) as venta_minima
            FROM ventas 
            WHERE DATE(fecha) BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        
        stats = c.fetchone()
        
        # Número de productos vendidos
        c.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        
        productos_vendidos = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_ventas': stats[0],
            'ingresos_totales': round(stats[1], 2),
            'venta_promedio': round(stats[2], 2),
            'venta_maxima': round(stats[3], 2),
            'venta_minima': round(stats[4], 2),
            'productos_vendidos': productos_vendidos
        }
    
    def get_ventas_por_dia(self, fecha_inicio, fecha_fin):
        """Obtiene ventas agrupadas por día"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                DATE(fecha) as dia,
                COUNT(*) as num_ventas,
                COALESCE(SUM(total), 0) as ingresos
            FROM ventas 
            WHERE DATE(fecha) BETWEEN ? AND ?
            GROUP BY DATE(fecha)
            ORDER BY dia
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'fecha': r[0], 'cantidad': r[1], 'total': round(r[2], 2)} for r in resultados]
    
    def get_ventas_por_hora(self, fecha_inicio, fecha_fin):
        """Obtiene ventas agrupadas por hora del día"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                CAST(strftime('%H', fecha) AS INTEGER) as hora,
                COUNT(*) as num_ventas,
                COALESCE(SUM(total), 0) as ingresos
            FROM ventas 
            WHERE DATE(fecha) BETWEEN ? AND ?
            GROUP BY hora
            ORDER BY hora
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'hora': r[0], 'cantidad': r[1], 'total': round(r[2], 2)} for r in resultados]
    
    def get_ventas_por_mes(self, fecha_inicio, fecha_fin):
        """Obtiene ventas agrupadas por mes"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                strftime('%Y-%m', fecha) as mes,
                COUNT(*) as num_ventas,
                COALESCE(SUM(total), 0) as ingresos
            FROM ventas 
            WHERE DATE(fecha) BETWEEN ? AND ?
            GROUP BY mes
            ORDER BY mes
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'mes': r[0], 'cantidad': r[1], 'total': round(r[2], 2)} for r in resultados]
    
    def get_productos_mas_vendidos(self, fecha_inicio, fecha_fin, limit=10):
        """Obtiene los productos más vendidos"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                vd.nombre,
                SUM(vd.cantidad) as cantidad_vendida,
                COALESCE(SUM(vd.subtotal), 0) as ingresos_producto
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY vd.nombre
            ORDER BY cantidad_vendida DESC
            LIMIT ?
        """, (fecha_inicio, fecha_fin, limit))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'nombre': r[0], 'cantidad': r[1], 'total_ingresos': round(r[2], 2)} for r in resultados]
    
    def get_ingresos_por_categoria(self, fecha_inicio, fecha_fin):
        """Obtiene ingresos agrupados por categoría de productos"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                COALESCE(p.categoria, 'Sin categoría') as categoria,
                COUNT(vd.id) as num_ventas,
                COALESCE(SUM(vd.subtotal), 0) as ingresos
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            LEFT JOIN productos p ON vd.producto_id = p.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY categoria
            ORDER BY ingresos DESC
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'categoria': r[0], 'cantidad': r[1], 'total': round(r[2], 2)} for r in resultados]
    
    def get_ventas_detalladas(self, fecha_inicio, fecha_fin):
        """Obtiene todas las ventas del período con información completa"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''SELECT v.id, v.fecha, v.total, v.usuario_id, u.usuario, u.nombre_completo
                     FROM ventas v 
                     LEFT JOIN usuarios u ON v.usuario_id = u.id 
                     WHERE DATE(v.fecha) BETWEEN ? AND ?
                     ORDER BY v.fecha ASC''', (fecha_inicio, fecha_fin))
        
        ventas = []
        for row in c.fetchall():
            ventas.append({
                'id': row[0],
                'fecha_hora': row[1],
                'total': row[2],
                'usuario_id': row[3],
                'vendedor': row[5] if row[5] else f"Usuario {row[4]}" if row[4] else "Usuario eliminado"
            })
        
        conn.close()
        return ventas
    
    def get_productos_venta(self, venta_id):
        """Obtiene los productos de una venta específica"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute('''SELECT nombre, cantidad, precio_unitario, subtotal 
                     FROM ventas_detalle 
                     WHERE venta_id = ? 
                     ORDER BY nombre''', (venta_id,))
        
        productos = []
        for row in c.fetchall():
            productos.append({
                'nombre': row[0],
                'cantidad': row[1],
                'precio': row[2],
                'subtotal': row[3]
            })
        
        conn.close()
        return productos
    
    def get_analisis_rentabilidad(self, fecha_inicio, fecha_fin):
        """Obtiene análisis completo de rentabilidad por producto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Análisis de rentabilidad por producto con costos reales
        c.execute("""
            SELECT 
                vd.nombre,
                SUM(vd.cantidad) as cantidad_vendida,
                AVG(p.precio_compra) as precio_compra_promedio,
                AVG(vd.precio_unitario) as precio_venta_promedio,
                SUM(vd.subtotal) as ingresos_totales,
                SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) as costos_totales,
                SUM(vd.subtotal) - SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) as ganancia_real,
                CASE 
                    WHEN SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) > 0 
                    THEN ((SUM(vd.subtotal) - SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7))) / SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7))) * 100
                    ELSE 0 
                END as margen_porcentaje
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            LEFT JOIN productos p ON vd.producto_id = p.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY vd.nombre
            ORDER BY ganancia_real DESC
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        analisis = []
        for r in resultados:
            analisis.append({
                'nombre': r[0],
                'cantidad_vendida': r[1],
                'precio_compra_promedio': round(r[2] or 0, 2),
                'precio_venta_promedio': round(r[3] or 0, 2),
                'ingresos_totales': round(r[4] or 0, 2),
                'costos_totales': round(r[5] or 0, 2),
                'ganancia_real': round(r[6] or 0, 2),
                'margen_porcentaje': round(r[7] or 0, 1)
            })
        
        return analisis

    def get_resumen_financiero(self, fecha_inicio, fecha_fin):
        """Obtiene resumen financiero completo del período"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        # Resumen financiero general
        c.execute("""
            SELECT 
                SUM(vd.subtotal) as ingresos_totales,
                SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) as costos_totales,
                COUNT(DISTINCT v.id) as numero_ventas,
                SUM(vd.cantidad) as productos_vendidos
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            LEFT JOIN productos p ON vd.producto_id = p.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
        """, (fecha_inicio, fecha_fin))
        
        resultado = c.fetchone()
        
        if resultado:
            ingresos = resultado[0] or 0
            costos = resultado[1] or 0
            ganancia_bruta = ingresos - costos
            margen_bruto = (ganancia_bruta / ingresos * 100) if ingresos > 0 else 0
            roi = (ganancia_bruta / costos * 100) if costos > 0 else 0
            
            resumen = {
                'ingresos_totales': round(ingresos, 2),
                'costos_totales': round(costos, 2),
                'ganancia_bruta': round(ganancia_bruta, 2),
                'margen_bruto': round(margen_bruto, 1),
                'roi': round(roi, 1),
                'numero_ventas': resultado[2] or 0,
                'productos_vendidos': resultado[3] or 0,
                'ticket_promedio': round(ingresos / (resultado[2] or 1), 2)
            }
        else:
            resumen = {
                'ingresos_totales': 0,
                'costos_totales': 0,
                'ganancia_bruta': 0,
                'margen_bruto': 0,
                'roi': 0,
                'numero_ventas': 0,
                'productos_vendidos': 0,
                'ticket_promedio': 0
            }
        
        conn.close()
    def get_resumen_financiero_completo(self, fecha_inicio, fecha_fin, gasto_model=None):
        """Obtiene resumen financiero completo incluyendo gastos operativos"""
        # Obtener resumen básico de ventas
        resumen_ventas = self.get_resumen_financiero(fecha_inicio, fecha_fin)
        
        # Verificar que el resumen no sea None
        if not resumen_ventas:
            resumen_ventas = {
                'ingresos_totales': 0,
                'costos_totales': 0,
                'ganancia_bruta': 0,
                'margen_bruto': 0,
                'roi': 0,
                'numero_ventas': 0,
                'productos_vendidos': 0,
                'ticket_promedio': 0
            }
        
        # Obtener gastos operativos si se proporciona el modelo
        gastos_operativos = 0
        if gasto_model:
            try:
                estadisticas_gastos = gasto_model.get_estadisticas_gastos(fecha_inicio, fecha_fin)
                gastos_operativos = estadisticas_gastos.get('gastos_totales', 0) if estadisticas_gastos else 0
            except Exception as e:
                print(f"Error al obtener gastos: {e}")
                gastos_operativos = 0
        
        # Calcular métricas finales
        ingresos_totales = resumen_ventas.get('ingresos_totales', 0)
        costos_productos = resumen_ventas.get('costos_totales', 0)
        gastos_operativos_total = gastos_operativos
        
        # Ganancia bruta (ingresos - costo de productos)
        ganancia_bruta = ingresos_totales - costos_productos
        
        # Ganancia neta (ganancia bruta - gastos operativos)
        ganancia_neta = ganancia_bruta - gastos_operativos_total
        
        # Márgenes
        margen_bruto = (ganancia_bruta / ingresos_totales * 100) if ingresos_totales > 0 else 0
        margen_neto = (ganancia_neta / ingresos_totales * 100) if ingresos_totales > 0 else 0
        
        # ROI considerando todos los costos
        costos_totales = costos_productos + gastos_operativos_total
        roi = (ganancia_neta / costos_totales * 100) if costos_totales > 0 else 0
        
        return {
            'ingresos_totales': round(ingresos_totales, 2),
            'costos_productos': round(costos_productos, 2),
            'gastos_operativos': round(gastos_operativos_total, 2),
            'costos_totales': round(costos_totales, 2),
            'ganancia_bruta': round(ganancia_bruta, 2),
            'ganancia_neta': round(ganancia_neta, 2),
            'margen_bruto': round(margen_bruto, 1),
            'margen_neto': round(margen_neto, 1),
            'roi': round(roi, 1),
            'numero_ventas': resumen_ventas.get('numero_ventas', 0),
            'productos_vendidos': resumen_ventas.get('productos_vendidos', 0),
            'ticket_promedio': resumen_ventas.get('ticket_promedio', 0),
            'eficiencia_operativa': round((ganancia_bruta / gastos_operativos_total * 100) if gastos_operativos_total > 0 else 0, 1)
        }

    def get_productos_menos_rentables(self, fecha_inicio, fecha_fin, limit=10):
        """Obtiene los productos menos rentables que necesitan atención"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                vd.nombre,
                AVG(COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) as precio_compra,
                AVG(vd.precio_unitario) as precio_venta,
                SUM(vd.cantidad) as cantidad_vendida,
                CASE 
                    WHEN AVG(COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) > 0 
                    THEN ((AVG(vd.precio_unitario) - AVG(COALESCE(p.precio_compra, vd.precio_unitario * 0.7))) / AVG(COALESCE(p.precio_compra, vd.precio_unitario * 0.7))) * 100
                    ELSE 0 
                END as margen_porcentaje
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            LEFT JOIN productos p ON vd.producto_id = p.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY vd.nombre
            HAVING margen_porcentaje < 20  -- Productos con margen menor al 20%
            ORDER BY margen_porcentaje ASC
            LIMIT ?
        """, (fecha_inicio, fecha_fin, limit))
        
        resultados = c.fetchall()
        conn.close()
        
        productos_atencion = []
        for r in resultados:
            productos_atencion.append({
                'nombre': r[0],
                'precio_compra': round(r[1] or 0, 2),
                'precio_venta': round(r[2] or 0, 2),
                'cantidad_vendida': r[3],
                'margen_porcentaje': round(r[4] or 0, 1),
                'recomendacion': self._generar_recomendacion_precio(r[1] or 0, r[4] or 0)
            })
        
        return productos_atencion
    
    def _generar_recomendacion_precio(self, precio_compra, margen_actual):
        """Genera recomendación de precio para mejorar margen"""
        if precio_compra <= 0:
            return "Verificar precio de compra"
        
        # Calcular precio sugerido para margen del 30%
        precio_sugerido = precio_compra * 1.3
        
        if margen_actual < 10:
            return f"CRÍTICO: Sugerir precio ${precio_sugerido:.2f} (margen 30%)"
        elif margen_actual < 20:
            return f"Mejorar: Sugerir precio ${precio_sugerido:.2f}"
        else:
            return "Margen aceptable"

    def get_analisis_por_categoria(self, fecha_inicio, fecha_fin):
        """Obtiene análisis de rentabilidad por categoría"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                COALESCE(p.categoria, 'Sin categoría') as categoria,
                SUM(vd.subtotal) as ingresos,
                SUM(vd.cantidad * COALESCE(p.precio_compra, vd.precio_unitario * 0.7)) as costos,
                SUM(vd.cantidad) as productos_vendidos,
                COUNT(DISTINCT vd.producto_id) as productos_diferentes
            FROM ventas_detalle vd
            JOIN ventas v ON vd.venta_id = v.id
            LEFT JOIN productos p ON vd.producto_id = p.id
            WHERE DATE(v.fecha) BETWEEN ? AND ?
            GROUP BY categoria
            ORDER BY ingresos DESC
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        analisis_categoria = []
        for r in resultados:
            ingresos = r[1] or 0
            costos = r[2] or 0
            ganancia = ingresos - costos
            margen = (ganancia / ingresos * 100) if ingresos > 0 else 0
            
            analisis_categoria.append({
                'categoria': r[0],
                'ingresos': round(ingresos, 2),
                'costos': round(costos, 2),
                'ganancia': round(ganancia, 2),
                'margen_porcentaje': round(margen, 1),
                'productos_vendidos': r[3],
                'productos_diferentes': r[4]
            })
        
        return analisis_categoria

class Gasto:
    """Modelo para gastos operativos"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create(self, categoria, descripcion, monto, fecha, usuario_id, subcategoria=None, comprobante=None, recurrente=False, frecuencia_dias=0):
        """Crea un nuevo gasto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""INSERT INTO gastos 
                     (categoria, subcategoria, descripcion, monto, fecha, usuario_id, comprobante, recurrente, frecuencia_dias) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (categoria, subcategoria, descripcion, monto, fecha, usuario_id, comprobante, 
                   1 if recurrente else 0, frecuencia_dias))
        
        gasto_id = c.lastrowid
        conn.commit()
        conn.close()
        return gasto_id
    
    def get_all(self, fecha_inicio=None, fecha_fin=None, categoria=None):
        """Obtiene todos los gastos con filtros opcionales"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        query = """SELECT g.*, u.nombre_completo, u.usuario 
                  FROM gastos g 
                  LEFT JOIN usuarios u ON g.usuario_id = u.id 
                  WHERE g.activo = 1"""
        params = []
        
        if fecha_inicio and fecha_fin:
            query += " AND DATE(g.fecha) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        
        if categoria:
            query += " AND g.categoria = ?"
            params.append(categoria)
        
        query += " ORDER BY g.fecha DESC"
        
        c.execute(query, params)
        gastos = c.fetchall()
        conn.close()
        return gastos
    
    def get_by_id(self, gasto_id):
        """Obtiene un gasto por ID"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM gastos WHERE id = ? AND activo = 1", (gasto_id,))
        gasto = c.fetchone()
        conn.close()
        return gasto
    
    def update(self, gasto_id, categoria, descripcion, monto, fecha, subcategoria=None, comprobante=None, recurrente=False, frecuencia_dias=0):
        """Actualiza un gasto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""UPDATE gastos SET 
                     categoria = ?, subcategoria = ?, descripcion = ?, monto = ?, fecha = ?, 
                     comprobante = ?, recurrente = ?, frecuencia_dias = ?
                     WHERE id = ?""",
                  (categoria, subcategoria, descripcion, monto, fecha, comprobante,
                   1 if recurrente else 0, frecuencia_dias, gasto_id))
        
        conn.commit()
        conn.close()
    
    def delete(self, gasto_id):
        """Elimina (desactiva) un gasto"""
        conn = self.db.get_connection()
        c = conn.cursor()
        c.execute("UPDATE gastos SET activo = 0 WHERE id = ?", (gasto_id,))
        conn.commit()
        conn.close()
    
    def get_gastos_por_categoria(self, fecha_inicio, fecha_fin):
        """Obtiene gastos agrupados por categoría"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                categoria,
                COUNT(*) as num_gastos,
                SUM(monto) as total_monto
            FROM gastos 
            WHERE DATE(fecha) BETWEEN ? AND ? AND activo = 1
            GROUP BY categoria
            ORDER BY total_monto DESC
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'categoria': r[0], 'cantidad': r[1], 'total': round(r[2], 2)} for r in resultados]
    
    def get_gastos_por_dia(self, fecha_inicio, fecha_fin):
        """Obtiene gastos agrupados por día"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                DATE(fecha) as dia,
                COUNT(*) as num_gastos,
                SUM(monto) as total_monto
            FROM gastos 
            WHERE DATE(fecha) BETWEEN ? AND ? AND activo = 1
            GROUP BY DATE(fecha)
            ORDER BY dia
        """, (fecha_inicio, fecha_fin))
        
        resultados = c.fetchall()
        conn.close()
        
        return [{'fecha': r[0], 'cantidad': r[1], 'total': round(r[2], 2)} for r in resultados]
    
    def get_estadisticas_gastos(self, fecha_inicio, fecha_fin):
        """Obtiene estadísticas generales de gastos"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                COUNT(*) as total_gastos,
                SUM(monto) as gastos_totales,
                AVG(monto) as gasto_promedio,
                MAX(monto) as gasto_maximo,
                MIN(monto) as gasto_minimo
            FROM gastos 
            WHERE DATE(fecha) BETWEEN ? AND ? AND activo = 1
        """, (fecha_inicio, fecha_fin))
        
        stats = c.fetchone()
        conn.close()
        
        return {
            'total_gastos': stats[0] or 0,
            'gastos_totales': round(stats[1] or 0, 2),
            'gasto_promedio': round(stats[2] or 0, 2),
            'gasto_maximo': round(stats[3] or 0, 2),
            'gasto_minimo': round(stats[4] or 0, 2)
        }
    
    def get_gastos_recurrentes(self):
        """Obtiene los gastos marcados como recurrentes"""
        conn = self.db.get_connection()
        c = conn.cursor()
        
        c.execute("""SELECT * FROM gastos 
                     WHERE recurrente = 1 AND activo = 1 
                     ORDER BY fecha DESC""")
        
        gastos = c.fetchall()
        conn.close()
        return gastos
    
    def get_categorias_predefinidas(self):
        """Obtiene las categorías de gastos predefinidas"""
        return {
            'Servicios Básicos': ['Luz', 'Agua', 'Gas', 'Internet', 'Teléfono'],
            'Transporte': ['Gasolina', 'Mantenimiento de vehículo', 'Transporte público', 'Estacionamiento'],
            'Pérdidas y Mermas': ['Productos vencidos', 'Productos dañados', 'Robo/Hurto', 'Desperdicios'],
            'Mantenimiento': ['Reparaciones', 'Limpieza', 'Suministros', 'Herramientas'],
            'Personal': ['Salarios', 'Bonificaciones', 'Prestaciones', 'Capacitación'],
            'Impuestos y Licencias': ['Impuestos', 'Licencias', 'Permisos', 'Multas'],
            'Suministros': ['Productos de limpieza', 'Papelería', 'Bolsas', 'Servilletas'],
            'Marketing': ['Publicidad', 'Promociones', 'Volantes', 'Redes sociales'],
            'Otros': ['Diversos', 'Imprevistos', 'Emergencias']
        }

class LogAccion:
    def __init__(self, db_manager):
        self.db = db_manager

    def registrar(self, usuario_id, accion, detalles=None):
        """Registra una acción en el log"""
        try:
            conn = self.db.get_connection()
            c = conn.cursor()
            c.execute("""
                INSERT INTO log_acciones (usuario_id, accion, detalles)
                VALUES (?, ?, ?)
            """, (usuario_id, accion, detalles))
            conn.commit()
            log_id = c.lastrowid
            conn.close()
            return log_id, None
        except Exception as e:
            return None, str(e)

    def get_filtered(self, usuario=None, fecha_desde=None, fecha_hasta=None, limit=100):
        """Obtiene los logs filtrados por usuario y rango de fechas"""
        conn = self.db.get_connection()
        c = conn.cursor()
        query = '''
            SELECT la.id, u.nombre_completo, la.accion, la.detalles, la.fecha, u.usuario, u.rol
            FROM log_acciones la
            LEFT JOIN usuarios u ON la.usuario_id = u.id
            WHERE 1=1
        '''
        params = []
        if usuario:
            query += ' AND u.id = ?'
            params.append(usuario)
        if fecha_desde:
            query += ' AND la.fecha >= ?'
            params.append(fecha_desde + ' 00:00:00')
        if fecha_hasta:
            query += ' AND la.fecha <= ?'
            params.append(fecha_hasta + ' 23:59:59')
        query += ' ORDER BY la.fecha DESC LIMIT ?'
        params.append(limit)
        c.execute(query, tuple(params))
        logs = c.fetchall()
        conn.close()
        return logs