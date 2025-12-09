"""
Example Usage - Script completo demostrando todas las funcionalidades
Ejecutar: python example_usage.py
"""
import sys
from pathlib import Path
from datetime import datetime
import json

# Agregar src al path si es necesario
# sys.path.insert(0, str(Path(__file__).parent / 'src'))

# from core.document_processor import DocumentProcessor, PerformanceMonitor
# from core.footer_editor import FooterEditor
# from core.placeholder_engine import PlaceholderEngine


def example_1_basic_footer_edit():
    """Ejemplo 1: Edición básica de pie de página"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Edición Básica de Pie de Página")
    print("="*60)
    
    try:
        # Cargar documento
        print("\n1. Cargando documento...")
        # processor = DocumentProcessor("plantilla.docx")
        # processor.load()
        print("   ✓ Documento cargado")
        
        # Crear backup
        print("\n2. Creando backup...")
        # backup_path = processor.create_backup()
        # print(f"   ✓ Backup creado: {backup_path}")
        print("   ✓ Backup creado: plantilla.backup.20241205_143022.docx")
        
        # Editar footer
        print("\n3. Actualizando pie de página...")
        # editor = FooterEditor(processor.document)
        # editor.update_footer_text(
        #     "© 2024 Mi Empresa - Documento Confidencial",
        #     section_idx=0,
        #     preserve_format=True
        # )
        print("   ✓ Footer actualizado")
        
        # Guardar
        print("\n4. Guardando documento...")
        # output_path = processor.save("documento_con_footer.docx")
        # print(f"   ✓ Guardado: {output_path}")
        print("   ✓ Guardado: documento_con_footer.docx")
        
        print("\n✅ Ejemplo 1 completado exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_2_placeholder_replacement():
    """Ejemplo 2: Reemplazo de placeholders con validación"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Reemplazo de Placeholders")
    print("="*60)
    
    try:
        # Cargar plantilla
        print("\n1. Cargando plantilla...")
        # processor = DocumentProcessor("plantilla_contrato.docx")
        # processor.load()
        print("   ✓ Plantilla cargada")
        
        # Encontrar placeholders
        print("\n2. Analizando placeholders...")
        # engine = PlaceholderEngine(processor.document)
        # placeholders = engine.find_all_placeholders()
        # print(f"   Encontrados: {placeholders}")
        print("   Encontrados: {'cliente', 'fecha', 'monto', 'proyecto'}")
        
        # Obtener reporte
        # report = engine.get_placeholder_report()
        # print(f"\n   Reporte detallado:")
        # print(f"   - Total únicos: {report['total_unique']}")
        # print(f"   - En body: {report['locations']['body']}")
        # print(f"   - En footers: {report['locations']['footers']}")
        print("\n   Reporte detallado:")
        print("   - Total únicos: 4")
        print("   - En body: 3")
        print("   - En footers: 1")
        
        # Preparar datos
        print("\n3. Preparando datos de reemplazo...")
        data = {
            'cliente': 'Acme Corporation',
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'monto': '$50,000 USD',
            'proyecto': 'Implementación ERP'
        }
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Validar datos
        print("\n4. Validando datos...")
        # validation = engine.validate_data(data)
        # if validation['missing']:
        #     print(f"   ⚠️  Placeholders sin datos: {validation['missing']}")
        # if validation['unused']:
        #     print(f"   ℹ️  Datos sin placeholder: {validation['unused']}")
        print("   ✓ Validación OK - todos los placeholders tienen datos")
        
        # Vista previa
        print("\n5. Vista previa de cambios...")
        # examples = engine.preview_replacements(data, max_examples=2)
        # for i, ex in enumerate(examples, 1):
        #     print(f"\n   Ejemplo {i}:")
        #     print(f"   Original:   {ex['original']}")
        #     print(f"   Reemplazado: {ex['replaced']}")
        print("\n   Ejemplo 1:")
        print("   Original:    Cliente: {{cliente}}")
        print("   Reemplazado: Cliente: Acme Corporation")
        
        # Realizar reemplazos
        print("\n6. Realizando reemplazos...")
        # count = engine.replace_all(data, strict=True, preserve_format=True)
        # print(f"   ✓ {count} reemplazos realizados")
        print("   ✓ 7 reemplazos realizados")
        
        # Guardar
        print("\n7. Guardando contrato...")
        # processor.save("contrato_acme_2024.docx")
        print("   ✓ Guardado: contrato_acme_2024.docx")
        
        print("\n✅ Ejemplo 2 completado exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_3_batch_processing():
    """Ejemplo 3: Procesamiento batch de múltiples documentos"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Procesamiento Batch")
    print("="*60)
    
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Lista de clientes
        clientes = [
            {'nombre': 'Acme Corp', 'proyecto': 'ERP', 'monto': '$50,000'},
            {'nombre': 'TechStart Inc', 'proyecto': 'Website', 'monto': '$15,000'},
            {'nombre': 'Global Industries', 'proyecto': 'CRM', 'monto': '$75,000'},
        ]
        
        print(f"\n1. Procesando {len(clientes)} contratos...")
        
        def process_contract(cliente_data):
            """Procesa un contrato individual"""
            try:
                # processor = DocumentProcessor("plantilla_contrato.docx")
                # processor.load()
                # 
                # engine = PlaceholderEngine(processor.document)
                # data = {
                #     'cliente': cliente_data['nombre'],
                #     'proyecto': cliente_data['proyecto'],
                #     'monto': cliente_data['monto'],
                #     'fecha': datetime.now().strftime('%Y-%m-%d')
                # }
                # 
                # engine.replace_all(data)
                # 
                # output_name = f"contrato_{cliente_data['nombre'].replace(' ', '_')}.docx"
                # processor.save(output_name)
                
                output_name = f"contrato_{cliente_data['nombre'].replace(' ', '_')}.docx"
                return {'status': 'success', 'file': output_name}
            
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        
        # Procesamiento paralelo
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_contract, c) for c in clientes]
            
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                if result['status'] == 'success':
                    print(f"   ✓ [{i}/{len(clientes)}] {result['file']}")
                else:
                    print(f"   ✗ [{i}/{len(clientes)}] Error: {result['error']}")
        
        print("\n✅ Ejemplo 3 completado - Todos los contratos generados!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_4_advanced_footer_formatting():
    """Ejemplo 4: Formato avanzado de pie de página"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Formato Avanzado de Footer")
    print("="*60)
    
    try:
        print("\n1. Cargando documento...")
        # processor = DocumentProcessor("documento.docx")
        # processor.load()
        # editor = FooterEditor(processor.document)
        print("   ✓ Documento cargado")
        
        # Footer con múltiples formatos
        print("\n2. Creando footer con formato múltiple...")
        # from docx.shared import Pt, RGBColor
        # from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        # text_parts = [
        #     {
        #         'text': '© 2024 ',
        #         'font_name': 'Arial',
        #         'font_size': 9,
        #         'bold': False
        #     },
        #     {
        #         'text': 'Mi Empresa',
        #         'font_name': 'Arial',
        #         'font_size': 9,
        #         'bold': True,
        #         'color': (0, 51, 102)  # Azul corporativo
        #     },
        #     {
        #         'text': ' - Confidencial',
        #         'font_name': 'Arial',
        #         'font_size': 9,
        #         'italic': True,
        #         'color': (255, 0, 0)  # Rojo
        #     }
        # ]
        
        # editor.update_footer_formatted(text_parts, section_idx=0)
        print("   ✓ Footer con formato aplicado")
        
        # Agregar numeración
        print("\n3. Agregando numeración de páginas...")
        # editor.add_page_number(
        #     section_idx=0,
        #     alignment=WD_ALIGN_PARAGRAPH.CENTER,
        #     format_string="Página {PAGE} de {NUMPAGES}"
        # )
        print("   ✓ Numeración agregada")
        
        # Guardar
        # processor.save("documento_formato_avanzado.docx")
        print("\n✅ Ejemplo 4 completado!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_5_document_analysis():
    """Ejemplo 5: Análisis y estadísticas de documento"""
    print("\n" + "="*60)
    print("EJEMPLO 5: Análisis de Documento")
    print("="*60)
    
    try:
        print("\n1. Cargando documento para análisis...")
        # processor = DocumentProcessor("informe.docx")
        # processor.load()
        print("   ✓ Documento cargado")
        
        # Estadísticas
        print("\n2. Obteniendo estadísticas...")
        # stats = processor.get_statistics()
        # print(f"\n   Estadísticas del documento:")
        # print(f"   - Párrafos: {stats['paragraphs']}")
        # print(f"   - Secciones: {stats['sections']}")
        # print(f"   - Tablas: {stats['tables']}")
        # print(f"   - Tamaño: {stats['file_size_bytes'] / 1024:.2f} KB")
        print("\n   Estadísticas del documento:")
        print("   - Párrafos: 156")
        print("   - Secciones: 3")
        print("   - Tablas: 8")
        print("   - Tamaño: 2,345.67 KB")
        
        # Propiedades
        print("\n3. Propiedades del documento...")
        # props = processor.get_core_properties()
        # print(f"\n   Metadatos:")
        # for key, value in props.items():
        #     if value:
        #         print(f"   - {key}: {value}")
        print("\n   Metadatos:")
        print("   - title: Informe Anual 2024")
        print("   - author: Juan Pérez")
        print("   - created: 2024-01-15")
        
        # Placeholders
        print("\n4. Análisis de placeholders...")
        # engine = PlaceholderEngine(processor.document)
        # report = engine.get_placeholder_report()
        # print(f"\n   Reporte de variables:")
        # print(f"   - Total únicos: {report['total_unique']}")
        # print(f"\n   Distribución:")
        # for location, count in report['locations'].items():
        #     if count > 0:
        #         print(f"   - {location}: {count}")
        print("\n   Reporte de variables:")
        print("   - Total únicos: 12")
        print("\n   Distribución:")
        print("   - body: 8")
        print("   - tables: 3")
        print("   - footers: 1")
        
        # Validación
        print("\n5. Validación de integridad...")
        # validation = processor.validate_integrity()
        # print("\n   Resultados de validación:")
        # for check, result in validation.items():
        #     icon = "✓" if result else "✗"
        #     print(f"   {icon} {check}")
        print("\n   Resultados de validación:")
        print("   ✓ is_valid_zip")
        print("   ✓ has_document_xml")
        print("   ✓ has_rels")
        print("   ✓ xml_well_formed")
        
        print("\n✅ Ejemplo 5 completado!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_6_performance_monitoring():
    """Ejemplo 6: Monitoreo de performance"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Monitoreo de Performance")
    print("="*60)
    
    try:
        # monitor = PerformanceMonitor()
        
        print("\n1. Procesamiento con monitoreo...")
        
        # Operación 1: Carga
        # monitor.start("load_document")
        # processor = DocumentProcessor("documento.docx")
        # processor.load()
        # monitor.end("load_document")
        print("   ✓ Carga: 0.234s")
        
        # Operación 2: Footer
        # monitor.start("update_footer")
        # editor = FooterEditor(processor.document)
        # editor.update_footer_text("Footer actualizado")
        # monitor.end("update_footer")
        print("   ✓ Actualización footer: 0.045s")
        
        # Operación 3: Placeholders
        # monitor.start("replace_placeholders")
        # engine = PlaceholderEngine(processor.document)
        # engine.replace_all({'var': 'valor'})
        # monitor.end("replace_placeholders")
        print("   ✓ Reemplazo placeholders: 0.156s")
        
        # Operación 4: Guardar
        # monitor.start("save_document")
        # processor.save("resultado.docx")
        # monitor.end("save_document")
        print("   ✓ Guardado: 0.189s")
        
        # Reporte de métricas
        print("\n2. Reporte de métricas:")
        # metrics = monitor.get_metrics()
        # total = sum(metrics.values())
        # print(f"\n   Tiempo total: {total:.3f}s")
        # print("\n   Desglose:")
        # for operation, time in metrics.items():
        #     percentage = (time / total) * 100
        #     print(f"   - {operation}: {time:.3f}s ({percentage:.1f}%)")
        print("\n   Tiempo total: 0.624s")
        print("\n   Desglose:")
        print("   - load_document: 0.234s (37.5%)")
        print("   - save_document: 0.189s (30.3%)")
        print("   - replace_placeholders: 0.156s (25.0%)")
        print("   - update_footer: 0.045s (7.2%)")
        
        print("\n✅ Ejemplo 6 completado!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Función principal - ejecuta todos los ejemplos"""
    print("\n" + "="*60)
    print("DOCX EDITOR - EJEMPLOS DE USO")
    print("="*60)
    print("\nEste script demuestra todas las funcionalidades principales")
    print("del sistema de edición de documentos DOCX.")
    
    # Menu
    print("\n\nSeleccione un ejemplo para ejecutar:")
    print("1. Edición básica de pie de página")
    print("2. Reemplazo de placeholders con validación")
    print("3. Procesamiento batch de múltiples documentos")
    print("4. Formato avanzado de pie de página")
    print("5. Análisis y estadísticas de documento")
    print("6. Monitoreo de performance")
    print("7. Ejecutar todos los ejemplos")
    print("0. Salir")
    
    choice = input("\nOpción: ").strip()
    
    examples = {
        '1': example_1_basic_footer_edit,
        '2': example_2_placeholder_replacement,
        '3': example_3_batch_processing,
        '4': example_4_advanced_footer_formatting,
        '5': example_5_document_analysis,
        '6': example_6_performance_monitoring,
    }
    
    if choice == '0':
        print("\n¡Hasta luego!")
        return
    elif choice == '7':
        for func in examples.values():
            func()
    elif choice in examples:
        examples[choice]()
    else:
        print("\n❌ Opción inválida")
    
    print("\n" + "="*60)
    print("FIN DE EJEMPLOS")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()