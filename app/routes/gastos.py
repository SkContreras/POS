"""
Rutas para el manejo de gastos operativos
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from datetime import datetime, timedelta
import json

# Crear el blueprint
gastos_bp = Blueprint('gastos', __name__)

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') != 'administrador':
            flash('Acceso denegado. Solo administradores pueden acceder a esta función.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def init_gastos_routes(app, db_manager):
    """Inicializa las rutas de gastos"""
    from ..models.database import Gasto, LogAccion
    
    gasto_model = Gasto(db_manager)
    log_model = LogAccion(db_manager)
    
    @gastos_bp.route("/gastos")
    @login_required
    @admin_required
    def lista_gastos():
        """Página principal de gestión de gastos"""
        # Obtener filtros de la URL
        categoria = request.args.get('categoria', '')
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        
        # Si no hay fechas, usar el mes actual
        if not fecha_inicio or not fecha_fin:
            hoy = datetime.now()
            fecha_inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
            # Último día del mes
            if hoy.month == 12:
                siguiente_mes = hoy.replace(year=hoy.year + 1, month=1, day=1)
            else:
                siguiente_mes = hoy.replace(month=hoy.month + 1, day=1)
            fecha_fin = (siguiente_mes - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Obtener gastos con filtros
        try:
            gastos = gasto_model.get_all(fecha_inicio, fecha_fin, categoria if categoria else None)
            
            # Obtener estadísticas
            estadisticas = gasto_model.get_estadisticas_gastos(fecha_inicio, fecha_fin)
            gastos_por_categoria = gasto_model.get_gastos_por_categoria(fecha_inicio, fecha_fin)
            
            # Obtener categorías predefinidas
            categorias = gasto_model.get_categorias_predefinidas()
        except Exception as e:
            print(f"Error al obtener datos de gastos: {e}")
            gastos = []
            estadisticas = {'gastos_totales': 0, 'total_gastos': 0, 'gasto_promedio': 0, 'gasto_maximo': 0, 'gasto_minimo': 0}
            gastos_por_categoria = []
            categorias = {}
        
        return render_template('gastos/lista.html',
                             gastos=gastos,
                             estadisticas=estadisticas,
                             gastos_por_categoria=gastos_por_categoria,
                             categorias=categorias,
                             fecha_inicio=fecha_inicio,
                             fecha_fin=fecha_fin,
                             categoria_filtro=categoria)
    
    @gastos_bp.route("/gastos/agregar")
    @login_required
    @admin_required
    def agregar_gasto():
        """Formulario para agregar nuevo gasto"""
        categorias = gasto_model.get_categorias_predefinidas()
        return render_template('gastos/agregar.html', categorias=categorias)
    
    @gastos_bp.route("/gastos/crear", methods=["POST"])
    @login_required
    @admin_required
    def crear_gasto():
        """Crear un nuevo gasto"""
        try:
            categoria = request.form.get('categoria')
            subcategoria = request.form.get('subcategoria')
            descripcion = request.form.get('descripcion')
            monto = float(request.form.get('monto'))
            fecha = request.form.get('fecha')
            comprobante = request.form.get('comprobante', '')
            recurrente = request.form.get('recurrente') == 'on'
            frecuencia_dias = int(request.form.get('frecuencia_dias', 0)) if recurrente else 0
            
            # Validaciones
            if not all([categoria, descripcion, monto, fecha]):
                flash('Todos los campos obligatorios deben ser completados.', 'error')
                return redirect(url_for('gastos.agregar_gasto'))
            
            if monto <= 0:
                flash('El monto debe ser mayor a cero.', 'error')
                return redirect(url_for('gastos.agregar_gasto'))
            
            # Crear el gasto
            gasto_id = gasto_model.create(
                categoria=categoria,
                subcategoria=subcategoria,
                descripcion=descripcion,
                monto=monto,
                fecha=fecha,
                usuario_id=session['user_id'],
                comprobante=comprobante,
                recurrente=recurrente,
                frecuencia_dias=frecuencia_dias
            )
            
            # Log de la acción
            log_model.registrar_accion(
                usuario_id=session['user_id'],
                accion='crear_gasto',
                detalles=f'Gasto creado: {descripcion} - ${monto:.2f} ({categoria})'
            )
            
            flash(f'Gasto registrado exitosamente: {descripcion} - ${monto:.2f}', 'success')
            return redirect(url_for('gastos.lista_gastos'))
            
        except ValueError as e:
            flash('Error en los datos ingresados. Verifique el monto.', 'error')
            return redirect(url_for('gastos.agregar_gasto'))
        except Exception as e:
            flash(f'Error al crear el gasto: {str(e)}', 'error')
            return redirect(url_for('gastos.agregar_gasto'))
    
    @gastos_bp.route("/gastos/editar/<int:gasto_id>")
    @login_required
    @admin_required
    def editar_gasto(gasto_id):
        """Formulario para editar gasto"""
        gasto = gasto_model.get_by_id(gasto_id)
        if not gasto:
            flash('Gasto no encontrado.', 'error')
            return redirect(url_for('gastos.lista_gastos'))
        
        categorias = gasto_model.get_categorias_predefinidas()
        return render_template('gastos/editar.html', gasto=gasto, categorias=categorias)
    
    @gastos_bp.route("/gastos/actualizar/<int:gasto_id>", methods=["POST"])
    @login_required
    @admin_required
    def actualizar_gasto(gasto_id):
        """Actualizar un gasto existente"""
        try:
            gasto = gasto_model.get_by_id(gasto_id)
            if not gasto:
                flash('Gasto no encontrado.', 'error')
                return redirect(url_for('gastos.lista_gastos'))
            
            categoria = request.form.get('categoria')
            subcategoria = request.form.get('subcategoria')
            descripcion = request.form.get('descripcion')
            monto = float(request.form.get('monto'))
            fecha = request.form.get('fecha')
            comprobante = request.form.get('comprobante', '')
            recurrente = request.form.get('recurrente') == 'on'
            frecuencia_dias = int(request.form.get('frecuencia_dias', 0)) if recurrente else 0
            
            # Validaciones
            if not all([categoria, descripcion, monto, fecha]):
                flash('Todos los campos obligatorios deben ser completados.', 'error')
                return redirect(url_for('gastos.editar_gasto', gasto_id=gasto_id))
            
            if monto <= 0:
                flash('El monto debe ser mayor a cero.', 'error')
                return redirect(url_for('gastos.editar_gasto', gasto_id=gasto_id))
            
            # Actualizar el gasto
            gasto_model.update(
                gasto_id=gasto_id,
                categoria=categoria,
                subcategoria=subcategoria,
                descripcion=descripcion,
                monto=monto,
                fecha=fecha,
                comprobante=comprobante,
                recurrente=recurrente,
                frecuencia_dias=frecuencia_dias
            )
            
            # Log de la acción
            log_model.registrar_accion(
                usuario_id=session['user_id'],
                accion='actualizar_gasto',
                detalles=f'Gasto actualizado: {descripcion} - ${monto:.2f} ({categoria})'
            )
            
            flash(f'Gasto actualizado exitosamente: {descripcion} - ${monto:.2f}', 'success')
            return redirect(url_for('gastos.lista_gastos'))
            
        except ValueError as e:
            flash('Error en los datos ingresados. Verifique el monto.', 'error')
            return redirect(url_for('gastos.editar_gasto', gasto_id=gasto_id))
        except Exception as e:
            flash(f'Error al actualizar el gasto: {str(e)}', 'error')
            return redirect(url_for('gastos.editar_gasto', gasto_id=gasto_id))
    
    @gastos_bp.route("/gastos/eliminar/<int:gasto_id>", methods=["POST"])
    @login_required
    @admin_required
    def eliminar_gasto(gasto_id):
        """Eliminar un gasto"""
        try:
            gasto = gasto_model.get_by_id(gasto_id)
            if not gasto:
                return jsonify({'success': False, 'message': 'Gasto no encontrado'})
            
            # Eliminar (desactivar) el gasto
            gasto_model.delete(gasto_id)
            
            # Log de la acción
            log_model.registrar_accion(
                usuario_id=session['user_id'],
                accion='eliminar_gasto',
                detalles=f'Gasto eliminado: {gasto[3]} - ${gasto[4]:.2f} ({gasto[1]})'
            )
            
            return jsonify({'success': True, 'message': 'Gasto eliminado exitosamente'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al eliminar gasto: {str(e)}'})
    
    @gastos_bp.route("/gastos/api/subcategorias/<categoria>")
    @login_required
    def get_subcategorias(categoria):
        """API para obtener subcategorías de una categoría"""
        categorias = gasto_model.get_categorias_predefinidas()
        subcategorias = categorias.get(categoria, [])
        return jsonify(subcategorias)
    
    @gastos_bp.route("/gastos/dashboard")
    @login_required
    @admin_required
    def dashboard_gastos():
        """Dashboard de análisis de gastos"""
        # Obtener parámetros de fecha
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        
        # Si no hay fechas, usar el mes actual
        if not fecha_inicio or not fecha_fin:
            hoy = datetime.now()
            fecha_inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
            if hoy.month == 12:
                siguiente_mes = hoy.replace(year=hoy.year + 1, month=1, day=1)
            else:
                siguiente_mes = hoy.replace(month=hoy.month + 1, day=1)
            fecha_fin = (siguiente_mes - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Obtener datos para el dashboard
        try:
            estadisticas = gasto_model.get_estadisticas_gastos(fecha_inicio, fecha_fin)
            gastos_por_categoria = gasto_model.get_gastos_por_categoria(fecha_inicio, fecha_fin)
            gastos_por_dia = gasto_model.get_gastos_por_dia(fecha_inicio, fecha_fin)
            gastos_recurrentes = gasto_model.get_gastos_recurrentes()
        except Exception as e:
            print(f"Error al obtener datos para dashboard: {e}")
            estadisticas = {'gastos_totales': 0, 'total_gastos': 0, 'gasto_promedio': 0, 'gasto_maximo': 0, 'gasto_minimo': 0}
            gastos_por_categoria = []
            gastos_por_dia = []
            gastos_recurrentes = []
        
        return render_template('gastos/dashboard.html',
                             estadisticas=estadisticas,
                             gastos_por_categoria=gastos_por_categoria,
                             gastos_por_dia=gastos_por_dia,
                             gastos_recurrentes=gastos_recurrentes,
                             fecha_inicio=fecha_inicio,
                             fecha_fin=fecha_fin)
    
    # Registrar el blueprint
    app.register_blueprint(gastos_bp)
