#!/usr/bin/env python3
"""
Rutas principales para el sistema POS
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, send_file
from app.models.database import Producto, Venta, LogAccion
from app.utils.auth import login_required, admin_required, get_current_user
from app.utils.helpers import obtener_ip_local, generar_qr_code, save_uploaded_file, allowed_file
import os
import time
import threading
from datetime import datetime

# Crear blueprint para rutas principales
main_bp = Blueprint('main', __name__)

def init_main_routes(app, db_manager):
    """Inicializa las rutas principales"""
    
    # Modelos
    producto_model = Producto(db_manager)
    venta_model = Venta(db_manager)
    log_model = LogAccion(db_manager)
    
    @main_bp.route("/")
    @login_required
    def index():
        """Página principal del POS"""
        productos = producto_model.get_all()
        return render_template("index.html", productos=productos)
    
    @main_bp.route('/shutdown', methods=['POST'])
    @admin_required
    def shutdown():
        """Cierra el servidor y la sesión"""
        from flask import session
        from app.utils.auth import clear_session
        
        current_user = get_current_user()
        if current_user:
            log_model.create(current_user['id'], "Cierre del servidor/tienda y sesión")
        
        # Limpiar la sesión antes de cerrar el servidor
        clear_session()
        
        def shutdown_server():
            time.sleep(1)
            os._exit(0)  # termina el proceso inmediatamente

        threading.Thread(target=shutdown_server).start()
        
        return jsonify({
            'status': 'success', 
            'message': 'Servidor y sesión cerrados - cerrando pestaña',
            'redirect': url_for('auth.login')
        })
    
    @main_bp.route('/qr_code')
    def qr_code():
        """Genera un código QR para acceder al sistema POS"""
        from flask import current_app
        
        # Usar el host de la aplicación en producción o configuración real del servidor
        if 'herokuapp.com' in request.host or 'pages.dev' in request.host:
            url = f"https://{request.host}"
        else:
            # Usar la información real del servidor configurada en app_modular.py
            server_info = current_app.config.get('SERVER_INFO', {})
            host = server_info.get('host', obtener_ip_local())
            port = server_info.get('port', 5000)
            protocol = server_info.get('protocol', 'http')
            
            # Construir URL con la configuración real
            if (protocol == 'http' and port == 80) or (protocol == 'https' and port == 443):
                # Puertos estándar no necesitan ser especificados
                url = f"{protocol}://{host}"
            else:
                # Incluir puerto no estándar
                url = f"{protocol}://{host}:{port}"

        # Generar QR
        buffer = generar_qr_code(url)
        
        # Debug: mostrar qué URL se está usando para el QR
        print(f"🔗 QR generado para URL: {url}")
        
        return send_file(buffer, mimetype='image/png')
    
    @main_bp.route('/qr_debug')
    def qr_debug():
        """Debug: Mostrar información del QR"""
        from flask import current_app
        import socket
        
        # Obtener la misma información que usa el QR
        if 'herokuapp.com' in request.host or 'pages.dev' in request.host:
            url = f"https://{request.host}"
            source = "Producción (host externo)"
        else:
            server_info = current_app.config.get('SERVER_INFO', {})
            host = server_info.get('host', obtener_ip_local())
            port = server_info.get('port', 5000)
            protocol = server_info.get('protocol', 'http')
            
            if (protocol == 'http' and port == 80) or (protocol == 'https' and port == 443):
                url = f"{protocol}://{host}"
            else:
                url = f"{protocol}://{host}:{port}"
            source = "Configuración del servidor"
        
        # Obtener información adicional de red
        try:
            hostname = socket.gethostname()
            all_ips = socket.gethostbyname_ex(hostname)[2]
            local_ips = [ip for ip in all_ips if not ip.startswith("127.")]
        except:
            hostname = "No disponible"
            local_ips = ["Error al obtener IPs"]
        
        return {
            'qr_url': url,
            'source': source,
            'server_info': current_app.config.get('SERVER_INFO', {}),
            'request_host': request.host,
            'detected_ip': obtener_ip_local(),
            'hostname': hostname,
            'all_local_ips': local_ips,
            'instructions': {
                'check_wifi': 'Asegúrate de que tu teléfono esté conectado a la misma red WiFi',
                'check_firewall': 'Verifica que no haya firewall bloqueando el puerto',
                'manual_url': f'Prueba acceder manualmente desde el navegador del teléfono: {url}'
            }
        }
    
    @main_bp.route('/ping')
    def ping():
        """Endpoint simple para probar conectividad"""
        return {
            'status': 'ok',
            'message': '🎉 ¡Conexión exitosa!',
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'your_ip': request.remote_addr,
            'server_ip': obtener_ip_local()
        }
    
    @main_bp.route("/historial")
    @login_required
    def historial():
        """Historial de ventas"""
        ventas_con_detalle = venta_model.get_all_with_details()
        return render_template("historial.html", ventas=ventas_con_detalle)
    
    @main_bp.route("/finalizar_venta", methods=["POST"])
    @login_required
    def finalizar_venta():
        """Finaliza una venta"""
        data = request.get_json()
        carrito = data.get("carrito", [])
        total = data.get("total", 0)
        
        current_user = get_current_user()
        venta_id = venta_model.create(total, current_user['id'], carrito)
        
        # Log de la venta
        log_model.create(current_user['id'], f"Venta realizada - ID: {venta_id}", 
                        f"Total: ${total:.2f}, Items: {len(carrito)}")
        
        return jsonify({"status": "ok"})
    
    # Registrar blueprint
    app.register_blueprint(main_bp)
    
    return main_bp
