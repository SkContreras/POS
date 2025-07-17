# 🔑 Cambio de Credenciales del Administrador

## Descripción
Se ha implementado una funcionalidad que permite al administrador cambiar sus credenciales de acceso desde la interfaz web, eliminando la necesidad de usar credenciales por defecto.

## Ubicación
La funcionalidad está disponible en la sección **"Gestión de Usuarios"** del menú principal, accesible solo para usuarios con rol de administrador.

## Características

### 🔐 Cambio de Contraseña
- Permite cambiar solo la contraseña manteniendo el mismo nombre de usuario
- Requiere la contraseña actual para confirmar la operación
- Mínimo 4 caracteres para la nueva contraseña
- Confirmación de la nueva contraseña

### 👤 Cambio de Nombre de Usuario
- Permite cambiar solo el nombre de usuario manteniendo la misma contraseña
- Requiere la contraseña actual para confirmar la operación
- Mínimo 3 caracteres para el nuevo nombre de usuario
- Verificación de que el nuevo nombre no esté en uso

### 🔄 Cambio Completo
- Permite cambiar tanto el nombre de usuario como la contraseña en una sola operación
- Todas las validaciones anteriores se aplican

## Flujo de Uso

1. **Acceso**: Iniciar sesión como administrador
2. **Navegación**: Ir a "Gestión de Usuarios" desde el menú principal
3. **Localización**: Buscar la sección "🔑 Cambiar Mis Credenciales"
4. **Completar Formulario**:
   - Ingresar contraseña actual (obligatorio)
   - Ingresar nuevo nombre de usuario (opcional)
   - Ingresar nueva contraseña (opcional)
   - Confirmar nueva contraseña (si se especificó una nueva)
5. **Confirmar**: Hacer clic en "🔄 Actualizar Credenciales"

## Validaciones de Seguridad

### ✅ Validaciones del Frontend
- Verificación de campos obligatorios
- Validación de longitud mínima
- Confirmación de contraseñas coincidentes
- Confirmación antes de enviar el formulario

### 🔒 Validaciones del Backend
- Verificación de contraseña actual
- Validación de que el usuario es administrador
- Verificación de unicidad del nombre de usuario
- Validación de longitud de credenciales
- Protección contra inyección SQL

## Comportamiento Especial

### 🔄 Cambio de Nombre de Usuario
Si se cambia el nombre de usuario:
- La sesión actual se cierra automáticamente
- Se redirige a la página de login
- Debe iniciar sesión con las nuevas credenciales

### 📝 Registro de Auditoría
Todos los cambios de credenciales se registran en el log de acciones del sistema con:
- Fecha y hora del cambio
- Usuario que realizó el cambio
- Tipo de cambio realizado (usuario, contraseña, o ambos)

## Archivos Modificados

### Backend
- **`app/models/database.py`**: Agregados métodos `update_credentials()` y `username_exists()`
- **`app/routes/auth.py`**: Agregada ruta `/cambiar_credenciales`

### Frontend
- **`templates/gestionar_usuarios.html`**: Agregado formulario de cambio de credenciales
- Funciones JavaScript de validación

## Seguridad

### 🛡️ Medidas Implementadas
- Verificación de rol de administrador
- Validación de contraseña actual antes de cualquier cambio
- Hashing seguro de contraseñas con Werkzeug
- Registro de auditoría de todos los cambios
- Validación de entrada tanto en frontend como backend
- Cierre automático de sesión al cambiar nombre de usuario

### 🚫 Protecciones
- No se pueden usar credenciales vacías
- No se puede reutilizar un nombre de usuario existente
- Todas las contraseñas se almacenan hasheadas
- La contraseña actual debe ser verificada antes de cualquier cambio

## Recomendaciones de Uso

1. **Cambio Inicial**: Cambiar las credenciales por defecto inmediatamente después de la instalación
2. **Contraseñas Seguras**: Usar contraseñas con al menos 8 caracteres, incluyendo números y símbolos
3. **Cambios Periódicos**: Cambiar credenciales periódicamente por seguridad
4. **Backup**: Asegurar el respaldo de la base de datos antes de cambios importantes

## Solución de Problemas

### Problema: "La contraseña actual es incorrecta"
- **Solución**: Verificar que está ingresando la contraseña correcta

### Problema: "El nombre de usuario ya existe"
- **Solución**: Elegir un nombre de usuario diferente

### Problema: No aparece la sección de cambio de credenciales
- **Solución**: Verificar que está logueado como administrador

### Problema: Formulario no se envía
- **Solución**: Verificar que todas las validaciones JavaScript pasen correctamente
