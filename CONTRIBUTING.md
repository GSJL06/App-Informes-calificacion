# Guía de Contribución - DOCX Editor

¡Gracias por tu interés en contribuir al proyecto! Esta guía te ayudará a configurar tu entorno de desarrollo y entender nuestras prácticas.

## 📋 Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Estándares de Código](#estándares-de-código)
3. [Testing](#testing)
4. [Workflow de Contribución](#workflow-de-contribución)
5. [Mejores Prácticas](#mejores-prácticas)
6. [Performance Guidelines](#performance-guidelines)

---

## Configuración del Entorno

### 1. Fork y Clone

```bash
# Fork del repositorio en GitHub
# Luego clone tu fork
git clone https://github.com/TU-USUARIO/docx-editor.git
cd docx-editor

# Agregar upstream remote
git remote add upstream https://github.com/ORIGINAL/docx-editor.git
```

### 2. Entorno de Desarrollo

```bash
# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Instalar en modo desarrollo con dependencias extra
pip install -e ".[dev]"

# Instalar pre-commit hooks
pip install pre-commit
pre-commit install
```

### 3. Estructura del Proyecto

```
docx-editor/
├── src/                    # Código fuente
│   ├── core/              # Módulos principales
│   ├── api/               # REST API
│   ├── cli/               # CLI commands
│   └── utils/             # Utilidades
├── tests/                 # Test suite
│   ├── unit/             # Tests unitarios
│   ├── integration/      # Tests de integración
│   └── fixtures/         # Datos de prueba
├── config/               # Configuración
├── docker/              # Docker files
└── docs/                # Documentación
```

---

## Estándares de Código

### Python Style Guide

Seguimos **PEP 8** con algunas extensiones:

```python
# ✅ Bueno
def process_document(file_path: Path, options: Dict[str, Any]) -> ProcessResult:
    """
    Procesa un documento DOCX aplicando las opciones especificadas.

    Args:
        file_path: Ruta al archivo DOCX
        options: Diccionario con opciones de procesamiento

    Returns:
        Resultado del procesamiento

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValidationError: Si el documento es inválido
    """
    logger.info(f"Procesando: {file_path}")
    # ... implementación
    return result

# ❌ Malo
def proc(fp, opts):
    # Sin documentación
    print("Processing...")
    return data
```

### Docstrings

Usar formato **Google Style**:

```python
def calculate_stats(documents: List[Document]) -> Dict[str, float]:
    """Calcula estadísticas de múltiples documentos.

    Analiza una lista de documentos y retorna métricas agregadas
    incluyendo tamaño promedio, número de placeholders, etc.

    Args:
        documents: Lista de objetos Document a analizar

    Returns:
        Dict con las siguientes keys:
            - avg_size: Tamaño promedio en bytes
            - total_placeholders: Total de placeholders únicos
            - processing_time: Tiempo de procesamiento en segundos

    Example:
        >>> docs = [load_document("file1.docx"), load_document("file2.docx")]
        >>> stats = calculate_stats(docs)
        >>> print(stats['avg_size'])
        1024.5
    """
    pass
```

### Type Hints

Usar siempre type hints:

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

# ✅ Bueno
def update_footer(
    document: Document,
    text: str,
    section_idx: int = 0,
    preserve_format: bool = True
) -> None:
    pass

# ❌ Malo
def update_footer(document, text, section_idx=0, preserve_format=True):
    pass
```

### Naming Conventions

```python
# Variables y funciones: snake_case
document_processor = DocumentProcessor()
def process_placeholders():
    pass

# Clases: PascalCase
class FooterEditor:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 20 * 1024 * 1024
DEFAULT_TIMEOUT = 300

# Variables privadas: _prefijo
class Document:
    def __init__(self):
        self._internal_state = {}
```

### Formateo Automático

```bash
# Black - formatter
black src/ tests/

# isort - ordenar imports
isort src/ tests/

# Configuración en pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 88
```

---

## Testing

### Estructura de Tests

```python
# tests/unit/test_footer_editor.py
import pytest
from src.core.footer_editor import FooterEditor

class TestFooterEditor:
    """Suite de tests para FooterEditor"""

    @pytest.fixture
    def sample_document(self):
        """Fixture que retorna documento de prueba"""
        # Setup
        doc = create_test_document()
        yield doc
        # Teardown si es necesario

    def test_update_footer_basic(self, sample_document):
        """Test: Actualización básica de footer"""
        editor = FooterEditor(sample_document)
        editor.update_footer_text("Test footer")

        assert get_footer_text(sample_document) == "Test footer"

    def test_update_footer_preserve_format(self, sample_document):
        """Test: Preservación de formato"""
        editor = FooterEditor(sample_document)
        original_format = get_footer_format(sample_document)

        editor.update_footer_text("New text", preserve_format=True)
        new_format = get_footer_format(sample_document)

        assert new_format == original_format

    @pytest.mark.parametrize("section_idx,expected", [
        (0, "Footer 0"),
        (1, "Footer 1"),
        (2, "Footer 2"),
    ])
    def test_update_multiple_sections(self, sample_document, section_idx, expected):
        """Test: Actualización de múltiples secciones"""
        editor = FooterEditor(sample_document)
        editor.update_footer_text(expected, section_idx=section_idx)

        assert get_footer_text(sample_document, section_idx) == expected
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src --cov-report=html --cov-report=term

# Tests específicos
pytest tests/unit/test_footer_editor.py -v

# Con marcadores
pytest -m "not slow"

# Parallel execution
pytest -n auto
```

### Coverage Requirements

- **Mínimo**: 80% de cobertura
- **Target**: 90%+
- Todas las funciones públicas deben tener tests

```bash
# Generar reporte
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Workflow de Contribución

### 1. Crear Branch

```bash
# Actualizar main
git checkout main
git pull upstream main

# Crear feature branch
git checkout -b feature/descripcion-breve
# o para bugs:
git checkout -b fix/descripcion-del-bug
```

### 2. Desarrollo

```bash
# Hacer cambios
# Ejecutar tests regularmente
pytest

# Commit frecuentes con mensajes descriptivos
git add .
git commit -m "feat: agregar soporte para múltiples footers"
```

### Convenciones de Commits

Seguimos **Conventional Commits**:

```
tipo(scope): descripción breve

[cuerpo opcional]

[footer opcional]
```

**Tipos:**

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato, no afecta código
- `refactor`: Refactorización
- `test`: Agregar o modificar tests
- `chore`: Mantenimiento

**Ejemplos:**

```bash
git commit -m "feat(footer): agregar soporte para numeración de páginas"
git commit -m "fix(placeholder): corregir regex para variables con guiones"
git commit -m "docs: actualizar README con ejemplos de API"
git commit -m "test(core): agregar tests para DocumentProcessor"
```

### 3. Pull Request

```bash
# Push a tu fork
git push origin feature/mi-feature

# Crear PR en GitHub
# Descripción debe incluir:
# - Qué cambia y por qué
# - Cómo testear
# - Screenshots si aplica
# - Link a issue relacionado
```

**Template de PR:**

```markdown
## Descripción

Breve descripción de los cambios.

## Tipo de Cambio

- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## Cómo Testear

1. Paso 1
2. Paso 2
3. Resultado esperado

## Checklist

- [ ] Tests agregados/actualizados
- [ ] Documentación actualizada
- [ ] Code style verificado (black, isort)
- [ ] Tests pasando
- [ ] Coverage no disminuye

## Issues Relacionados

Closes #123
```

---

## Mejores Prácticas

### 1. Manejo de Errores

```python
# ✅ Bueno - Específico y con contexto
try:
    processor = DocumentProcessor(file_path)
    processor.load()
except FileNotFoundError:
    logger.error(f"Archivo no encontrado: {file_path}")
    raise
except ValidationError as e:
    logger.error(f"Documento inválido: {e}")
    raise

# ❌ Malo - Catch all
try:
    # código
except Exception:
    pass  # Silencia errores
```

### 2. Logging

```python
import logging
logger = logging.getLogger(__name__)

# Niveles apropiados
logger.debug(f"Detalle interno: {variable}")     # Debugging
logger.info(f"Procesando: {file}")               # Info general
logger.warning(f"Placeholder sin datos: {key}")  # Advertencias
logger.error(f"Error al procesar: {error}")      # Errores
logger.critical(f"Sistema inestable: {issue}")   # Crítico

# ✅ Usar f-strings en logger
logger.info(f"Procesados {count} documentos")

# ❌ Evitar concatenación
logger.info("Procesados " + str(count) + " documentos")
```

### 3. Performance

```python
# ✅ Bueno - Usar comprensiones
placeholders = {match.group(1) for match in pattern.finditer(text)}

# ❌ Malo - Loop manual
placeholders = set()
for match in pattern.finditer(text):
    placeholders.add(match.group(1))

# ✅ Usar generators para datos grandes
def process_large_file(file_path):
    with open(file_path) as f:
        for line in f:  # No carga todo en memoria
            yield process_line(line)

# ✅ Context managers
with DocumentProcessor(file_path) as processor:
    processor.load()
    # ... operaciones
    # Auto-cleanup
```

### 4. Documentos de Prueba

```python
# Crear fixtures reutilizables
@pytest.fixture
def sample_docx():
    """Documento con placeholders y footer"""
    doc = Document()
    doc.add_paragraph("Cliente: {{cliente}}")
    section = doc.sections[0]
    section.footer.add_paragraph("© {{empresa}}")

    temp_path = Path(tempfile.mktemp(suffix='.docx'))
    doc.save(temp_path)
    yield temp_path
    temp_path.unlink()  # Cleanup
```

---

## Performance Guidelines

### Objetivos

- **Carga de documento**: < 500ms para archivos de 5MB
- **Procesamiento**: < 2s por documento
- **Memoria**: < 500MB peak para archivos de 20MB

### Medición

```python
from src.core.document_processor import PerformanceMonitor

monitor = PerformanceMonitor()

monitor.start("operation")
# ... código
monitor.end("operation")

metrics = monitor.get_metrics()
print(f"Tiempo: {metrics['operation']:.3f}s")
```

### Optimizaciones

```python
# ✅ Batch processing de runs
for para in document.paragraphs:
    # Procesar todos los runs juntos
    para_text = para.text
    # ... procesamiento

# ❌ Procesar run por run
for para in document.paragraphs:
    for run in para.runs:
        # Múltiples accesos al DOM
        text = run.text
```

---

## Code Review Checklist

### Para Autores

- [ ] Código sigue style guide
- [ ] Tests agregados y pasando
- [ ] Documentación actualizada
- [ ] Sin warnings de linter
- [ ] Coverage no disminuye
- [ ] Performance considerado
- [ ] Logs apropiados
- [ ] Manejo de errores robusto

### Para Reviewers

- [ ] Código claro y mantenible
- [ ] Tests adecuados
- [ ] Sin security issues
- [ ] Performance aceptable
- [ ] Documentación suficiente
- [ ] Edge cases considerados

---

## Recursos

### Documentación

- [Python docx docs](https://python-docx.readthedocs.io/)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [Click docs](https://click.palletsprojects.com/)

### Herramientas

- [Black playground](https://black.vercel.app/)
- [mypy docs](http://mypy-lang.org/)
- [pytest docs](https://docs.pytest.org/)

### Contacto

- **Issues**: GitHub Issues
- **Discord**: [Link al servidor]
- **Email**: dev@ejemplo.com

---

¡Gracias por contribuir! 🎉
