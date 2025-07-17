#!/usr/bin/env python3
"""
Rutas de autenticación para el sistema POS
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.database import Usuario, LogAccion
from app.utils.auth import login_required, admin_required, create_session, clear_session, get_current_user
from datetime import datetime
import sqlite3

# Crear blueprint para autenticación
auth_bp = Blueprint('auth', __name__)

def init_auth_routes(app, db_manager):
    """Inicializa las rutas de autenticación"""
    
    # Modelos
    usuario_model = Usuario(db_manager)
    log_model = LogAccion(db_manager)
    
    @auth_bp.route("/login", methods=['GET', 'POST'])
    def login():
        """Página de login"""
        if request.method == 'POST':
            username = request.form['usuario']
            password = request.form['password']
            
            user_data = usuario_model.get_by_username(username)
            
            if user_data and check_password_hash(user_data[1], password):
                # Crear sesión
                user_info = (user_data[0], username, user_data[2], user_data[3])
                create_session(user_info)
                
                # Log de inicio de sesión
                log_model.create(user_data[0], f"Inicio de sesión - {user_data[2]}")
                flash(f'Bienvenido, {user_data[3]}!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        
        return render_template('login.html')
    
    @auth_bp.route("/logout")
    def logout():
        """Cerrar sesión"""
        current_user = get_current_user()
        if current_user:
            log_model.create(current_user['id'], "Cierre de sesión")
        
        clear_session()
        flash('Sesión cerrada correctamente', 'info')
        return redirect(url_for('auth.login'))
    
    @auth_bp.route("/verificar_admin", methods=['POST'])
    @login_required
    def verificar_admin():
        """Verifica la contraseña del admin para acciones críticas"""
        data = request.get_json()
        password = data.get('password')
        
        current_user = get_current_user()
        if not current_user or current_user['rol'] != 'administrador':
            return jsonify({'success': False, 'message': 'Solo administradores pueden realizar esta acción'})
        
        password_hash = usuario_model.get_password_hash(current_user['id'])
        
        if password_hash and check_password_hash(password_hash, password):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Contraseña incorrecta'})
    
    @auth_bp.route("/gestionar_usuarios")
    @admin_required
    def gestionar_usuarios():
        """Vista para gestionar usuarios del sistema"""
        usuarios = usuario_model.get_all()
        return render_template('gestionar_usuarios.html', usuarios=usuarios)
    
    @auth_bp.route("/crear_usuario", methods=['POST'])
    @admin_required
    def crear_usuario():
        """Crear nuevo usuario"""
        usuario = request.form['usuario']
        password = request.form['password']
        rol = request.form['rol']
        nombre_completo = request.form['nombre_completo']
        
        if not all([usuario, password, rol, nombre_completo]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        password_hash = generate_password_hash(password)
        
        try:
            usuario_model.create(usuario, password_hash, rol, nombre_completo)
            
            current_user = get_current_user()
            log_model.create(current_user['id'], f"Usuario creado: {usuario} ({rol})")
            flash(f'Usuario "{nombre_completo}" creado exitosamente', 'success')
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe', 'error')
        
        return redirect(url_for('auth.gestionar_usuarios'))
    
    @auth_bp.route("/cambiar_estado_usuario/<int:user_id>")
    @admin_required
    def cambiar_estado_usuario(user_id):
        """Activar/desactivar usuario"""
        current_user = get_current_user()
        if user_id == current_user['id']:
            flash('No puedes desactivar tu propia cuenta', 'error')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        user_data = usuario_model.get_by_id(user_id)
        
        if user_data:
            nuevo_estado = 0 if user_data[5] else 1  # user_data[5] es el campo 'activo'
            usuario_model.update_status(user_id, nuevo_estado)
            
            estado_texto = "activado" if nuevo_estado else "desactivado"
            log_model.create(current_user['id'], f"Usuario {estado_texto}: {user_data[1]}")
            flash(f'Usuario {user_data[1]} {estado_texto}', 'success')
        
        return redirect(url_for('auth.gestionar_usuarios'))
    
    @auth_bp.route("/log_acciones")
    @admin_required
    def log_acciones():
        """Ver log de acciones del sistema"""
        # Obtener filtros de la URL
        usuario_filtro = request.args.get('usuario', '')
        fecha_desde = request.args.get('fecha_desde', '')
        fecha_hasta = request.args.get('fecha_hasta', '')
        
        # Obtener logs filtrados
        logs = log_model.get_filtered(usuario_filtro, fecha_desde, fecha_hasta)
        
        # Obtener lista de usuarios para el filtro
        usuarios_list = usuario_model.get_all()
        
        # Obtener estadísticas
        stats = log_model.get_stats()
        
        return render_template('log_acciones.html', 
                             logs=logs, 
                             usuarios_list=usuarios_list,
                             usuarios_activos=stats['usuarios_activos'],
                             ventas_hoy=stats['ventas_hoy'])
    
    @auth_bp.route("/cambiar_credenciales", methods=['POST'])
    @admin_required
    def cambiar_credenciales():
        """Cambiar credenciales del administrador actual"""
        current_user = get_current_user()
        
        # Verificar que es administrador
        if current_user['rol'] != 'administrador':
            flash('Solo los administradores pueden cambiar sus credenciales', 'error')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        # Obtener datos del formulario
        password_actual = request.form.get('password_actual')
        nuevo_usuario = request.form.get('nuevo_usuario', '').strip()
        nueva_password = request.form.get('nueva_password', '').strip()
        confirmar_password = request.form.get('confirmar_password', '').strip()
        
        # Validaciones básicas
        if not password_actual:
            flash('Debe ingresar su contraseña actual', 'error')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        if not nuevo_usuario and not nueva_password:
            flash('Debe especificar al menos un nuevo usuario o contraseña', 'error')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        # Verificar contraseña actual
        password_hash = usuario_model.get_password_hash(current_user['id'])
        if not password_hash or not check_password_hash(password_hash, password_actual):
            flash('La contraseña actual es incorrecta', 'error')
            return redirect(url_for('auth.gestionar_usuarios'))
        
        # Validar nueva contraseña si se proporciona
        if nueva_password:
            if len(nueva_password) < 4:
                flash('La nueva contraseña debe tener al menos 4 caracteres', 'error')
                return redirect(url_for('auth.gestionar_usuarios'))
            
            if nueva_password != confirmar_password:
                flash('Las contraseñas no coinciden', 'error')
                return redirect(url_for('auth.gestionar_usuarios'))
        
        # Validar nuevo usuario si se proporciona
        if nuevo_usuario:
            if len(nuevo_usuario) < 3:
                flash('El nuevo nombre de usuario debe tener al menos 3 caracteres', 'error')
                return redirect(url_for('auth.gestionar_usuarios'))
            
            if usuario_model.username_exists(nuevo_usuario, current_user['id']):
                flash('El nombre de usuario ya existe', 'error')
                return redirect(url_for('auth.gestionar_usuarios'))
        
        # Preparar datos para actualizar
        new_username = nuevo_usuario if nuevo_usuario else None
        new_password_hash = generate_password_hash(nueva_password) if nueva_password else None
        
        try:
            # Actualizar credenciales
            usuario_model.update_credentials(current_user['id'], new_username, new_password_hash)
            
            # Registrar en log
            cambios = []
            if new_username:
                cambios.append(f"usuario: {current_user['usuario']} → {new_username}")
            if new_password_hash:
                cambios.append("contraseña actualizada")
            
            log_model.create(current_user['id'], f"Credenciales actualizadas: {', '.join(cambios)}")
            
            flash('Credenciales actualizadas exitosamente', 'success')
            
            # Si cambió el nombre de usuario, cerrar sesión para que vuelva a autenticarse
            if new_username:
                flash('Su nombre de usuario ha cambiado. Por favor, inicie sesión nuevamente.', 'info')
                clear_session()
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            flash(f'Error al actualizar credenciales: {str(e)}', 'error')
        
        return redirect(url_for('auth.gestionar_usuarios'))
    
    # Registrar blueprint
    app.register_blueprint(auth_bp)
    
    return auth_bp
