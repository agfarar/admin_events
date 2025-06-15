# Modernización del Sistema de Gestión de Eventos

## Entrega de proyecto 1

### Motivación

**Enunciado:** La problemática que motiva la modernización del sistema de gestión de eventos radica en múltiples limitaciones arquitecturales, técnicas y **críticas vulnerabilidades de seguridad** que impiden su evolución, mantenimiento eficiente y operación segura en producción.

**Tecnología origen:** Django 4.2 Framework con arquitectura monolítica basada en el administrador nativo de Django.

**Problemática detallada:**

El sistema actual presenta las siguientes limitaciones críticas que justifican su modernización:

#### 1. **🔴 CRÍTICO: Vulnerabilidades de Seguridad Graves**

**Hallazgos de seguridad inmediatos:**
```python
# settings.py - EXPOSICIÓN CRÍTICA
SECRET_KEY = 'django-insecure-(1_^+jp786nhhqo#s@*6$i0m^b(d(kj+0*r1c+lzef@x47s!f!'
DEBUG = True  # NUNCA en producción
ALLOWED_HOSTS = []  # Configuración insegura
```

**Impacto:**
- **Secret key expuesta** permite falsificación de sesiones y tokens CSRF
- **DEBUG=True** expone información sensible del sistema en errores
- **Configuración de desarrollo** en código de producción
- **Vulnerabilidades no parchadas** de Django 4.2 (múltiples CVEs)

**Riesgo:** **CRÍTICO** - Compromiso total del sistema

#### 2. **🔴 CRÍTICO: Versión Obsoleta con Vulnerabilidades Conocidas**

**Estado actual:**
- **Django 4.2** (abril 2023) - 2 años de antigüedad
- **Django 5.2.3 LTS** disponible (abril 2025) con soporte hasta 2028

**Vulnerabilidades no parchadas en Django 4.2:**
- **CVE-2025-32873**: Denegación de servicio en `strip_tags()`
- **CVE-2024-45230**: DoS en `urlize()` y `urlizetrunc()`
- **CVE-2024-45231**: Enumeración de usuarios via reset de contraseña
- **Múltiples parches de seguridad** no aplicados

#### 3. **🔴 CRÍTICO: Ausencia Total de Pruebas Automatizadas**

**Evidencia del código:**
```python
# Todos los archivos tests.py están vacíos:
# apps/events/tests.py, apps/attendees/tests.py, etc.
from django.test import TestCase
# Create your tests here.
```

**Impacto:**
- **0% de cobertura** de pruebas unitarias, integración y funcionales
- **Alto riesgo** en modificaciones y actualizaciones
- **Imposibilidad de refactoring** seguro
- **Calidad del software** no garantizada

#### 4. **🟡 Fuerte Acoplamiento Frontend-Backend**

**Evidencia cuantificada:**
- **11,350 líneas de CSS** (84.3% del código total)
- **Solo 1,584 líneas de Python** (11.8% del código)
- **Ratio CSS/Python**: 7:1 (indicador de sobrecomplejidad)

**Problemas identificados:**
```css
/* static/css/login.css - Modificaciones invasivas del admin */
#header { display: none !important; }
#footer { display: none !important; }
.clear { display: none !important; }
#content { padding: 0 0 0 0 !important; }
```

**Limitaciones:**
- Dependencia total del Django Admin panel
- Imposibilidad de crear interfaces modernas y responsivas
- Desarrollo frontend/backend no separable
- UX limitada para usuarios finales

#### 5. **🟡 Problemas Críticos de Rendimiento**

**Evidencia en el código:**
```python
# apps/events/admin.py - Sin paginación configurada
class EventAdmin(admin.ModelAdmin):
    # list_per_page = 25  # NO CONFIGURADO
    # Sin optimización de consultas
    def get_queryset(self, request):
        qs = super().get_queryset(request)  # Carga TODOS los registros
```

