from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, session
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import socket
import io
import webbrowser
import time
import threading
import qrcode
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '14/Oct/14')
app.permanent_session_lifetime = timedelta(hours=8)  # Sesión expira en 8 horas
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Cookie no accesible desde JavaScript
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiar a True en producción con HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protección CSRF básica
DB_NAME = 'database.db'
UPLOAD_FOLDER = 'static/img'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Marca temporal de inicio del servidor (para invalidar sesiones anteriores)
SERVER_START_TIME = datetime.now()

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabla de productos existente
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    imagen TEXT NOT NULL
                )''')
    
    # Tabla de ventas existente
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
        # La columna no existe, agregarla
        c.execute("ALTER TABLE ventas ADD COLUMN usuario_id INTEGER")
        print("✅ Migración aplicada: Columna usuario_id agregada a la tabla ventas")
    
    # Tabla de detalles de ventas existente
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
    
    # Nueva tabla de usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    nombre_completo TEXT NOT NULL,
                    activo INTEGER DEFAULT 1,
                    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Nueva tabla de log de acciones
    c.execute('''CREATE TABLE IF NOT EXISTS log_acciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    accion TEXT NOT NULL,
                    detalles TEXT,
                    fecha TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )''')
    
    # Crear usuarios por defecto si no existen
    c.execute("SELECT COUNT(*) FROM usuarios")
    count = c.fetchone()[0]
    if count == 0:
        # Usuario administrador por defecto
        admin_hash = generate_password_hash('admin123')
        c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                     VALUES (?, ?, ?, ?)''', 
                 ('admin', admin_hash, 'administrador', 'Administrador del Sistema'))
        
        # Usuario cajero por defecto
        cajero_hash = generate_password_hash('cajero123')
        c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                     VALUES (?, ?, ?, ?)''', 
                 ('cajero', cajero_hash, 'cajero', 'Cajero Principal'))
    
    conn.commit()
    conn.close()

# Decoradores de autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Verificar si la sesión es anterior al inicio del servidor actual
        if 'session_start' in session:
            session_start = datetime.fromisoformat(session['session_start'])
            if session_start < SERVER_START_TIME:
                session.clear()
                flash('La sesión ha expirado debido al reinicio del servidor. Inicia sesión nuevamente.', 'info')
                return redirect(url_for('login'))
        else:
            # Si no tiene marca de tiempo de sesión, es una sesión antigua
            session.clear()
            flash('Sesión inválida. Inicia sesión nuevamente.', 'info')
            return redirect(url_for('login'))
        
        # Verificar timeout de sesión (8 horas)
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(hours=8):
                session.clear()
                flash('Sesión expirada por inactividad. Inicia sesión nuevamente.', 'info')
                return redirect(url_for('login'))
        
        # Actualizar última actividad
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('rol') != 'administrador':
            flash('Acceso denegado. Solo administradores pueden realizar esta acción.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def log_action(user_id, action, details=None):
    """Registra una acción en el log"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO log_acciones (usuario_id, accion, detalles, fecha) VALUES (?, ?, ?, ?)",
              (user_id, action, details, fecha))
    conn.commit()
    conn.close()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, password_hash, rol, nombre_completo FROM usuarios WHERE usuario = ? AND activo = 1", (usuario,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[1], password):
            # Limpiar cualquier sesión anterior
            session.clear()
            
            # Configurar nueva sesión como temporal (se borra al cerrar navegador)
            session.permanent = False
            session['user_id'] = user_data[0]
            session['usuario'] = usuario
            session['rol'] = user_data[2]
            session['nombre_completo'] = user_data[3]
            session['last_activity'] = datetime.now().isoformat()
            session['session_start'] = datetime.now().isoformat()  # Marca temporal de la sesión
            
            log_action(user_data[0], f"Inicio de sesión - {user_data[2]}")
            flash(f'Bienvenido, {user_data[3]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    if 'user_id' in session:
        log_action(session['user_id'], "Cierre de sesión")
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

@app.route("/verificar_admin", methods=['POST'])
@login_required
def verificar_admin():
    """Verifica la contraseña del admin para acciones críticas"""
    data = request.get_json()
    password = data.get('password')
    
    if session.get('rol') != 'administrador':
        return jsonify({'success': False, 'message': 'Solo administradores pueden realizar esta acción'})
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM usuarios WHERE id = ?", (session['user_id'],))
    password_hash = c.fetchone()[0]
    conn.close()
    
    if check_password_hash(password_hash, password):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Contraseña incorrecta'})

@app.route("/gestionar_usuarios")
@admin_required
def gestionar_usuarios():
    """Vista para gestionar usuarios del sistema"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, usuario, rol, nombre_completo, activo, fecha_creacion FROM usuarios ORDER BY fecha_creacion DESC")
    usuarios = c.fetchall()
    conn.close()
    return render_template('gestionar_usuarios.html', usuarios=usuarios)

@app.route("/crear_usuario", methods=['POST'])
@admin_required
def crear_usuario():
    """Crear nuevo usuario"""
    usuario = request.form['usuario']
    password = request.form['password']
    rol = request.form['rol']
    nombre_completo = request.form['nombre_completo']
    
    if not all([usuario, password, rol, nombre_completo]):
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('gestionar_usuarios'))
    
    password_hash = generate_password_hash(password)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO usuarios (usuario, password_hash, rol, nombre_completo) 
                     VALUES (?, ?, ?, ?)''', 
                 (usuario, password_hash, rol, nombre_completo))
        conn.commit()
        conn.close()
        
        log_action(session['user_id'], f"Usuario creado: {usuario} ({rol})")
        flash(f'Usuario "{nombre_completo}" creado exitosamente', 'success')
    except sqlite3.IntegrityError:
        flash('El nombre de usuario ya existe', 'error')
    
    return redirect(url_for('gestionar_usuarios'))

