// Módulo para el sistema de notificaciones toast mejorado
function mostrarToast(mensaje, tipo = "success", duracion = 3500) {
    const toast = document.getElementById("toast");
    
    if (!toast) {
        console.warn("Elemento toast no encontrado");
        return;
    }

    // Iconos por tipo
    const iconos = {
        success: "🎉",
        error: "❌", 
        warning: "⚠️",
        info: "ℹ️"
    };

    // Limpiar clases anteriores
    toast.className = "";
    
    // Crear contenido con icono
    const icono = iconos[tipo] || iconos["info"];
    toast.innerHTML = `
        <span style="font-size: 1.4rem; margin-right: 8px; display: inline-block;">${icono}</span>
        <span style="vertical-align: middle;">${mensaje}</span>
    `;
    
    // Aplicar clases
    toast.classList.add("show", tipo);

    // Remover clase hide si existía
    toast.classList.remove("hide");

    // Ocultar después de la duración especificada
    setTimeout(() => {
        toast.classList.add("hide");
        toast.classList.remove("show", tipo);
        
        // Limpiar completamente después de la animación
        setTimeout(() => {
            toast.classList.remove("hide");
            toast.innerHTML = "";
        }, 300);
    }, duracion);
}

function mostrarToastExito(mensaje, duracion = 3500) {
    mostrarToast(mensaje, "success", duracion);
}

function mostrarToastError(mensaje, duracion = 4000) {
    mostrarToast(mensaje, "error", duracion);
}

function mostrarToastAdvertencia(mensaje, duracion = 4000) {
    mostrarToast(mensaje, "warning", duracion);
}

function mostrarToastInfo(mensaje, duracion = 3000) {
    mostrarToast(mensaje, "info", duracion);
}

// Función especial para celebrar ventas
function celebrarVenta(total) {
    const mensajeCelebracion = `¡Venta finalizada con éxito por $${total}!`;
    mostrarToast(mensajeCelebracion, "success", 4000);
}

// Exportar funciones para uso global
window.toastManager = {
    mostrarToast,
    mostrarToastExito,
    mostrarToastError,
    mostrarToastAdvertencia,
    mostrarToastInfo,
    celebrarVenta
};
