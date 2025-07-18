#!/usr/bin/env python3
"""
Rutas principales para el sistema POS
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, send_file
from app.models.database import Producto, Venta, LogAccion, Gasto
from app.utils.auth import login_required, admin_required, get_current_user
from app.utils.helpers import obtener_ip_local, generar_qr_code, save_uploaded_file, allowed_file
import os
import time
import threading
from datetime import datetime
from io import BytesIO, StringIO

# Crear blueprint para rutas principales
main_bp = Blueprint('main', __name__)

def init_main_routes(app, db_manager):
    """Inicializa las rutas principales"""
    
    # Modelos
    producto_model = Producto(db_manager)
    venta_model = Venta(db_manager)
    log_model = LogAccion(db_manager)
    gasto_model = Gasto(db_manager)
    
    @main_bp.route("/")
    @login_required
    def index():
        """Página principal del POS"""
        # Obtener parámetros de filtro y ordenamiento
        order_by = request.args.get('order_by', 'recientes')
        categoria = request.args.get('categoria', 'todas')
        busqueda = request.args.get('busqueda', '')
        
        # Obtener productos filtrados
        productos = producto_model.get_all_filtered(order_by, categoria, busqueda)
        
        # Obtener todas las categorías para el selector
        categorias = producto_model.get_categories()
        
        return render_template("index.html", 
                             productos=productos, 
                             categorias=categorias,
                             order_by=order_by,
                             categoria_actual=categoria,
                             busqueda_actual=busqueda)
    
    @main_bp.route('/shutdown', methods=['POST'])
    @admin_required
    def shutdown():
        """Cierra el servidor y la sesión"""
        from flask import session
        from app.utils.auth import clear_session
        
        current_user = get_current_user()
        if current_user:
            log_model.registrar(current_user['id'], "Cierre del servidor/tienda y sesión")
        
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
        
        # Crear venta con manejo de stock
        venta_id, error = venta_model.create(total, current_user['id'], carrito, producto_model)
        
        if error:
            # Si hay un error (como stock insuficiente), devolver error
            return jsonify({"status": "error", "message": error}), 400
        
        # Incrementar contador de ventas para cada producto vendido
        for item in carrito:
            producto_id = item.get('id')
            cantidad = item.get('cantidad', 1)
            # Incrementar tantas veces como la cantidad vendida
            for _ in range(cantidad):
                producto_model.increment_sales_count(producto_id)
        
        # Log de la venta
        log_model.registrar(current_user['id'], f"Venta realizada - ID: {venta_id}", 
                        f"Total: ${total:.2f}, Items: {len(carrito)}")
        
        return jsonify({"status": "ok"})
    
    @main_bp.route("/stock_info")
    @login_required
    def stock_info():
        """Información de stock"""
        productos_stock_bajo = producto_model.get_low_stock_products(umbral=5)
        productos_agotados = producto_model.get_low_stock_products(umbral=0)
        
        return jsonify({
            "stock_bajo": len(productos_stock_bajo),
            "agotados": len([p for p in productos_agotados if p[7] == 0]),  # stock en posición 7
            "productos_stock_bajo": [
                {
                    "id": p[0],
                    "nombre": p[1],
                    "stock": p[7],
                    "categoria": p[4]
                } for p in productos_stock_bajo
            ]
        })
    
    @main_bp.route("/contabilidad")
    @admin_required
    def contabilidad():
        """Página de contabilidad con estadísticas y gráficas"""
        from datetime import datetime, timedelta
        import calendar
        
        # Obtener parámetros de filtro
        periodo = request.args.get('periodo', 'mes')  # mes, semana, año, dia, rango
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Calcular fechas según el período
        hoy = datetime.now()
        
        if periodo == 'dia':
            fecha_inicio = fecha_inicio or hoy.strftime('%Y-%m-%d')
            fecha_fin = fecha_inicio
        elif periodo == 'semana':
            # Semana actual por defecto
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fecha_inicio = fecha_inicio or inicio_semana.strftime('%Y-%m-%d')
            fecha_fin = fecha_fin or (inicio_semana + timedelta(days=6)).strftime('%Y-%m-%d')
        elif periodo == 'mes':
            # Mes actual por defecto
            fecha_inicio = fecha_inicio or hoy.replace(day=1).strftime('%Y-%m-%d')
            ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
            fecha_fin = fecha_fin or hoy.replace(day=ultimo_dia).strftime('%Y-%m-%d')
        elif periodo == 'año':
            # Año actual por defecto
            fecha_inicio = fecha_inicio or hoy.replace(month=1, day=1).strftime('%Y-%m-%d')
            fecha_fin = fecha_fin or hoy.replace(month=12, day=31).strftime('%Y-%m-%d')
        # Para 'rango' usar las fechas proporcionadas o defaults
        
        if not fecha_inicio:
            fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        if not fecha_fin:
            fecha_fin = hoy.strftime('%Y-%m-%d')
        
        # Obtener estadísticas
        estadisticas = venta_model.get_estadisticas_periodo(fecha_inicio, fecha_fin)
        
        # Datos para gráficas
        ventas_por_dia = venta_model.get_ventas_por_dia(fecha_inicio, fecha_fin)
        ventas_por_hora = venta_model.get_ventas_por_hora(fecha_inicio, fecha_fin)
        ventas_por_mes = venta_model.get_ventas_por_mes(fecha_inicio, fecha_fin)
        productos_mas_vendidos = venta_model.get_productos_mas_vendidos(fecha_inicio, fecha_fin)
        ingresos_por_categoria = venta_model.get_ingresos_por_categoria(fecha_inicio, fecha_fin)
        
        # ✨ NUEVOS: Análisis de rentabilidad con precios de compra/venta
        analisis_rentabilidad = venta_model.get_analisis_rentabilidad(fecha_inicio, fecha_fin)
        resumen_financiero = venta_model.get_resumen_financiero_completo(fecha_inicio, fecha_fin, gasto_model)
        productos_menos_rentables = venta_model.get_productos_menos_rentables(fecha_inicio, fecha_fin)
        analisis_por_categoria = venta_model.get_analisis_por_categoria(fecha_inicio, fecha_fin)
        
        # ✨ NUEVOS: Datos de gastos operativos
        try:
            estadisticas_gastos = gasto_model.get_estadisticas_gastos(fecha_inicio, fecha_fin)
            gastos_por_categoria = gasto_model.get_gastos_por_categoria(fecha_inicio, fecha_fin)
        except Exception as e:
            print(f"Error al obtener datos de gastos: {e}")
            estadisticas_gastos = {'gastos_totales': 0, 'total_gastos': 0, 'gasto_promedio': 0, 'gasto_maximo': 0, 'gasto_minimo': 0}
            gastos_por_categoria = []
        
        # Transformar datos para compatibilidad con la página
        # Verificar que los datos existen antes de transformarlos
        ventas_periodo = []
        if ventas_por_dia:
            ventas_periodo = [{'fecha': v['fecha'], 'cantidad': v['cantidad'], 'total': v['total']} for v in ventas_por_dia]
        
        productos_top = []
        if productos_mas_vendidos:
            productos_top = [{'nombre': p['nombre'], 'cantidad': p['cantidad'], 'ingresos': p['total_ingresos']} for p in productos_mas_vendidos]
        
        # Calcular estadísticas adicionales
        promedio_diario = estadisticas['ingresos_totales'] / max(len(ventas_por_dia), 1) if ventas_por_dia else 0
        ticket_promedio = estadisticas['venta_promedio']
        total_transacciones = estadisticas['total_ventas']
        margen_utilidad = 0  # Por implementar
        
        return render_template('contabilidad.html',
                             # Datos originales
                             estadisticas=estadisticas,
                             ventas_por_dia=ventas_por_dia,
                             ventas_por_hora=ventas_por_hora,
                             ventas_por_mes=ventas_por_mes,
                             productos_mas_vendidos=productos_mas_vendidos,
                             ingresos_por_categoria=ingresos_por_categoria,
                             # ✨ NUEVOS: Análisis de rentabilidad
                             analisis_rentabilidad=analisis_rentabilidad,
                             resumen_financiero=resumen_financiero,
                             productos_menos_rentables=productos_menos_rentables,
                             analisis_por_categoria=analisis_por_categoria,
                             # ✨ NUEVOS: Datos de gastos
                             estadisticas_gastos=estadisticas_gastos,
                             gastos_por_categoria=gastos_por_categoria,
                             # Datos para compatibilidad con template
                             ingresos_totales=resumen_financiero['ingresos_totales'],
                             gastos_totales=resumen_financiero['gastos_operativos'],
                             productos_vendidos=estadisticas['productos_vendidos'],
                             ventas_periodo=ventas_periodo,
                             productos_top=productos_top,
                             promedio_diario=promedio_diario,
                             ticket_promedio=ticket_promedio,
                             total_transacciones=total_transacciones,
                             margen_utilidad=resumen_financiero['margen_neto'],
                             periodo=periodo,
                             fecha_inicio=fecha_inicio,
                             fecha_fin=fecha_fin)

    @main_bp.route("/contabilidad/exportar")
    @admin_required
    def exportar_contabilidad():
        """Exportar datos de contabilidad en diferentes formatos"""
        formato = request.args.get('formato', 'pdf')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        tipo = request.args.get('tipo', 'contabilidad')
        
        # Si no hay fechas, usar el último mes
        if not fecha_inicio or not fecha_fin:
            from datetime import datetime, timedelta
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            # Obtener datos
            estadisticas = venta_model.get_estadisticas_periodo(fecha_inicio, fecha_fin)
            ventas_por_dia = venta_model.get_ventas_por_dia(fecha_inicio, fecha_fin)
            productos_mas_vendidos = venta_model.get_productos_mas_vendidos(fecha_inicio, fecha_fin)
            
            if formato == 'excel':
                return exportar_excel(estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin)
            elif formato == 'pdf':
                return exportar_pdf(estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin, tipo)
            elif formato == 'csv':
                return exportar_csv(ventas_por_dia, fecha_inicio, fecha_fin)
            else:
                flash('Formato no soportado', 'error')
                return redirect(url_for('main.contabilidad'))
                
        except Exception as e:
            flash(f'Error al exportar: {str(e)}', 'error')
            return redirect(url_for('main.contabilidad'))

    def exportar_excel(estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin):
        """Exportar a Excel usando openpyxl"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from io import BytesIO
            
            wb = openpyxl.Workbook()
            
            # Hoja de resumen
            ws_resumen = wb.active
            ws_resumen.title = "Resumen"
            
            # Encabezado
            ws_resumen['A1'] = "Reporte de Contabilidad"
            ws_resumen['A1'].font = Font(size=16, bold=True)
            ws_resumen['A2'] = f"Período: {fecha_inicio} al {fecha_fin}"
            
            # Estadísticas
            stats_row = 4
            ws_resumen[f'A{stats_row}'] = "Total de Ventas:"
            ws_resumen[f'B{stats_row}'] = estadisticas['total_ventas']
            
            stats_row += 1
            ws_resumen[f'A{stats_row}'] = "Ingresos Totales:"
            ws_resumen[f'B{stats_row}'] = estadisticas['ingresos_totales']
            
            stats_row += 1
            ws_resumen[f'A{stats_row}'] = "Venta Promedio:"
            ws_resumen[f'B{stats_row}'] = estadisticas['venta_promedio']
            
            # Hoja de ventas por día
            ws_dias = wb.create_sheet("Ventas por Día")
            ws_dias['A1'] = "Fecha"
            ws_dias['B1'] = "Número de Ventas"
            ws_dias['C1'] = "Ingresos"
            
            for i, venta in enumerate(ventas_por_dia, 2):
                ws_dias[f'A{i}'] = venta['dia']
                ws_dias[f'B{i}'] = venta['ventas']
                ws_dias[f'C{i}'] = venta['ingresos']
            
            # Hoja de productos más vendidos
            ws_productos = wb.create_sheet("Productos Más Vendidos")
            ws_productos['A1'] = "Producto"
            ws_productos['B1'] = "Cantidad Vendida"
            ws_productos['C1'] = "Ingresos"
            
            for i, producto in enumerate(productos_mas_vendidos, 2):
                ws_productos[f'A{i}'] = producto['nombre']
                ws_productos[f'B{i}'] = producto['cantidad']
                ws_productos[f'C{i}'] = producto['ingresos']
            
            # Guardar en memoria
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            
            filename = f"contabilidad_{fecha_inicio}_{fecha_fin}.xlsx"
            
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except ImportError:
            flash('openpyxl no está instalado. Use pip install openpyxl', 'error')
            return redirect(url_for('main.contabilidad'))
    
    def exportar_pdf(estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin, tipo='contabilidad'):
        """Exportar a PDF usando reportlab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.units import inch
            from io import BytesIO
            from datetime import datetime
            
            print(f"DEBUG: Iniciando exportación PDF tipo='{tipo}', período={fecha_inicio} - {fecha_fin}")
            
            output = BytesIO()
            p = canvas.Canvas(output, pagesize=letter)
            width, height = letter
            
            if tipo == 'recibos':
                # Generar recibos detallados
                print("DEBUG: Generando recibos detallados")
                return generar_recibos_detallados(p, output, fecha_inicio, fecha_fin, width, height)
            else:
                # Reporte de contabilidad normal
                print("DEBUG: Generando reporte de contabilidad")
                return generar_reporte_contabilidad(p, output, estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin, width, height)
            
        except ImportError as e:
            print(f"ERROR: ImportError en exportar_pdf: {e}")
            # Si reportlab no está instalado, crear un PDF simple con texto
            from io import BytesIO
            
            output = BytesIO()
            
            # Crear contenido de texto simple
            content = f"""