**Problemas identificados:**
- **Carga completa** de todos los registros sin paginación
- **Sin optimización de consultas** (problemas N+1)
- **Consumo excesivo de memoria** en operaciones masivas
- **Sin lazy loading** en relaciones

#### 6. **🔴 CRÍTICO: Base de Datos No Escalable**

**Configuración actual:**
```python
# settings.py - SQLite para producción (INADECUADO)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Limitaciones críticas:**
- **SQLite**: No soporta conexiones concurrentes
- **Sin transacciones** complejas
- **Sin replicación** ni backup automático
- **Inadecuada para producción** con múltiples usuarios

Esta problemática impacta directamente la capacidad de la organización para:
- Mantener la seguridad de los datos de eventos y usuarios
- Escalar el sistema para manejar mayor volumen de eventos
- Integrar con sistemas externos o desarrollar aplicaciones móviles
- Garantizar la continuidad del servicio en producción

## Entendimiento del Legado

### Tecnología Legada: Django 4.2 Framework

**Enunciado:** Django es un framework web de alto nivel escrito en Python que fomenta el desarrollo rápido y el diseño limpio y pragmático. Las características principales de la tecnología legada son:

#### Características Principales de Django 4.2:

1. **Framework Web Basado en Python**
   - Lenguaje de programación interpretado y de alto nivel
   - Sintaxis clara y legible que facilita el desarrollo
   - Amplio ecosistema de librerías y paquetes

2. **Arquitectura MVT (Model-View-Template)**
   - **Model**: Define la estructura de datos y reglas de negocio
   - **View**: Contiene la lógica de presentación y control
   - **Template**: Maneja la presentación y renderizado HTML

3. **ORM (Object-Relational Mapping) Integrado**
   - Abstrae las operaciones de base de datos
   - Permite trabajar con objetos Python en lugar de SQL directo
   - Soporte para múltiples motores de base de datos

4. **Sistema de Administración Automático**
   - Genera interfaces administrativas automáticamente
   - Basado en los modelos definidos
   - Personalizable mediante clases Admin

5. **Sistema de Autenticación y Autorización**
   - Manejo integrado de usuarios, grupos y permisos
   - Middleware de autenticación incorporado
   - Soporte para autenticación personalizada

6. **Sistema de Plantillas Robusto**
   - Motor de plantillas para generar HTML dinámico
   - Herencia de plantillas y bloques reutilizables
   - Filtros y etiquetas personalizables

7. **Middleware Personalizable**
   - Capas de procesamiento de requests/responses
   - Permite interceptar y modificar peticiones HTTP
   - Implementación de funcionalidades transversales

8. **Seguridad por Defecto**
   - Protección contra CSRF, XSS, SQL Injection
   - Validación automática de formularios
   - Manejo seguro de sesiones y cookies

9. **Internacionalización Incorporada**
   - Soporte nativo para múltiples idiomas
   - Localización de fechas, números y monedas
   - Sistema de traducción integrado

10. **Manejo Avanzado de Formularios**
    - Validación automática y personalizada
    - Renderizado automático de campos
    - Integración con modelos de datos

### Arquitectura de la Tecnología Legada

**Enunciado:** Django implementa una **arquitectura por capas** basada en el patrón **MVT (Model-View-Template)** que separa las responsabilidades del sistema en capas bien definidas. Los elementos estructurales y sus relaciones son:

#### Elementos Estructurales de Django:

1. **Capa de Middleware**
   - **Función**: Procesa todas las peticiones HTTP antes y después de llegar a las vistas
   - **Componentes**: SecurityMiddleware, SessionMiddleware, AuthenticationMiddleware
   - **Relación**: Intercepta requests/responses de forma secuencial

2. **URL Dispatcher (URLconf)**
   - **Función**: Mapea URLs a funciones de vista específicas
   - **Componentes**: Patrones de URL, expresiones regulares, parámetros
   - **Relación**: Enruta peticiones HTTP a las vistas correspondientes

3. **Views Layer (Capa de Vistas)**
   - **Función**: Contiene la lógica de negocio y coordina entre modelos y plantillas
   - **Componentes**: Function-based views, Class-based views
   - **Relación**: Recibe requests, consulta modelos, retorna responses

4. **Models Layer (Capa de Modelos)**
   - **Función**: Define la estructura de datos y reglas de negocio
   - **Componentes**: Clases de modelo, campos, relaciones, validadores
   - **Relación**: Abstrae la base de datos mediante el ORM

5. **Template Engine (Motor de Plantillas)**
   - **Función**: Genera HTML dinámico combinando datos con plantillas
   - **Componentes**: Plantillas HTML, contexto de datos, filtros, etiquetas
   - **Relación**: Recibe contexto de las vistas y genera respuesta HTML

6. **ORM (Object-Relational Mapping)**
   - **Función**: Abstrae las operaciones de base de datos
   - **Componentes**: QuerySets, Managers, Migrations
   - **Relación**: Traduce operaciones Python a consultas SQL

7. **Admin Interface**
   - **Función**: Interfaz administrativa automática basada en los modelos
   - **Componentes**: ModelAdmin, AdminSite, Forms
   - **Relación**: Genera CRUD automático para los modelos registrados

#### Diagrama de Arquitectura Django:
![alt text](<assets/Django Project Structure.png>)
```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Browser)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Request/Response
┌─────────────────────▼───────────────────────────────────────┐
│                  WEB SERVER                                 │
│                (Apache/Nginx)                               │
└─────────────────────┬───────────────────────────────────────┘
                      │ WSGI
