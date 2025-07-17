let carrito = [];
let productoPendiente = null;

function agregarAlCarrito(id, nombre, precio) {
    // Mostrar modal personalizado
    productoPendiente = { id, nombre, precio };
    document.getElementById('modalTitle').textContent = `¿Cuánto "${nombre}" quieres añadir al carrito?`;
    document.getElementById('cantidadInput').value = 1;
    document.getElementById('cantidadModal').style.display = 'flex';
}

// Evento para confirmar cantidad
document.getElementById('confirmCantidadBtn').onclick = function() {
    const cantidad = parseFloat(document.getElementById('cantidadInput').value);
    if (isNaN(cantidad) || cantidad <= 0) return;
    const { id, nombre, precio } = productoPendiente;
    // Lógica original
    const idx = carrito.findIndex(p => p.id === id);
    if (idx !== -1) {
        carrito[idx].cantidad += cantidad;
    } else {
        carrito.push({ id, nombre, precio: parseFloat(precio), cantidad });
    }
    actualizarCarrito();
    document.getElementById('cantidadModal').style.display = 'none';
};

// Cerrar modal
document.getElementById('closeModal').onclick = function() {
    document.getElementById('cantidadModal').style.display = 'none';
};

// Opcional: cerrar modal al hacer click fuera
window.onclick = function(event) {
    const modal = document.getElementById('cantidadModal');
    if (event.target === modal) modal.style.display = 'none';
};

function eliminarDelCarrito(idx) {
    carrito.splice(idx, 1);
    actualizarCarrito();
}

function actualizarCarrito() {
    let total = 0;
    const lista = document.getElementById("carrito");
    lista.innerHTML = "";
    carrito.forEach((p, idx) => {
        const subtotal = p.precio * p.cantidad;
        total += subtotal;
        const li = document.createElement("li");
        
        // Crear contenedor para el texto del producto
        const textoProducto = document.createElement("span");
        textoProducto.className = "producto-texto";
        textoProducto.textContent = `${p.nombre} x${p.cantidad} - $${subtotal.toFixed(2)}`;
        
        // Botón eliminar
        const btn = document.createElement("button");
        btn.innerHTML = "🗑️";
        btn.className = "carrito-eliminar-btn";
        btn.title = "Eliminar del carrito";
        btn.onclick = () => eliminarDelCarrito(idx);
        
        li.appendChild(textoProducto);
        li.appendChild(btn);
        lista.appendChild(li);
    });
    document.getElementById("total").textContent = total.toFixed(2);
}

function mostrarToast(mensaje, tipo = "success") {
    const toast = document.getElementById("toast");

    // Limpiar clases anteriores
    toast.className = "";
    toast.classList.add("show", tipo);
    toast.textContent = mensaje;

    // Ocultar después de unos segundos
    setTimeout(() => {
        toast.classList.remove("show", tipo);
    }, 3500);
}


function finalizarVenta() {
    const total = parseFloat(document.getElementById("total").textContent);
    if (total === 0) {
        mostrarToast("🛒 El carrito está vacío.", "warning");
        return;
    }

    fetch("/finalizar_venta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ carrito, total })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "ok") {
            mostrarToast("¡Venta guardada con éxito! 🎉", "success");
            carrito = [];
            actualizarCarrito();
        } else {
            mostrarToast("❌ Hubo un error al guardar.", "error");
        }
    })
    .catch(() => {
        mostrarToast("⚠️ Error en la conexión.", "error");
    });
}



function toggleGestion() {
    const gestion = document.getElementById('gestionSidebar');
    gestion.classList.toggle('collapsed');
    // Añade o quita la clase al body para animar el título
    if (gestion.classList.contains('collapsed')) {
        document.body.classList.add('left-collapsed');
    } else {
        document.body.classList.remove('left-collapsed');
    }

    // --- NUEVO: Actualiza las clases de body para las columnas ---
    const cart = document.getElementById('cartSidebar');
    const leftClosed = gestion.classList.contains('collapsed');
    const rightClosed = cart.classList.contains('collapsed');
    if (leftClosed && rightClosed) {
        document.body.classList.add('both-collapsed');
        document.body.classList.remove('sidebar-open', 'sidebar-closed');
    } else if (leftClosed || rightClosed) {
        document.body.classList.add('sidebar-closed');
        document.body.classList.remove('sidebar-open', 'both-collapsed');
    } else {
        document.body.classList.add('sidebar-open');
        document.body.classList.remove('sidebar-closed', 'both-collapsed');
    }
}

document.querySelectorAll('.producto').forEach(producto => {
    producto.addEventListener('click', function() {
        // Animación
        this.classList.remove('bounce');
        void this.offsetWidth;
        this.classList.add('bounce');
        // Lógica de añadir al carrito
        const id = this.dataset.id;
        const nombre = this.dataset.nombre;
        const precio = this.dataset.precio;
        agregarAlCarrito(id, nombre, precio);
    });
});

