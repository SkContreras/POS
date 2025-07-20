# Sistema POS (Punto de Venta)

Aplicación web modular para gestión de ventas, inventario y usuarios, desarrollada con Flask y SQLite. Incluye interfaz web responsive, seguridad avanzada y empaquetado para ejecutable (.exe).

## Características Principales

- Gestión de productos: agregar, editar, eliminar y visualizar inventario.
- Sistema de ventas con carrito y generación de historial.
- Gestión de gastos y contabilidad.
- Administración de usuarios y autenticación segura.
- Generación de códigos QR para acceso móvil.
- Interfaz web responsive y moderna.
- Cierre automático de pestaña al finalizar sesión.
- Seguridad avanzada: headers, cookies, soporte HTTPS y advertencias.
- Empaquetado como ejecutable con PyInstaller y soporte de icono personalizado.
- Soporte para despliegue local y en la nube (Cloudflare Pages).

## Estructura del Proyecto

```
├── app_modular.py           # Archivo principal de la aplicación
├── cambiar_credenciales.py  # Utilidad para cambiar credenciales
├── database.db              # Base de datos SQLite
├── punto_de_venta.spec      # Configuración PyInstaller para .exe
├── requirements.txt         # Dependencias Python
├── secret_keys.py           # Claves secretas (no compartir)
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
├── templates/               # Plantillas HTML
├── app/                     # Módulos internos (modelos, rutas, utilidades)
│   ├── models/
│   ├── routes/
│   └── utils/
├── certificates/            # Certificados SSL (para HTTPS)
├── config/                  # Configuración de la aplicación
├── imgexample/              # Imágenes de ejemplo
├── build/                   # Archivos generados por PyInstaller
├── dist/                    # Ejecutable generado (.exe)
└── README.md                # Este archivo
```

## Instalación y Ejecución Local

1. **Clona el repositorio:**
   ```bash
   git clone <URL-del-repositorio>
   cd POS
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación:**
   ```bash
   python app_modular.py
   ```
   Accede desde tu navegador a `http://localhost:5000`

5. **(Opcional) Ejecuta como .exe en Windows:**
   - Instala PyInstaller:
     ```bash
     pip install pyinstaller
     ```
   - Genera el ejecutable:
     ```bash
     pyinstaller punto_de_venta.spec
     ```
   - El ejecutable estará en la carpeta `dist/`.

## Requisitos

- Python 3.8 o superior (compatible con 3.13)
- pip
- Flask
- PyInstaller (solo para generar .exe)
- Navegador web moderno
- (Opcional) Certificados SSL para HTTPS

## Variables de Entorno

- `SECRET_KEY`: Clave secreta para Flask (opcional, usa valor por defecto)
- `FLASK_ENV`: `production` para producción, `development` para desarrollo
- `SSL_CERT_PATH` y `SSL_KEY_PATH`: Rutas a certificados SSL (opcional)

## Funcionalidades Detalladas

### Productos
- Agregar, editar, eliminar productos
- Visualización de inventario
- Búsqueda y filtrado

### Ventas
- Carrito de compras
- Registro de ventas
- Historial y reportes

### Gastos y Contabilidad
- Registro y edición de gastos
- Dashboard de contabilidad

### Usuarios y Seguridad
- Autenticación y gestión de usuarios
- Cambio de credenciales
- Seguridad avanzada: headers, cookies, advertencias HTTP/HTTPS

### Utilidades
- Generación de QR para acceso móvil
- Cierre automático de pestaña
- Apertura automática de navegador en desarrollo

### Empaquetado y Despliegue
- Empaquetado como ejecutable con icono personalizado (`POS.ico`)
- Soporte para despliegue en Cloudflare Pages y otros servicios

## Herramientas y Librerías Usadas

- **Flask**: Framework principal
- **SQLite**: Base de datos local
- **PyInstaller**: Empaquetado como ejecutable
- **Jinja2**: Plantillas HTML
- **Bootstrap/CSS**: Interfaz web
- **JavaScript**: Funcionalidad frontend
- **QR Code**: Generación de códigos QR

## Despliegue en Cloudflare Pages

### Opción 1: Desde Git Repository

1. Sube tu código a un repositorio (GitHub, GitLab, etc.)
2. Ve a [Cloudflare Pages](https://pages.cloudflare.com/)
3. Conecta tu repositorio
4. Configura los settings de build:
   - Build command: `pip install -r requirements.txt`
   - Build output directory: `/`
   - Root directory: `/`

### Opción 2: Upload Manual

1. Ve a [Cloudflare Pages](https://pages.cloudflare.com/)
2. Crea un nuevo proyecto
3. Sube manualmente los archivos del proyecto

## Archivos Importantes

- `app_modular.py`: Entrada principal de la app
- `punto_de_venta.spec`: Configuración para generar el ejecutable
- `requirements.txt`: Lista de dependencias
- `database.db`: Base de datos SQLite
- `static/` y `templates/`: Recursos web

## Notas de Seguridad

- Si usas HTTP, el sistema advierte sobre vulnerabilidad en campos de contraseña.
- Para máxima seguridad, configura y usa HTTPS con certificados válidos.

## Contacto y Soporte

Para dudas, sugerencias o reportes de errores, abre un issue en el repositorio o contacta al propietario.
