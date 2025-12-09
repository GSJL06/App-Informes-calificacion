"""
Script de prueba completo para todas las funcionalidades del DOCX Editor
"""
import sys
import json
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.document_processor import DocumentProcessor
from core.placeholder_engine import PlaceholderEngine
from core.footer_editor import FooterEditor


def test_document_processor():
    """Prueba el DocumentProcessor"""
    print("\n" + "="*60)
    print("🔧 PRUEBA: DocumentProcessor")
    print("="*60)
    
    doc_path = "test_documents/contrato_template.docx"
    
    # Cargar documento
    processor = DocumentProcessor(doc_path)
    processor.load()
    print(f"✓ Documento cargado: {doc_path}")
    
    # Obtener estadísticas
    stats = processor.get_statistics()
    print(f"\n📊 Estadísticas:")
    print(f"   - Párrafos: {stats['paragraphs']}")
    print(f"   - Secciones: {stats['sections']}")
    print(f"   - Tablas: {stats['tables']}")
    print(f"   - Tamaño: {stats['file_size_bytes'] / 1024:.2f} KB")
    
    # Validar integridad
    validation = processor.validate_integrity()
    print(f"\n✅ Validación:")
    for check, passed in validation.items():
        icon = "✓" if passed else "✗"
        print(f"   {icon} {check}")
    
    # Crear backup
    backup_path = processor.create_backup()
    print(f"\n💾 Backup creado: {backup_path}")
    
    return True


def test_placeholder_engine():
    """Prueba el PlaceholderEngine"""
    print("\n" + "="*60)
    print("🔧 PRUEBA: PlaceholderEngine")
    print("="*60)
    
    doc_path = "test_documents/contrato_template.docx"
    
    processor = DocumentProcessor(doc_path)
    processor.load()
    
    engine = PlaceholderEngine(processor.document)
    
    # Encontrar placeholders
    placeholders = engine.find_all_placeholders()
    print(f"\n📋 Placeholders encontrados ({len(placeholders)}):")
    for ph in sorted(placeholders):
        print(f"   - {{{{{ph}}}}}")
    
    # Obtener reporte
    report = engine.get_placeholder_report()
    print(f"\n📊 Reporte:")
    print(f"   - Total únicos: {report['total_unique']}")
    print(f"   - Ubicaciones: {report['locations']}")
    
    # Cargar datos
    with open("test_documents/datos_contrato.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Vista previa
    preview = engine.preview_replacements(data, max_examples=3)
    print(f"\n👁️ Vista previa de reemplazos:")
    for ex in preview:
        print(f"   Original: {ex['original'][:50]}...")
        print(f"   Reemplazado: {ex['replaced'][:50]}...")
        print()
    
    # Realizar reemplazos
    count = engine.replace_all(data)
    print(f"✓ Reemplazos realizados: {count}")
    
    # Guardar
    output_path = "test_documents/contrato_procesado.docx"
    processor.save(output_path)
    print(f"✓ Documento guardado: {output_path}")
    
    return True


def test_footer_editor():
    """Prueba el FooterEditor"""
    print("\n" + "="*60)
    print("🔧 PRUEBA: FooterEditor")
    print("="*60)
    
    doc_path = "test_documents/contrato_template.docx"
    
    processor = DocumentProcessor(doc_path)
    processor.load()
    
    editor = FooterEditor(processor.document)
    
    # Obtener información de secciones
    sections_count = editor.get_sections_count()
    print(f"\n📄 Secciones en el documento: {sections_count}")
    
    # Obtener footer actual
    footer_text = editor.get_footer_text(section_idx=0)
    print(f"\n📝 Footer actual:")
    print(f"   {footer_text}")
    
    # Obtener footer con formato
    footer_data = editor.get_footer_with_format(section_idx=0)
    print(f"\n📋 Footer con formato:")
    for para in footer_data:
        print(f"   Texto: {para['text']}")
        print(f"   Alineación: {para['alignment']}")
    
    # Actualizar footer
    new_footer = "Soluciones Digitales S.L. - Documento Confidencial - 2024"
    editor.update_footer_text(new_footer, section_idx=0, preserve_format=True)
    print(f"\n✓ Footer actualizado: {new_footer}")
    
    # Guardar
    output_path = "test_documents/contrato_footer_editado.docx"
    processor.save(output_path)
    print(f"✓ Documento guardado: {output_path}")
    
    return True


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🚀 DOCX EDITOR - PRUEBAS COMPLETAS")
    print("="*60)
    
    results = {}
    
    try:
        results['DocumentProcessor'] = test_document_processor()
    except Exception as e:
        print(f"❌ Error en DocumentProcessor: {e}")
        results['DocumentProcessor'] = False
    
    try:
        results['PlaceholderEngine'] = test_placeholder_engine()
    except Exception as e:
        print(f"❌ Error en PlaceholderEngine: {e}")
        results['PlaceholderEngine'] = False
    
    try:
        results['FooterEditor'] = test_footer_editor()
    except Exception as e:
        print(f"❌ Error en FooterEditor: {e}")
        results['FooterEditor'] = False
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    for test, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"   {icon} {test}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 ¡Todas las pruebas pasaron!" if all_passed else "⚠️ Algunas pruebas fallaron"))
    
    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

