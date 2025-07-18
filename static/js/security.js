/**
 * Sistema de Advertencias de Seguridad para POS
 * Detecta y advierte sobre condiciones inseguras
 */

class SecurityManager {
    constructor() {
        this.warnings = [];
        this.init();
    }

    init() {
        // Verificar condiciones de seguridad al cargar la página
        this.checkPasswordFieldsSecurity();
        this.checkHTTPSStatus();
        this.showWarningsIfNeeded();
    }

    /**
     * Verificar si hay campos de contraseña en una conexión insegura
     */
    checkPasswordFieldsSecurity() {
        const isHTTPS = window.location.protocol === 'https:';
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        if (!isHTTPS && passwordFields.length > 0) {
            this.addWarning('password-http', {
                type: 'error',
                title: '🔓 Conexión Insegura Detectada',
                message: 'Esta página contiene campos de contraseña pero está siendo servida a través de HTTP. Las credenciales pueden ser interceptadas.',
                details: 'Para mayor seguridad, el administrador debería configurar HTTPS.',
                showDetails: true
            });
        }
    }

    /**
     * Verificar el estado de HTTPS
     */
    checkHTTPSStatus() {
        const isHTTPS = window.location.protocol === 'https:';
        
        if (!isHTTPS) {
            // Verificar si es localhost o desarrollo
            const isLocalhost = window.location.hostname === 'localhost' || 
                              window.location.hostname === '127.0.0.1' || 
                              window.location.hostname.startsWith('192.168.');
            
            if (!isLocalhost) {
                this.addWarning('https-missing', {
                    type: 'warning',
                    title: '⚠️ Conexión HTTP',
                    message: 'Esta aplicación no está usando HTTPS. Los datos transmitidos no están cifrados.',
                    details: 'Se recomienda configurar HTTPS para proteger la información sensible.',
                    showDetails: false
                });
            }
        }
    }

    /**
     * Agregar una advertencia al sistema
     */
    addWarning(id, warning) {
        if (!this.warnings.find(w => w.id === id)) {
            this.warnings.push({ id, ...warning });
        }
    }

    /**
     * Mostrar advertencias si las hay
     */
    showWarningsIfNeeded() {
        if (this.warnings.length === 0) return;

        // Mostrar advertencias críticas primero
        const criticalWarnings = this.warnings.filter(w => w.type === 'error');
        const otherWarnings = this.warnings.filter(w => w.type !== 'error');

        [...criticalWarnings, ...otherWarnings].forEach((warning, index) => {
            setTimeout(() => this.showWarning(warning), index * 500);
        });
    }

    /**
     * Mostrar una advertencia individual
     */
    showWarning(warning) {
        // Si existe confirmacionManager, usar modal estilizado
        if (window.confirmacionManager) {
            this.showStyledWarning(warning);
        } else {
            // Fallback a alerta del navegador
            this.showBrowserWarning(warning);
        }
    }

    /**
     * Mostrar advertencia usando el sistema de modales estilizado
     */
    async showStyledWarning(warning) {
        const detailsHtml = warning.showDetails && warning.details ? 
            `<br><br><small><strong>Detalles:</strong> ${warning.details}</small>` : '';

        await window.confirmacionManager.crearModal(
            warning.type,
            warning.title,
            warning.message + detailsHtml,
            {
                textoConfirmar: '✅ Entendido',
                textoCancelar: null, // Solo botón de confirmar
                soloConfirmar: true
            }
        );
    }

    /**
     * Mostrar advertencia usando alert del navegador (fallback)
     */
    showBrowserWarning(warning) {
        const message = `${warning.title}\n\n${warning.message}`;
        const details = warning.showDetails && warning.details ? `\n\nDetalles: ${warning.details}` : '';
        alert(message + details);
    }

    /**
     * Crear banner de advertencia persistente para advertencias críticas
     */
    createSecurityBanner(warning) {
        // Verificar si ya existe un banner
        if (document.getElementById('security-banner')) return;

        const banner = document.createElement('div');
        banner.id = 'security-banner';
        banner.className = `security-banner ${warning.type}`;
        banner.innerHTML = `
            <div class="security-banner-content">
                <span class="security-banner-icon">${warning.type === 'error' ? '🔓' : '⚠️'}</span>
                <span class="security-banner-text">
                    <strong>${warning.title}</strong>
                    <br><small>${warning.message}</small>
                </span>
                <button class="security-banner-close" onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;

        // Agregar estilos si no existen
        this.addBannerStyles();

        // Insertar al inicio del body
        document.body.insertBefore(banner, document.body.firstChild);

        // Auto-remover después de 10 segundos para warnings no críticos
        if (warning.type !== 'error') {
            setTimeout(() => {
                if (banner.parentNode) banner.remove();
            }, 10000);
        }
    }

    /**
     * Agregar estilos CSS para el banner de seguridad
     */
    addBannerStyles() {
        if (document.getElementById('security-banner-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'security-banner-styles';
        styles.textContent = `
            .security-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 10000;
                padding: 10px 15px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                animation: slideDown 0.3s ease-out;
            }
            
            .security-banner.error {
                background: linear-gradient(135deg, #dc3545, #c82333);
                color: white;
            }
            
            .security-banner.warning {
                background: linear-gradient(135deg, #ffc107, #e0a800);
                color: #212529;
            }
            
            .security-banner-content {
                display: flex;
                align-items: center;
                max-width: 1200px;
                margin: 0 auto;
                gap: 10px;
            }
            
            .security-banner-icon {
                font-size: 18px;
                flex-shrink: 0;
            }
            
            .security-banner-text {
                flex: 1;
                line-height: 1.3;
            }
            
            .security-banner-close {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: inherit;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                cursor: pointer;
                font-weight: bold;
                flex-shrink: 0;
            }
            
            .security-banner-close:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            
            @keyframes slideDown {
                from { transform: translateY(-100%); }
                to { transform: translateY(0); }
            }
            
            /* Ajustar el margen del contenido principal cuando hay banner */
            body:has(.security-banner) .container {
                margin-top: 110px !important;
            }
        `;
        
        document.head.appendChild(styles);
    }

    /**
     * Verificar la seguridad de formularios específicos
     */
    checkFormSecurity(formElement) {
        const isHTTPS = window.location.protocol === 'https:';
        const passwordFields = formElement.querySelectorAll('input[type="password"]');
        
        if (!isHTTPS && passwordFields.length > 0) {
            return {
                secure: false,
                warnings: ['password-fields-http']
            };
        }
        
        return { secure: true, warnings: [] };
    }
}

// Inicializar el gestor de seguridad cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    window.securityManager = new SecurityManager();
});

// Exportar para uso global
window.SecurityManager = SecurityManager;