@app.route("/cambiar_estado_usuario/<int:user_id>")
@admin_required
def cambiar_estado_usuario(user_id):
    """Activar/desactivar usuario"""
    if user_id == session['user_id']:
        flash('No puedes desactivar tu propia cuenta', 'error')
        return redirect(url_for('gestionar_usuarios'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT usuario, activo FROM usuarios WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    
    if user_data:
        nuevo_estado = 0 if user_data[1] else 1
        c.execute("UPDATE usuarios SET activo = ? WHERE id = ?", (nuevo_estado, user_id))
        conn.commit()
        
        estado_texto = "activado" if nuevo_estado else "desactivado"
        log_action(session['user_id'], f"Usuario {estado_texto}: {user_data[0]}")
        flash(f'Usuario {user_data[0]} {estado_texto}', 'success')
    
    conn.close()
    return redirect(url_for('gestionar_usuarios'))

@app.route("/log_acciones")
@admin_required
def log_acciones():
    """Ver log de acciones del sistema"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Obtener filtros de la URL
    usuario_filtro = request.args.get('usuario', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    
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
    
    # Obtener lista de usuarios para el filtro
    c.execute("SELECT id, usuario, rol FROM usuarios ORDER BY usuario")
    usuarios_list = c.fetchall()
    
    # Estadísticas
    c.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
    usuarios_activos = c.fetchone()[0]
    
    hoy = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
    ventas_hoy = c.fetchone()[0]
    
    conn.close()
    
    return render_template('log_acciones.html', 
                         logs=logs, 
                         usuarios_list=usuarios_list,
                         usuarios_activos=usuarios_activos,
                         ventas_hoy=ventas_hoy)

@app.route("/")
@login_required
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    productos = c.fetchall()
    conn.close()
    return render_template("index.html", productos=productos)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    # Registrar el cierre del servidor si hay un usuario logueado
    if 'user_id' in session:
        log_action(session['user_id'], "Cierre del servidor/tienda")
    
    def shutdown_server():
        time.sleep(1)
        os._exit(0)  # termina el proceso inmediatamente

    threading.Thread(target=shutdown_server).start()
    
    # Limpiar la sesión y redirigir al login
    session.clear()
    return jsonify({
        'status': 'success', 
        'message': 'Servidor apagado - redirigiendo al login',
        'redirect': url_for('login')
    })

def abrir_navegador_con_retraso():
    time.sleep(1)  # Espera 1 segundo para que el servidor esté listo
    abrir_navegador()

def abrir_navegador():
    """Abre el navegador web con la URL correcta del servidor"""
    ip_local = obtener_ip_local()
    port = int(os.environ.get('PORT', 5000))
    url = f"http://{ip_local}:{port}/"
    print(f"Abriendo navegador en: {url}")
    webbrowser.open(url, new=1)  # new=1 para usar pestaña existente si hay una

@app.route('/qr_code')
def qr_code():
    """Genera un código QR para acceder al sistema POS"""
    # Usar el host de la aplicación en producción o IP local en desarrollo
    if 'herokuapp.com' in request.host or 'pages.dev' in request.host:
        url = f"https://{request.host}"
    else:
        ip_local = obtener_ip_local()
        port = int(os.environ.get('PORT', 5000))
        url = f"http://{ip_local}:{port}"

    # Crear QR
    qr = qrcode.make(url)
    buffer = io.BytesIO()
    qr.save(buffer, "PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

@app.route('/agregar_producto', methods=['GET', 'POST'])
@admin_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        file = request.files.get('fileInput')

        if file and file.filename:
            # Aseguramos nombre único y seguro
            filename_original = secure_filename(file.filename)
            extension = os.path.splitext(filename_original)[1]
            filename = f"prod_{uuid.uuid4().hex}{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            filename = 'default.png'
        # Guardar producto en la base de datos con filename como imagen
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO productos (nombre, precio, imagen) VALUES (?, ?, ?)",
                  (nombre, precio, filename))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

@app.route("/editar_producto", methods=["GET", "POST"])
@admin_required
def editar_producto():
    producto_id = request.values.get("producto_id")
    print("ID recibido:", producto_id)

    if not producto_id:
        flash("No se especificó el producto a editar.")
        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        file = request.files.get("fileInput")

        cursor.execute("SELECT imagen FROM productos WHERE id = ?", (producto_id,))
        row = cursor.fetchone()
        imagen_url = row[0] if row else "default.png"

        if file and file.filename:
            filename_original = file.filename
            filename_original = secure_filename(filename_original)
            extension = os.path.splitext(filename_original)[1]
            filename = f"prod_{producto_id}_{uuid.uuid4().hex}{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            imagen_url = filename


        cursor.execute("""
            UPDATE productos
            SET nombre = ?, precio = ?, imagen = ?
            WHERE id = ?
        """, (nombre, precio, imagen_url, producto_id))
        conn.commit()
        conn.close()
        flash("Producto actualizado con éxito.")
        return redirect(url_for("index"))

    else:
        cursor.execute("SELECT id, nombre, precio, imagen FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        conn.close()

        if producto:
            producto_dict = {
                "id": producto[0],
                "nombre": producto[1],
                "precio": producto[2],
                "imagen_url": producto[3]
            }
            return render_template("edit.html", producto=producto_dict)
        else:
            flash("Producto no encontrado.")
            return redirect(url_for("index"))

@app.route("/editar_lista")
def editar_lista():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio, imagen FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template("editar_producto.html", productos=productos)

@app.route("/eliminar_producto", methods=["GET", "POST"])
@admin_required
def eliminar_producto():
    if request.method == "POST":
        producto_id = request.form["producto_id"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("eliminar_producto"))  # o index si prefieres

    # GET: mostrar productos
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    productos = c.fetchall()
    conn.close()
    return render_template("eliminar_producto.html", productos=productos)

@app.route("/historial")
@login_required
def historial():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Obtener ventas con información del usuario
    c.execute('''SELECT v.id, v.fecha, v.total, v.usuario_id, u.usuario, u.nombre_completo, u.rol
                 FROM ventas v 
                 LEFT JOIN usuarios u ON v.usuario_id = u.id 
                 ORDER BY v.fecha DESC''')
    ventas = c.fetchall()

    # Traer los detalles de cada venta
    ventas_con_detalle = []
    for venta in ventas:
        c.execute("SELECT nombre, cantidad, precio_unitario, subtotal FROM ventas_detalle WHERE venta_id = ?", (venta[0],))
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
    return render_template("historial.html", ventas=ventas_con_detalle)

@app.route("/finalizar_venta", methods=["POST"])
@login_required
def finalizar_venta():
    data = request.get_json()
    carrito = data.get("carrito", [])
    total = data.get("total", 0)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario_id = session['user_id']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO ventas (fecha, total, usuario_id) VALUES (?, ?, ?)", (fecha, total, usuario_id))
    venta_id = c.lastrowid

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
    
    # Log de la venta
    log_action(usuario_id, f"Venta realizada - ID: {venta_id}", f"Total: ${total:.2f}, Items: {len(carrito)}")
    
    return jsonify({"status": "ok"})

def obtener_ip_local():
    """Obtiene la IP local del sistema de forma automática"""
    try:
        # Crear un socket temporal para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        # Fallback a localhost si no se puede obtener la IP
        return "127.0.0.1"

if __name__ == "__main__":
    init_db()
    # Variable para controlar si ya se abrió el navegador
    navegador_abierto = False
    
    # Obtener IP local automáticamente
    host_ip = obtener_ip_local()
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Iniciando servidor POS en http://{host_ip}:{port}")
    
    # Solo abrir navegador en desarrollo local y una sola vez
    if os.environ.get('FLASK_ENV') != 'production' and not navegador_abierto:
        navegador_abierto = True
        thread = threading.Thread(target=abrir_navegador_con_retraso)
        thread.daemon = True  # Thread se cierra cuando el programa principal termine
        thread.start()
    
    # Usar 0.0.0.0 para que sea accesible desde cualquier interfaz de red
    app.run(debug=False, host="0.0.0.0", port=port, use_reloader=False)