┌─────────────────────▼───────────────────────────────────────┐
│                DJANGO APPLICATION                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MIDDLEWARE STACK                       │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ SecurityMiddleware                          │   │   │
│  │  │ SessionMiddleware                           │   │   │
│  │  │ AuthenticationMiddleware                    │   │   │
│  │  │ ...                                         │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────┬───────────────────────────────────┘   │
│                    │                                       │
│  ┌─────────────────▼───────────────────────────────────┐   │
│  │              URL DISPATCHER                         │   │
│  │           (URLconf - urls.py)                       │   │
│  └─────────────────┬───────────────────────────────────┘   │
│                    │                                       │
│  ┌─────────────────▼───────────────────────────────────┐   │
│  │                 VIEWS                               │   │
│  │        (Function/Class-based Views)                 │   │
│  │  ┌─────────────┐    ┌─────────────┐                │   │
│  │  │   Models    │◄──►│  Templates  │                │   │
│  │  │             │    │             │                │   │
│  │  │ ┌─────────┐ │    │ ┌─────────┐ │                │   │
│  │  │ │   ORM   │ │    │ │Template │ │                │   │
│  │  │ │         │ │    │ │ Engine  │ │                │   │
│  │  │ └─────────┘ │    │ └─────────┘ │                │   │
│  │  └─────────────┘    └─────────────┘                │   │
│  └─────────────────┬───────────────────────────────────┘   │
│                    │                                       │
│  ┌─────────────────▼───────────────────────────────────┐   │
│  │              ADMIN INTERFACE                        │   │
│  │           (Django Admin Site)                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ Database Queries
┌─────────────────────▼───────────────────────────────────────┐
│                   DATABASE                                  │
│                 (SQLite/PostgreSQL)                         │
└─────────────────────────────────────────────────────────────┘
```

#### Flujo de Procesamiento:

1. **Request llega al servidor** → Middleware procesa la petición
2. **URL Dispatcher** → Mapea URL a vista correspondiente
3. **Vista ejecuta lógica** → Consulta modelos si es necesario
4. **Modelos interactúan con BD** → A través del ORM
5. **Vista prepara contexto** → Datos para la plantilla
6. **Template Engine renderiza** → Genera HTML final
7. **Response retorna** → A través del middleware al cliente

### Aplicación de Ejemplo

**Enunciado:** El código de la aplicación seleccionada es un sistema completo de gestión de eventos corporativos desarrollado en Django 4.2. La aplicación está disponible en un repositorio privado de GitHub y cumple con todos los requisitos establecidos.

#### Descripción de la Aplicación

**Sistema de Gestión de Eventos Corporativos**

El sistema es una aplicación web completa que permite la administración integral de eventos empresariales, desde la planificación hasta el seguimiento financiero post-evento.

#### Funcionalidades Principales

1. **Gestión de Eventos**
   - Creación y edición de eventos con información detallada
   - Configuración de fechas, ubicaciones y descripciones
   - Clasificación por tipo de evento (conferencias, seminarios, etc.)

2. **Manejo de Asistentes**
   - Registro de participantes con información de contacto
   - Control de asistencia y confirmaciones
   - Gestión de listas de espera

3. **Sistema de Tickets y Categorías**
   - Creación de diferentes categorías de entradas
   - Control de disponibilidad y precios por categoría
   - Seguimiento de tickets vendidos vs disponibles

4. **Control Financiero**
   - **Gestión de Gastos**: Registro y categorización de egresos
   - **Manejo de Ingresos**: Seguimiento de revenues por evento
   - Reportes financieros básicos

5. **Sistema de Archivos Adjuntos**
   - Carga y gestión de documentos relacionados
   - Almacenamiento de materiales del evento
   - Control de acceso a archivos

6. **Autenticación y Autorización**
   - Sistema de login personalizado
   - Gestión de usuarios por empresa
   - Control de permisos por rol

7. **Panel Administrativo**
   - Interfaz de administración basada en Django Admin
   - Personalización de formularios y vistas
   - Exportación de datos a Excel/CSV

8. **Auditoría y Trazabilidad**
   - Histórico de cambios con django-simple-history
   - Seguimiento de modificaciones por usuario
   - Logs de actividad del sistema

#### Especificaciones Técnicas

**Métricas del Código:**
- **Total de archivos**: 90
- **Total de líneas de código**: 13,443
- **Distribución por tipo**:
  - Python: 1,584 líneas (11.8%)
  - HTML: 337 líneas (2.5%)
  - CSS: 11,326 líneas (84.3%)
  - JavaScript: 196 líneas (1.5%)

**Estructura del Proyecto:**
```
admin_manage_events/
├── accounts/                    # Gestión de usuarios personalizados
├── apps/
│   ├── events/                 # Gestión de eventos principales
│   ├── attendees/              # Manejo de asistentes
│   ├── ticket_categories/      # Categorías de tickets
│   ├── expenses/               # Control de gastos
│   ├── revenues/               # Manejo de ingresos
│   └── attachments/            # Archivos adjuntos
├── templates/                  # Plantillas HTML personalizadas
├── static/                     # Archivos CSS, JS e imágenes
├── utils/                      # Utilidades compartidas
└── scripts/                    # Scripts de inicialización
```

**Tecnologías Utilizadas:**
- Django 4.2 (Framework principal)
- SQLite (Base de datos)
- Django REST Framework (API - instalado pero no implementado)
- django-simple-history (Auditoría)
- django-import-export (Exportación de datos)
- django-widget-tweaks (Personalización de formularios)
- django-phonenumber-field (Validación de teléfonos)

#### Repositorio

**Enlace al repositorio:** https://github.com/lesmesl/admin_events
**Documentacion generada** https://deepwiki.com/lesmesl/admin_events/1-overview

**Estado del código:**
- ✅ **Código completo y funcional**
- ✅ **Más de 2000 líneas de código** (13,443 líneas totales)
- ✅ **Aplicación ejecutable** con instrucciones de instalación
- ✅ **Familiar al equipo** (desarrollado por miembro del equipo)
- ✅ **Dominio de negocio conocido** (gestión de eventos)

**Instrucciones de ejecución:**
1. Clonar el repositorio: `git clone https://github.com/lesmesl/admin_events.git`
2. Crear entorno virtual Python: `python -m venv venv`
3. Activar entorno virtual: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Ejecutar migraciones: `python manage.py migrate`
6. Crear datos iniciales: `python scripts/insert_data_user_company.py`
7. Ejecutar servidor: `python manage.py runserver`
8. Acceder al admin: `http://localhost:8000/admin/`

