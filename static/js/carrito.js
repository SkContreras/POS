// Módulo para el manejo del carrito de compras
let carrito = [];

// Exponer carrito globalmente para que otros módulos puedan accederlo
window.carrito = carrito;

function agregarAlCarrito(id, nombre, precio) {
    // Verificar que el modal manager esté disponible antes de usarlo
    if (window.modalManager && window.modalManager.mostrarModalCantidad) {
        window.modalManager.mostrarModalCantidad(id, nombre, precio);
    } else {
        // Fallback: usar prompt si el modal no está disponible
        const cantidad = prompt(`¿Cuánto "${nombre}" quieres añadir al carrito?`, "1");
        if (cantidad && !isNaN(cantidad) && parseFloat(cantidad) > 0) {
            confirmarAgregarAlCarrito(id, nombre, precio, parseFloat(cantidad));
        }
    }
}

function confirmarAgregarAlCarrito(id, nombre, precio, cantidad) {
    if (isNaN(cantidad) || cantidad <= 0) return;
    
    // Buscar si el producto ya existe en el carrito
    const idx = carrito.findIndex(p => p.id === id);
    if (idx !== -1) {
        carrito[idx].cantidad += cantidad;
    } else {
        carrito.push({ id, nombre, precio: parseFloat(precio), cantidad });
    }
    
    actualizarCarrito();
}

function eliminarDelCarrito(idx) {
    carrito.splice(idx, 1);
    window.carrito = carrito; // Sincronizar con la referencia global
    actualizarCarrito();
}

function actualizarCarrito() {
    // Sincronizar con la referencia global
    window.carrito = carrito;
    
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

async function finalizarVenta() {
    const total = parseFloat(document.getElementById("total").textContent);
    if (total === 0) {
        if (window.mostrarConfirmacion) {
            await window.mostrarConfirmacion('advertencia', 
                'Carrito vacío',
                "🛒 El carrito está vacío<br><br>" + 
                "<span style='color: #666; font-size: 0.9rem;'>Agrega algunos productos antes de finalizar la venta</span>",
                { soloOk: true }
            );
        } else if (window.confirmacionManager) {
            await window.confirmacionManager.mostrarAdvertencia(
                "🛒 El carrito está vacío<br><br>" + 
                "<span style='color: #666; font-size: 0.9rem;'>Agrega algunos productos antes de finalizar la venta</span>"
            );
        } else {
            mostrarToastSeguro("🛒 El carrito está vacío.", "warning");
        }
        return;
    }

    // Mostrar confirmación elegante
    let confirmar = true;
    if (window.mostrarConfirmacion) {
        confirmar = await window.mostrarConfirmacion('venta',
            '¿Finalizar venta?',
            `¿Estás seguro de que quieres finalizar esta venta por un total de <strong>$${total.toFixed(2)}</strong>?<br><small>Esta acción registrará la venta en el sistema.</small>`,
            {
                textoConfirmar: 'Sí, finalizar venta',
                textoCancelar: 'Cancelar'
            }
        );
    } else if (window.confirmacionManager) {
        confirmar = await window.confirmacionManager.confirmarVenta(total.toFixed(2), carrito);
    } else {
        // Fallback simple como el de eliminar
        confirmar = confirm(`¿Estás seguro de que quieres finalizar esta venta por un total de $${total.toFixed(2)}?`);
    }

    if (!confirmar) return;

    try {
        const response = await fetch("/finalizar_venta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ carrito, total })
        });
        
        const data = await response.json();
        
        if (data.status === "ok") {
            // Mostrar éxito con modal elegante
            if (window.mostrarConfirmacion) {
                await window.mostrarConfirmacion('exito',
                    '¡Operación exitosa!',
                    `¡Venta finalizada con éxito!<br>Total: <strong>$${total.toFixed(2)}</strong>`,
                    { soloOk: true, textoOk: '¡Genial!' }
                );
            } else if (window.confirmacionManager) {
                await window.confirmacionManager.mostrarExito(
                    `¡Venta finalizada con éxito!<br>Total: <strong>$${total.toFixed(2)}</strong>`
                );
            } else {
                // Usar la nueva función de celebración completa
                if (window.celebracionManager && window.celebracionManager.celebrarVentaCompleta) {
                    window.celebracionManager.celebrarVentaCompleta(total.toFixed(2));
                } else if (window.toastManager && window.toastManager.celebrarVenta) {
                    window.toastManager.celebrarVenta(total.toFixed(2));
                } else {
                    mostrarToastSeguro("¡Venta guardada con éxito! 🎉", "success");
                }
            }
            carrito = [];
            window.carrito = carrito;
            actualizarCarrito();
            
            // Actualizar indicador de stock sin recargar toda la página
            setTimeout(() => {
                if (window.verificarStockBajo) {
                    window.verificarStockBajo();
                }
                // Solo recargar si es necesario (después de más tiempo)
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            }, 1000);
            
        } else if (data.status === "error") {
            // Manejar errores de stock
            if (window.mostrarConfirmacion) {
                await window.mostrarConfirmacion('error',
                    '❌ Error en la venta',
                    `<strong>No se pudo completar la venta:</strong><br>${data.message}`,
                    { soloOk: true, textoOk: 'Entendido' }
                );
            } else if (window.confirmacionManager) {
                await window.confirmacionManager.mostrarError(
                    `No se pudo completar la venta:<br>${data.message}`
                );
            } else {
                mostrarToastSeguro(`❌ ${data.message}`, "error");
            }
        } else {
            throw new Error('Error del servidor');
        }
    } catch (error) {
        console.error('Error al finalizar venta:', error);
        if (window.mostrarConfirmacion) {
            await window.mostrarConfirmacion('error',
                'Error',
                "Hubo un problema al procesar la venta. Por favor, intenta nuevamente.",
                { soloOk: true, textoOk: 'Entendido' }
            );
        } else if (window.confirmacionManager) {
            await window.confirmacionManager.mostrarError(
                "Hubo un problema al procesar la venta. Por favor, intenta nuevamente."
            );
        } else {
            mostrarToastSeguro("❌ Hubo un error al guardar.", "error");
        }
    }
}

// Función auxiliar para generar resumen del carrito
function generarResumenCarrito() {
    if (carrito.length === 0) return '';
    
    let resumen = '';
    let totalItems = 0;
    
    carrito.forEach(item => {
        totalItems += item.cantidad;
        const subtotal = (item.precio * item.cantidad).toFixed(2);
        resumen += `• ${item.nombre} x${item.cantidad} = $${subtotal}\n`;
    });
    
    return {
        items: resumen,
        totalItems: totalItems,
        resumenCompleto: `📦 ${totalItems} producto${totalItems > 1 ? 's' : ''} en el carrito\n\n${resumen}`
    };
}

// Función auxiliar para mostrar toast de forma segura
function mostrarToastSeguro(mensaje, tipo) {
    if (window.toastManager && window.toastManager.mostrarToast) {
        window.toastManager.mostrarToast(mensaje, tipo);
    } else {
        // Fallback: usar alert si no está disponible
        alert(mensaje);
    }
}

function vaciarCarrito() {
    carrito = [];
    window.carrito = carrito;
    actualizarCarrito();
}

function obtenerCarrito() {
    return carrito;
}

// Exportar funciones para uso global
window.carritoManager = {
    agregarAlCarrito,
    confirmarAgregarAlCarrito,
    eliminarDelCarrito,
    actualizarCarrito,
    finalizarVenta,
    vaciarCarrito,
    obtenerCarrito,
    generarResumenCarrito
};
