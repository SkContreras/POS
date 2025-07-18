// Módulo para cerrar pestañas del navegador de manera cross-browser
// Implementa múltiples técnicas para maximizar la compatibilidad

/**
 * Intenta cerrar la pestaña actual usando múltiples técnicas
 * @param {string} fallbackUrl - URL a la que redirigir si no se puede cerrar
 * @param {Object} options - Opciones de configuración
 */
function cerrarPestana(fallbackUrl = '/login', options = {}) {
    const {
        intentos = 5,
        delayEntreTentativos = 200,
        mostrarMensaje = true,
        delayMensaje = 2000,
        autoRedirect = true,
        tiempoRedirect = 5000
    } = options;

    // Disparar evento personalizado antes del cierre
    try {
        const evento = new CustomEvent('appClosing', {
            detail: { reason: 'shutdown', fallbackUrl }
        });
        window.dispatchEvent(evento);
    } catch (e) {
        console.log('No se pudo disparar evento appClosing:', e);
    }

    let intentoActual = 0;
    let cerradoExitoso = false;

    function intentarCerrar() {
        if (cerradoExitoso || intentoActual >= intentos) {
            // Si no se pudo cerrar, mostrar mensaje y redirigir
            if (!cerradoExitoso && mostrarMensaje) {
                mostrarMensajeCierre(fallbackUrl, autoRedirect, tiempoRedirect);
            }
            return;
        }

        const tecnicas = [
            // Técnica 1: window.close() directo
            () => {
                window.close();
                return window.closed;
            },
            
            // Técnica 2: Para PWAs - usar location.replace con about:blank
            () => {
                if (esPWA) {
                    window.location.replace('about:blank');
                    setTimeout(() => window.close(), 100);
                }
                return esPWA;
            },
            
            // Técnica 3: Usar window.open con self-replace
            () => {
                const self = window.open('', '_self');
                self.close();
                return self.closed;
            },
            
            // Técnica 4: Para móviles - intentar enviar a la app nativa
            () => {
                if (esMovil) {
                    try {
                        window.location.href = 'intent://close/#Intent;scheme=close;end';
                        setTimeout(() => window.close(), 200);
                    } catch (e) {
                        // Ignorar errores en móviles
                    }
                }
                return false;
            },
            
            // Técnica 5: Location replace + close
            () => {
                window.location.replace('about:blank');
                setTimeout(() => window.close(), 50);
                return false; // No podemos verificar inmediatamente
            },
            
            // Técnica 6: History manipulation
            () => {
                if (window.history.length > 1) {
                    window.history.back();
                    setTimeout(() => window.close(), 100);
                }
                return false;
            },
            
            // Técnica 7: Para PWAs y aplicaciones web
            () => {
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.getRegistrations().then(registrations => {
                        registrations.forEach(registration => registration.unregister());
                    });
                }
                window.close();
                return window.closed;
            }
        ];

        try {
            const tecnica = tecnicas[intentoActual % tecnicas.length];
            if (tecnica && tecnica()) {
                cerradoExitoso = true;
                return;
            }
        } catch (error) {
            console.log(`Técnica ${intentoActual + 1} falló:`, error);
        }

        intentoActual++;
        setTimeout(intentarCerrar, delayEntreTentativos);
    }

    // Comenzar intentos después de un pequeño delay
    setTimeout(intentarCerrar, 100);
}

/**
 * Muestra mensaje de cierre cuando no se puede cerrar automáticamente
 */
