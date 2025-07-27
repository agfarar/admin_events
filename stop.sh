#!/bin/bash

# Script para detener la aplicación Django admin_events
# Autor: Generado automáticamente

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Buscando procesos de Django en ejecución..."

# Buscar procesos de Django runserver
DJANGO_PIDS=$(pgrep -f "manage.py runserver" 2>/dev/null)

if [ -z "$DJANGO_PIDS" ]; then
    print_status "No se encontraron procesos de Django en ejecución"
else
    print_status "Deteniendo procesos de Django..."
    for pid in $DJANGO_PIDS; do
        print_status "Deteniendo proceso PID: $pid"
        kill -TERM "$pid" 2>/dev/null
        sleep 2
        
        # Verificar si el proceso aún existe
        if kill -0 "$pid" 2>/dev/null; then
            print_status "Forzando cierre del proceso PID: $pid"
            kill -KILL "$pid" 2>/dev/null
        fi
    done
    print_success "Procesos de Django detenidos"
fi

# Buscar procesos Python que puedan estar ejecutando Django
PYTHON_DJANGO_PIDS=$(pgrep -f "python.*manage.py" 2>/dev/null)

if [ ! -z "$PYTHON_DJANGO_PIDS" ]; then
    print_status "Deteniendo procesos Python de Django..."
    for pid in $PYTHON_DJANGO_PIDS; do
        print_status "Deteniendo proceso Python PID: $pid"
        kill -TERM "$pid" 2>/dev/null
        sleep 2
        
        if kill -0 "$pid" 2>/dev/null; then
            kill -KILL "$pid" 2>/dev/null
        fi
    done
    print_success "Procesos Python de Django detenidos"
fi

print_success "Aplicación Django detenida completamente"
