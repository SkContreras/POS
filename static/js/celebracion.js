// Módulo para efectos de celebración especiales
function crearEfectoConfeti() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ffa500', '#ff69b4'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        setTimeout(() => {
            createConfettiPiece();
        }, i * 50);
    }
}

function createConfettiPiece() {
    const confetti = document.createElement('div');
    confetti.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: ${getRandomColor()};
        top: -10px;
        left: ${Math.random() * 100}vw;
        z-index: 10001;
        pointer-events: none;
        border-radius: 50%;
        animation: confetti-fall ${Math.random() * 2 + 3}s linear forwards;
    `;
    
    document.body.appendChild(confetti);
    
    // Remover después de la animación
    setTimeout(() => {
        if (confetti.parentNode) {
            confetti.parentNode.removeChild(confetti);
        }
    }, 5000);
}

function getRandomColor() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ffa500', '#ff69b4'];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Función principal para celebrar una venta
function celebrarVentaCompleta(total) {
    // Mostrar toast mejorado
    if (window.toastManager && window.toastManager.celebrarVenta) {
        window.toastManager.celebrarVenta(total);
    }
    
    // Agregar efecto de confeti
    crearEfectoConfeti();
    
    // Efecto de vibración sutil (si el dispositivo lo soporta)
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }
}

// Agregar estilos CSS para las animaciones
function agregarEstilosCelebracion() {
    if (!document.getElementById('celebracion-styles')) {
        const styles = document.createElement('style');
        styles.id = 'celebracion-styles';
        styles.textContent = `
            @keyframes confetti-fall {
                0% {
                    transform: translateY(-10px) rotateZ(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) rotateZ(720deg);
                    opacity: 0;
                }
            }
            
            @keyframes pulse-celebration {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .celebration-pulse {
                animation: pulse-celebration 0.6s ease-in-out;
            }
        `;
        document.head.appendChild(styles);
    }
}

// Inicializar estilos cuando se carga el módulo
agregarEstilosCelebracion();

// Exportar funciones
window.celebracionManager = {
    celebrarVentaCompleta,
    crearEfectoConfeti
};
