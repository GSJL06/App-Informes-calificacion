# DOCX Editor - Editor Profesional de Archivos Word

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production-brightgreen)

Editor de archivos DOCX de alto rendimiento con enfoque en **pies de página** y **procesamiento de plantillas con variables**. Diseñado para manejar documentos de hasta 20MB preservando completamente el formato original.

## 🎯 Características Principales

- ✅ **Edición de Pies de Página**: Modificación completa con preservación de formato (fuentes, estilos, colores)
- ✅ **Procesamiento de Placeholders**: Sistema `{{variable}}` para plantillas dinámicas
- ✅ **Preservación de Formato**: Mantiene estilos, fuentes, colores y alineación
- ✅ **Procesamiento Batch**: Pool de workers para múltiples documentos (2-4 simultáneos)
- ✅ **API REST**: Interfaz FastAPI completa y documentada
- ✅ **CLI Potente**: Comandos Click para uso desde terminal
- ✅ **Validación Robusta**: Verificación de integridad XML y estructura OOXML
- ✅ **Backup Automático**: Versionado timestamped antes de modificaciones
- ✅ **Docker Ready**: Containerización completa con docker-compose

## 📋 Requisitos

- Python 3.9 o superior
- 512MB RAM mínimo (recomendado 1GB para procesamiento batch)
- Plataformas soportadas: Windows, macOS, Linux

## 🚀 Instalación

### Instalación vía pip (recomendado)

```bash
# Clonar repositorio
git clone https://github.com/yourusername/docx-editor.git
cd docx-editor

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o en Windows: venv\Scripts\activate

# Instalar paquete
pip install -e .

# Verificar instalación
docx-editor --version
```

### Instalación con Docker

```bash
# Build image
docker build -t docx-editor -f docker/Dockerfile .

# Ejecutar API
docker run -p 8000:8000 docx-editor

# O usar docker-compose
docker-compose up -d
```

## 📖 Guía de Uso Rápido

### CLI - Línea de Comandos

#### 1. Actualizar Pie de Página

```bash
# Actualizar footer en primera sección
docx-editor footer update documento.docx \
  --text "© 2024 Mi Empresa - Confidencial" \
  --output documento_modificado.docx

# Actualizar en sección específica
docx-editor footer update documento.docx \
  --text "Página confidencial" \
  --section 2

# Aplicar mismo footer a todas las secciones
docx-editor footer apply-all documento.docx \
  --text "© 2024 Global Corp"
```

#### 2. Ver Contenido de Footer

```bash
# Ver footer actual
docx-editor footer get documento.docx

# Ver en formato JSON
docx-editor footer get documento.docx --format json
```

#### 3. Reemplazar Placeholders

```bash
# Reemplazo con JSON inline
docx-editor placeholder replace plantilla.docx \
  --data '{"nombre":"Juan Pérez","fecha":"2024-12-05","empresa":"TechCorp"}' \
  --output salida.docx

# Vista previa sin modificar
docx-editor placeholder replace plantilla.docx \
  --data '{"nombre":"María"}' \
  --preview

# Desde archivo JSON
docx-editor placeholder from-file plantilla.docx datos.json \
  --output resultado.docx
```

#### 4. Listar Placeholders

```bash
# Listar todas las variables
docx-editor placeholder list plantilla.docx

# Reporte detallado
docx-editor placeholder list plantilla.docx --report --format json
```

#### 5. Procesamiento Batch

```bash
# Procesar múltiples archivos
docx-editor batch process "contratos/*.docx" \
  --operation placeholder \
  --data '{"cliente":"Acme Corp","año":"2024"}' \
  --output-dir contratos_procesados \
  --workers 4
```

#### 6. Información del Documento

```bash
# Info básica
docx-editor info documento.docx

# Información detallada
docx-editor info documento.docx --verbose
```

#### 7. Validar Documento

```bash
docx-editor validate documento.docx
```

### API REST

#### Iniciar Servidor

```bash
# Desarrollo
uvicorn src.api.rest_server:app --reload --port 8000

# Producción
gunicorn src.api.rest_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Documentación Interactiva

Accede a http://localhost:8000/docs para Swagger UI automático.

#### Ejemplos de Endpoints

**1. Actualizar Footer**

```bash
curl -X POST "http://localhost:8000/document/footer/update" \
  -F "file=@documento.docx" \
  -F 'request={"text":"© 2024 Confidencial","section_idx":0}' \
  --output documento_modificado.docx
```

**2. Reemplazar Placeholders**

```bash
curl -X POST "http://localhost:8000/document/placeholders/replace" \
  -F "file=@plantilla.docx" \
  -F 'request={"data":{"nombre":"Ana García","cargo":"Directora"},"strict":false}' \
  --output resultado.docx
```

**3. Listar Placeholders**

```bash
curl -X GET "http://localhost:8000/document/placeholders/list" \
  -F "file=@plantilla.docx"
