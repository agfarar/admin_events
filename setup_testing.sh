#!/bin/bash

# setup_testing.sh
# Script para configurar el entorno de testing para validación de modernización
# Admin Events - Sistema Legado

echo "=================================================================="
echo "🚀 CONFIGURACIÓN DE ENTORNO DE TESTING"
echo "Admin Events - Validación de Modernización"
echo "=================================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ] && [ ! -d "admin_manage_events" ]; then
    print_error "Este script debe ejecutarse desde el directorio admin_events"
    print_error "Estructura esperada: admin_events/admin_manage_events/manage.py"
    exit 1
fi

# Navegar al directorio del proyecto Django
cd admin_manage_events

print_status "Verificando estructura del proyecto..."

# Verificar archivos de tests
test_files=(
    "accounts/tests.py"
    "apps/attendees/tests.py"
    "apps/events/tests.py"
    "apps/ticket_categories/tests.py"
    "apps/attachments/tests.py"
    "apps/inventory/tests.py"
)

print_status "Verificando archivos de tests..."
for test_file in "${test_files[@]}"; do
    if [ -f "$test_file" ]; then
        print_success "✓ $test_file"
    else
        print_error "✗ $test_file no encontrado"
    fi
done

# Verificar dependencias de Python
print_status "Verificando dependencias de Python..."

# Función para verificar si un paquete está instalado
check_python_package() {
    python -c "import $1" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "✓ $1 está instalado"
        return 0
    else
        print_warning "✗ $1 no está instalado"
        return 1
    fi
}

# Verificar Django
check_python_package "django" || {
    print_status "Instalando Django..."
    pip install django || {
        print_error "Error instalando Django"
        exit 1
    }
}

# Verificar coverage (opcional)
check_python_package "coverage" || {
    print_warning "Coverage no está instalado. Tests de cobertura no estarán disponibles."
    print_status "Para instalar: pip install coverage"
}

# Verificar otras dependencias comunes
dependencies=("rest_framework" "import_export" "widget_tweaks" "simple_history")
for dep in "${dependencies[@]}"; do
    check_python_package "$dep" || {
        print_warning "$dep no encontrado. Algunos tests podrían fallar."
    }
done

print_status "Verificando configuración de Django..."

# Verificar settings.py
if [ -f "admin_manage_events/settings.py" ]; then
    print_success "✓ settings.py encontrado"
else
    print_error "✗ settings.py no encontrado"
    exit 1
fi

# Crear base de datos de tests
print_status "Preparando base de datos de tests..."

# Ejecutar migraciones
python manage.py makemigrations --dry-run > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "✓ Migraciones verificadas"
else
    print_warning "Algunas migraciones podrían estar pendientes"
fi

# Verificar que se puede crear base de datos de tests
python manage.py check --tag database > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "✓ Configuración de base de datos válida"
else
    print_warning "Problemas con configuración de base de datos"
fi

# Crear directorio para reportes si no existe
mkdir -p ../reports
mkdir -p ../htmlcov

print_status "Configurando archivos auxiliares..."

# Crear archivo de configuración para pytest (opcional)
cat > pytest.ini << EOF
[tool:pytest]
DJANGO_SETTINGS_MODULE = admin_manage_events.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test* *Tests
python_functions = test_*
addopts = --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    security: marks tests as security tests
    performance: marks tests as performance tests
EOF

print_success "✓ pytest.ini creado"

# Crear archivo de configuración para coverage
cat > .coveragerc << EOF
[run]
source = .
omit = 
    */migrations/*
    */venv/*
    */env/*
    manage.py
    */settings/*
    */tests/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = ../htmlcov
EOF

print_success "✓ .coveragerc creado"

# Verificar que los tests se pueden importar
print_status "Verificando importación de tests..."

test_modules=(
    "accounts.tests"
    "apps.attendees.tests"
    "apps.events.tests"
    "apps.ticket_categories.tests"
    "apps.attachments.tests"
    "apps.inventory.tests"
)

for module in "${test_modules[@]}"; do
    python -c "
