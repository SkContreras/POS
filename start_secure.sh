#!/bin/bash

# Script para iniciar el servidor POS con opciones de seguridad
# Uso: ./start_secure.sh [http|https]

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏪 Mega-Mas POS - Iniciador de Servidor${NC}"
echo "=========================================="

# Función para mostrar ayuda
show_help() {
    echo -e "${YELLOW}Uso: $0 [http|https]${NC}"
    echo ""
    echo "Opciones:"
    echo "  http   - Iniciar servidor en HTTP (puerto 5000)"
    echo "  https  - Iniciar servidor en HTTPS (puerto 5443)"
    echo ""
    echo "Si no se especifica, se usará HTTP por defecto."
    echo ""
    echo -e "${YELLOW}Ejemplos:${NC}"
    echo "  $0           # HTTP en puerto 5000"
    echo "  $0 http      # HTTP en puerto 5000" 
    echo "  $0 https     # HTTPS en puerto 5443"
}

# Función para verificar certificados SSL
check_certificates() {
    if [[ ! -f "certificates/cert.pem" || ! -f "certificates/key.pem" ]]; then
        echo -e "${RED}❌ Certificados SSL no encontrados.${NC}"
        echo "Generando certificados self-signed..."
        
        # Crear directorio si no existe
        mkdir -p certificates
        
        # Generar certificados
        openssl req -x509 -newkey rsa:4096 -keyout certificates/key.pem -out certificates/cert.pem -days 365 -nodes \
            -subj "/C=MX/ST=Estado/L=Ciudad/O=POS System/OU=IT/CN=localhost" 2>/dev/null
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ Certificados SSL generados exitosamente.${NC}"
        else
            echo -e "${RED}❌ Error al generar certificados SSL.${NC}"
            echo "Asegúrate de tener OpenSSL instalado."
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Certificados SSL encontrados.${NC}"
    fi
}

# Función para iniciar el servidor
start_server() {
    local mode=$1
    
    if [[ "$mode" == "https" ]]; then
        echo -e "${GREEN}🔐 Iniciando servidor en modo HTTPS...${NC}"
        check_certificates
        export USE_HTTPS=true
        export HTTPS_PORT=5443
        echo -e "${BLUE}Servidor disponible en: https://localhost:5443${NC}"
        echo -e "${YELLOW}⚠️  Nota: Los navegadores mostrarán una advertencia de certificado self-signed.${NC}"
        echo -e "${YELLOW}   Esto es normal en desarrollo. Selecciona 'Avanzado' -> 'Continuar al sitio'.${NC}"
    else
        echo -e "${YELLOW}🔓 Iniciando servidor en modo HTTP...${NC}"
        export USE_HTTPS=false
        echo -e "${BLUE}Servidor disponible en: http://localhost:5000${NC}"
        echo -e "${RED}⚠️  ADVERTENCIA: Los campos de contraseña no estarán cifrados.${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Presiona Ctrl+C para detener el servidor${NC}"
    echo "=========================================="
    
    # Activar entorno virtual si existe
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
        echo -e "${GREEN}✅ Entorno virtual activado${NC}"
    fi
    
    # Verificar dependencias
    if ! python3 -c "import flask" 2>/dev/null; then
        echo -e "${RED}❌ Flask no está instalado. Instalando dependencias...${NC}"
        pip install -r requirements.txt
    fi
    
    # Iniciar servidor
    python3 app_modular.py
}

# Procesar argumentos
case "$1" in
    "http")
        start_server "http"
        ;;
    "https")
        start_server "https"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        echo -e "${YELLOW}No se especificó modo. Usando HTTP por defecto.${NC}"
        start_server "http"
        ;;
    *)
        echo -e "${RED}❌ Opción inválida: $1${NC}"
        show_help
        exit 1
        ;;
esac