REPORTE DE CONTABILIDAD
Período: {fecha_inicio} al {fecha_fin}

ESTADÍSTICAS:
- Total de Ventas: {estadisticas.get('total_ventas', 0) if estadisticas else 0}
- Ingresos Totales: ${estadisticas.get('ingresos_totales', 0):.2f if estadisticas else 0}
- Venta Promedio: ${estadisticas.get('venta_promedio', 0):.2f if estadisticas else 0}

VENTAS POR DÍA:
"""
            
            if ventas_por_dia:
                for venta in ventas_por_dia[:10]:
                    fecha = venta.get('fecha', 'N/A')
                    total = venta.get('total', 0)
                    content += f"- {fecha}: ${total:.2f}\n"
            
            # Escribir contenido como bytes
            output.write(content.encode('utf-8'))
            output.seek(0)
            
            filename = f"contabilidad_{fecha_inicio}_{fecha_fin}.txt"
            
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='text/plain'
            )
        except Exception as e:
            print(f"ERROR: Excepción general en exportar_pdf: {e}")
            import traceback
            traceback.print_exc()
            
            # Crear un PDF básico con el error
            from io import BytesIO
            output = BytesIO()
            
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                
                p = canvas.Canvas(output, pagesize=letter)
                width, height = letter
                
                p.setFont("Helvetica-Bold", 16)
                p.drawString(100, height - 100, "Error al generar PDF")
                p.setFont("Helvetica", 12)
                p.drawString(100, height - 130, f"Error: {str(e)}")
                p.drawString(100, height - 150, f"Tipo: {tipo}")
                p.drawString(100, height - 170, f"Período: {fecha_inicio} al {fecha_fin}")
                p.showPage()
                p.save()
                output.seek(0)
                
                return send_file(output, as_attachment=True, download_name=f"error_{tipo}.pdf", mimetype='application/pdf')
                
            except:
                # Si todo falla, devolver texto
                error_text = f"Error al generar PDF: {str(e)}"
                output = BytesIO(error_text.encode('utf-8'))
                return send_file(output, as_attachment=True, download_name="error.txt", mimetype='text/plain')
    
    def exportar_csv(ventas_por_dia, fecha_inicio, fecha_fin):
        """Exportar a CSV"""
        import csv
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        writer.writerow(['Fecha', 'Número de Ventas', 'Ingresos'])
        
        # Datos
        for venta in ventas_por_dia:
            writer.writerow([venta['dia'], venta['ventas'], venta['ingresos']])
        
        # Convertir a bytes
        csv_data = output.getvalue().encode('utf-8')
        output_bytes = BytesIO(csv_data)
        
        filename = f"ventas_{fecha_inicio}_{fecha_fin}.csv"
        
        return send_file(
            output_bytes,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    def generar_recibos_detallados(p, output, fecha_inicio, fecha_fin, width, height):
        """Generar recibos detallados para cada venta"""
        from datetime import datetime
        
        try:
            # Obtener todas las ventas del período con detalles completos
            ventas = venta_model.get_ventas_detalladas(fecha_inicio, fecha_fin)
            
            print(f"DEBUG: Encontradas {len(ventas) if ventas else 0} ventas para el período {fecha_inicio} - {fecha_fin}")
            
            if not ventas or len(ventas) == 0:
                # Si no hay ventas, crear un PDF con mensaje
                p.setFont("Helvetica-Bold", 16)
                p.drawString(100, height - 100, "Recibos de Ventas")
                p.setFont("Helvetica", 12)
                p.drawString(100, height - 130, f"Período: {fecha_inicio} al {fecha_fin}")
                p.drawString(100, height - 160, "No se encontraron ventas en este período")
                p.showPage()
                p.save()
                output.seek(0)
                return send_file(output, as_attachment=True, download_name=f"recibos_{fecha_inicio}_{fecha_fin}.pdf", mimetype='application/pdf')
            
            # Generar portada
            generar_portada_recibos(p, width, height, fecha_inicio, fecha_fin, len(ventas))
            p.showPage()
            
            # Generar un recibo por cada venta
            for i, venta in enumerate(ventas):
                print(f"DEBUG: Generando recibo {i+1} para venta ID {venta.get('id')}")
                generar_recibo_individual(p, venta, width, height, i + 1, len(ventas))
                p.showPage()
            
            # Generar página de resumen final
            print("DEBUG: Generando página de resumen final")
            generar_pagina_resumen_final(p, ventas, width, height, fecha_inicio, fecha_fin)
            p.showPage()
            
            p.save()
            output.seek(0)
            
            print(f"DEBUG: PDF generado con {len(output.getvalue())} bytes")
            
            filename = f"recibos_detallados_{fecha_inicio}_{fecha_fin}.pdf"
            return send_file(output, as_attachment=True, download_name=filename, mimetype='application/pdf')
            
        except Exception as e:
            print(f"ERROR en generar_recibos_detallados: {e}")
            import traceback
            traceback.print_exc()
            # Retornar un PDF básico en caso de error
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 100, "Error al generar recibos")
            p.setFont("Helvetica", 12)
            p.drawString(100, height - 130, f"Error: {str(e)}")
            p.showPage()
            p.save()
            output.seek(0)
            return send_file(output, as_attachment=True, download_name=f"error_recibos.pdf", mimetype='application/pdf')
    
    def generar_portada_recibos(p, width, height, fecha_inicio, fecha_fin, total_ventas):
        """Generar portada del documento de recibos"""
        # Título principal
        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(width/2, height - 150, "RECIBOS DE VENTAS")
        
        # Información del período
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width/2, height - 200, f"Período: {fecha_inicio} al {fecha_fin}")
        
        # Total de ventas
        p.setFont("Helvetica", 14)
        p.drawCentredString(width/2, height - 240, f"Total de ventas incluidas: {total_ventas}")
        
        # Fecha de generación
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        p.drawCentredString(width/2, height - 280, f"Generado el: {fecha_actual}")
        
        # Línea decorativa
        p.line(100, height - 320, width - 100, height - 320)
        
        # Información adicional
        p.setFont("Helvetica", 10)
        p.drawCentredString(width/2, height - 350, "Este documento contiene un recibo detallado por cada venta realizada")
        p.drawCentredString(width/2, height - 370, "Incluye información del vendedor, productos y totales")
    
    def generar_recibo_individual(p, venta, width, height, numero_recibo, total_recibos):
        """Generar un recibo individual para una venta"""
        from datetime import datetime
        
        # Encabezado del recibo
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, height - 50, f"RECIBO DE VENTA #{numero_recibo}")
        p.setFont("Helvetica", 10)
        p.drawRightString(width - 50, height - 50, f"Recibo {numero_recibo} de {total_recibos}")
        
        # Línea separadora
        p.line(50, height - 70, width - 50, height - 70)
        
        y = height - 100
        
        # Información de la venta
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "INFORMACIÓN DE LA VENTA")
        y -= 25
        
        p.setFont("Helvetica", 10)
        p.drawString(70, y, f"ID de Venta: {venta.get('id', 'N/A')}")
        y -= 15
        
        # Formatear fecha
        fecha_venta = venta.get('fecha_hora', 'N/A')
        if fecha_venta != 'N/A':
            try:
                fecha_obj = datetime.fromisoformat(fecha_venta.replace('Z', '+00:00'))
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
            except:
                fecha_formateada = fecha_venta
        else:
            fecha_formateada = 'N/A'
        
        p.drawString(70, y, f"Fecha y Hora: {fecha_formateada}")
        y -= 15
        
        # Información del vendedor
        vendedor = venta.get('vendedor', 'Usuario no especificado')
        p.drawString(70, y, f"Atendido por: {vendedor}")
        y -= 15
        
        total_venta = venta.get('total', 0)
        p.drawString(70, y, f"Total de la Venta: ${total_venta:.2f}")
        y -= 30
        
        # Productos vendidos
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "PRODUCTOS VENDIDOS")
        y -= 20
        
        # Encabezados de tabla
        p.setFont("Helvetica-Bold", 9)
        p.drawString(70, y, "Producto")
        p.drawString(300, y, "Cant.")
        p.drawString(350, y, "Precio Unit.")
        p.drawString(450, y, "Subtotal")
        y -= 15
        
        # Línea de separación
        p.line(70, y, width - 50, y)
        y -= 10
        
        # Obtener productos de esta venta
        productos_venta = venta_model.get_productos_venta(venta.get('id'))
        
        p.setFont("Helvetica", 9)
        subtotal_productos = 0
        
        for producto in productos_venta:
            # Truncar nombre si es muy largo
            nombre = producto.get('nombre', 'Producto')
            if len(nombre) > 25:
                nombre = nombre[:22] + "..."
            
            cantidad = producto.get('cantidad', 1)
            precio = producto.get('precio', 0)
            subtotal = cantidad * precio
            subtotal_productos += subtotal
            
            p.drawString(70, y, nombre)
            p.drawString(300, y, str(cantidad))
            p.drawString(350, y, f"${precio:.2f}")
            p.drawString(450, y, f"${subtotal:.2f}")
            y -= 12
            
            # Verificar si necesitamos nueva página
            if y < 100:
                p.showPage()
                y = height - 50
        
        # Total
        y -= 10
        p.line(350, y, width - 50, y)
        y -= 15
        p.setFont("Helvetica-Bold", 11)
        p.drawString(350, y, "TOTAL:")
        p.drawString(450, y, f"${total_venta:.2f}")
        
        # Información adicional
        y -= 40
        p.setFont("Helvetica", 8)
        p.drawString(50, y, "Gracias por su compra")
        y -= 12
        p.drawString(50, y, f"Recibo generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Línea final
        p.line(50, 50, width - 50, 50)
    
    def generar_reporte_contabilidad(p, output, estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin, width, height):
        """Generar reporte de contabilidad normal"""
        # Título
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 50, "Reporte de Contabilidad")
        
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 80, f"Período: {fecha_inicio} al {fecha_fin}")
        
        # Estadísticas
        y = height - 120
        if estadisticas:
            p.drawString(100, y, f"Total de Ventas: {estadisticas.get('total_ventas', 0)}")
            y -= 20
            p.drawString(100, y, f"Ingresos Totales: ${estadisticas.get('ingresos_totales', 0):.2f}")
            y -= 20
            p.drawString(100, y, f"Venta Promedio: ${estadisticas.get('venta_promedio', 0):.2f}")
            y -= 30
        
        # Datos de ventas por día
        if ventas_por_dia and len(ventas_por_dia) > 0:
            p.drawString(100, y, "Ventas por Día:")
            y -= 20
            for venta in ventas_por_dia[:10]:  # Solo primeros 10
                fecha = venta.get('fecha', 'N/A')
                total = venta.get('total', 0)
                p.drawString(120, y, f"• {fecha}: ${total:.2f}")
                y -= 15
                if y < 100:  # Nueva página si es necesario
                    p.showPage()
                    y = height - 50
        
        p.save()
        output.seek(0)
        
        filename = f"contabilidad_{fecha_inicio}_{fecha_fin}.pdf"
        return send_file(output, as_attachment=True, download_name=filename, mimetype='application/pdf')

    @main_bp.route("/test_pdf")
    def test_pdf():
        """Endpoint temporal para probar PDF sin autenticación"""
        from datetime import datetime, timedelta
        
        # Usar fechas predeterminadas
        fecha_fin = datetime.now().strftime('%Y-%m-%d')
        fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            # Obtener datos
            estadisticas = venta_model.get_estadisticas_periodo(fecha_inicio, fecha_fin)
            ventas_por_dia = venta_model.get_ventas_por_dia(fecha_inicio, fecha_fin)
            productos_mas_vendidos = venta_model.get_productos_mas_vendidos(fecha_inicio, fecha_fin)
            
            # Generar PDF de recibos detallados
            return exportar_pdf(estadisticas, ventas_por_dia, productos_mas_vendidos, fecha_inicio, fecha_fin, 'recibos')
                
        except Exception as e:
            return f"Error: {str(e)}", 500

    def generar_pagina_resumen_final(p, ventas, width, height, fecha_inicio, fecha_fin):
        """Generar página de resumen final con totales generales"""
        from datetime import datetime
        
        # Calcular totales
        total_general = sum(venta.get('total', 0) for venta in ventas)
        cantidad_ventas = len(ventas)
        promedio_venta = total_general / cantidad_ventas if cantidad_ventas > 0 else 0
        
        # Título principal
        p.setFont("Helvetica-Bold", 24)
        p.drawCentredString(width/2, height - 100, "RESUMEN GENERAL")
        
        # Línea decorativa
        p.line(100, height - 130, width - 100, height - 130)
        
        # Información del período
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width/2, height - 170, f"Período: {fecha_inicio} al {fecha_fin}")
        
        # Fecha de generación
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        p.setFont("Helvetica", 12)
        p.drawCentredString(width/2, height - 200, f"Reporte generado el: {fecha_actual}")
        
        # Recuadro para totales
        y_start = height - 250
        box_height = 200
        box_width = 400
        box_x = (width - box_width) / 2
        
        # Dibujar recuadro
        p.rect(box_x, y_start - box_height, box_width, box_height)
        
        # Contenido del recuadro
        y = y_start - 40
        
        # Título del recuadro
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width/2, y, "TOTALES GENERALES")
        y -= 40
        
        # Cantidad de ventas
        p.setFont("Helvetica-Bold", 14)
        p.drawString(box_x + 20, y, "Cantidad de Ventas:")
        p.drawRightString(box_x + box_width - 20, y, f"{cantidad_ventas}")
        y -= 25
        
        # Línea separadora
        p.line(box_x + 20, y + 10, box_x + box_width - 20, y + 10)
        y -= 15
        
        # Total general
        p.setFont("Helvetica-Bold", 16)
        p.drawString(box_x + 20, y, "TOTAL GENERAL:")
        p.drawRightString(box_x + box_width - 20, y, f"${total_general:.2f}")
        y -= 30
        
        # Promedio por venta
        p.setFont("Helvetica", 12)
        p.drawString(box_x + 20, y, "Promedio por venta:")
        p.drawRightString(box_x + box_width - 20, y, f"${promedio_venta:.2f}")
        
        # Información adicional debajo del recuadro
        y = y_start - box_height - 40
        
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(width/2, y, "DETALLES DEL PERÍODO")
        y -= 30
        
        # Ventas por rango de fechas
        ventas_por_dia = {}
        for venta in ventas:
            fecha_venta = venta.get('fecha_hora', '')
            if fecha_venta:
                try:
                    fecha_obj = datetime.fromisoformat(fecha_venta.replace('Z', '+00:00'))
                    dia = fecha_obj.strftime('%Y-%m-%d')
                    if dia not in ventas_por_dia:
                        ventas_por_dia[dia] = {'cantidad': 0, 'total': 0}
                    ventas_por_dia[dia]['cantidad'] += 1
                    ventas_por_dia[dia]['total'] += venta.get('total', 0)
                except:
                    pass
        
        # Mostrar resumen por día (máximo 10 días)
        p.setFont("Helvetica", 10)
        dias_ordenados = sorted(ventas_por_dia.keys())
        
        if dias_ordenados:
            p.drawString(100, y, "Resumen por día:")
            y -= 15
            
            for dia in dias_ordenados[:10]:  # Máximo 10 días
                info_dia = ventas_por_dia[dia]
                fecha_formateada = datetime.strptime(dia, '%Y-%m-%d').strftime('%d/%m/%Y')
                p.drawString(120, y, f"• {fecha_formateada}: {info_dia['cantidad']} ventas - ${info_dia['total']:.2f}")
                y -= 12
                
                if y < 100:  # Si nos quedamos sin espacio
                    break
        
        # Nota final
        y = 80
        p.setFont("Helvetica", 8)
        p.drawCentredString(width/2, y, "Este resumen incluye todas las ventas del período especificado")
        p.drawCentredString(width/2, y - 12, f"Documento generado automáticamente por el Sistema POS")

    # Registrar blueprint
    app.register_blueprint(main_bp)
    
    return main_bp
