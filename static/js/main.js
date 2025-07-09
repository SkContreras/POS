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
        li.textContent = `${p.nombre} x${p.cantidad} - $${subtotal.toFixed(2)}`;
        // Botón eliminar
        const btn = document.createElement("button");
        btn.textContent = "Eliminar";
        btn.className = "carrito-eliminar-btn"; // <-- agrega la clase aquí
        btn.onclick = () => eliminarDelCarrito(idx);
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