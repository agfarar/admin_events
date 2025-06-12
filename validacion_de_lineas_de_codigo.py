import os
import re
from pathlib import Path

def count_lines_python(file_path):
    """Cuenta líneas de código Python excluyendo SOLO comentarios y docstrings (mantiene líneas vacías como separadores)"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    lines = content.split('\n')
    code_lines = 0
    in_multiline_string = False
    multiline_delimiter = None
    
    for line in lines:
        stripped = line.strip()
        
        # Detectar inicio/fin de docstrings
        if '"""' in stripped or "'''" in stripped:
            if not in_multiline_string:
                # Buscar el delimitador
                if '"""' in stripped:
                    multiline_delimiter = '"""'
                else:
                    multiline_delimiter = "'''"
                
                # Verificar si el docstring termina en la misma línea
                delimiter_count = stripped.count(multiline_delimiter)
                if delimiter_count >= 2:
                    # Docstring de una línea, no contar
                    continue
                else:
                    in_multiline_string = True
                    continue
            else:
                # Fin del docstring
                if multiline_delimiter in stripped:
                    in_multiline_string = False
                    multiline_delimiter = None
                    continue
        
        # Si estamos en un docstring, no contar
        if in_multiline_string:
            continue
            
        # Comentario de línea completa (solo si la línea ÚNICAMENTE contiene comentario)
        if stripped.startswith('#') and not any(char for char in stripped if char not in '# \t'):
            continue
            
        # Contar TODAS las otras líneas (incluyendo vacías como separadores válidos)
        code_lines += 1
    
    return code_lines

def count_lines_python_strict(file_path):
    """Cuenta líneas de código Python excluyendo comentarios, líneas vacías y docstrings (versión estricta)"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    lines = content.split('\n')
    code_lines = 0
    in_multiline_string = False
    multiline_delimiter = None
    
    for line in lines:
        stripped = line.strip()
        
        # Línea vacía - NO CONTAR
        if not stripped:
            continue
            
        # Detectar inicio/fin de docstrings
        if '"""' in stripped or "'''" in stripped:
            if not in_multiline_string:
                # Buscar el delimitador
                if '"""' in stripped:
                    multiline_delimiter = '"""'
                else:
                    multiline_delimiter = "'''"
                
                # Verificar si el docstring termina en la misma línea
                delimiter_count = stripped.count(multiline_delimiter)
                if delimiter_count >= 2:
                    # Docstring de una línea, no contar
                    continue
                else:
                    in_multiline_string = True
                    continue
            else:
                # Fin del docstring
                if multiline_delimiter in stripped:
                    in_multiline_string = False
                    multiline_delimiter = None
                    continue
        
        # Si estamos en un docstring, no contar
        if in_multiline_string:
            continue
            
        # Comentario de línea completa
        if stripped.startswith('#'):
            continue
            
        # Línea de código válida
        code_lines += 1
    
    return code_lines

def count_lines_html(file_path):
    """Cuenta líneas de HTML excluyendo comentarios (mantiene líneas vacías)"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    # Remover comentarios HTML
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    lines = content.split('\n')
    return len(lines)

def count_lines_css(file_path):
    """Cuenta líneas de CSS excluyendo comentarios (mantiene líneas vacías)"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    # Remover comentarios CSS
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    lines = content.split('\n')
    return len(lines)

