// Módulo para el manejo de los sidebars
function toggleGestion() {
    const gestion = document.getElementById('gestionSidebar');
    const cart = document.getElementById('cartSidebar');
    const toggleGestionBtn = document.querySelector('.toggle-gestion-fixed');
    
    if (!gestion) return;
    
    gestion.classList.toggle('collapsed');
    
    // Añade o quita la clase al body para animar el título
    if (gestion.classList.contains('collapsed')) {
        document.body.classList.add('left-collapsed');
        // Mostrar el botón flotante cuando el sidebar está cerrado
        if (toggleGestionBtn) {
            toggleGestionBtn.style.display = 'block';
            toggleGestionBtn.style.removeProperty('display');
        }
    } else {
        document.body.classList.remove('left-collapsed');
        // Ocultar el botón flotante cuando el sidebar está abierto
        if (toggleGestionBtn) {
            toggleGestionBtn.style.display = 'none';
            toggleGestionBtn.style.setProperty('display', 'none', 'important');
        }
    }

    // Actualiza las clases de body para las columnas
    actualizarEstadoColumnas(gestion, cart);
}

function toggleCarrito() {
    const cart = document.getElementById('cartSidebar');
    const gestion = document.getElementById('gestionSidebar');
    const showCartBtn = document.getElementById('showCartBtn');
    
    if (!cart) return;
    
    cart.classList.toggle('collapsed');
    
    // Manejar visibilidad del botón flotante
    if (showCartBtn) {
        if (cart.classList.contains('collapsed')) {
            showCartBtn.style.display = 'block';
        } else {
            showCartBtn.style.display = 'none';
        }
    }
    
    // Actualiza las clases de body para las columnas
    actualizarEstadoColumnas(gestion, cart);
}

function actualizarEstadoColumnas(gestion, cart) {
    if (!gestion || !cart) return;
    
    const leftClosed = gestion.classList.contains('collapsed');
    const rightClosed = cart.classList.contains('collapsed');
    
    // Limpiar clases anteriores
    document.body.classList.remove('sidebar-open', 'sidebar-closed', 'both-collapsed', 'right-collapsed');
    
    if (leftClosed && rightClosed) {
        document.body.classList.add('both-collapsed');
    } else if (leftClosed && !rightClosed) {
        document.body.classList.add('left-collapsed');
        document.body.classList.add('sidebar-closed');
    } else if (!leftClosed && rightClosed) {
        document.body.classList.add('right-collapsed');
        document.body.classList.add('sidebar-closed');
    } else {
        document.body.classList.add('sidebar-open');
    }
}

function inicializarSidebars() {
    // Configurar estado inicial de los sidebars
    const gestion = document.getElementById('gestionSidebar');
    const cart = document.getElementById('cartSidebar');
    const showCartBtn = document.getElementById('showCartBtn');
    const toggleGestionBtn = document.querySelector('.toggle-gestion-fixed');
    
    // Asegurar que el sidebar de gestión inicie abierto
    if (gestion) {
        gestion.classList.remove('collapsed');
        document.body.classList.remove('left-collapsed');
        
        // Forzar que el botón flotante esté oculto cuando el sidebar está abierto
        if (toggleGestionBtn) {
            toggleGestionBtn.style.display = 'none';
            toggleGestionBtn.style.setProperty('display', 'none', 'important');
        }
    }
    
    // Asegurar que el carrito también inicie abierto
    if (cart) {
        cart.classList.remove('collapsed');
        
        // Ocultar el botón flotante del carrito cuando está abierto
        if (showCartBtn) {
            showCartBtn.style.display = 'none';
        }
    }
    
    if (gestion && cart) {
        actualizarEstadoColumnas(gestion, cart);
    }
}

// Exportar funciones para uso global
window.sidebarManager = {
    toggleGestion,
    toggleCarrito,
    inicializarSidebars,
    actualizarEstadoColumnas
};
