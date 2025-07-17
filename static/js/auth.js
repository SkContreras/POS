/**
 * Sistema de autenticación para acciones críticas
 * Maneja la verificación de contraseña del administrador
 */

class AuthManager {
    constructor() {
        this.init();
    }

    init() {
        // Crear modal de verificación si no existe
        this.createAuthModal();
    }

    createAuthModal() {
        if (document.getElementById('authModal')) return;

        const modal = document.createElement('div');
        modal.id = 'authModal';
        modal.className = 'modal';
        modal.style.display = 'none';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 400px;">
                <div class="modal-header" style="background: #dc3545; color: white; padding: 15px; border-radius: 8px 8px 0 0;">
                    <h3 style="margin: 0; display: flex; align-items: center;">
                        🔐 Verificación de Administrador
                    </h3>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <p id="authMessage" style="margin-bottom: 15px; color: #666;">
                        Esta acción requiere confirmación del administrador.
                    </p>
                    <div class="form-group">
                        <label for="adminPassword" style="display: block; margin-bottom: 8px; font-weight: bold;">
                            Contraseña de Administrador:
                        </label>
                        <input type="password" 
                               id="adminPassword" 
                               placeholder="Ingresa tu contraseña"
                               style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 1rem;"
                               autocomplete="current-password">
                    </div>
                    <div id="authError" style="color: #dc3545; margin-top: 10px; display: none;"></div>
                </div>
                <div class="modal-footer" style="padding: 15px; text-align: right; border-top: 1px solid #eee;">
                    <button id="authCancel" class="btn btn-secondary" style="margin-right: 10px;">
                        Cancelar
                    </button>
                    <button id="authConfirm" class="btn btn-danger">
                        Confirmar Acción
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event listeners
        const passwordInput = document.getElementById('adminPassword');
        const confirmBtn = document.getElementById('authConfirm');
        const cancelBtn = document.getElementById('authCancel');

        // Permitir confirmar con Enter
        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                confirmBtn.click();
            }
        });

        // Botón cancelar
        cancelBtn.addEventListener('click', () => {
            this.hideAuthModal();
            if (this.currentReject) {
                this.currentReject(new Error('Acción cancelada por el usuario'));
            }
        });

        // Cerrar con click fuera del modal
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                cancelBtn.click();
            }
        });
    }

    /**
     * Solicita verificación de contraseña del administrador
     * @param {string} message - Mensaje personalizado para mostrar
     * @returns {Promise<boolean>} - Resuelve true si la contraseña es correcta
     */
    async verifyAdmin(message = null) {
        return new Promise((resolve, reject) => {
            this.currentResolve = resolve;
            this.currentReject = reject;

            const modal = document.getElementById('authModal');
            const messageEl = document.getElementById('authMessage');
            const passwordInput = document.getElementById('adminPassword');
            const confirmBtn = document.getElementById('authConfirm');
            const errorEl = document.getElementById('authError');

            // Configurar mensaje
            if (message) {
                messageEl.textContent = message;
            }

            // Limpiar campos
            passwordInput.value = '';
            errorEl.style.display = 'none';
            errorEl.textContent = '';

            // Mostrar modal
            modal.style.display = 'block';
            setTimeout(() => passwordInput.focus(), 100);

            // Configurar botón confirmar (remover listeners previos)
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
            
            newConfirmBtn.addEventListener('click', async () => {
                const password = passwordInput.value.trim();
                
                if (!password) {
                    this.showAuthError('Debes ingresar la contraseña');
                    return;
                }

                newConfirmBtn.disabled = true;
                newConfirmBtn.textContent = 'Verificando...';

                try {
                    const response = await fetch('/verificar_admin', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ password: password })
                    });

                    const data = await response.json();

                    if (data.success) {
                        this.hideAuthModal();
                        resolve(true);
                    } else {
                        this.showAuthError(data.message || 'Contraseña incorrecta');
                        newConfirmBtn.disabled = false;
                        newConfirmBtn.textContent = 'Confirmar Acción';
                        passwordInput.focus();
                        passwordInput.select();
                    }
                } catch (error) {
                    console.error('Error verificando administrador:', error);
                    this.showAuthError('Error de conexión. Intenta nuevamente.');
                    newConfirmBtn.disabled = false;
                    newConfirmBtn.textContent = 'Confirmar Acción';
                }
            });
        });
    }

    showAuthError(message) {
        const errorEl = document.getElementById('authError');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }

    hideAuthModal() {
        const modal = document.getElementById('authModal');
        modal.style.display = 'none';
    }

    /**
     * Wrapper para acciones que requieren verificación de administrador
     * @param {Function} action - Función a ejecutar después de verificar
     * @param {string} message - Mensaje de confirmación personalizado
     */
    async executeWithVerification(action, message = null) {
        try {
            await this.verifyAdmin(message);
            return await action();
        } catch (error) {
            if (error.message !== 'Acción cancelada por el usuario') {
                console.error('Error en verificación:', error);
                if (window.toastManager) {
                    window.toastManager.mostrar('Error en la verificación', 'error');
                }
            }
            throw error;
        }
    }
}

// Inicializar manager global
document.addEventListener('DOMContentLoaded', function() {
    window.authManager = new AuthManager();
});

// Función global de conveniencia
window.verificarAdmin = async function(message = null) {
    if (window.authManager) {
        return await window.authManager.verifyAdmin(message);
    }
    throw new Error('AuthManager no inicializado');
};

window.ejecutarConVerificacion = async function(action, message = null) {
    if (window.authManager) {
        return await window.authManager.executeWithVerification(action, message);
    }
    throw new Error('AuthManager no inicializado');
};
