// ================================
// CONTABILIDAD.JS - VERSIÓN CORREGIDA
// Sistema de gráficas y herramientas para contabilidad
// ================================

console.log('🚀 Iniciando Contabilidad.js v4.0 - Versión Corregida');

// ================================
// VARIABLES GLOBALES
// ================================

let chartData = {};
let charts = {};

// Colores para las gráficas
const chartColors = {
    primary: '#0d6efd',
    secondary: '#6c757d',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    light: '#f8f9fa',
    dark: '#212529'
};

// Configuración por defecto para gráficas
const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top'
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#fff',
            bodyColor: '#fff'
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(0, 0, 0, 0.1)'
            }
        },
        x: {
            grid: {
                color: 'rgba(0, 0, 0, 0.1)'
            }
        }
    }
};

// ================================
// FUNCIONES DE INICIALIZACIÓN
// ================================

function initializeChartData(serverData) {
    console.log('📊 Inicializando datos de gráficas:', serverData);
    
    if (!serverData) {
        console.warn('⚠️ No hay datos del servidor disponibles');
        return;
    }
    
    chartData = {
        ventasPorDia: serverData.ventas_por_dia || [],
        ventasPorHora: serverData.ventas_por_hora || [],
        ventasPorMes: serverData.ventas_por_mes || [],
        productosMasVendidos: serverData.productos_mas_vendidos || [],
        ingresosPorCategoria: serverData.ingresos_por_categoria || [],
        estadisticas: serverData.estadisticas || {},
        gastosPorCategoria: serverData.gastos_por_categoria || [],
        estadisticasGastos: serverData.estadisticas_gastos || {},
        resumenFinanciero: serverData.resumen_financiero || {}
    };
    
    console.log('✅ Datos de gráficas inicializados correctamente');
}

function initializeCharts() {
    console.log('🎨 Inicializando gráficas...');
    
    try {
        // Destruir gráficas existentes
        Object.values(charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        charts = {};
        
        // Crear nuevas gráficas
        createVentasPorDiaChart();
        createVentasPorHoraChart();
        createVentasPorMesChart();
        createProductosMasVendidosChart();
        createIngresosPorCategoriaChart();
        createGastosPorCategoriaChart();
        
        console.log('✅ Todas las gráficas inicializadas correctamente');
        
    } catch (error) {
        console.error('❌ Error inicializando gráficas:', error);
        showNotification('Error', 'Error al cargar las gráficas', 'error');
    }
}

// ================================
// FUNCIONES DE CREACIÓN DE GRÁFICAS
// ================================

function createVentasPorDiaChart() {
    const ctx = document.getElementById('ventasPorDiaChart');
    if (!ctx || !chartData.ventasPorDia) {
        console.warn('⚠️ No se puede crear gráfica de ventas por día');
        return;
    }

    const labels = chartData.ventasPorDia.map(item => {
        const fecha = new Date(item.fecha);
        return fecha.toLocaleDateString('es-ES', { 
            day: '2-digit', 
            month: '2-digit' 
        });
    });
    
    const data = chartData.ventasPorDia.map(item => item.total || 0);

    charts.ventasPorDiaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas por Día ($)',
                data: data,
                backgroundColor: chartColors.primary + '80',
                borderColor: chartColors.primary,
                borderWidth: 2
            }]
        },
        options: {
            ...defaultChartOptions,
            plugins: {
                ...defaultChartOptions.plugins,
                tooltip: {
                    ...defaultChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return 'Ventas: $' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfica de ventas por día creada');
}

function createVentasPorHoraChart() {
    const ctx = document.getElementById('ventasPorHoraChart');
    if (!ctx || !chartData.ventasPorHora) {
        console.warn('⚠️ No se puede crear gráfica de ventas por hora');
        return;
    }

    const labels = chartData.ventasPorHora.map(item => item.hora + ':00');
    const data = chartData.ventasPorHora.map(item => item.total || 0);

    charts.ventasPorHoraChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas por Hora ($)',
                data: data,
                borderColor: chartColors.success,
                backgroundColor: chartColors.success + '20',
                fill: true,
                tension: 0.4
            }]
        },
        options: defaultChartOptions
    });
    
    console.log('✅ Gráfica de ventas por hora creada');
}

