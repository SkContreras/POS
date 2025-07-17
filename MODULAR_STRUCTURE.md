# Documentación de la Estructura Modular del Sistema POS

## Visión General

El código JavaScript del sistema POS ha sido refactorizado en módulos independientes para mejorar el mantenimiento, la legibilidad y la escalabilidad del código.

## Estructura de Módulos

### 1. `toast.js` - Sistema de Notificaciones
Maneja todas las notificaciones emergentes del sistema.

**Funciones principales:**
- `mostrarToast(mensaje, tipo)` - Muestra una notificación
- `mostrarToastExito(mensaje)` - Notificación de éxito
- `mostrarToastError(mensaje)` - Notificación de error
- `mostrarToastAdvertencia(mensaje)` - Notificación de advertencia

**Uso:**
```javascript
window.toastManager.mostrarToast("Mensaje de éxito", "success");
```

### 2. `modal.js` - Gestión de Ventanas Modales
Controla la apertura, cierre y eventos de las ventanas modales.

**Funciones principales:**
- `inicializarModal()` - Configura eventos del modal
- `mostrarModalCantidad(id, nombre, precio)` - Muestra modal de cantidad
- `cerrarModalCantidad()` - Cierra el modal

### 3. `sidebar.js` - Manejo de Barras Laterales
Gestiona el comportamiento de los sidebars izquierdo y derecho.

**Funciones principales:**
- `toggleGestion()` - Alterna el sidebar de gestión
- `toggleCarrito()` - Alterna el sidebar del carrito
- `inicializarSidebars()` - Configura el estado inicial

### 4. `carrito.js` - Funcionalidad del Carrito
Maneja toda la lógica del carrito de compras.

**Funciones principales:**
- `agregarAlCarrito(id, nombre, precio)` - Añade producto al carrito
- `eliminarDelCarrito(idx)` - Elimina producto del carrito
- `actualizarCarrito()` - Actualiza la visualización del carrito
- `finalizarVenta()` - Procesa la venta
- `vaciarCarrito()` - Limpia el carrito

### 5. `productos.js` - Gestión de Productos
Maneja las interacciones con los productos en pantalla.

**Funciones principales:**
- `inicializarProductos()` - Configura eventos de productos
- `aplicarAnimacionProducto(elemento)` - Aplica animaciones
- `obtenerDatosProducto(elemento)` - Extrae datos del producto

### 6. `busqueda.js` - Sistema de Búsqueda
Implementa la funcionalidad de búsqueda en tiempo real.

**Funciones principales:**
- `inicializarBusqueda()` - Configura el sistema de búsqueda
- `filtrarProductos(termino, productos, contenedor)` - Filtra productos
- `limpiarBusqueda()` - Limpia la búsqueda actual
- `buscarProducto(termino)` - Busca un producto específico

### 7. `main.js` - Coordinador Principal
Archivo principal que inicializa todos los módulos y mantiene compatibilidad.

**Funciones principales:**
- `inicializarAplicacion()` - Inicializa todo el sistema
- `verificarModulos()` - Verifica que todos los módulos estén cargados
- Funciones de compatibilidad para mantener la API existente

## Orden de Carga de Scripts

Es importante cargar los scripts en el siguiente orden:

1. `toast.js` - Sistema base de notificaciones
2. `modal.js` - Gestión de modales
3. `sidebar.js` - Manejo de barras laterales
4. `carrito.js` - Funcionalidad del carrito
5. `productos.js` - Gestión de productos
6. `busqueda.js` - Sistema de búsqueda
7. `main.js` - Inicializador principal

## Compatibilidad

Se mantienen las funciones globales originales para compatibilidad:
- `agregarAlCarrito()`
- `eliminarDelCarrito()`
- `finalizarVenta()`
- `toggleGestion()`
- `mostrarToast()`

## Ventajas de la Nueva Estructura

### Mantenibilidad
- Cada módulo tiene una responsabilidad específica
- Fácil localización de bugs y funcionalidades
- Código más organizado y legible

### Escalabilidad
- Fácil agregar nuevas funcionalidades
- Módulos independientes permiten desarrollo paralelo
- Reutilización de código entre diferentes páginas

### Debugging
- Logs específicos por módulo
- Verificación de dependencias
- Manejo de errores granular

### Performance
- Carga selectiva de módulos según necesidad
- Menor acoplamiento entre componentes
- Mejor gestión de memoria

## Patrones de Uso

### Agregar Nueva Funcionalidad

1. Crear nuevo archivo `.js` en `/static/js/`
2. Seguir el patrón de exportación:
```javascript
window.nuevoManager = {
    funcion1,
    funcion2,
    // ...
};
```
3. Agregar al orden de carga en los templates
4. Actualizar `verificarModulos()` en `main.js`

### Debugging

1. Abrir Developer Tools
2. Verificar logs de inicialización
3. Comprobar `window.nombreManager` en consola
4. Revisar errores específicos por módulo

## Migración de Código Existente

Si tienes código que usa las funciones antiguas, no necesitas cambiarlo inmediatamente. El sistema mantiene compatibilidad hacia atrás a través de las funciones proxy en `main.js`.

Para migrar gradualmente:
```javascript
// Antiguo
agregarAlCarrito(id, nombre, precio);

// Nuevo (recomendado)
window.carritoManager.agregarAlCarrito(id, nombre, precio);
```