// Función de búsqueda de productos en tiempo real
function inicializarBusqueda() {
    const input = document.getElementById("busqueda");
    const clearBtn = document.getElementById("clearSearch");
    const productos = document.querySelectorAll(".producto");
    const menuContainer = document.getElementById("menuProductos");

    if (!input || productos.length === 0) {
        console.warn("No se encontró el input de búsqueda o productos");
        return;
    }

    // Guardar el orden original de los productos
    const ordenOriginal = Array.from(productos);

    // Eventos de búsqueda
    input.addEventListener("input", function () {
        filtrarProductos(this.value, productos, menuContainer, ordenOriginal);
        toggleClearButton(this.value, clearBtn);
    });

    input.addEventListener("keyup", function () {
        filtrarProductos(this.value, productos, menuContainer, ordenOriginal);
        toggleClearButton(this.value, clearBtn);
    });

    // Limpiar búsqueda al presionar Escape
    input.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            limpiarBusqueda(input, clearBtn, productos, menuContainer, ordenOriginal);
        }
    });

    // Botón para limpiar búsqueda
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            limpiarBusqueda(input, clearBtn, productos, menuContainer, ordenOriginal);
        });
    }

    // Estado inicial
    toggleClearButton("", clearBtn);
}

// Función para limpiar búsqueda
function limpiarBusqueda(input, clearBtn, productos, menuContainer, ordenOriginal) {
    input.value = "";
    
    // Restaurar el orden original de los productos
    if (menuContainer && ordenOriginal) {
        ordenOriginal.forEach(producto => {
            menuContainer.appendChild(producto);
        });
    }
    
    filtrarProductos("", productos, menuContainer, ordenOriginal);
    toggleClearButton("", clearBtn);
    input.focus();
}

// Función para mostrar/ocultar botón de limpiar
function toggleClearButton(valor, clearBtn) {
    if (clearBtn) {
        clearBtn.style.display = valor.trim() ? "flex" : "none";
    }
}

// Función para filtrar productos
function filtrarProductos(termino, productos, menuContainer, ordenOriginal) {
    const filtro = termino.toLowerCase().trim();
    let productosVisibles = 0;
    
    // Crear arrays para productos coincidentes y no coincidentes
    const productosCoincidentes = [];
    const productosNoCoincidentes = [];

    productos.forEach(function (producto) {
        const nombre = producto.dataset.nombre.toLowerCase();
        const esVisible = filtro === "" || nombre.includes(filtro);
        
        if (esVisible) {
            producto.classList.remove("oculto");
            productosVisibles++;
            productosCoincidentes.push(producto);
        } else {
            producto.classList.add("oculto");
            productosNoCoincidentes.push(producto);
        }
    });

    // Reorganizar productos solo si hay un filtro activo
    if (filtro !== "" && menuContainer) {
        // Primero agregar los productos coincidentes
        productosCoincidentes.forEach(producto => {
            menuContainer.appendChild(producto);
        });
        
        // Luego agregar los productos no coincidentes (ocultos)
        productosNoCoincidentes.forEach(producto => {
            menuContainer.appendChild(producto);
        });
    } else if (filtro === "" && menuContainer && ordenOriginal) {
        // Si no hay filtro, restaurar el orden original
        ordenOriginal.forEach(producto => {
            menuContainer.appendChild(producto);
        });
    }

    // Mostrar mensaje si no hay resultados
    mostrarEstadoBusqueda(productosVisibles, filtro);
}

// Función para mostrar estado de búsqueda
function mostrarEstadoBusqueda(productosVisibles, termino) {
    let mensajeContainer = document.getElementById("mensajeBusqueda");
    
    // Crear el contenedor del mensaje si no existe
    if (!mensajeContainer) {
        mensajeContainer = document.createElement("div");
        mensajeContainer.id = "mensajeBusqueda";
        mensajeContainer.className = "mensaje-busqueda";
        const menu = document.getElementById("menuProductos");
        if (menu) {
            menu.parentNode.insertBefore(mensajeContainer, menu.nextSibling);
        }
    }

    if (termino && productosVisibles === 0) {
        mensajeContainer.innerHTML = `
            <div class="no-resultados">
                <span class="icono">🔍</span>
                <p>No se encontraron productos para "<strong>${termino}</strong>"</p>
                <small>Intenta con otro término de búsqueda</small>
            </div>
        `;
        mensajeContainer.style.display = "block";
    } else {
        mensajeContainer.style.display = "none";
    }
}

// Inicializar búsqueda cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function() {
    inicializarBusqueda();
});