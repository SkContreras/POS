#!/usr/bin/env python3
"""
Utilidades generales para el sistema POS
"""
import socket
import os
import qrcode
import io
import webbrowser
import time
import threading
from werkzeug.utils import secure_filename
import uuid

def obtener_ip_local():
    """Obtiene la IP local del sistema de forma automática"""
    try:
        # Método 1: Crear un socket temporal para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        
        # Verificar que no sea una IP de loopback
        if ip_local.startswith('127.'):
            raise Exception("IP de loopback detectada")
            
        return ip_local
    except Exception:
        try:
            # Método 2: Usar hostname para obtener IP
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            
            # Verificar que no sea loopback
            if not ip_local.startswith('127.'):
                return ip_local
        except Exception:
            pass
        
        try:
            # Método 3: Obtener todas las IPs y filtrar
            hostname = socket.gethostname()
            ip_list = socket.gethostbyname_ex(hostname)[2]
            
            # Filtrar IPs válidas (no loopback, no link-local)
            for ip in ip_list:
                if (not ip.startswith('127.') and 
                    not ip.startswith('169.254.') and 
                    not ip.startswith('::1')):
                    return ip
        except Exception:
            pass
        
        # Fallback final a localhost
        return "127.0.0.1"

def generar_qr_code(url):
    """Genera un código QR para una URL"""
    qr = qrcode.make(url)
    buffer = io.BytesIO()
    qr.save(buffer, "PNG")
    buffer.seek(0)
    return buffer

def abrir_navegador_con_retraso():
    """Abre el navegador después de un pequeño retraso"""
    time.sleep(1)  # Espera 1 segundo para que el servidor esté listo
    abrir_navegador()

def abrir_navegador():
    """Abre el navegador web con la URL correcta del servidor"""
    ip_local = obtener_ip_local()
    port = int(os.environ.get('PORT', 5000))
    url = f"http://{ip_local}:{port}/"
    print(f"Abriendo navegador en: {url}")
    webbrowser.open(url, new=1)  # new=1 para usar pestaña existente si hay una

def iniciar_navegador_background():
    """Inicia el navegador en un hilo separado"""
    thread = threading.Thread(target=abrir_navegador_con_retraso)
    thread.daemon = True  # Thread se cierra cuando el programa principal termine
    thread.start()

def allowed_file(filename, allowed_extensions):
    """Verifica si un archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder, product_id=None):
    """Guarda un archivo subido y retorna el nombre del archivo"""
    if file and file.filename:
        # Asegurar nombre único y seguro
        filename_original = secure_filename(file.filename)
        extension = os.path.splitext(filename_original)[1]
        
        if product_id:
            filename = f"prod_{product_id}_{uuid.uuid4().hex}{extension}"
        else:
            filename = f"prod_{uuid.uuid4().hex}{extension}"
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None

def format_currency(amount):
    """Formatea una cantidad como moneda"""
    return f"${amount:.2f}"

def validate_price(price_str):
    """Valida y convierte un string de precio a float"""
    try:
        price = float(price_str)
        if price < 0:
            raise ValueError("El precio no puede ser negativo")
        return price
    except (ValueError, TypeError):
        raise ValueError("Precio inválido")

def generate_filename(original_filename, prefix="prod"):
    """Genera un nombre de archivo único y seguro"""
    if not original_filename:
        return None
    
    # Sanitizar el nombre original
    filename_original = secure_filename(original_filename)
    extension = os.path.splitext(filename_original)[1]
    
    # Generar nombre único
    unique_filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
    return unique_filename

def clean_filename(filename):
    """Limpia y sanitiza un nombre de archivo"""
    return secure_filename(filename) if filename else None
