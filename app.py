from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import socket
import io
import webbrowser
import time
import threading
import qrcode

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '14/Oct/14')
DB_NAME = 'database.db'
UPLOAD_FOLDER = 'static/img'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    imagen TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    total REAL NOT NULL
                )''')
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
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM productos")
    productos = c.fetchall()
    conn.close()
    return render_template("index.html", productos=productos)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    def shutdown_server():
        time.sleep(1)
        os._exit(0)  # termina el proceso inmediatamente

    threading.Thread(target=shutdown_server).start()
    return 'Servidor apagado'

def abrir_navegador_con_retraso():
    time.sleep(1)  # Espera 1 segundo para que el servidor esté listo
    abrir_navegador()

def abrir_navegador():
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    port = 5000
    webbrowser.open(f"http://{ip_local}:{port}/", new=1)  # new=1 para usar pestaña existente si hay una

@app.route('/qr_code')
def qr_code():
    # Usar el host de la aplicación en producción o IP local en desarrollo
    if 'herokuapp.com' in request.host or 'pages.dev' in request.host:
        url = f"https://{request.host}"
    else:
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        port = 5000
        url = f"http://{ip_local}:{port}"

    # Crear QR
    qr = qrcode.make(url)
    buffer = io.BytesIO()
    qr.save(buffer, "PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

@app.route('/agregar_producto', methods=['GET', 'POST'])
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
def historial():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM ventas ORDER BY fecha DESC")
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
            "detalles": detalles
        })
    conn.close()
    return render_template("historial.html", ventas=ventas_con_detalle)

@app.route("/finalizar_venta", methods=["POST"])
def finalizar_venta():
    data = request.get_json()
    carrito = data.get("carrito", [])
    total = data.get("total", 0)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))
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
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    init_db()
    # Variable para controlar si ya se abrió el navegador
    navegador_abierto = False
    
    # Solo abrir navegador en desarrollo local y una sola vez
    if os.environ.get('FLASK_ENV') != 'production' and not navegador_abierto:
        navegador_abierto = True
        thread = threading.Thread(target=abrir_navegador_con_retraso)
        thread.daemon = True  # Thread se cierra cuando el programa principal termine
        thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host="192.168.1.105", port=port, use_reloader=False)

