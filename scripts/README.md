# Scripts Administrativos ILISB

Este directorio contiene scripts para la administración del sistema ILISB Flask.

## Archivos disponibles

### `admin_manager.py`
Script principal para gestión de administradores del sistema.

**Uso:**
```bash
# Crear un nuevo super administrador
python scripts/admin_manager.py create

# Listar todos los administradores
python scripts/admin_manager.py list

# Eliminar un administrador
python scripts/admin_manager.py delete <username>

# Mostrar ayuda
python scripts/admin_manager.py help
```

**Características:**
- ✅ Creación interactiva de super administradores
- ✅ Validación de datos de entrada
- ✅ Verificación de duplicados
- ✅ Listado organizado de administradores
- ✅ Eliminación segura con confirmación
- ✅ Interfaz amigable con emojis

## Requisitos

- Python 3.7+
- Entorno virtual activado
- Base de datos configurada
- Aplicación Flask configurada

## Ejecución

Desde el directorio raíz del proyecto:

```bash
cd /path/to/ILISB_Flask
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

python scripts/admin_manager.py [comando]
```

## Seguridad

- Las contraseñas se almacenan hasheadas usando Werkzeug
- Los super administradores tienen permisos especiales
- Confirmación requerida para eliminar super administradores
- Validación de datos de entrada

## Estructura de archivos

```
scripts/
├── __init__.py          # Inicialización del módulo
├── admin_manager.py     # Gestión de administradores
└── README.md           # Esta documentación
```