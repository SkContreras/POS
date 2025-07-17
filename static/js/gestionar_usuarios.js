/**
 * JavaScript para la página de gestión de usuarios
 * Maneja la creación de usuarios, cambio de credenciales y cambio de estado
 */

/**
 * Confirma la creación de un nuevo usuario
 * @returns {boolean} - true si el usuario confirma, false si cancela
 */
function confirmarCreacion() {
    const nombre = document.getElementById('nombre_completo').value;
    const usuario = document.getElementById('usuario').value;
    const rol = document.getElementById('rol').value;
    
    return confirm(`¿Crear usuario "${nombre}" con rol de ${rol}?`);
}

/**
 * Valida los datos del formulario de cambio de credenciales
 * @returns {Promise<boolean>} - true si la validación pasa y el usuario confirma
 */
async function validarCambioCredenciales() {
    const passwordActual = document.getElementById('password_actual').value;
    const nuevoUsuario = document.getElementById('nuevo_usuario').value.trim();
    const nuevaPassword = document.getElementById('nueva_password').value;
    const confirmarPassword = document.getElementById('confirmar_password').value;
    
    // Verificar que se ingresó la contraseña actual
    if (!passwordActual) {
        if (window.confirmacionManager) {
            await window.confirmacionManager.mostrarError('Debe ingresar su contraseña actual para confirmar los cambios');
        } else {
            alert('Debe ingresar su contraseña actual');
        }
        return false;
    }
    
    // Verificar que se especificó al menos un cambio
    if (!nuevoUsuario && !nuevaPassword) {
        if (window.confirmacionManager) {
            await window.confirmacionManager.mostrarAdvertencia('Debe especificar al menos un nuevo usuario o contraseña para actualizar');
        } else {
            alert('Debe especificar al menos un nuevo usuario o contraseña');
        }
        return false;
    }
    
    // Validar nueva contraseña si se especificó
    if (nuevaPassword) {
        if (nuevaPassword.length < 4) {
            if (window.confirmacionManager) {
                await window.confirmacionManager.mostrarError('La nueva contraseña debe tener al menos 4 caracteres');
            } else {
                alert('La nueva contraseña debe tener al menos 4 caracteres');
            }
            return false;
        }
        
        if (nuevaPassword !== confirmarPassword) {
            if (window.confirmacionManager) {
                await window.confirmacionManager.mostrarError('Las contraseñas no coinciden. Verifique que ambas sean idénticas');
            } else {
                alert('Las contraseñas no coinciden');
            }
            return false;
        }
    }
    
    // Validar nuevo usuario si se especificó
    if (nuevoUsuario && nuevoUsuario.length < 3) {
        if (window.confirmacionManager) {
            await window.confirmacionManager.mostrarError('El nuevo nombre de usuario debe tener al menos 3 caracteres');
        } else {
            alert('El nuevo nombre de usuario debe tener al menos 3 caracteres');
        }
        return false;
    }
    
    // Confirmar los cambios con modal estilizado
    let mensaje = '¿Está seguro de que desea actualizar ';
    let cambios = [];
    
    if (nuevoUsuario) {
        cambios.push('su nombre de usuario');
    }
    if (nuevaPassword) {
        cambios.push('su contraseña');
    }
    
    mensaje += cambios.join(' y ') + '?';
    
    if (nuevoUsuario) {
        mensaje += '<br><br><small style="color: #ff9800; font-weight: bold;">⚠️ Nota: Si cambia su nombre de usuario, deberá iniciar sesión nuevamente.</small>';
    }
    
    // Usar el sistema de confirmación estilizado si está disponible
    if (window.confirmacionManager) {
        const modal = await window.confirmacionManager.crearModal('advertencia',
            '🔑 Confirmar Cambio de Credenciales',
            mensaje,
            {
                textoConfirmar: '✅ Sí, actualizar credenciales',
                textoCancelar: '❌ Cancelar'
            }
        );
        
        // Aplicar estilo personalizado al modal
        setTimeout(() => {
            const modalElement = document.querySelector('.modal-confirmacion:last-child');
            if (modalElement) {
                modalElement.classList.add('modal-credenciales');
            }
        }, 50);
        
        return modal;
    } else {
        // Fallback para navegadores sin soporte
        return confirm(mensaje.replace(/<[^>]*>/g, ''));
    }
}

/**
 * Maneja el envío del formulario de cambio de credenciales de forma asíncrona
 * @param {Event} event - Evento del formulario
 * @returns {boolean} - Siempre false para prevenir envío automático
 */
async function manejarEnvioCredenciales(event) {
    event.preventDefault(); // Prevenir envío inmediato
    
    try {
        const confirmado = await validarCambioCredenciales();
        if (confirmado) {
            // Si se confirma, enviar el formulario
            event.target.submit();
        }
    } catch (error) {
        console.error('Error en validación:', error);
        if (window.confirmacionManager) {
            await window.confirmacionManager.mostrarError('Ocurrió un error durante la validación. Intente nuevamente.');
        } else {
            alert('Error durante la validación');
        }
    }
    
    return false; // Siempre prevenir el envío automático
}

/**
 * Confirma el cambio de estado de un usuario (activar/desactivar)
 * @param {string} usuario - Nombre del usuario
 * @param {boolean} estadoActual - Estado actual del usuario (true = activo, false = inactivo)
 * @returns {Promise<boolean>} - true si se confirma la acción
 */
async function confirmarCambioEstado(usuario, estadoActual) {
    const accion = estadoActual ? 'desactivar' : 'activar';
    let confirmar = false;
    
    if (window.confirmacionManager) {
        confirmar = await window.confirmacionManager.crearModal('advertencia',
            `${accion.charAt(0).toUpperCase() + accion.slice(1)} Usuario`,
            `¿Estás seguro de que quieres ${accion} al usuario "${usuario}"?`,
            {
                textoConfirmar: `Sí, ${accion}`,
                textoCancelar: 'Cancelar'
            }
        );
    } else {
        confirmar = confirm(`¿Estás seguro de que quieres ${accion} al usuario "${usuario}"?`);
    }
    
    if (!confirmar) return false;
    
    // Verificar contraseña del administrador
    try {
        await window.verificarAdmin(`Confirma tu contraseña para ${accion} al usuario "${usuario}":`);
        return true;
    } catch (error) {
        return false;
    }
}
