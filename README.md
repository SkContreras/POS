# Sistema POS (Punto de Venta)

Una aplicación web para gestión de punto de venta construida con Flask.

## Características

- Gestión de productos (agregar, editar, eliminar)
- Sistema de ventas con carrito
- Historial de ventas
- Generación de códigos QR para acceso móvil
- Interfaz web responsive

## Despliegue en Cloudflare Pages

### Opción 1: Desde Git Repository

1. Sube tu código a un repositorio de Git (GitHub, GitLab, etc.)
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

## Variables de Entorno

- `SECRET_KEY`: Clave secreta para Flask (opcional, usa valor por defecto)
- `FLASK_ENV`: Configurar como 'production' para producción

## Instalación Local

```bash
pip install -r requirements.txt
python app.py
```

## Estructura del Proyecto

- `app.py`: Aplicación principal Flask
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `database.db`: Base de datos SQLite
- `requirements.txt`: Dependencias Python
