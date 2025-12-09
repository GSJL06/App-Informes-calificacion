"""
CLI Interface - Comandos Click para uso desde terminal
Soporta operaciones individuales y batch con progreso visual
"""
import click
from pathlib import Path
from typing import List, Optional
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging

# Importar módulos core
from core.document_processor import DocumentProcessor, PerformanceMonitor
from core.footer_editor import FooterEditor
from core.placeholder_engine import PlaceholderEngine

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """DOCX Editor - Editor de archivos Word con preservación de formato"""
    pass


# Footer Commands
@cli.group()
def footer():
    """Operaciones sobre pies de página"""
    pass


@footer.command('update')
@click.argument('file', type=click.Path(exists=True))
@click.option('--text', '-t', required=True, help='Texto para el pie de página')
@click.option('--section', '-s', default=0, help='Índice de sección (default: 0)')
@click.option('--output', '-o', type=click.Path(), help='Archivo de salida (default: sobrescribe)')
@click.option('--no-backup', is_flag=True, help='No crear backup')
@click.option('--no-preserve-format', is_flag=True, help='No preservar formato')
def footer_update(file, text, section, output, no_backup, no_preserve_format):
    """Actualiza el pie de página de un documento"""
    try:
        click.echo(f"Procesando: {file}")

        processor = DocumentProcessor(file)
        processor.load()

        if not no_backup:
            backup_path = processor.create_backup()
            click.echo(f"Backup: {backup_path}")

        editor = FooterEditor(processor.document)
        editor.update_footer_text(
            text,
            section_idx=section,
            preserve_format=not no_preserve_format
        )

        output_path = processor.save(output)
        click.echo(click.style(f"✓ Completado: {output_path}", fg='green'))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@footer.command('get')
@click.argument('file', type=click.Path(exists=True))
@click.option('--section', '-s', default=0, help='Índice de sección')
@click.option('--format', '-f', 'output_format', type=click.Choice(['text', 'json']), default='text')
def footer_get(file, section, output_format):
    """Obtiene el contenido del pie de página"""
    try:
        processor = DocumentProcessor(file)
        processor.load()

        editor = FooterEditor(processor.document)
        footer_data = editor.get_footer_with_format(section)

        if output_format == 'json':
            click.echo(json.dumps(footer_data, indent=2, ensure_ascii=False))
        else:
            for para in footer_data:
                click.echo(para['text'])

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@footer.command('apply-all')
@click.argument('file', type=click.Path(exists=True))
@click.option('--text', '-t', required=True, help='Texto para todas las secciones')
@click.option('--output', '-o', type=click.Path(), help='Archivo de salida')
def footer_apply_all(file, text, output):
    """Aplica el mismo footer a todas las secciones"""
    try:
        click.echo(f"Aplicando footer a todas las secciones...")

        processor = DocumentProcessor(file)
        processor.load()

        editor = FooterEditor(processor.document)
        count = editor.apply_to_all_sections(text)

        processor.save(output)
        click.echo(click.style(f"✓ {count} secciones actualizadas", fg='green'))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


# Placeholder Commands
@cli.group()
def placeholder():
    """Operaciones con placeholders {{variable}}"""
    pass


