import subprocess
import time
import sys
import signal
import os

def start_flask_server():
    """Inicia el servidor Flask"""
    print("🚀 Iniciando servidor Flask...")
    return subprocess.Popen([sys.executable, "app.py"], 
                          cwd=os.getcwd(),
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)

def start_cloudflare_tunnel():
    """Inicia el túnel de Cloudflare"""
    print("🌐 Iniciando túnel de Cloudflare...")
    try:
        result = subprocess.run(["cloudflared", "tunnel", "--url", "http://192.168.1.105:5000"], 
                              check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar túnel: {e}")
        return None
    except FileNotFoundError:
        print("❌ cloudflared no encontrado. Instálalo primero con:")
        print("   winget install --id Cloudflare.cloudflared")
        return None

def main():
    flask_process = None
    
    try:
        # Iniciar servidor Flask
        flask_process = start_flask_server()
        
        # Esperar a que Flask inicie
        print("⏳ Esperando que Flask inicie...")
        time.sleep(5)
        
        # Verificar si Flask está corriendo
        if flask_process.poll() is None:
            print("✅ Servidor Flask iniciado correctamente")
            print("📍 Ejecutándose en: http://192.168.1.105:5000")
            
            # Iniciar túnel de Cloudflare
            start_cloudflare_tunnel()
        else:
            print("❌ Error al iniciar servidor Flask")
            if flask_process.stderr:
                error = flask_process.stderr.read().decode()
                print(f"Error: {error}")
                
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        
    finally:
        # Limpiar procesos
        if flask_process and flask_process.poll() is None:
            print("🔄 Terminando servidor Flask...")
            flask_process.terminate()
            flask_process.wait()
            
        print("✅ Servicios detenidos")

if __name__ == "__main__":
    main()