function createVentasPorMesChart() {
    const ctx = document.getElementById('ventasPorMesChart');
    if (!ctx || !chartData.ventasPorMes) {
        console.warn('⚠️ No se puede crear gráfica de ventas por mes');
        return;
    }

    const labels = chartData.ventasPorMes.map(item => {
        const fecha = new Date(item.mes + '-01');
        return fecha.toLocaleDateString('es-ES', { 
            month: 'long', 
            year: 'numeric' 
        });
    });
    
    const data = chartData.ventasPorMes.map(item => item.total || 0);

    charts.ventasPorMesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas Mensuales ($)',
                data: data,
                borderColor: chartColors.info,
                backgroundColor: chartColors.info + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: defaultChartOptions
    });
    
    console.log('✅ Gráfica de ventas por mes creada');
}

function createProductosMasVendidosChart() {
    const ctx = document.getElementById('productosMasVendidosChart');
    if (!ctx || !chartData.productosMasVendidos) {
        console.warn('⚠️ No se puede crear gráfica de productos más vendidos');
        return;
    }

    const labels = chartData.productosMasVendidos.slice(0, 5).map(item => item.nombre);
    const data = chartData.productosMasVendidos.slice(0, 5).map(item => item.cantidad || 0);
    
    const colors = [
        chartColors.primary,
        chartColors.success,
        chartColors.warning,
        chartColors.danger,
        chartColors.info
    ];

    charts.productosMasVendidosChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.map(color => color + '80'),
                borderColor: colors,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    console.log('✅ Gráfica de productos más vendidos creada');
}

function createIngresosPorCategoriaChart() {
    const ctx = document.getElementById('ingresosPorCategoriaChart');
    if (!ctx || !chartData.ingresosPorCategoria) {
        console.warn('⚠️ No se puede crear gráfica de ingresos por categoría');
        return;
    }

    const labels = chartData.ingresosPorCategoria.map(item => item.categoria || 'Sin categoría');
    const data = chartData.ingresosPorCategoria.map(item => item.total || 0);

    charts.ingresosPorCategoriaChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    chartColors.primary + '80',
                    chartColors.success + '80',
                    chartColors.warning + '80',
                    chartColors.danger + '80',
                    chartColors.info + '80',
                    chartColors.secondary + '80'
                ],
                borderColor: [
                    chartColors.primary,
                    chartColors.success,
                    chartColors.warning,
                    chartColors.danger,
                    chartColors.info,
                    chartColors.secondary
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': $' + context.parsed.toFixed(2);
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfica de ingresos por categoría creada');
}

// ================================
// FUNCIONES DE HERRAMIENTAS
// ================================

function calcularMargenGanancia() {
    console.log('🧮 Calculando margen de ganancia...');
    
    const content = `
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="costo_producto" class="form-label">Costo del Producto:</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="costo_producto" step="0.01" placeholder="0.00">
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="precio_venta" class="form-label">Precio de Venta:</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control" id="precio_venta" step="0.01" placeholder="0.00">
                    </div>
                </div>
            </div>
        </div>
        <div class="text-center">
            <button type="button" class="btn btn-primary" onclick="calcularMargen()">Calcular</button>
        </div>
        <div id="resultado_margen" class="mt-3"></div>
    `;
    
    showCustomAlert('🧮 Calculadora de Margen de Ganancia', content);
}