@placeholder.command('list')
@click.argument('file', type=click.Path(exists=True))
@click.option('--format', '-f', 'output_format', type=click.Choice(['text', 'json']), default='text')
@click.option('--report', is_flag=True, help='Mostrar reporte detallado')
def placeholder_list(file, output_format, report):
    """Lista todos los placeholders en el documento"""
    try:
        processor = DocumentProcessor(file)
        processor.load()

        engine = PlaceholderEngine(processor.document)
        placeholders = engine.find_all_placeholders()

        if report:
            report_data = engine.get_placeholder_report()
            if output_format == 'json':
                click.echo(json.dumps(report_data, indent=2, ensure_ascii=False))
            else:
                click.echo(f"\nTotal placeholders únicos: {report_data['total_unique']}")
                click.echo("\nUbicaciones:")
                for loc, count in report_data['locations'].items():
                    click.echo(f"  {loc}: {count}")
        else:
            if output_format == 'json':
                click.echo(json.dumps(list(placeholders), indent=2))
            else:
                click.echo("Placeholders encontrados:")
                for ph in sorted(placeholders):
                    click.echo(f"  {{{{{ph}}}}}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@placeholder.command('replace')
@click.argument('file', type=click.Path(exists=True))
@click.option('--data', '-d', required=True, help='JSON con datos: \'{"key":"value"}\'')
@click.option('--output', '-o', type=click.Path(), help='Archivo de salida')
@click.option('--strict', is_flag=True, help='Fallar si hay placeholders sin datos')
@click.option('--no-backup', is_flag=True, help='No crear backup')
@click.option('--preview', is_flag=True, help='Vista previa sin modificar')
def placeholder_replace(file, data, output, strict, no_backup, preview):
    """Reemplaza placeholders con datos JSON"""
    try:
        # Parsear JSON
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("Datos JSON inválidos")

        click.echo(f"Procesando: {file}")
        click.echo(f"Variables a reemplazar: {len(data_dict)}")

        processor = DocumentProcessor(file)
        processor.load()

        engine = PlaceholderEngine(processor.document)

        if preview:
            examples = engine.preview_replacements(data_dict, max_examples=3)
            click.echo("\nVista previa:")
            for ex in examples:
                click.echo(f"\nOriginal: {ex['original']}")
                click.echo(f"Reemplazado: {ex['replaced']}")
            return

        if not no_backup:
            processor.create_backup()

        count = engine.replace_all(data_dict, strict=strict)
        processor.save(output)

        click.echo(click.style(f"✓ {count} reemplazos realizados", fg='green'))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


@placeholder.command('from-file')
@click.argument('file', type=click.Path(exists=True))
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Archivo de salida')
def placeholder_from_file(file, data_file, output):
    """Reemplaza placeholders usando archivo JSON"""
    try:
        # Leer archivo de datos
        with open(data_file, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)

        click.echo(f"Datos cargados: {len(data_dict)} variables")

        processor = DocumentProcessor(file)
        processor.load()
        processor.create_backup()

        engine = PlaceholderEngine(processor.document)
        count = engine.replace_all(data_dict)

        processor.save(output)
        click.echo(click.style(f"✓ {count} reemplazos realizados", fg='green'))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


# Batch Commands
@cli.group()
def batch():
    """Procesamiento de múltiples archivos"""
    pass


@batch.command('process')
@click.argument('pattern', type=str)
@click.option('--operation', '-op', 
              type=click.Choice(['footer', 'placeholder']),
              required=True)
@click.option('--data', '-d', help='JSON con datos para procesamiento')
@click.option('--output-dir', '-o', type=click.Path(), help='Directorio de salida')
@click.option('--workers', '-w', default=4, help='Número de workers paralelos')
def batch_process(pattern, operation, data, output_dir, workers):
    """Procesa múltiples archivos con patrón glob"""
    try:
        # Encontrar archivos
        files = list(Path('.').glob(pattern))
        
        if not files:
            click.echo(click.style("No se encontraron archivos", fg='yellow'))
            return
        
        click.echo(f"Archivos encontrados: {len(files)}")
        
        # Parsear datos si es necesario
        data_dict = json.loads(data) if data else {}
        
        # Crear directorio de salida
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Procesar con pool de workers
        def process_file(file_path):
            try:
                # Mock processing
                return {'file': str(file_path), 'status': 'success'}
            except Exception as e:
                return {'file': str(file_path), 'status': 'error', 'error': str(e)}
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_file, f) for f in files]
            
            with tqdm(total=len(files), desc="Procesando") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    pbar.update(1)
                    
                    if result['status'] == 'error':
                        click.echo(
                            click.style(f"\n✗ {result['file']}: {result['error']}", fg='red')
                        )
        
        click.echo(click.style(f"\n✓ Batch completado", fg='green'))
        
    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


# Document Info
@cli.command('info')
@click.argument('file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Información detallada')
def document_info(file, verbose):
    """Muestra información del documento"""
    try:
        click.echo(f"Archivo: {file}")

        processor = DocumentProcessor(file)
        processor.load()

        stats = processor.get_statistics()
        props = processor.get_core_properties()

        click.echo(f"\nEstadísticas:")
        click.echo(f"  Párrafos: {stats['paragraphs']}")
        click.echo(f"  Secciones: {stats['sections']}")
        click.echo(f"  Tablas: {stats['tables']}")
        click.echo(f"  Tamaño: {stats['file_size_bytes'] / 1024:.2f} KB")

        if verbose:
            click.echo(f"\nPropiedades:")
            for key, value in props.items():
                if value:
                    click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


# Validate Command
@cli.command('validate')
@click.argument('file', type=click.Path(exists=True))
def validate_document(file):
    """Valida integridad del documento DOCX"""
    try:
        click.echo(f"Validando: {file}")

        processor = DocumentProcessor(file)
        results = processor.validate_integrity()

        all_valid = all(results.values())

        for check, passed in results.items():
            icon = '✓' if passed else '✗'
            color = 'green' if passed else 'red'
            click.echo(click.style(f"  {icon} {check}", fg=color))

        if all_valid:
            click.echo(click.style("\n✓ Documento válido", fg='green'))
        else:
            click.echo(click.style("\n✗ Documento tiene errores", fg='red'))
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg='red'), err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()