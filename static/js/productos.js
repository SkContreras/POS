// Módulo para el manejo de productos y animaciones
function inicializarProductos() {
    const productos = document.querySelectorAll('.producto');
    
    productos.forEach(producto => {
        producto.addEventListener('click', function() {
            // Animación bounce
            this.classList.remove('bounce');
            void this.offsetWidth; // Forzar reflow
            this.classList.add('bounce');
            
            // Obtener datos del producto
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const precio = this.dataset.precio;
            
            // Agregar al carrito
            if (window.carritoManager && window.carritoManager.agregarAlCarrito) {
                window.carritoManager.agregarAlCarrito(id, nombre, precio);
            } else if (typeof agregarAlCarrito === 'function') {
                // Fallback a la función global
                agregarAlCarrito(id, nombre, precio);
            } else {
                console.error('No se pudo encontrar la función agregarAlCarrito');
            }
        });

        // Agregar efecto hover mejorado
        producto.addEventListener('mouseenter', function() {
            this.classList.add('hover-effect');
        });

        producto.addEventListener('mouseleave', function() {
            this.classList.remove('hover-effect');
        });
    });
}

function aplicarAnimacionProducto(elemento) {
    if (!elemento) return;
    
    elemento.classList.remove('bounce');
    void elemento.offsetWidth; // Forzar reflow
    elemento.classList.add('bounce');
}

function obtenerDatosProducto(elemento) {
    if (!elemento) return null;
    
    return {
        id: elemento.dataset.id,
        nombre: elemento.dataset.nombre,
        precio: elemento.dataset.precio
    };
}

// Exportar funciones para uso global
window.productosManager = {
    inicializarProductos,
    aplicarAnimacionProducto,
    obtenerDatosProducto
};
