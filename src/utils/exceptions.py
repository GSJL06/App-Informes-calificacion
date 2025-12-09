"""
exceptions.py - Excepciones personalizadas del sistema
"""

class DocxEditorException(Exception):
    """Excepción base para todas las excepciones del sistema"""
    pass


class FileValidationError(DocxEditorException):
    """Error en la validación de archivos"""
    pass


class FileSizeExceededError(FileValidationError):
    """El archivo excede el tamaño máximo permitido"""
    def __init__(self, size_mb, max_size_mb):
        self.size_mb = size_mb
        self.max_size_mb = max_size_mb
        super().__init__(
            f"Archivo de {size_mb:.2f}MB excede límite de {max_size_mb}MB"
        )


class InvalidDocxFileError(FileValidationError):
    """El archivo no es un DOCX válido"""
    pass


class DocumentLoadError(DocxEditorException):
    """Error al cargar el documento"""
    pass


class PlaceholderError(DocxEditorException):
    """Error en el procesamiento de placeholders"""
    pass


class PlaceholderMissingDataError(PlaceholderError):
    """Placeholders sin datos en modo estricto"""
    def __init__(self, missing_placeholders):
        self.missing_placeholders = missing_placeholders
        super().__init__(
            f"Placeholders sin datos: {', '.join(missing_placeholders)}"
        )


class FooterEditError(DocxEditorException):
    """Error en la edición de pies de página"""
    pass


class SectionNotFoundError(FooterEditError):
    """Sección especificada no existe"""
    def __init__(self, section_idx, total_sections):
        self.section_idx = section_idx
        self.total_sections = total_sections
        super().__init__(
            f"Sección {section_idx} no existe (total: {total_sections})"
        )


class ValidationError(DocxEditorException):
    """Error en la validación de integridad"""
    pass


class BackupError(DocxEditorException):
    """Error al crear backup"""
    pass


class ProcessingTimeoutError(DocxEditorException):
    """El procesamiento excedió el tiempo límite"""
    def __init__(self, timeout_seconds):
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Procesamiento excedió límite de {timeout_seconds}s"
        )


# ============================================================
# logger.py - Sistema de logging configurado
# ============================================================

"""
logger.py - Sistema de logging centralizado
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Verde
        'WARNING': '\033[33m',  # Amarillo
        'ERROR': '\033[31m',    # Rojo
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str = "docx_editor",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    use_colors: bool = True
) -> logging.Logger:
    """
    Configura y retorna un logger
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path para archivo de log (opcional)
        max_bytes: Tamaño máximo del archivo de log
        backup_count: Número de backups a mantener
        use_colors: Usar colores en salida de consola
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if use_colors:
        console_formatter = ColoredFormatter(log_format, date_format)
    else:
        console_formatter = logging.Formatter(log_format, date_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File Handler (si se especifica)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "docx_editor") -> logging.Logger:
    """
    Obtiene un logger existente o crea uno nuevo
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configurar con valores por defecto
        log_dir = Path("logs")
        log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        setup_logger(name, log_file=log_file)
    
    return logger


class LogContext:
    """Context manager para logging temporal"""
    
    def __init__(self, logger: logging.Logger, level: str = "INFO"):
        self.logger = logger
        self.level = getattr(logging, level.upper())
        self.original_level = logger.level
    
    def __enter__(self):
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


# Ejemplo de uso
if __name__ == '__main__':
    # Setup básico
    logger = setup_logger("test_logger", level="DEBUG")
    
    logger.debug("Mensaje de debug")
    logger.info("Mensaje informativo")
    logger.warning("Advertencia")
    logger.error("Error")
    logger.critical("Crítico")
    
    # Context manager
    with LogContext(logger, "WARNING"):
        logger.debug("Esto no se verá")
        logger.warning("Esto sí se verá")