#### Justificación de la Selección

Esta aplicación es ideal para el proyecto de modernización porque:

1. **Tamaño Adecuado**: Con 13,443 líneas de código, supera ampliamente el mínimo requerido de 2000 líneas
2. **Complejidad Representativa**: Incluye múltiples módulos interrelacionados que representan casos de uso reales
3. **Problemáticas Reales**: Presenta los desafíos típicos de aplicaciones Django legacy identificados en la motivación
4. **Dominio Conocido**: El equipo tiene experiencia en el dominio de gestión de eventos
5. **Código Funcional**: La aplicación está completamente operativa y puede ejecutarse para probar funcionalidades
6. **Casos de Uso Diversos**: Permite evaluar diferentes estrategias de modernización en distintos módulos
7. **Arquitectura Típica**: Representa la arquitectura monolítica típica que requiere modernización


## Sección de Uso de IAG

### ¿Se hizo uso de IAG?
Sí, se utilizó Inteligencia Artificial Generativa para el desarrollo de este entregable.

### ¿Qué herramientas de IAG se usaron?
Se utilizó **Claude Sonnet 4** (Abacus.AI ChatLLM Teams) como herramienta principal de IAG para:
- Análisis y estructuración del contenido
- Generación de diagramas de arquitectura
- Redacción y mejora de secciones técnicas
- Validación de criterios de calificación