function mostrarMensajeCierre(fallbackUrl, autoRedirect, tiempoRedirect) {
    setTimeout(() => {
        const esCerrarTienda = fallbackUrl && fallbackUrl.includes('login');
        const emoji = esCerrarTienda ? '🏪' : '🚪';
        const accion = esCerrarTienda ? 'Tienda y sesión cerradas' : 'Sesión cerrada';
        
        if (window.confirmacionManager) {
            window.confirmacionManager.mostrarExito(
                `${emoji} ${accion} correctamente.<br><br>` +
                '💡 <strong>Puedes cerrar esta pestaña manualmente</strong><br>' +
                `<small>📱 En móvil: usa el botón de cerrar de tu navegador<br>` +
                `🖥️ En escritorio: presiona Ctrl+W o ⌘+W<br>` +
                `${autoRedirect ? `O serás redirigido en ${tiempoRedirect/1000} segundos` : 'O serás redirigido pronto'}</small>`
            ).then(() => {
                if (autoRedirect) {
                    setTimeout(() => {
                        window.location.href = fallbackUrl;
                    }, tiempoRedirect);
                }
            });
        } else if (window.toastManager) {
            window.toastManager.mostrar(
                `${emoji} ${accion}. Puedes cerrar esta pestaña manualmente.`,
                'success',
                6000
            );
            if (autoRedirect) {
                setTimeout(() => {
                    window.location.href = fallbackUrl;
                }, tiempoRedirect);
            }
        } else {
            alert(`${emoji} ${accion} correctamente. Puedes cerrar esta pestaña manualmente.`);
            if (autoRedirect) {
                setTimeout(() => {
                    window.location.href = fallbackUrl;
                }, tiempoRedirect);
            }
        }
    }, 200);
}

/**
 * Cierra la pestaña específicamente al cerrar la tienda
 */
function cerrarPestanaTienda(redirectUrl) {
    cerrarPestana(redirectUrl, {
        intentos: 3,
        delayEntreTentativos: 300,
        mostrarMensaje: true,
        delayMensaje: 1500,
        autoRedirect: true,
        tiempoRedirect: 5000
    });
}

/**
 * Cierra la pestaña al hacer logout (más agresivo)
 */
function cerrarPestanaLogout(redirectUrl) {
    cerrarPestana(redirectUrl, {
        intentos: 2,
        delayEntreTentativos: 100,
        mostrarMensaje: false,
        autoRedirect: true,
        tiempoRedirect: 2000
    });
}

/**
 * Versión simple para compatibilidad con código existente
 */
function cerrarPestanaConFallback(redirectUrl) {
    cerrarPestanaTienda(redirectUrl);
}

// Detectar si la pestaña fue abierta por JavaScript (más fácil de cerrar)
let pestanaAbieraPorJS = false;
let esPWA = false;
let esMovil = false;

try {
    pestanaAbieraPorJS = window.opener !== null || window.history.length <= 1;
    
    // Detectar PWA
    esPWA = window.matchMedia && window.matchMedia('(display-mode: standalone)').matches ||
            window.navigator.standalone === true ||
            document.referrer.includes('android-app://');
    
    // Detectar móvil
    esMovil = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
} catch (e) {
    // En caso de error, usar valores por defecto
    console.log('Error detectando características del navegador:', e);
}

// Exportar funciones para uso global
window.tabCloser = {
    cerrarPestana,
    cerrarPestanaTienda,
    cerrarPestanaLogout,
    cerrarPestanaConFallback,
    pestanaAbieraPorJS,
    esPWA,
    esMovil
};

// Mantener compatibilidad con código existente
window.cerrarPestanaConFallback = cerrarPestanaConFallback;

// Información de debug
if (window.POS_CONFIG && window.POS_CONFIG.DEBUG && window.POS_CONFIG.DEBUG.LOGS_HABILITADOS) {
    console.log('[TabCloser] Módulo cargado.');
    console.log('[TabCloser] Pestaña abierta por JS:', pestanaAbieraPorJS);
    console.log('[TabCloser] Es PWA:', esPWA);
    console.log('[TabCloser] Es móvil:', esMovil);
}

// Configurar listener para intentos de cierre manual
let cierreManualEnProgreso = false;

// Agregar listener para detectar cuando la aplicación se está cerrando
window.addEventListener('appClosing', function(e) {
    cierreManualEnProgreso = true;
    
    // Log del cierre si está habilitado
    if (window.POS_CONFIG && window.POS_CONFIG.DEBUG && window.POS_CONFIG.DEBUG.LOGS_HABILITADOS) {
        console.log('[TabCloser] Cerrando aplicación:', e.detail);
    }
});

// Listener para beforeunload - ayuda con algunos navegadores
window.addEventListener('beforeunload', function(e) {
    if (cierreManualEnProgreso) {
        // Si estamos cerrando intencionalmente, no mostrar confirmación
        return;
    }
});
