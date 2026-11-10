#!/usr/bin/env python3
"""
Utilidades de autenticación y autorización para el sistema POS
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from datetime import datetime, timedelta

# Marca temporal de inicio del servidor (para invalidar sesiones anteriores)
SERVER_START_TIME = datetime.now()

def login_required(f):
    """Decorador que requiere autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar múltiples condiciones de sesión válida
        if ('user_id' not in session or 
            'authenticated' not in session or 
            not session.get('authenticated')):
            flash('Por favor, inicia sesión para continuar.', 'info')
            return redirect(url_for('auth.login'))
        
        # Verificar timeout de sesión (8 horas)
        if 'last_activity' in session:
            try:
                last_activity = datetime.fromisoformat(session['last_activity'])
                if datetime.now() - last_activity > timedelta(hours=8):
                    session.clear()
                    flash('Sesión expirada por inactividad. Inicia sesión nuevamente.', 'info')
                    return redirect(url_for('auth.login'))
            except ValueError:
                # Si hay error en el formato de fecha, limpiar sesión
                session.clear()
                flash('Sesión inválida. Inicia sesión nuevamente.', 'info')
                return redirect(url_for('auth.login'))
        
        # Actualizar última actividad
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador que requiere permisos de administrador"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('rol') != 'administrador':
            flash('Acceso denegado. Solo administradores pueden realizar esta acción.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Obtiene información del usuario actual de la sesión"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'usuario': session.get('usuario'),
            'rol': session.get('rol'),
            'nombre_completo': session.get('nombre_completo')
        }
    return None

def is_admin():
    """Verifica si el usuario actual es administrador"""
    return session.get('rol') == 'administrador'

def create_session(user_data):
    """Crea una nueva sesión de usuario"""
    # Limpiar cualquier sesión anterior
    session.clear()
    
    # Configurar nueva sesión como permanente para mejor compatibilidad
    session.permanent = True
    
    # Datos básicos del usuario
    session['user_id'] = user_data[0]
    session['usuario'] = user_data[1] if len(user_data) > 1 else ''
    session['rol'] = user_data[2] if len(user_data) > 2 else ''
    session['nombre_completo'] = user_data[3] if len(user_data) > 3 else ''
    
    # Timestamps para control de sesión
    now = datetime.now().isoformat()
    session['last_activity'] = now
    session['session_start'] = now
    
    # Flag de sesión válida para verificaciones adicionales
    session['authenticated'] = True
    session['session_id'] = f"{user_data[0]}_{datetime.now().timestamp()}"

def clear_session():
    """Limpia la sesión actual"""
    session.clear()
