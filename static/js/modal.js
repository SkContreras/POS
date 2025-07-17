// Módulo para el manejo de modales
let productoPendiente = null;

function inicializarModal() {
    // Evento para confirmar cantidad
    const confirmBtn = document.getElementById('confirmCantidadBtn');
    if (confirmBtn) {
        confirmBtn.onclick = function() {
            const cantidad = parseFloat(document.getElementById('cantidadInput').value);
            if (productoPendiente && cantidad > 0) {
                const { id, nombre, precio } = productoPendiente;
                window.carritoManager.confirmarAgregarAlCarrito(id, nombre, precio, cantidad);
                cerrarModalCantidad();
            }
        };
    }

    // Cerrar modal con botón X
    const closeBtn = document.getElementById('closeModal');
    if (closeBtn) {
        closeBtn.onclick = function() {
            cerrarModalCantidad();
        };
    }

    // Cerrar modal al hacer click fuera
    window.onclick = function(event) {
        const modal = document.getElementById('cantidadModal');
        if (event.target === modal) {
            cerrarModalCantidad();
        }
    };

    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            cerrarModalCantidad();
        }
    });
}

function mostrarModalCantidad(id, nombre, precio) {
    productoPendiente = { id, nombre, precio };
    const modal = document.getElementById('cantidadModal');
    const title = document.getElementById('modalTitle');
    const input = document.getElementById('cantidadInput');
    
    if (title) {
        title.textContent = `¿Cuánto "${nombre}" quieres añadir al carrito?`;
    }
    if (input) {
        input.value = 1;
        input.focus();
        input.select();
    }
    if (modal) {
        modal.style.display = 'flex';
    }
}

function cerrarModalCantidad() {
    const modal = document.getElementById('cantidadModal');
    if (modal) {
        modal.style.display = 'none';
    }
    productoPendiente = null;
}

// Exportar funciones para uso global
window.modalManager = {
    inicializarModal,
    mostrarModalCantidad,
    cerrarModalCantidad
};
