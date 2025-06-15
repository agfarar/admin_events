# Gestor de eventos

## Levantar proyecto local
1. Clonar el repositorio
2. Ejecutar lo siguientes comandos:
``` bash
# construir entorno de desarrollo
py -m venv .venv
# activar entorno de desarrollo
source .venv/Scripts/activate
# instalar dependencias
pip install -r requirements.txt
```

3. Paso opcional: Migrar datos de la base de datos esté paso es opcional, si se quiere crear una base de datos nueva.
``` bash
python admin_manage_events/manage.py makemigrations
python admin_manage_events/manage.py migrate
```

4. Paso opcional: Poblar datos de la base de datos con usuario y compañía
``` bash
python admin_manage_events/scripts/insert_data_user_company.py
```
5. Levantar aplicación
``` bash
# levantar aplicación
python admin_manage_events/manage.py runserver 0.0.0.0:8000
```

6. Para acceder al admin ir a la siguiente dirección y solicitar credenciales de superusuario con los acceso en el admin_manage_events/scripts/insert_data_user_company.py
``` bash
http://localhost:8000/admin/
```

## Informe de lineas de codigo
Total de archivos analizados: 90
Total de líneas de código: 13443

Desglose por tipo de archivo:
  Python    :   1584 líneas ( 11.8%)
  Html      :    337 líneas (  2.5%)
  Css       :  11326 líneas ( 84.3%)
  Js        :    196 líneas (  1.5%)

## Estructura de carpetas

``` bash

admin_manage_events
├── accounts
│   ├── migrations
│   │   └── 0001_initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── admin_manage_events
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps
│   ├── attachments
│   │   ├── migrations
│   │   │   └── 0001_initial.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── resources.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── attendees
│   │   ├── migrations
│   │   │   └── 0001_initial.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── events
│   │   ├── migrations
│   │   │   └── 0001_initial.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── signals.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── expenses
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── signals.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── revenues
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── signals.py
│   │   ├── tests.py
│   │   └── views.py
│   └──ticket_categories
│       ├── migrations
│       │   └── 0001_initial.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── tests.py
│       └── views.py
├── scripts
│   └── insert_data_user_company.py
├── static
│   ├── css
│   │   ├── login.css
│   │   └── phone_number.css
│   └── js
│      └── phone_number_init.js
├── templates
│   ├── admin
│   │   └── login.html
├── utils
│    └── models.py
├── .gitignore
├── requirements.txt
└── README.md

```


## Comandos base Django
``` bash
# Crear proyecto
django-admin startproject <nombre_proyecto>
# Crear aplicación
python manage.py startapp <nombre_app>
python manage.py startapp <nombre_app> <ruta> 
django-admin startapp <nombre_app> <ruta> # django-admin startapp revenues apps/revenues
# Crear migraciones
python admin_manage_events/manage.py makemigrations
python admin_manage_events/manage.py makemigrations inventory
# Aplicar migraciones
python admin_manage_events/manage.py migrate
# Crear superusuario y alimentar la tabla company
python admin_manage_events/scripts/insert_data_user_company.py
# Crear superusuario
python manage.py createsuperuser
# Levantar aplicación
python manage.py runserver
# borrar migrations y excluya la carpeta venv
find . -path "*/migrations/*.py" -not -path "./venv/*" -not -name "__init__.py" -delete
# Comando para borrar pycache y omitir la carpeta de venv
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -r {} +
``` 