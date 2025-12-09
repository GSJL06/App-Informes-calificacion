"""
REST API Server - FastAPI con endpoints para procesamiento batch
Optimizado para concurrencia con pool de workers
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import tempfile
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime

# Importar módulos core
from core.document_processor import DocumentProcessor
from core.footer_editor import FooterEditor
from core.placeholder_engine import PlaceholderEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DOCX Editor API",
    description="API REST para edición de archivos DOCX con enfoque en pies de página",
    version="1.0.0"
)

# Pool de workers para procesamiento paralelo
WORKER_POOL = ThreadPoolExecutor(max_workers=4)
TEMP_DIR = Path(tempfile.gettempdir()) / "docx_editor"
TEMP_DIR.mkdir(exist_ok=True)


# Pydantic Models
class FooterUpdateRequest(BaseModel):
    text: str = Field(..., description="Nuevo texto para el pie de página")
    section_idx: int = Field(0, description="Índice de sección (default: 0)")
    preserve_format: bool = Field(True, description="Preservar formato existente")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "© 2024 Mi Empresa - Confidencial",
                "section_idx": 0,
                "preserve_format": True
            }
        }


class PlaceholderReplaceRequest(BaseModel):
    data: Dict[str, str] = Field(..., description="Diccionario de placeholders")
    strict: bool = Field(False, description="Fallar si hay placeholders sin datos")
    preserve_format: bool = Field(True, description="Preservar formato de texto")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "nombre": "Juan Pérez",
                    "fecha": "2024-12-05",
                    "empresa": "TechCorp"
                },
                "strict": False,
                "preserve_format": True
            }
        }


class BatchProcessRequest(BaseModel):
    operation: str = Field(..., description="Operación: 'footer' o 'placeholders'")
    footer_text: Optional[str] = None
    placeholder_data: Optional[Dict[str, str]] = None
    preserve_format: bool = True


class DocumentInfo(BaseModel):
    filename: str
    size_bytes: int
    sections: int
    paragraphs: int
    tables: int


# Health Check
@app.get("/health")
async def health_check():
    """Endpoint de salud del servicio"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "workers": WORKER_POOL._max_workers
    }


