// Módulo para el sistema de búsqueda de productos
let ordenOriginal = [];

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
    ordenOriginal = Array.from(productos);

    // Configurar eventos de búsqueda
    configurarEventosBusqueda(input, clearBtn, productos, menuContainer);

    // Estado inicial
    toggleClearButton("", clearBtn);
}

function configurarEventosBusqueda(input, clearBtn, productos, menuContainer) {
    // Eventos de búsqueda
    input.addEventListener("input", function () {
        filtrarProductos(this.value, productos, menuContainer);
        toggleClearButton(this.value, clearBtn);
    });

    input.addEventListener("keyup", function () {
        filtrarProductos(this.value, productos, menuContainer);
        toggleClearButton(this.value, clearBtn);
    });

    // Limpiar búsqueda al presionar Escape
    input.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            limpiarBusqueda(input, clearBtn, productos, menuContainer);
        }
    });

    // Botón para limpiar búsqueda
    if (clearBtn) {
        clearBtn.addEventListener("click", function () {
            limpiarBusqueda(input, clearBtn, productos, menuContainer);
        });
    }
}

function limpiarBusqueda(input, clearBtn, productos, menuContainer) {
    input.value = "";
    
    // Restaurar el orden original de los productos
    if (menuContainer && ordenOriginal.length > 0) {
        ordenOriginal.forEach(producto => {
            menuContainer.appendChild(producto);
        });
    }
    
    filtrarProductos("", productos, menuContainer);
    toggleClearButton("", clearBtn);
    input.focus();
}

function toggleClearButton(valor, clearBtn) {
    if (clearBtn) {
        clearBtn.style.display = valor.trim() ? "flex" : "none";
    }
}

function filtrarProductos(termino, productos, menuContainer) {
    const filtro = termino.toLowerCase().trim();
    let productosVisibles = 0;
    
    // Crear arrays para productos coincidentes y no coincidentes
    const productosCoincidentes = [];
    const productosNoCoincidentes = [];

    productos.forEach(function (producto) {
        const nombre = producto.dataset.nombre ? producto.dataset.nombre.toLowerCase() : "";
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
    reorganizarProductos(filtro, menuContainer, productosCoincidentes, productosNoCoincidentes);

    // Mostrar mensaje si no hay resultados
    mostrarEstadoBusqueda(productosVisibles, filtro);
}

function reorganizarProductos(filtro, menuContainer, productosCoincidentes, productosNoCoincidentes) {
    if (!menuContainer) return;

    if (filtro !== "") {
        // Primero agregar los productos coincidentes
        productosCoincidentes.forEach(producto => {
            menuContainer.appendChild(producto);
        });
        
        // Luego agregar los productos no coincidentes (ocultos)
        productosNoCoincidentes.forEach(producto => {
            menuContainer.appendChild(producto);
        });
    } else if (filtro === "" && ordenOriginal.length > 0) {
        // Si no hay filtro, restaurar el orden original
        ordenOriginal.forEach(producto => {
            menuContainer.appendChild(producto);
        });
    }
}

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

function buscarProducto(termino) {
    const input = document.getElementById("busqueda");
    if (input) {
        input.value = termino;
        const productos = document.querySelectorAll(".producto");
        const menuContainer = document.getElementById("menuProductos");
        filtrarProductos(termino, productos, menuContainer);
    }
}

// Exportar funciones para uso global
window.busquedaManager = {
    inicializarBusqueda,
    limpiarBusqueda,
    filtrarProductos,
    buscarProducto,
    mostrarEstadoBusqueda
};
