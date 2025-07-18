// Módulo para el manejo de productos y animaciones
function inicializarProductos() {
    const productos = document.querySelectorAll('.producto');
    
    productos.forEach(producto => {
        producto.addEventListener('click', function() {
            // Verificar stock antes de permitir agregar al carrito
            const stock = parseInt(this.dataset.stock || '999');
            const categoria = this.dataset.categoria || '';
            
            // Si es pescadería y no hay stock, mostrar alerta
            if (categoria === 'Pescadería' && stock === 0) {
                if (window.toastManager) {
                    window.toastManager.mostrar('❌ Producto agotado - Sin stock disponible', 'error');
                } else {
                    alert('❌ Producto agotado - Sin stock disponible');
                }
                return;
            }
            
            // Verificar si ya hay este producto en el carrito
            const carritoActual = Array.isArray(window.carrito) ? window.carrito : [];
            const productoEnCarrito = carritoActual.find(item => item.id === this.dataset.id);
            const cantidadEnCarrito = productoEnCarrito ? productoEnCarrito.cantidad : 0;
            
            // Para pescadería, verificar que no exceda el stock
            if (categoria === 'Pescadería' && cantidadEnCarrito >= stock) {
                if (window.toastManager) {
                    window.toastManager.mostrar(`⚠️ Stock insuficiente - Solo quedan ${stock} unidades`, 'warning');
                } else {
                    alert(`⚠️ Stock insuficiente - Solo quedan ${stock} unidades`);
                }
                return;
            }
            
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