# Document Upload & Info
@app.post("/document/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    """
    Carga un documento DOCX y retorna información básica
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Solo archivos .docx permitidos")
    
    # Guardar temporalmente
    temp_path = TEMP_DIR / f"upload_{datetime.now().timestamp()}_{file.filename}"
    
    try:
        with temp_path.open('wb') as f:
            content = await file.read()
            f.write(content)

        processor = DocumentProcessor(str(temp_path))
        processor.load()
        stats = processor.get_statistics()

        return DocumentInfo(
            filename=file.filename,
            size_bytes=stats['file_size_bytes'],
            sections=stats['sections'],
            paragraphs=stats['paragraphs'],
            tables=stats['tables']
        )
    
    except Exception as e:
        logger.error(f"Error al cargar documento: {e}")
        raise HTTPException(500, f"Error al procesar documento: {str(e)}")
    
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


# Footer Operations
@app.post("/document/footer/update")
async def update_footer(
    file: UploadFile = File(...),
    request: FooterUpdateRequest = None
):
    """
    Actualiza el pie de página de un documento
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Solo archivos .docx permitidos")
    
    temp_input = TEMP_DIR / f"input_{datetime.now().timestamp()}_{file.filename}"
    temp_output = TEMP_DIR / f"output_{datetime.now().timestamp()}_{file.filename}"
    
    try:
        # Guardar archivo de entrada
        with temp_input.open('wb') as f:
            content = await file.read()
            f.write(content)

        # Procesar documento
        processor = DocumentProcessor(str(temp_input))
        processor.load()
        processor.create_backup()

        footer_editor = FooterEditor(processor.document)
        footer_editor.update_footer_text(
            request.text,
            section_idx=request.section_idx,
            preserve_format=request.preserve_format
        )

        processor.save(str(temp_output))

        # Retornar archivo modificado
        return FileResponse(
            temp_output,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"updated_{file.filename}"
        )
    
    except Exception as e:
        logger.error(f"Error actualizando footer: {e}")
        raise HTTPException(500, f"Error: {str(e)}")
    
    finally:
        # Cleanup en background
        pass


@app.get("/document/footer/get")
async def get_footer(
    file: UploadFile = File(...),
    section_idx: int = 0
):
    """
    Obtiene el contenido actual del pie de página
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Solo archivos .docx permitidos")
    
    temp_path = TEMP_DIR / f"read_{datetime.now().timestamp()}_{file.filename}"
    
    try:
        with temp_path.open('wb') as f:
            content = await file.read()
            f.write(content)

        processor = DocumentProcessor(str(temp_path))
        processor.load()

        footer_editor = FooterEditor(processor.document)
        footer_data = footer_editor.get_footer_with_format(section_idx)

        return {"footer": footer_data}
    
    except Exception as e:
        logger.error(f"Error leyendo footer: {e}")
        raise HTTPException(500, f"Error: {str(e)}")
    
    finally:
        if temp_path.exists():
            temp_path.unlink()


# Placeholder Operations
@app.post("/document/placeholders/replace")
async def replace_placeholders(
    file: UploadFile = File(...),
    request: PlaceholderReplaceRequest = None
):
    """
    Reemplaza placeholders {{variable}} en el documento
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Solo archivos .docx permitidos")
    
    temp_input = TEMP_DIR / f"input_{datetime.now().timestamp()}_{file.filename}"
    temp_output = TEMP_DIR / f"output_{datetime.now().timestamp()}_{file.filename}"
    
    try:
        with temp_input.open('wb') as f:
            content = await file.read()
            f.write(content)

        processor = DocumentProcessor(str(temp_input))
        processor.load()
        processor.create_backup()

        engine = PlaceholderEngine(processor.document)
        replacements = engine.replace_all(
            request.data,
            strict=request.strict,
            preserve_format=request.preserve_format
        )

        processor.save(str(temp_output))

        return FileResponse(
            temp_output,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"processed_{file.filename}",
            headers={"X-Replacements-Count": str(replacements)}
        )
    
    except Exception as e:
        logger.error(f"Error reemplazando placeholders: {e}")
        raise HTTPException(500, f"Error: {str(e)}")


@app.get("/document/placeholders/list")
async def list_placeholders(file: UploadFile = File(...)):
    """
    Lista todos los placeholders encontrados en el documento
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Solo archivos .docx permitidos")
    
    temp_path = TEMP_DIR / f"read_{datetime.now().timestamp()}_{file.filename}"
    
    try:
        with temp_path.open('wb') as f:
            content = await file.read()
            f.write(content)

        processor = DocumentProcessor(str(temp_path))
        processor.load()

        engine = PlaceholderEngine(processor.document)
        placeholders = engine.find_all_placeholders()
        report = engine.get_placeholder_report()

        return {
            "placeholders": list(placeholders),
            "report": report
        }
    
    except Exception as e:
        logger.error(f"Error listando placeholders: {e}")
        raise HTTPException(500, f"Error: {str(e)}")
    
    finally:
        if temp_path.exists():
            temp_path.unlink()


# Batch Processing
@app.post("/batch/process")
async def batch_process(
    files: List[UploadFile] = File(...),
    request: BatchProcessRequest = None,
    background_tasks: BackgroundTasks = None
):
    """
    Procesa múltiples documentos en paralelo
    """
    if len(files) > 10:
        raise HTTPException(400, "Máximo 10 archivos por batch")
    
    results = []
    
    def process_single(file_data: tuple) -> Dict:
        """Procesa un solo documento"""
        filename, content = file_data
        temp_path = TEMP_DIR / f"batch_{datetime.now().timestamp()}_{filename}"
        output_path = TEMP_DIR / f"batch_out_{datetime.now().timestamp()}_{filename}"

        try:
            # Guardar
            with temp_path.open('wb') as f:
                f.write(content)

            # Procesar según operación
            processor = DocumentProcessor(str(temp_path))
            processor.load()

            if request and request.operation == 'footer' and request.footer_text:
                editor = FooterEditor(processor.document)
                editor.apply_to_all_sections(request.footer_text)
            elif request and request.operation == 'placeholders' and request.placeholder_data:
                engine = PlaceholderEngine(processor.document)
                engine.replace_all(request.placeholder_data, preserve_format=request.preserve_format)

            processor.save(str(output_path))

            return {
                "filename": filename,
                "status": "success",
                "message": "Procesado correctamente"
            }

        except Exception as e:
            return {
                "filename": filename,
                "status": "error",
                "message": str(e)
            }

        finally:
            if temp_path.exists():
                temp_path.unlink()
            if output_path.exists():
                output_path.unlink()
    
    # Leer contenido de archivos antes del procesamiento paralelo
    file_data_list = []
    for file in files:
        content = file.file.read()
        file_data_list.append((file.filename, content))

    # Procesamiento paralelo
    futures = [
        WORKER_POOL.submit(process_single, file_data)
        for file_data in file_data_list
    ]
    
    for future in as_completed(futures):
        results.append(future.result())
    
    return {
        "total": len(files),
        "results": results
    }


# Cleanup endpoint
@app.post("/admin/cleanup")
async def cleanup_temp():
    """Limpia archivos temporales"""
    count = 0
    for file in TEMP_DIR.glob("*"):
        try:
            file.unlink()
            count += 1
        except Exception:
            pass
    
    return {"deleted_files": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)