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
            precio = request.form['precio']
            file = request.files.get('fileInput')

            # Manejar imagen
            if file and file.filename and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                filename = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            else:
                filename = 'default.png'
            
            # Crear producto
            producto_id = producto_model.create(nombre, precio, filename)
            
            # Log de la acción
            current_user = get_current_user()
            log_model.create(current_user['id'], f"Producto agregado: {nombre}", f"ID: {producto_id}")
            
            flash(f'Producto "{nombre}" agregado exitosamente', 'success')
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
            precio = request.form.get("precio")
            file = request.files.get("fileInput")

            # Obtener imagen actual
            producto_actual = producto_model.get_by_id(producto_id)
            imagen_url = producto_actual[3] if producto_actual else "default.png"

            # Manejar nueva imagen si se subió
            if file and file.filename and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                imagen_url = save_uploaded_file(file, app.config['UPLOAD_FOLDER'], producto_id)

            # Actualizar producto
            producto_model.update(producto_id, nombre, precio, imagen_url)
            
            # Log de la acción
            current_user = get_current_user()
            log_model.create(current_user['id'], f"Producto editado: {nombre}", f"ID: {producto_id}")
            
            flash("Producto actualizado con éxito.", 'success')
            return redirect(url_for("main.index"))

        else:
            producto = producto_model.get_by_id(producto_id)
            
            if producto:
                producto_dict = {
                    "id": producto[0],
                    "nombre": producto[1],
                    "precio": producto[2],
                    "imagen_url": producto[3]
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
                log_model.create(current_user['id'], f"Producto eliminado: {producto[1]}", f"ID: {producto_id}")
                
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
