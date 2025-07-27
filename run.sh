#!/bin/bash

# Script para ejecutar la aplicación Django admin_events
# Autor: Generado automáticamente
# Fecha: $(date)

set -e  # Salir si algún comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con colores
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

# Directorio base del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DJANGO_DIR="$PROJECT_DIR/admin_manage_events"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_EXEC="$VENV_DIR/bin/python"
PIP_EXEC="$VENV_DIR/bin/pip"

print_status "Iniciando aplicación Django admin_events..."
print_status "Directorio del proyecto: $PROJECT_DIR"

# Verificar que estamos en el directorio correcto
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    print_error "No se encontró requirements.txt en $PROJECT_DIR"
    exit 1
fi

if [ ! -f "$DJANGO_DIR/manage.py" ]; then
    print_error "No se encontró manage.py en $DJANGO_DIR"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
    print_success "Entorno virtual creado en $VENV_DIR"
else
    print_status "Entorno virtual ya existe"
fi

# Activar entorno virtual y verificar
if [ ! -f "$PYTHON_EXEC" ]; then
    print_error "No se pudo encontrar el ejecutable de Python en $PYTHON_EXEC"
    exit 1
fi

# Actualizar pip
print_status "Actualizando pip..."
"$PIP_EXEC" install --upgrade pip

# Instalar dependencias
print_status "Instalando dependencias desde requirements.txt..."
"$PIP_EXEC" install -r "$PROJECT_DIR/requirements.txt"
print_success "Dependencias instaladas correctamente"

# Cambiar al directorio de Django
cd "$DJANGO_DIR"

# Verificar configuración de Django
print_status "Verificando configuración de Django..."
"$PYTHON_EXEC" manage.py check --deploy
if [ $? -eq 0 ]; then
    print_success "Configuración de Django verificada"
else
    print_warning "Se encontraron advertencias en la configuración de Django"
fi

# Aplicar migraciones
print_status "Aplicando migraciones de base de datos..."
"$PYTHON_EXEC" manage.py migrate
print_success "Migraciones aplicadas correctamente"

# Recopilar archivos estáticos (si es necesario)
print_status "Recopilando archivos estáticos..."
"$PYTHON_EXEC" manage.py collectstatic --noinput --clear
print_success "Archivos estáticos recopilados"

# Verificar si existe un superusuario
print_status "Verificando superusuario..."
SUPERUSER_EXISTS=$("$PYTHON_EXEC" manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')
" 2>/dev/null)

if [ "$SUPERUSER_EXISTS" = "no" ]; then
    print_warning "No se encontró ningún superusuario."
    read -p "¿Deseas crear un superusuario ahora? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "$PYTHON_EXEC" manage.py createsuperuser
        print_success "Superusuario creado"
    else
        print_warning "Puedes crear un superusuario más tarde con: python manage.py createsuperuser"
    fi
else
    print_success "Superusuario encontrado"
fi

# Mostrar información del proyecto
echo
print_success "=============================================="
print_success "  Aplicación Django lista para ejecutarse"
print_success "=============================================="
echo
print_status "URLs disponibles:"
echo "  - Aplicación principal: http://localhost:8000/"
echo "  - Panel de administración: http://localhost:8000/admin/"
echo
print_status "Para detener el servidor, presiona Ctrl+C"
echo

# Iniciar servidor de desarrollo
print_status "Iniciando servidor de desarrollo Django..."
"$PYTHON_EXEC" manage.py runserver localhost:8000
