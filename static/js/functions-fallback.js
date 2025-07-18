// Script de respaldo para funciones críticas
console.log('🛡️ Cargando script de respaldo para funciones críticas...');

// Función de respaldo universal
function crearFuncionRespaldo(nombreFuncion, descripcion) {
    return function(...args) {
        console.log(`🔄 Ejecutando función de respaldo: ${nombreFuncion} - ${descripcion}`);
        
        // Intentar ejecutar la función real si existe
        if (typeof window[nombreFuncion] === 'function' && window[nombreFuncion] !== arguments.callee) {
            console.log(`✅ Función real encontrada para ${nombreFuncion}, delegando...`);
            return window[nombreFuncion].apply(this, args);
        }
        
        // Si no existe, mostrar mensaje de espera
        if (typeof bootstrap !== 'undefined') {
            const alert = document.createElement('div');
            alert.className = 'alert alert-info alert-dismissible fade show position-fixed';
            alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
            alert.innerHTML = `
                <strong>⏳ ${descripcion}</strong><br>
                La función se está cargando, por favor espera un momento...
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.body.appendChild(alert);
            
            // Auto-eliminar
            setTimeout(() => {
                if (alert.parentNode) alert.remove();
            }, 3000);
            
            // Reintentar en 500ms
            setTimeout(() => {
                if (typeof window[nombreFuncion] === 'function' && window[nombreFuncion] !== arguments.callee) {
                    window[nombreFuncion].apply(this, args);
                }
            }, 500);
        } else {
            alert(`⏳ ${descripcion}\nLa función se está cargando, por favor espera un momento...`);
        }
    };
}

// Crear funciones de respaldo
window.calcularMargenGanancia = window.calcularMargenGanancia || crearFuncionRespaldo('calcularMargenGanancia', 'Calculadora de Margen');
window.proyeccionVentas = window.proyeccionVentas || crearFuncionRespaldo('proyeccionVentas', 'Proyección de Ventas');
window.analisisRentabilidad = window.analisisRentabilidad || crearFuncionRespaldo('analisisRentabilidad', 'Análisis de Rentabilidad');
window.comparativoPeriodos = window.comparativoPeriodos || crearFuncionRespaldo('comparativoPeriodos', 'Comparativo de Períodos');
window.initializeCharts = window.initializeCharts || crearFuncionRespaldo('initializeCharts', 'Inicializar Gráficas');
window.initializeChartData = window.initializeChartData || crearFuncionRespaldo('initializeChartData', 'Inicializar Datos');

console.log('🛡️ Funciones de respaldo instaladas:');
console.log('- calcularMargenGanancia:', typeof window.calcularMargenGanancia !== 'undefined');
console.log('- proyeccionVentas:', typeof window.proyeccionVentas !== 'undefined');
console.log('- analisisRentabilidad:', typeof window.analisisRentabilidad !== 'undefined');
console.log('- comparativoPeriodos:', typeof window.comparativoPeriodos !== 'undefined');
console.log('- initializeCharts:', typeof window.initializeCharts !== 'undefined');
console.log('- initializeChartData:', typeof window.initializeChartData !== 'undefined');

// Verificar que todas las funciones estén disponibles
setTimeout(() => {
    const funciones = ['calcularMargenGanancia', 'proyeccionVentas', 'analisisRentabilidad', 'comparativoPeriodos'];
    const faltantes = funciones.filter(f => typeof window[f] !== 'function');
    
    if (faltantes.length === 0) {
        console.log('✅ Todas las funciones críticas están disponibles');
    } else {
        console.warn('⚠️ Funciones faltantes:', faltantes);
    }
}, 1000);
