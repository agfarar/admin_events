# Scripts de Ejecución - Admin Events

Este directorio contiene scripts para facilitar la ejecución y gestión de la aplicación Django admin_events.

## Scripts Disponibles

### 🚀 `run.sh` - Ejecutar la aplicación

Script principal para iniciar la aplicación Django. Automatiza todo el proceso de configuración y ejecución.

**Uso:**
```bash
./run.sh
```

**Lo que hace:**
- ✅ Verifica que el entorno virtual existe (lo crea si no existe)
- ✅ Instala/actualiza todas las dependencias del `requirements.txt`
- ✅ Verifica la configuración de Django
- ✅ Aplica migraciones de base de datos
- ✅ Recopila archivos estáticos
- ✅ Verifica si existe un superusuario (opción de crear uno)
- ✅ Inicia el servidor de desarrollo en `http://localhost:8000`

### 🛑 `stop.sh` - Detener la aplicación

Script para detener limpiamente todos los procesos de Django en ejecución.

**Uso:**
```bash
./stop.sh
```

**Lo que hace:**
- 🔍 Busca procesos de Django en ejecución
- 🛑 Detiene los procesos de manera ordenada
- 🔪 Fuerza el cierre si es necesario
- ✅ Confirma que todos los procesos han sido detenidos

## Requisitos Previos

- Python 3.8 o superior
- Acceso a internet (para instalar dependencias)
- Permisos de ejecución en los scripts

## URLs de la Aplicación

Una vez iniciada la aplicación, estará disponible en:

- **Aplicación principal:** http://localhost:8000/
- **Panel de administración:** http://localhost:8000/admin/

## Solución de Problemas

### Error de permisos
Si obtienes un error de permisos, ejecuta:
```bash
chmod +x run.sh stop.sh
```

### Puerto ocupado
Si el puerto 8000 está ocupado, puedes modificar el script `run.sh` y cambiar el puerto en la última línea:
```bash
"$PYTHON_EXEC" manage.py runserver 0.0.0.0:8080
```

### Problemas con dependencias
El script intentará instalar automáticamente todas las dependencias. Si hay problemas:
1. Verifica tu conexión a internet
2. Asegúrate de tener Python 3.8+ instalado
3. Verifica que tienes permisos para instalar paquetes

### Crear superusuario manualmente
Si necesitas crear un superusuario después de la instalación:
```bash
cd admin_manage_events
../.venv/bin/python manage.py createsuperuser
```

## Estructura del Proyecto

```
admin_events/
├── run.sh                    # Script principal de ejecución
├── stop.sh                   # Script para detener la aplicación
├── requirements.txt          # Dependencias de Python
├── admin_manage_events/      # Directorio principal de Django
│   ├── manage.py            # Comando de gestión de Django
│   ├── db.sqlite3           # Base de datos SQLite
│   └── ...
└── .venv/                   # Entorno virtual (se crea automáticamente)
```

## Desarrollo

Para desarrollo activo, puedes usar los comandos de Django directamente:

```bash
# Activar entorno virtual
source .venv/bin/activate

# Cambiar al directorio de Django
cd admin_manage_events

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver

# Ejecutar tests
python manage.py test
```

---

**Nota:** Los scripts están configurados para usar el entorno virtual local (`.venv`) y manejar automáticamente la configuración del proyecto.