def count_lines_js(file_path):
    """Cuenta líneas de JavaScript excluyendo comentarios (mantiene líneas vacías)"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    # Remover comentarios de bloque
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    lines = content.split('\n')
    code_lines = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Comentario de línea completa
        if stripped.startswith('//'):
            continue
            
        # Contar todas las otras líneas (incluyendo vacías)
        code_lines += 1
    
    return code_lines

def scan_directory(root_path, strict_mode=False):
    """Escanea el directorio y cuenta líneas por tipo de archivo"""
    results = {
        'python': {'files': [], 'total_lines': 0, 'total_files': 0},
        'html': {'files': [], 'total_lines': 0, 'total_files': 0},
        'css': {'files': [], 'total_lines': 0, 'total_files': 0},
        'js': {'files': [], 'total_lines': 0, 'total_files': 0}
    }
    
    # Seleccionar función de conteo para Python
    python_count_func = count_lines_python_strict if strict_mode else count_lines_python
    
    # Extensiones a buscar
    extensions = {
        '.py': ('python', python_count_func),
        '.html': ('html', count_lines_html),
        '.css': ('css', count_lines_css),
        '.js': ('js', count_lines_js)
    }
    
    # Directorios a excluir
    excluded_dirs = {
        '__pycache__', 
        '.git', 
        'node_modules', 
        '.venv',
        'venv',
        '.env',
        'env',
        '.idea',
        '.vscode',
        'dist',
        'build'
    }
    
    for root, dirs, files in os.walk(root_path):
        # Excluir directorios que no queremos analizar
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = Path(file).suffix.lower()
            
            if file_ext in extensions:
                file_type, count_function = extensions[file_ext]
                
                try:
                    lines = count_function(file_path)
                    relative_path = os.path.relpath(file_path, root_path)
                    
                    results[file_type]['files'].append({
                        'path': relative_path,
                        'lines': lines
                    })
                    results[file_type]['total_lines'] += lines
                    results[file_type]['total_files'] += 1
                    
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
    
    return results

def generate_report(results, strict_mode=False):
    """Genera el reporte de líneas de código"""
    mode_text = "ESTRICTO" if strict_mode else "INCLUSIVO"
    exclusions = "comentarios, líneas vacías y docstrings" if strict_mode else "solo comentarios y docstrings"
    
    print("=" * 80)
    print(f"INFORME DE LÍNEAS DE CÓDIGO - PROYECTO ADMIN_MANAGE_EVENTS ({mode_text})")
    print("=" * 80)
    print(f"(Excluyendo {exclusions})")
    print("(Carpetas omitidas: .venv, __pycache__, .git, migrations, node_modules)")
    print()
    
    total_files = 0
    total_lines = 0
    
    for file_type in ['python', 'html', 'css', 'js']:
        data = results[file_type]
        if data['total_files'] > 0:
            print(f"📁 ARCHIVOS {file_type.upper()}")
            print("-" * 50)
            
            # Ordenar archivos por líneas (descendente)
            sorted_files = sorted(data['files'], key=lambda x: x['lines'], reverse=True)
            
            for file_info in sorted_files:
                print(f"  {file_info['path']:<50} {file_info['lines']:>6} líneas")
            
            print(f"\n  Total archivos {file_type}: {data['total_files']}")
            print(f"  Total líneas {file_type}: {data['total_lines']}")
            print()
            
            total_files += data['total_files']
            total_lines += data['total_lines']
    
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Total de archivos analizados: {total_files}")
    print(f"Total de líneas de código: {total_lines}")
    
    # Desglose por tipo
    print("\nDesglose por tipo de archivo:")
    for file_type in ['python', 'html', 'css', 'js']:
        data = results[file_type]
        if data['total_files'] > 0:
            percentage = (data['total_lines'] / total_lines * 100) if total_lines > 0 else 0
            print(f"  {file_type.capitalize():<10}: {data['total_lines']:>6} líneas ({percentage:>5.1f}%)")
    
    print("=" * 80)

if __name__ == "__main__":
    # Ruta del proyecto (ajusta según sea necesario)
    project_path = "."  # Directorio actual
    
    print("Analizando proyecto...")
    print(f"Directorio: {os.path.abspath(project_path)}")
    print()
    
    # Generar ambos reportes
    print("MODO INCLUSIVO (incluye líneas vacías como separadores):")
    print("=" * 80)
    results_inclusive = scan_directory(project_path, strict_mode=False)
    generate_report(results_inclusive, strict_mode=False)
    
    print("\n\n")
    print("MODO ESTRICTO (excluye líneas vacías):")
    print("=" * 80)
    results_strict = scan_directory(project_path, strict_mode=True)
    generate_report(results_strict, strict_mode=True)