```

**4. Procesamiento Batch**

```bash
curl -X POST "http://localhost:8000/batch/process" \
  -F "files=@doc1.docx" \
  -F "files=@doc2.docx" \
  -F 'request={"operation":"placeholder","placeholder_data":{"var":"value"}}'
```

### Uso como Librería Python

```python
from docx_editor.core import DocumentProcessor, FooterEditor, PlaceholderEngine

# Cargar documento
processor = DocumentProcessor("documento.docx")
processor.load()
processor.create_backup()

# Editar footer
footer_editor = FooterEditor(processor.document)
footer_editor.update_footer_text(
    "© 2024 Mi Empresa",
    section_idx=0,
    preserve_format=True
)

# Reemplazar placeholders
engine = PlaceholderEngine(processor.document)
data = {
    "nombre": "Juan Pérez",
    "fecha": "2024-12-05",
    "empresa": "TechCorp"
}
replacements = engine.replace_all(data, strict=False)
print(f"Reemplazos realizados: {replacements}")

# Guardar
processor.save("documento_modificado.docx")
```

## 🏗️ Arquitectura

```
docx-editor/
├── src/
│   ├── core/                    # Motor principal
│   │   ├── document_processor.py   # Procesador de documentos
│   │   ├── footer_editor.py        # Editor de footers
│   │   ├── placeholder_engine.py   # Motor de placeholders
│   │   ├── validator.py            # Validación
│   │   └── backup_manager.py       # Sistema de backups
│   ├── api/                     # REST API
│   │   ├── rest_server.py          # FastAPI server
│   │   └── schemas.py              # Pydantic models
│   └── cli/                     # CLI interface
│       └── commands.py             # Click commands
├── tests/                       # Test suite
├── config/                      # Configuración
├── docker/                      # Docker files
└── requirements.txt             # Dependencias
```

## ⚡ Optimización de Rendimiento

### Objetivos de Performance

- **Procesamiento**: < 2 segundos por documento de 5MB
- **Memoria**: < 500MB RAM pico para archivos de 20MB
- **Concurrencia**: 2-4 documentos simultáneos (configurable)

### Configuración de Workers

```python
# CLI
docx-editor batch process "*.docx" --workers 4

# API (docker-compose.yml)
environment:
  - WORKER_POOL_SIZE=4
```

## 🔒 Consideraciones de Seguridad

- ✅ Validación de tamaño de archivo (límite 20MB configurable)
- ✅ Verificación de integridad XML
- ✅ Usuario no-root en containers Docker
- ✅ Límites de recursos en docker-compose
- ✅ Backup automático antes de modificaciones

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_footer.py -v
```

## 📊 Ejemplos de Casos de Uso

### 1. Contratos Masivos

```bash
# Generar 100 contratos desde plantilla
for cliente in $(cat clientes.txt); do
  docx-editor placeholder replace plantilla_contrato.docx \
    --data "{\"cliente\":\"$cliente\",\"fecha\":\"2024-12-05\"}" \
    --output "contratos/contrato_${cliente}.docx"
done
```

### 2. Actualización de Footers Corporativos

```bash
# Actualizar footer en todos los documentos
docx-editor batch process "documentos/**/*.docx" \
  --operation footer \
  --data '{"text":"© 2024 Acme Corp - Todos los derechos reservados"}' \
  --workers 4
```

### 3. Reportes Dinámicos

```python
# Generar reporte desde base de datos
import json
from docx_editor.core import DocumentProcessor, PlaceholderEngine

# Datos desde DB
data = fetch_report_data_from_db()  # {"ventas": "1.2M", "trimestre": "Q4"}

processor = DocumentProcessor("plantilla_reporte.docx")
processor.load()

engine = PlaceholderEngine(processor.document)
engine.replace_all(data)

processor.save(f"reporte_{data['trimestre']}.docx")
```

## 🛠️ Troubleshooting

### Error: "Archivo excede límite de 20MB"

```python
# Aumentar límite en código
from docx_editor.core import DocumentProcessor
DocumentProcessor.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### Error: "Placeholders sin datos"

```bash
# Usar modo no-estricto
docx-editor placeholder replace doc.docx \
  --data '{"nombre":"Juan"}' \
  # --strict flag NO incluido
```

### Documento Corrupto

```bash
# Validar primero
docx-editor validate documento.docx

# Restaurar desde backup
cp documento.backup.20241205_143022.docx documento.docx
```

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuir

Contribuciones son bienvenidas! Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guía de desarrollo.

## 📧 Soporte

- Issues: https://github.com/yourusername/docx-editor/issues
- Email: support@example.com
- Docs: https://docx-editor.readthedocs.io

## 🔄 Changelog

### v1.0.0 (2024-12-05)

- ✨ Release inicial
- ✅ Editor de footers completo
- ✅ Motor de placeholders
- ✅ API REST FastAPI
- ✅ CLI con Click
- ✅ Docker support
- ✅ Procesamiento batch

---

**Hecho con ❤️ para la comunidad de desarrolladores**
"# App-Informes-calificacion" 
