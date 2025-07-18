#!/usr/bin/env python3
"""
Script para probar la generación de PDF directamente
"""
import sys
import os
sys.path.append('/home/ayase/Documentos/code/POS')

from app.models.database import DatabaseManager, Venta
from datetime import datetime

def test_pdf_generation():
    """Test directo de la generación de PDF"""
    
    # Configurar base de datos
    db_manager = DatabaseManager('database.db')
    venta_model = Venta(db_manager)
    
    # Parámetros de prueba
    fecha_inicio = '2025-07-01'
    fecha_fin = '2025-07-31'
    
    print(f"🔍 Probando generación PDF para período: {fecha_inicio} - {fecha_fin}")
    
    # Probar obtener ventas detalladas
    try:
        ventas = venta_model.get_ventas_detalladas(fecha_inicio, fecha_fin)
        print(f"✅ Ventas encontradas: {len(ventas) if ventas else 0}")
        
        if ventas:
            # Mostrar primera venta como ejemplo
            primera_venta = ventas[0]
            print(f"📄 Primera venta - ID: {primera_venta.get('id')}, Total: ${primera_venta.get('total', 0):.2f}")
            
            # Probar obtener productos de la primera venta
            productos = venta_model.get_productos_venta(primera_venta.get('id'))
            print(f"🛒 Productos en primera venta: {len(productos) if productos else 0}")
            
            if productos:
                for i, producto in enumerate(productos[:3]):  # Solo primeros 3
                    print(f"   {i+1}. {producto.get('nombre', 'N/A')} - Cant: {producto.get('cantidad', 0)} - ${producto.get('precio', 0):.2f}")
        
        # Probar generación básica de PDF
        print("\n🔧 Probando generación básica de PDF...")
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from io import BytesIO
            
            output = BytesIO()
            p = canvas.Canvas(output, pagesize=letter)
            width, height = letter
            
            # Generar contenido básico
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 100, "Test de PDF")
            p.setFont("Helvetica", 12)
            p.drawString(100, height - 130, f"Período: {fecha_inicio} al {fecha_fin}")
            p.drawString(100, height - 160, f"Ventas encontradas: {len(ventas) if ventas else 0}")
            
            # Añadir detalles de ventas
            y = height - 200
            for i, venta in enumerate(ventas[:10]):  # Solo primeras 10
                p.drawString(100, y, f"Venta {i+1}: ID {venta.get('id')} - ${venta.get('total', 0):.2f} - {venta.get('vendedor', 'N/A')}")
                y -= 20
                if y < 100:
                    break
            
            p.save()
            pdf_size = len(output.getvalue())
            print(f"✅ PDF generado exitosamente: {pdf_size} bytes")
            
            # Guardar archivo de prueba
            with open('test_pdf_output.pdf', 'wb') as f:
                output.seek(0)
                f.write(output.read())
            print("📁 PDF guardado como 'test_pdf_output.pdf'")
            
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Error obteniendo ventas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