### ¿En qué partes del entregable se usó la IAG?
La IAG se utilizó en las siguientes secciones:

1. **Motivación**: 
   - Estructuración de problemáticas críticas
   - Análisis de vulnerabilidades de seguridad
   - Cuantificación de métricas del código

2. **Entendimiento del Legado**:
   - Descripción detallada de características de Django
   - Creación del diagrama de arquitectura
   - Explicación del flujo de procesamiento


### ¿Qué calidad tenían los resultados de la IAG?
Los resultados de la IAG fueron de **alta calidad** en términos de:

**Fortalezas:**
- **Estructura coherente** y bien organizada
- **Contenido técnico preciso** y actualizado
- **Análisis detallado** de problemáticas
- **Cumplimiento completo** de criterios de calificación

**Limitaciones identificadas:**
- Necesidad de validación de datos específicos del proyecto
- Requerimiento de contextualización con la aplicación real
- Ajustes menores en terminología técnica específica

### ¿Los resultados de la IAG se integraron sin modificación o los estudiantes debieron intervenirlos?
Los resultados de la IAG **requirieron intervención y refinamiento** por parte de los estudiantes:

**Modificaciones realizadas:**
1. **Validación técnica**: Verificación de versiones, CVEs y vulnerabilidades específicas
2. **Contextualización**: Adaptación del contenido a la aplicación específica seleccionada
3. **Integración de evidencias**: Incorporación de código real y métricas específicas del proyecto
4. **Refinamiento de diagramas**: Ajuste de la representación arquitectural para mayor precisión
5. **Validación de criterios**: Verificación del cumplimiento completo de todos los requisitos

**Proceso de refinamiento:**
- **Revisión técnica** de cada sección por expertos del equipo
- **Validación cruzada** entre versiones generadas
- **Integración manual** de elementos específicos del proyecto
- **Prueba de coherencia** entre todas las secciones

La IAG sirvió como **herramienta de apoyo y aceleración** del proceso, pero el contenido final refleja la **experiencia y conocimiento técnico del equipo** aplicado al proyecto específico.