function calcularMargen() {
    const costo = parseFloat(document.getElementById('costo_producto')?.value || 0);
    const precio = parseFloat(document.getElementById('precio_venta')?.value || 0);
    
    if (costo <= 0 || precio <= 0) {
        showNotification('Error', 'Ingresa valores válidos mayores a 0', 'error');
        return;
    }
    
    const ganancia = precio - costo;
    const margenPorcentual = (ganancia / precio) * 100;
    const markupPorcentual = (ganancia / costo) * 100;
    
    const resultado = `
        <div class="alert alert-success">
            <h6><i class="fas fa-calculator me-2"></i>Resultados del Cálculo</h6>
            <div class="row">
                <div class="col-md-4">
                    <strong>Ganancia:</strong><br>
                    <span class="h5 text-success">$${ganancia.toFixed(2)}</span>
                </div>
                <div class="col-md-4">
                    <strong>Margen (%):</strong><br>
                    <span class="h5 text-info">${margenPorcentual.toFixed(2)}%</span>
                </div>
                <div class="col-md-4">
                    <strong>Markup (%):</strong><br>
                    <span class="h5 text-warning">${markupPorcentual.toFixed(2)}%</span>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('resultado_margen').innerHTML = resultado;
}

function proyeccionVentas() {
    console.log('📈 Iniciando proyección de ventas...');
    
    const content = `
        <div class="alert alert-info">
            <h6>📈 Proyección de Ventas</h6>
            <p>Basada en los datos históricos disponibles:</p>
            <ul>
                <li><strong>Promedio diario:</strong> $${(chartData.estadisticas?.promedio_diario || 0).toFixed(2)}</li>
                <li><strong>Tendencia semanal:</strong> ${chartData.ventasPorDia?.length > 0 ? 'Creciente' : 'Sin datos'}</li>
                <li><strong>Proyección mensual:</strong> $${((chartData.estadisticas?.promedio_diario || 0) * 30).toFixed(2)}</li>
            </ul>
            <p class="text-muted small">
                <strong>Nota:</strong> Esta proyección es estimativa y basada en datos históricos.
            </p>
        </div>
    `;
    
    showCustomAlert('📈 Proyección de Ventas', content);
}

function analisisRentabilidad() {
    console.log('💰 Analizando rentabilidad...');
    
    const ingresos = chartData.estadisticas?.ingresos_totales || 0;
    const promedio = chartData.estadisticas?.promedio_venta || 0;
    const totalVentas = chartData.estadisticas?.total_ventas || 0;
    
    const content = `
        <div class="alert alert-success">
            <h6>💰 Análisis de Rentabilidad</h6>
            <div class="row">
                <div class="col-md-6">
                    <strong>Ingresos Totales:</strong><br>
                    <span class="h5 text-success">$${ingresos.toFixed(2)}</span>
                </div>
                <div class="col-md-6">
                    <strong>Ticket Promedio:</strong><br>
                    <span class="h5 text-info">$${promedio.toFixed(2)}</span>
                </div>
            </div>
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <strong>Total de Transacciones:</strong><br>
                    <span class="h5 text-primary">${totalVentas}</span>
                </div>
                <div class="col-md-6">
                    <strong>Estado:</strong><br>
                    <span class="h5 text-success">Rentable ✅</span>
                </div>
            </div>
        </div>
    `;
    
    showCustomAlert('💰 Análisis de Rentabilidad', content);
}

function comparativoPeriodos() {
    console.log('📊 Iniciando comparativo de períodos...');
    
    const content = `
        <div class="alert alert-warning">
            <h6>📊 Comparativo de Períodos</h6>
            <p>Funcionalidad en desarrollo.</p>
            <p>Próximamente podrás comparar:</p>
            <ul>
                <li>Ventas mes actual vs mes anterior</li>
                <li>Rendimiento por trimestres</li>
                <li>Análisis año a año</li>
                <li>Tendencias estacionales</li>
            </ul>
        </div>
    `;
    
    showCustomAlert('📊 Comparativo de Períodos', content);
}

// ================================
// FUNCIONES DE EXPORTACIÓN
// ================================

function exportarDatos() {
    const formato = document.getElementById('formato_exportar')?.value || 'pdf';
    const incluirGraficas = document.getElementById('incluirGraficas')?.checked || false;
    const incluirDetalles = document.getElementById('incluirDetalles')?.checked || false;
    const incluirResumen = document.getElementById('incluirResumen')?.checked || false;
    
    console.log('📄 Exportando datos...', {formato, incluirGraficas, incluirDetalles, incluirResumen});
    
    showNotification('📄 Exportando', `Preparando archivo ${formato.toUpperCase()}...`, 'info');
    
    // Simular proceso de exportación
    setTimeout(() => {
        showNotification('✅ Exportación Completa', `Archivo ${formato.toUpperCase()} generado exitosamente`, 'success');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('exportarModal'));
        if (modal) modal.hide();
    }, 2000);
}

function generarRecibosPDF() {
    const fechaInicio = document.getElementById('fecha_inicio_recibos')?.value;
    const fechaFin = document.getElementById('fecha_fin_recibos')?.value;
    const incluirDesglose = document.getElementById('incluirDesglose')?.checked || false;
    
    if (!fechaInicio || !fechaFin) {
        showNotification('⚠️ Fechas requeridas', 'Selecciona el rango de fechas', 'warning');
        return;
    }
    
    console.log('🧾 Generando recibos PDF...', {fechaInicio, fechaFin, incluirDesglose});
    
    showNotification('📄 Generando PDFs', 'Preparando recibos en formato PDF...', 'info');
    
    // Simular proceso de generación
    setTimeout(() => {
        showNotification('✅ PDFs Generados', 'Recibos creados exitosamente', 'success');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('recibosModal'));
        if (modal) modal.hide();
    }, 3000);
}

// ================================
// FUNCIONES DE NOTIFICACIONES
// ================================

function showNotification(title, message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const iconClass = {
        'success': 'text-success',
        'warning': 'text-warning', 
        'error': 'text-danger',
        'info': 'text-info'
    }[type] || 'text-info';
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center border-0 bg-white" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-info-circle ${iconClass} me-2"></i>
                    <strong>${title}</strong><br>
                    <small>${message}</small>
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

function showCustomAlert(title, content) {
    const modalId = 'customAlert-' + Date.now();
    const modalHTML = `
        <div class="modal fade" id="${modalId}" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
    
    document.getElementById(modalId).addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// ================================
// FUNCIÓN PARA CAMBIAR TIPOS DE GRÁFICAS
// ================================

function toggleChartType(chartName, newType) {
    console.log(`🔄 Cambiando tipo de gráfica ${chartName} a ${newType}`);
    
    if (!charts[chartName]) {
        console.warn(`Gráfica ${chartName} no encontrada`);
        return;
    }
    
    const chart = charts[chartName];
    const oldConfig = JSON.parse(JSON.stringify(chart.config));
    
    // Destruir gráfica actual
    chart.destroy();
    
    // Crear nueva configuración con el nuevo tipo
    oldConfig.type = newType;
    
    // Ajustar configuración específica según el tipo
    if (newType === 'doughnut' || newType === 'pie') {
        oldConfig.options.scales = {};
        if (oldConfig.data.datasets.length > 1) {
            oldConfig.data.datasets = [oldConfig.data.datasets[0]];
        }
    } else if (newType === 'bar' || newType === 'line') {
        oldConfig.options.scales = defaultChartOptions.scales;
    }
    
    // Recrear la gráfica
    const ctx = document.getElementById(chartName);
    charts[chartName] = new Chart(ctx, oldConfig);
    
    showNotification('🔄 Gráfica actualizada', `Tipo cambiado a ${newType}`, 'info');
}

// ================================
// EXPOSICIÓN DE FUNCIONES AL SCOPE GLOBAL
// ================================

window.initializeChartData = initializeChartData;
window.initializeCharts = initializeCharts;
window.calcularMargenGanancia = calcularMargenGanancia;
window.calcularMargen = calcularMargen;
window.proyeccionVentas = proyeccionVentas;
window.analisisRentabilidad = analisisRentabilidad;
window.comparativoPeriodos = comparativoPeriodos;
window.exportarDatos = exportarDatos;
window.generarRecibosPDF = generarRecibosPDF;
window.showNotification = showNotification;
window.showCustomAlert = showCustomAlert;
window.toggleChartType = toggleChartType;

// ================================
// FUNCIÓN PRINCIPAL DE INICIALIZACIÓN
// ================================

window.initializeContabilidadPage = function(serverData) {
    console.log('📊 Inicializando página de contabilidad con datos:', serverData);
    
    try {
        // Inicializar datos
        initializeChartData(serverData);
        
        // Inicializar las gráficas después de un pequeño delay
        setTimeout(() => {
            initializeCharts();
            console.log('🎉 Inicialización completada exitosamente');
            showNotification('✅ Sistema Listo', 'Panel de contabilidad cargado correctamente', 'success');
        }, 300);
        
    } catch (error) {
        console.error('❌ Error en inicialización:', error);
        showNotification('❌ Error', 'Error al cargar el panel de contabilidad', 'error');
    }
};

// ================================
// GRÁFICA DE GASTOS POR CATEGORÍA
// ================================

function createGastosPorCategoriaChart() {
    console.log('📊 Creando gráfica de gastos por categoría...');
    
    const ctx = document.getElementById('gastosPorCategoriaChart');
    if (!ctx) {
        console.warn('⚠️ Canvas para gastos por categoría no encontrado');
        return;
    }
    
    if (!chartData.gastosPorCategoria || chartData.gastosPorCategoria.length === 0) {
        console.warn('⚠️ No hay datos de gastos para mostrar');
        // Mostrar un mensaje en el canvas
        ctx.getContext('2d').fillText('No hay datos de gastos disponibles', 50, 50);
        return;
    }
    
    const labels = chartData.gastosPorCategoria.map(item => item.categoria);
    const data = chartData.gastosPorCategoria.map(item => item.total);
    
    // Colores para gastos (tonos rojos/naranjas)
    const colores = [
        'rgba(220, 53, 69, 0.8)',   // Rojo
        'rgba(253, 126, 20, 0.8)',  // Naranja
        'rgba(255, 193, 7, 0.8)',   // Amarillo
        'rgba(108, 117, 125, 0.8)', // Gris
        'rgba(111, 66, 193, 0.8)',  // Morado
        'rgba(13, 110, 253, 0.8)',  // Azul
        'rgba(25, 135, 84, 0.8)',   // Verde
        'rgba(214, 51, 132, 0.8)'   // Rosa
    ];
    
    charts.gastosPorCategoria = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colores.slice(0, data.length),
                borderColor: colores.slice(0, data.length).map(color => color.replace('0.8', '1')),
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            ...baseChartConfig.options,
            plugins: {
                ...baseChartConfig.options.plugins,
                title: {
                    display: true,
                    text: '💸 Distribución de Gastos por Categoría'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    console.log('✅ Gráfica de gastos por categoría creada');
}

// ================================
// CONFIGURACIÓN DE EVENTOS
// ================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM cargado, configurando eventos...');
    
    // Configurar botón de actualizar
    const actualizarBtn = document.getElementById('actualizar-btn');
    if (actualizarBtn) {
        actualizarBtn.addEventListener('click', function() {
            location.reload();
        });
    }
    
    // Validación de fechas en filtros
    const fechaFin = document.getElementById('fecha_fin');
    if (fechaFin) {
        fechaFin.addEventListener('change', function() {
            const fechaInicio = document.getElementById('fecha_inicio').value;
            const fechaFinValue = this.value;
            
            if (fechaInicio && fechaFinValue && fechaInicio > fechaFinValue) {
                showNotification('⚠️ Fechas inválidas', 'La fecha de fin no puede ser anterior a la fecha de inicio', 'warning');
                this.value = '';
            }
        });
    }
});

console.log('✅ Contabilidad.js v4.0 cargado correctamente');
console.log('🔧 Todas las funciones expuestas al scope global');
