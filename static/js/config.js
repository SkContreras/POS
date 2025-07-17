// Configuración global del sistema POS
// Este archivo contiene constantes y configuraciones para todos los módulos

window.POS_CONFIG = {
    // Configuración de notificaciones
    TOAST: {
        DURACION_DEFECTO: 3500,
        TIPOS: {
            SUCCESS: 'success',
            ERROR: 'error',
            WARNING: 'warning',
            INFO: 'info'
        }
    },
    
    // Configuración del carrito
    CARRITO: {
        CANTIDAD_MINIMA: 1,
        CANTIDAD_MAXIMA: 999,
        DECIMALES_PRECIO: 2
    },
    
    // Configuración de búsqueda
    BUSQUEDA: {
        DELAY_BUSQUEDA: 300, // ms
        MIN_CARACTERES: 1,
        MAX_RESULTADOS: 50
    },
    
    // Configuración de animaciones
    ANIMACIONES: {
        DURACION_BOUNCE: 300,
        DURACION_FADE: 250,
        DURACION_SLIDE: 200
    },
    
    // Elementos del DOM
    SELECTORES: {
        CARRITO: '#carrito',
        TOTAL: '#total',
        BUSQUEDA: '#busqueda',
        PRODUCTOS: '.producto',
        MENU_PRODUCTOS: '#menuProductos',
        MODAL_CANTIDAD: '#cantidadModal',
        TOAST: '#toast',
        SIDEBAR_GESTION: '#gestionSidebar',
        SIDEBAR_CARRITO: '#cartSidebar'
    },
    
    // URLs del API
    API: {
        FINALIZAR_VENTA: '/finalizar_venta',
        BUSCAR_PRODUCTOS: '/buscar_productos',
        ACTUALIZAR_PRODUCTO: '/actualizar_producto'
    },
    
    // Mensajes del sistema
    MENSAJES: {
        CARRITO_VACIO: '🛒 El carrito está vacío.',
        VENTA_EXITOSA: '¡Venta guardada con éxito! 🎉',
        ERROR_CONEXION: '⚠️ Error en la conexión.',
        ERROR_GUARDAR: '❌ Hubo un error al guardar.',
        SISTEMA_LISTO: 'Sistema POS listo para usar 🚀',
        SIN_RESULTADOS: 'No se encontraron productos para'
    },
    
    // Configuración de desarrollo
    DEBUG: {
        LOGS_HABILITADOS: true,
        MOSTRAR_TIEMPOS: false,
        VERIFICAR_DEPENDENCIAS: true
    }
};

// Función de utilidad para logging
window.POS_LOG = function(modulo, mensaje, tipo = 'info') {
    if (!window.POS_CONFIG.DEBUG.LOGS_HABILITADOS) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `[POS-${modulo}] ${timestamp}:`;
    
    switch(tipo) {
        case 'error':
            console.error(prefix, mensaje);
            break;
        case 'warn':
            console.warn(prefix, mensaje);
            break;
        case 'success':
            console.log(`%c${prefix} ${mensaje}`, 'color: green; font-weight: bold');
            break;
        default:
            console.log(prefix, mensaje);
    }
};

// Función de utilidad para validaciones
window.POS_UTILS = {
    // Validar que un valor sea un número positivo
    esNumeroPositivo: function(valor) {
        return !isNaN(valor) && parseFloat(valor) > 0;
    },
    
    // Formatear precio con decimales
    formatearPrecio: function(precio) {
        return parseFloat(precio).toFixed(window.POS_CONFIG.CARRITO.DECIMALES_PRECIO);
    },
    
    // Sanitizar texto para búsqueda
    sanitizarTexto: function(texto) {
        return texto.toLowerCase().trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    },
    
    // Debounce para optimizar búsquedas
    debounce: function(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },
    
    // Verificar si un elemento existe en el DOM
    existeElemento: function(selector) {
        return document.querySelector(selector) !== null;
    }
};