import django
django.setup()
import $module
print('✓ $module importado correctamente')
" 2>/dev/null || print_warning "✗ Problema importando $module"
done

# Crear script de ejecución rápida
cat > quick_test.sh << 'EOF'
#!/bin/bash
# Script de ejecución rápida de tests

echo "🧪 Ejecutando tests rápidos..."

# Tests básicos sin coverage
python manage.py test --verbosity=1 --parallel --keepdb

echo "✅ Tests completados"
EOF

chmod +x quick_test.sh
print_success "✓ quick_test.sh creado"

# Crear script de tests completos
cat > full_test.sh << 'EOF'
#!/bin/bash
# Script de ejecución completa con coverage

echo "🧪 Ejecutando suite completa de tests..."

# Limpiar reportes anteriores
rm -rf ../htmlcov/*
rm -f .coverage

# Ejecutar tests con coverage
coverage run --source='.' manage.py test --verbosity=2

# Generar reportes
coverage report
coverage html

echo "📊 Reportes generados en ../htmlcov/index.html"
echo "✅ Suite completa terminada"
EOF

chmod +x full_test.sh
print_success "✓ full_test.sh creado"

# Volver al directorio original
cd ..

print_status "Creando documentación de ejecución..."

# Crear guía rápida de ejecución
cat > QUICK_START_TESTS.md << 'EOF'
# 🚀 Guía Rápida - Tests de Validación de Modernización

## Ejecución Inmediata

### Tests Básicos (Rápido)
```bash
cd admin_manage_events
./quick_test.sh
```

### Tests Completos con Cobertura
```bash
cd admin_manage_events
./full_test.sh
```

### Tests por Módulo
```bash
cd admin_manage_events

# Asistentes (módulo principal)
python manage.py test apps.attendees.tests --verbosity=2

# Autenticación
python manage.py test accounts.tests --verbosity=2

# Eventos
python manage.py test apps.events.tests --verbosity=2

# Categorías de Tickets
python manage.py test apps.ticket_categories.tests --verbosity=2

# Archivos Adjuntos
python manage.py test apps.attachments.tests --verbosity=2

# Inventario
python manage.py test apps.inventory.tests --verbosity=2
```

## Interpretación de Resultados

### ✅ Éxito
- Todos los tests pasan
- Cobertura ≥70%
- Tiempo total <60s

### ⚠️ Advertencias
- Algunos tests fallan (revisar logs)
- Cobertura <70%
- Tiempo excesivo

### ❌ Fallas Críticas
- Errores de importación
- Fallas de configuración
- Tests de seguridad fallan

## Archivos Generados

- `htmlcov/index.html` - Reporte de cobertura
- `.coverage` - Datos de cobertura
- `pytest.ini` - Configuración de tests
- `.coveragerc` - Configuración de cobertura

## Próximos Pasos

1. Revisar reportes de cobertura
2. Analizar tests fallidos
3. Verificar métricas de rendimiento
4. Validar compatibilidad con microservicio
EOF

print_success "✓ QUICK_START_TESTS.md creado"

echo ""
echo "=================================================================="
print_success "🎉 CONFIGURACIÓN COMPLETADA"
echo "=================================================================="
echo ""
print_status "Archivos creados:"
echo "  • admin_manage_events/pytest.ini"
echo "  • admin_manage_events/.coveragerc"
echo "  • admin_manage_events/quick_test.sh"
echo "  • admin_manage_events/full_test.sh"
echo "  • reports/ (directorio)"
echo "  • htmlcov/ (directorio)"
echo "  • QUICK_START_TESTS.md"
echo ""
print_status "Para ejecutar tests inmediatamente:"
echo "  cd admin_manage_events && ./quick_test.sh"
echo ""
print_status "Para documentación completa:"
echo "  cat README_TESTS.md"
echo ""
print_status "Para tests con cobertura:"
echo "  cd admin_manage_events && ./full_test.sh"
echo ""
print_success "🚀 ¡Listo para validar la modernización!"
echo "=================================================================="
