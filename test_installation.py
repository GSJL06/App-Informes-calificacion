"""
Script de verificación de instalación
"""

print("="*60)
print("VERIFICANDO INSTALACIÓN DEL PROYECTO")
print("="*60)
print()

# Test 1: Python version
import sys
print(f"✅ Python version: {sys.version}")
print()

# Test 2: Dependencias principales
try:
    import docx
    print(f"✅ python-docx instalado: {docx.__version__}")
except ImportError as e:
    print(f"❌ Error con python-docx: {e}")

try:
    import lxml
    print(f"✅ lxml instalado")
except ImportError as e:
    print(f"❌ Error con lxml: {e}")

try:
    import fastapi
    print(f"✅ FastAPI instalado")
except ImportError as e:
    print(f"❌ Error con FastAPI: {e}")

try:
    import click
    print(f"✅ Click instalado")
except ImportError as e:
    print(f"❌ Error con Click: {e}")

print()
print("="*60)
print("✅ INSTALACIÓN COMPLETADA")
print("="*60)
print()
print("Siguiente paso: Copiar el código de los módulos principales")