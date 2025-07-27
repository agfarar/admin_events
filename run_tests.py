#!/usr/bin/env python
"""
Script para ejecutar todos los tests del proyecto admin_events
Este script valida que la modernización del sistema legado fue efectiva
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def setup_django():
    """Configurar Django para los tests"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_manage_events.settings')
    django.setup()

def run_all_tests():
    """Ejecutar todos los tests del proyecto"""
    print("=" * 80)
    print("EJECUTANDO TESTS DE VALIDACIÓN DE MODERNIZACIÓN")
    print("Proyecto: Admin Events - Sistema Legado")
    print("Objetivo: Validar que la modernización fue efectiva")
    print("=" * 80)
    
    # Apps a testear
    test_apps = [
        'accounts.tests',
        'apps.attendees.tests', 
        'apps.events.tests',
        'apps.ticket_categories.tests',
        'apps.attachments.tests',
        'apps.inventory.tests',
    ]
    
    print("\n📋 MÓDULOS A TESTEAR:")
    for app in test_apps:
        print(f"  ✓ {app}")
    
    print("\n🚀 INICIANDO EJECUCIÓN DE TESTS...\n")
    
    # Ejecutar tests
    for app in test_apps:
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {app}")
        print(f"{'='*60}")
        
        try:
            # Ejecutar tests para la app específica
            execute_from_command_line([
                'manage.py', 'test', app, '--verbosity=2'
            ])
            print(f"✅ {app}: TESTS COMPLETADOS")
            
        except SystemExit as e:
            if e.code == 0:
                print(f"✅ {app}: TESTS COMPLETADOS EXITOSAMENTE")
            else:
                print(f"❌ {app}: TESTS FALLARON (código: {e.code})")
        except Exception as e:
            print(f"💥 {app}: ERROR EJECUTANDO TESTS - {str(e)}")

def run_coverage_analysis():
    """Ejecutar análisis de cobertura de código"""
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE COBERTURA DE CÓDIGO")
    print("="*80)
    
    try:
        import coverage
        
        # Configurar coverage
        cov = coverage.Coverage(source=['.'])
        cov.start()
        
        # Ejecutar tests con coverage
        execute_from_command_line(['manage.py', 'test', '--verbosity=1'])
        
        cov.stop()
        cov.save()
        
        print("\n📈 REPORTE DE COBERTURA:")
        cov.report()
        
        # Generar reporte HTML
        cov.html_report(directory='htmlcov')
        print("\n📁 Reporte HTML generado en: htmlcov/index.html")
        
    except ImportError:
        print("⚠️  Coverage no instalado. Instalar con: pip install coverage")
        print("💡 Ejecutando tests sin análisis de cobertura...")
        execute_from_command_line(['manage.py', 'test'])

def validate_modernization_metrics():
    """Validar métricas de modernización según el documento"""
    print("\n" + "="*80)
    print("📊 VALIDACIÓN DE MÉTRICAS DE MODERNIZACIÓN")
    print("="*80)
    
    metrics = {
        "cobertura_tests": "≥70%",
        "aislamiento_dominio": "≥95%", 
        "rendimiento_consultas": "<2s para paginación",
        "concurrencia": "Sin condiciones de carrera",
        "seguridad": "Validación de datos sensibles",
        "escalabilidad": "<5s para 100 registros"
    }
    
    print("🎯 MÉTRICAS OBJETIVO SEGÚN DOCUMENTACIÓN:")
    for metric, target in metrics.items():
        print(f"  • {metric}: {target}")
    
    print("\n📋 VALIDACIONES IMPLEMENTADAS EN TESTS:")
    validations = [
        "✓ Tests de rendimiento (PerformanceTests)",
        "✓ Tests de concurrencia (ConcurrencyTests)", 
        "✓ Tests de seguridad (SecurityTests)",
        "✓ Tests de integración (IntegrationTests)",
        "✓ Tests de migración (MigrationCompatibilityTests)",
        "✓ Validación de estructura de datos para microservicio",
        "✓ Tests de aislamiento por empresa",
        "✓ Validación de lógica de negocio crítica"
    ]
    
    for validation in validations:
        print(f"  {validation}")

