// Archivo principal que inicializa todos los módulos del sistema POS
// Este archivo coordina la inicialización de todos los componentes

// Funciones de compatibilidad disponibles inmediatamente
function agregarAlCarrito(id, nombre, precio) {
    if (window.carritoManager && window.carritoManager.agregarAlCarrito) {
        window.carritoManager.agregarAlCarrito(id, nombre, precio);
    } else {
        console.warn('carritoManager no disponible, reintentando...');
        // Reintentar después de un breve delay
        setTimeout(() => agregarAlCarrito(id, nombre, precio), 100);
    }
}

function eliminarDelCarrito(idx) {
    if (window.carritoManager && window.carritoManager.eliminarDelCarrito) {
        window.carritoManager.eliminarDelCarrito(idx);
    }
}

function finalizarVenta() {
    if (window.carritoManager && window.carritoManager.finalizarVenta) {
        window.carritoManager.finalizarVenta();
    }
}

function toggleGestion() {
    if (window.sidebarManager && window.sidebarManager.toggleGestion) {
        window.sidebarManager.toggleGestion();
    }
}

function mostrarToast(mensaje, tipo = "success") {
    if (window.toastManager && window.toastManager.mostrarToast) {
        window.toastManager.mostrarToast(mensaje, tipo);
    }
}

// Función mejorada para mostrar confirmaciones con fallback
function mostrarConfirmacion(tipo, titulo, mensaje, opciones = {}) {
    if (window.confirmacionManager && window.confirmacionManager.crearModal) {
        return window.confirmacionManager.crearModal(tipo, titulo, mensaje, opciones);
    } else {
        console.warn('confirmacionManager no disponible, usando fallback');
        // Fallback básico
        if (tipo === 'advertencia' || tipo === 'error' || tipo === 'exito' || tipo === 'info') {
            alert(mensaje.replace(/<[^>]*>/g, '')); // Remover HTML
            return Promise.resolve(true);
        } else {
            return Promise.resolve(confirm(mensaje.replace(/<[^>]*>/g, '')));
        }
    }
}

// Función principal de inicialización
function inicializarAplicacion() {
    console.log('Inicializando sistema POS...');
    
    try {
        // Verificar y inicializar módulos en orden específico con verificaciones
        let modulosInicializados = 0;
        const totalModulos = 6;
        
        if (window.confirmacionManager) {
            console.log('✓ Confirmación manager disponible');
            modulosInicializados++;
        } else {
            console.warn('⚠️ Confirmación manager NO disponible - usando fallbacks');
        }
        
        if (window.modalManager && window.modalManager.inicializarModal) {
            window.modalManager.inicializarModal();
            console.log('✓ Modal manager inicializado');
            modulosInicializados++;
        } else {
            console.warn('⚠️ Modal manager NO disponible - usando fallbacks');
        }
        
        if (window.sidebarManager && window.sidebarManager.inicializarSidebars) {
            window.sidebarManager.inicializarSidebars();
            console.log('✓ Sidebar manager inicializado');
            modulosInicializados++;
        } else {
            console.warn('⚠️ Sidebar manager NO disponible');
        }
        
        if (window.carritoManager && window.carritoManager.actualizarCarrito) {
            window.carritoManager.actualizarCarrito();
            console.log('✓ Carrito manager inicializado');
            modulosInicializados++;
        } else {
            console.warn('⚠️ Carrito manager NO disponible');
        }
        
        if (window.productosManager && window.productosManager.inicializarProductos) {
            window.productosManager.inicializarProductos();
            console.log('✓ Productos manager inicializado');
            modulosInicializados++;
        } else {
            console.warn('⚠️ Productos manager NO disponible');
        }
        
        if (window.busquedaManager && window.busquedaManager.inicializarBusqueda) {
            window.busquedaManager.inicializarBusqueda();
            console.log('✓ Búsqueda manager inicializado');
            modulosInicializados++;
        } else {
            console.warn('⚠️ Búsqueda manager NO disponible');
        }
        
        console.log(`✓ Sistema POS inicializado: ${modulosInicializados}/${totalModulos} módulos disponibles`);
        
        // Mostrar mensaje de bienvenida
        setTimeout(() => {
            if (window.toastManager) {
                window.toastManager.mostrarToast(`Sistema POS listo para usar 🚀 (${modulosInicializados}/${totalModulos} módulos)`, 'success');
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error al inicializar la aplicación:', error);
        if (window.toastManager) {
            window.toastManager.mostrarToast('Error al inicializar el sistema', 'error');
        }
    }
}

// Verificar que todos los módulos necesarios estén cargados
function verificarModulos() {
    const modulosRequeridos = [
        'toastManager',
        'confirmacionManager',
        'modalManager', 
        'sidebarManager',
        'carritoManager',
        'productosManager',
        'busquedaManager'
    ];
    
    const modulosFaltantes = modulosRequeridos.filter(modulo => !window[modulo]);
    
    if (modulosFaltantes.length > 0) {
        console.warn('Módulos faltantes:', modulosFaltantes);
        return false;
    }
    
    return true;
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function() {
    // Esperar un poco más para asegurar que todos los scripts se hayan cargado
    setTimeout(() => {
        inicializarAplicacion();
        
        // Verificar módulos después de la inicialización
        if (!verificarModulos()) {
            console.warn('Algunos módulos no están disponibles, pero continuando...');
        }
    }, 200);
});

// Función de diagnóstico para el desarrollador
function diagnosticarSistema() {
    console.log('=== DIAGNÓSTICO DEL SISTEMA POS ===');
    
    const modulos = {
        'toastManager': window.toastManager,
        'confirmacionManager': window.confirmacionManager,
        'modalManager': window.modalManager,
        'sidebarManager': window.sidebarManager,
        'carritoManager': window.carritoManager,
        'productosManager': window.productosManager,
        'busquedaManager': window.busquedaManager,
        'celebracionManager': window.celebracionManager
    };
    
    Object.entries(modulos).forEach(([nombre, modulo]) => {
        const estado = modulo ? '✅ Disponible' : '❌ No disponible';
        console.log(`${nombre}: ${estado}`);
        
        if (modulo && typeof modulo === 'object') {
            const funciones = Object.keys(modulo).filter(key => typeof modulo[key] === 'function');
            if (funciones.length > 0) {
                console.log(`  └── Funciones: ${funciones.join(', ')}`);
            }
        }
    });
    
    console.log('=====================================');
    return modulos;
}

// Exportar funciones globales para compatibilidad
window.agregarAlCarrito = agregarAlCarrito;
window.eliminarDelCarrito = eliminarDelCarrito;
window.finalizarVenta = finalizarVenta;
window.toggleGestion = toggleGestion;
window.mostrarToast = mostrarToast;
window.mostrarConfirmacion = mostrarConfirmacion;
window.diagnosticarSistema = diagnosticarSistema;