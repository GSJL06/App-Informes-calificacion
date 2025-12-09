"""
Script para crear automáticamente todos los archivos del proyecto
Ejecutar: python download_project.py
"""

import os
from pathlib import Path

# Contenido de cada archivo
FILES = {
    "src/__init__.py": "",
    
    "src/core/__init__.py": """# Core modules
from .document_processor import DocumentProcessor, PerformanceMonitor
from .footer_editor import FooterEditor
from .placeholder_engine import PlaceholderEngine

__all__ = [
    'DocumentProcessor',
    'PerformanceMonitor',
    'FooterEditor',
    'PlaceholderEngine',
]
""",

    "src/utils/__init__.py": """# Utilities
from .exceptions import *
from .logger import setup_logger, get_logger

__all__ = [
    'setup_logger',
    'get_logger',
]
""",

    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# VS Code
.vscode/
*.code-workspace

# PyCharm
.idea/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Temp files
temp/
*.docx
!tests/fixtures/*.docx

# Logs
logs/
*.log

# Backups
backups/

# OS
.DS_Store
Thumbs.db
""",

    "src/api/__init__.py": "",
    "src/cli/__init__.py": "",
    "tests/__init__.py": "",
}

def create_file(file_path, content):
    """Crea un archivo con contenido"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Creado: {file_path}")

def main():
    print("="*60)
    print("CREANDO ESTRUCTURA DEL PROYECTO DOCX EDITOR")
    print("="*60)
    print()
    
    # Crear archivos
    for file_path, content in FILES.items():
        try:
            create_file(file_path, content)
        except Exception as e:
            print(f"❌ Error creando {file_path}: {e}")
    
    print()
    print("="*60)
    print("✅ ESTRUCTURA BÁSICA CREADA")
    print("="*60)
    print()
    print("PRÓXIMOS PASOS:")
    print("1. Copia el código de los artefactos a los archivos correspondientes")
    print("2. Ejecuta: python -m venv venv")
    print("3. Activa el entorno: venv\\Scripts\\activate (Windows)")
    print("4. Instala dependencias: pip install -r requirements.txt")
    print()

if __name__ == '__main__':
    main()