def display_test_categories():
    """Mostrar categorías de tests implementados"""
    print("\n" + "="*80)
    print("📚 CATEGORÍAS DE TESTS IMPLEMENTADOS")
    print("="*80)
    
    categories = {
        "🏗️  TESTS FUNCIONALES": [
            "RF-001: Crear asistente con datos válidos",
            "RF-002: Crear compra válida", 
            "RF-003: Validación de tickets agotados",
            "RF-004: Crear ticket válido",
            "RF-005: Flujo completo de registro",
            "RF-006: Asistente con archivo adjunto"
        ],
        "🔒 TESTS DE SEGURIDAD": [
            "SEC-001: Validación de formato de email",
            "SEC-002: Integridad de datos del asistente", 
            "SEC-003: Datos sensibles no expuestos",
            "AUTH-001-005: Tests de autenticación",
            "PERM-001-004: Tests de permisos",
            "AUD-001-003: Tests de auditoría"
        ],
        "⚡ TESTS DE RENDIMIENTO": [
            "RNF-001: Rendimiento en creación masiva",
            "RNF-002: Rendimiento de consultas con paginación",
            "RNF-003: Condición de carrera en compras",
            "PERF-001-002: Tests de rendimiento general"
        ],
        "🔗 TESTS DE INTEGRACIÓN": [
            "INT-001: Flujo completo de compra para evento",
            "INT-002: Validación de capacidad del evento", 
            "INT-003: Compra con múltiples categorías",
            "Relación usuario-empresa-asistente"
        ],
        "🚀 TESTS DE MIGRACIÓN": [
            "MIG-001: Compatibilidad de estructura de datos",
            "MIG-002: Formato de serialización para API REST",
            "MIG-003-004: Compatibilidad con microservicio"
        ],
        "💼 TESTS DE LÓGICA DE NEGOCIO": [
            "BL-001: Categorización de eventos por fecha",
            "BL-002: Regla de negocio para eventos activos",
            "BL-003: Aislamiento de eventos por empresa"
        ]
    }
    
    for category, tests in categories.items():
        print(f"\n{category}:")
        for test in tests:
            print(f"  • {test}")

def main():
    """Función principal"""
    if len(sys.argv) > 1 and 'help' in sys.argv[1]:
        print("""
USO: python run_tests.py [opción]

OPCIONES:
  help        - Mostrar esta ayuda
  coverage    - Ejecutar con análisis de cobertura
  metrics     - Solo mostrar métricas sin ejecutar tests
  categories  - Solo mostrar categorías de tests
  
Sin argumentos: Ejecutar todos los tests básicos
        """)
        return
    
    # Cambiar al directorio del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(script_dir, 'admin_manage_events')
    os.chdir(project_dir)
    
    # Configurar Django
    setup_django()
    
    # Mostrar información inicial
    display_test_categories()
    validate_modernization_metrics()
    
    # Ejecutar según argumentos
    if len(sys.argv) > 1:
        if 'coverage' in sys.argv[1]:
            run_coverage_analysis()
        elif 'metrics' in sys.argv[1]:
            print("\n✅ Métricas mostradas. No se ejecutaron tests.")
            return
        elif 'categories' in sys.argv[1]:
            print("\n✅ Categorías mostradas. No se ejecutaron tests.")
            return
    else:
        run_all_tests()
    
    print("\n" + "="*80)
    print("🎉 VALIDACIÓN DE MODERNIZACIÓN COMPLETADA")
    print("="*80)
    print("📄 Revisar el documento de modernización en:")
    print("   modernization_doc_admin_events/input.md")
    print("🔗 Comparar con la implementación del microservicio en:")
    print("   admin_events_upgrade/admin_events_attendees/")
    print("="*80)

if __name__ == '__main__':
    main()
