// Módulo para manejar confirmaciones y alertas personalizadas
function crearModal(tipo, titulo, mensaje, opciones = {}) {
    return new Promise((resolve) => {
        // Crear el overlay del modal
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            backdrop-filter: blur(3px);
        `;

        // Crear el contenedor del modal
        const modal = document.createElement('div');
        modal.className = `modal-confirmacion ${tipo}`;
        
        // Estilos base y específicos por tipo
        let borderColor = 'rgba(0, 123, 255, 0.2)';
        let gradientOverlay = '';
        
        if (tipo === 'advertencia') {
            borderColor = 'rgba(255, 152, 0, 0.3)';
            gradientOverlay = 'linear-gradient(135deg, rgba(255, 152, 0, 0.05), rgba(255, 193, 7, 0.02))';
        } else if (tipo === 'error') {
            borderColor = 'rgba(220, 53, 69, 0.3)';
            gradientOverlay = 'linear-gradient(135deg, rgba(220, 53, 69, 0.05), rgba(248, 113, 113, 0.02))';
        } else if (tipo === 'exito') {
            borderColor = 'rgba(40, 167, 69, 0.3)';
            gradientOverlay = 'linear-gradient(135deg, rgba(40, 167, 69, 0.05), rgba(72, 187, 120, 0.02))';
        }
        
        modal.style.cssText = `
            background: white;
            background-image: ${gradientOverlay};
            padding: 30px;
            border-radius: 15px;
            border: 2px solid ${borderColor};
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            width: 90%;
            text-align: center;
            transform: scale(0.7);
            opacity: 0;
            transition: all 0.3s ease;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        `;

        // Crear el icono según el tipo
        const iconos = {
            'confirmar': '❓',
            'eliminar': '🗑️',
            'editar': '✏️',
            'venta': '💰',
            'exito': '✅',
            'error': '❌',
            'advertencia': '⚠️',
            'info': 'ℹ️'
        };

        const icono = document.createElement('div');
        icono.className = 'icono';
        icono.style.cssText = `
            font-size: 4rem;
            margin-bottom: 20px;
            animation: ${tipo === 'advertencia' ? 'shake 0.5s ease-in-out, pulse 2s ease-in-out infinite 1s' : 'bounce 0.5s ease'};
            ${tipo === 'advertencia' ? 'color: #ff9800; text-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);' : ''}
        `;
        icono.textContent = iconos[tipo] || iconos['info'];

        // Crear el título
        const tituloElement = document.createElement('h3');
        tituloElement.style.cssText = `
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.4rem;
            font-weight: 600;
        `;
        tituloElement.textContent = titulo;

        // Crear el mensaje
        const mensajeElement = document.createElement('p');
        mensajeElement.style.cssText = `
            margin: 0 0 25px 0;
            color: #666;
            font-size: 1rem;
            line-height: 1.5;
        `;
        mensajeElement.innerHTML = mensaje;

        // Crear contenedor de botones
        const botonesContainer = document.createElement('div');
        botonesContainer.style.cssText = `
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        `;

        // Función para crear botones
        function crearBoton(texto, esAfirmativo = false, esCancelacion = false) {
            const boton = document.createElement('button');
            boton.textContent = texto;
            
            let colorBase = '#6c757d';
            if (esAfirmativo && tipo === 'eliminar') colorBase = '#dc3545';
            else if (esAfirmativo && tipo === 'editar') colorBase = '#28a745';
            else if (esAfirmativo && tipo === 'venta') colorBase = '#007bff';
            else if (esAfirmativo && tipo === 'advertencia') colorBase = '#ff9800';
            else if (esAfirmativo && tipo === 'exito') colorBase = '#28a745';
            else if (esAfirmativo && tipo === 'error') colorBase = '#dc3545';
            else if (esAfirmativo) colorBase = '#007bff';
            
            boton.style.cssText = `
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 100px;
                background: ${colorBase};
                color: white;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            `;

            // Efectos hover
            boton.addEventListener('mouseenter', () => {
                boton.style.transform = 'translateY(-2px)';
                boton.style.boxShadow = `0 8px 16px ${colorBase}40`;
            });

            boton.addEventListener('mouseleave', () => {
                boton.style.transform = 'translateY(0)';
                boton.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            });

            return boton;
        }

        // Determinar qué botones mostrar según el tipo
        if (opciones.soloOk || tipo === 'exito' || tipo === 'error' || tipo === 'info') {
            const botonOk = crearBoton(opciones.textoOk || 'Entendido', true);
            botonOk.onclick = () => {
                cerrarModal();
                resolve(true);
            };
            botonesContainer.appendChild(botonOk);
        } else {
            // Modal de confirmación con dos botones
            const botonCancelar = crearBoton(opciones.textoCancelar || 'Cancelar');
            botonCancelar.onclick = () => {
                cerrarModal();
                resolve(false);
            };

            const botonConfirmar = crearBoton(opciones.textoConfirmar || 'Confirmar', true);
            botonConfirmar.onclick = () => {
                cerrarModal();
                resolve(true);
            };

            botonesContainer.appendChild(botonCancelar);
            botonesContainer.appendChild(botonConfirmar);
        }

        // Función para cerrar modal
        function cerrarModal() {
            modal.style.transform = 'scale(0.7)';
            modal.style.opacity = '0';
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 300);
        }

        // Cerrar con ESC
        function manejarTecla(e) {
            if (e.key === 'Escape') {
                document.removeEventListener('keydown', manejarTecla);
                cerrarModal();
                resolve(false);
            }
        }
        document.addEventListener('keydown', manejarTecla);

        // Cerrar al hacer clic fuera (opcional)
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                cerrarModal();
                resolve(false);
            }
        };

        // Ensamblar el modal
        modal.appendChild(icono);
        modal.appendChild(tituloElement);
        modal.appendChild(mensajeElement);
        modal.appendChild(botonesContainer);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Animación de entrada
        setTimeout(() => {
            modal.style.transform = 'scale(1)';
            modal.style.opacity = '1';
        }, 10);

        // Agregar estilos de animación
        if (!document.getElementById('modal-styles')) {
            const styles = document.createElement('style');
            styles.id = 'modal-styles';
            styles.textContent = `
                @keyframes bounce {
                    0%, 20%, 53%, 80%, 100% { transform: translate3d(0,0,0); }
                    40%, 43% { transform: translate3d(0,-30px,0); }
                    70% { transform: translate3d(0,-15px,0); }
                    90% { transform: translate3d(0,-4px,0); }
                }
                
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
                    20%, 40%, 60%, 80% { transform: translateX(10px); }
                }
                
                @keyframes pulse {
                    0% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.8; transform: scale(1.05); }
                    100% { opacity: 1; transform: scale(1); }
                }
                
                .modal-confirmacion.advertencia .icono {
                    animation: shake 0.5s ease-in-out, pulse 2s ease-in-out infinite 1s;
                }
            `;
            document.head.appendChild(styles);
        }
    });
}

// Funciones específicas para diferentes tipos de confirmación
async function confirmarEliminar(nombreItem) {
    return await crearModal('eliminar', 
        '¿Eliminar producto?', 
        `¿Estás seguro de que quieres eliminar "<strong>${nombreItem}</strong>"?<br><small>Esta acción no se puede deshacer.</small>`,
        {
            textoConfirmar: 'Sí, eliminar',
            textoCancelar: 'Cancelar'
        }
    );
}

async function confirmarEdicion(nombreItem) {
    return await crearModal('editar',
        'Confirmar cambios',
        `¿Guardar los cambios realizados en "<strong>${nombreItem}</strong>"?`,
        {
            textoConfirmar: 'Guardar cambios',
            textoCancelar: 'Cancelar'
        }
    );
}

async function confirmarVenta(total, carrito = []) {
    return await crearModal('venta',
        '¿Finalizar venta?',
        `¿Estás seguro de que quieres finalizar esta venta por un total de <strong>$${total}</strong>?<br><small>Esta acción registrará la venta en el sistema.</small>`,
        {
            textoConfirmar: 'Sí, finalizar venta',
            textoCancelar: 'Cancelar'
        }
    );
}

async function mostrarExito(mensaje) {
    return await crearModal('exito',
        '¡Operación exitosa!',
        mensaje,
        { soloOk: true, textoOk: '¡Genial!' }
    );
}

async function mostrarError(mensaje) {
    return await crearModal('error',
        'Error',
        mensaje,
        { soloOk: true, textoOk: 'Entendido' }
    );
}

async function mostrarAdvertencia(mensaje) {
    return await crearModal('advertencia',
        '⚠️ Atención',
        mensaje,
        { soloOk: true, textoOk: '✅ De acuerdo' }
    );
}

async function mostrarInfo(titulo, mensaje) {
    return await crearModal('info',
        titulo,
        mensaje,
        { soloOk: true, textoOk: 'Entendido' }
    );
}

// Exportar funciones para uso global
window.confirmacionManager = {
    confirmarEliminar,
    confirmarEdicion,
    confirmarVenta,
    mostrarExito,
    mostrarError,
    mostrarAdvertencia,
    mostrarInfo,
    crearModal
};
