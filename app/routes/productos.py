#!/usr/bin/env python3
"""
Rutas para gestión de productos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.database import Producto, LogAccion
from app.utils.auth import admin_required, get_current_user
from app.utils.helpers import save_uploaded_file, allowed_file
import os

# Crear blueprint para productos
productos_bp = Blueprint('productos', __name__)

def init_productos_routes(app, db_manager):
    """Inicializa las rutas de productos"""
    
    # Modelos
    producto_model = Producto(db_manager)
    log_model = LogAccion(db_manager)
    
    @productos_bp.route('/agregar_producto', methods=['GET', 'POST'])
    @admin_required
    def agregar_producto():
        """Agregar nuevo producto"""
        if request.method == 'POST':
            nombre = request.form['nombre']
            precio_compra = float(request.form.get('precio_compra', 0))
            precio_venta = float(request.form['precio_venta'])
            categoria = request.form.get('categoria', 'Platillos de cocina')
            stock = request.form.get('stock', '0')
            
            # Validar que el precio de venta sea mayor al precio de compra
            if precio_venta <= precio_compra:
                flash('El precio de venta debe ser mayor al precio de compra', 'error')
                return render_template('agregar_producto.html')
            
            # Convertir stock a entero
            try:
                stock = int(stock)
            except ValueError:
                stock = 10 if categoria == 'Pescadería' else 999
            
            file = request.files.get('fileInput')

            # Manejar imagen
            if file and file.filename and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                filename = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            else:
                filename = 'default.png'
            
            # Crear producto con precios separados
            producto_id = producto_model.create(nombre, precio_venta, filename, categoria, stock, precio_compra)
            
            # Calcular margen de ganancia
            margen = ((precio_venta - precio_compra) / precio_compra) * 100
            
            # Log de la acción
            current_user = get_current_user()
            log_model.registrar(current_user['id'], f"Producto agregado: {nombre}", 
                              f"ID: {producto_id}, Precio compra: ${precio_compra:.2f}, Precio venta: ${precio_venta:.2f}, Margen: {margen:.1f}%, Stock inicial: {stock}")
            
            flash(f'Producto "{nombre}" agregado exitosamente. Margen de ganancia: {margen:.1f}%', 'success')
            return redirect(url_for('main.index'))
            
        return render_template('agregar_producto.html')

    @productos_bp.route("/editar_producto", methods=["GET", "POST"])
    @admin_required
    def editar_producto():
        """Editar producto existente"""
        producto_id = request.values.get("producto_id")
        
        if not producto_id:
            flash("No se especificó el producto a editar.", 'error')
            return redirect(url_for("main.index"))

        if request.method == "POST":
            nombre = request.form.get("nombre")
            precio_compra = float(request.form.get("precio_compra", 0))
            precio_venta = float(request.form.get("precio_venta"))
            categoria = request.form.get("categoria", "Platillos de cocina")
            stock = request.form.get("stock", "0")
            
            # Validar que el precio de venta sea mayor al precio de compra
            if precio_venta <= precio_compra:
                flash('El precio de venta debe ser mayor al precio de compra', 'error')
                producto = producto_model.get_by_id(producto_id)
                if producto:
                    producto_dict = {
                        "id": producto[0],
                        "nombre": producto[1],
                        "precio_compra": producto[2] if len(producto) > 2 else 0,
                        "precio_venta": producto[3] if len(producto) > 3 else producto[2],  # Compatibilidad
                        "imagen_url": producto[4] if len(producto) > 4 else producto[3],
                        "categoria": producto[5] if len(producto) > 5 else "Platillos de cocina",
                        "stock": producto[8] if len(producto) > 8 else 0
                    }
                    return render_template("edit.html", producto=producto_dict)
            
            # Convertir stock a entero
            try:
                stock = int(stock)
            except ValueError:
                stock = 0
            
            file = request.files.get("fileInput")

            # Obtener imagen actual
            producto_actual = producto_model.get_by_id(producto_id)
            imagen_url = producto_actual[4] if len(producto_actual) > 4 else "default.png"

            # Manejar nueva imagen si se subió
            if file and file.filename and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                imagen_url = save_uploaded_file(file, app.config['UPLOAD_FOLDER'], producto_id)

            # Actualizar producto con precios separados
            producto_model.update(producto_id, nombre, precio_venta, imagen_url, categoria, stock, precio_compra)
            
            # Calcular margen de ganancia
            margen = ((precio_venta - precio_compra) / precio_compra) * 100 if precio_compra > 0 else 0
            
            # Log de la acción
            current_user = get_current_user()
            log_model.registrar(current_user['id'], f"Producto editado: {nombre}", 
                              f"ID: {producto_id}, Precio compra: ${precio_compra:.2f}, Precio venta: ${precio_venta:.2f}, Margen: {margen:.1f}%, Stock: {stock}")
            
            flash(f"Producto actualizado con éxito. Margen de ganancia: {margen:.1f}%", 'success')
            return redirect(url_for("main.index"))

        else:
            producto = producto_model.get_by_id(producto_id)
            
            if producto:
                producto_dict = {
                    "id": producto[0],
                    "nombre": producto[1],
                    "precio_compra": producto[2] if len(producto) > 2 else 0,
                    "precio_venta": producto[3] if len(producto) > 3 else producto[2],  # Compatibilidad con estructura antigua
                    "imagen_url": producto[4] if len(producto) > 4 else producto[3],
                    "categoria": producto[5] if len(producto) > 5 else "Platillos de cocina",
                    "stock": producto[8] if len(producto) > 8 else 0
                }
                return render_template("edit.html", producto=producto_dict)
            else:
                flash("Producto no encontrado.", 'error')
                return redirect(url_for("main.index"))

    @productos_bp.route("/editar_lista")
    @admin_required
    def editar_lista():
        """Lista de productos para editar"""
        productos = producto_model.get_all()
        return render_template("editar_producto.html", productos=productos)

    @productos_bp.route("/eliminar_producto", methods=["GET", "POST"])
    @admin_required
    def eliminar_producto():
        """Eliminar producto"""
        if request.method == "POST":
            producto_id = request.form["producto_id"]
            
            # Obtener info del producto antes de eliminarlo
            producto = producto_model.get_by_id(producto_id)
            
            if producto:
                producto_model.delete(producto_id)
                
                # Log de la acción
                current_user = get_current_user()
                log_model.registrar(current_user['id'], f"Producto eliminado: {producto[1]}", f"ID: {producto_id}")
                
                flash(f'Producto "{producto[1]}" eliminado exitosamente', 'success')
            else:
                flash("Producto no encontrado", 'error')
                
            return redirect(url_for("productos.eliminar_producto"))

        # GET: mostrar productos
        productos = producto_model.get_all()
        return render_template("eliminar_producto.html", productos=productos)
    
    # Registrar blueprint
    app.register_blueprint(productos_bp)
    
    return productos_bp
