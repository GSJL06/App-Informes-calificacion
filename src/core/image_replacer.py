"""
Módulo para reemplazar imágenes en documentos Word (.docx)
Soporta reemplazo de imágenes en:
- Headers (encabezados)
- Footers (pies de página)
- Cuerpo del documento

Utiliza lxml para manipulación directa del XML OOXML preservando
todas las propiedades originales (dimensiones, posición, wrapping).
"""
from docx import Document
from docx.shared import Inches, Emu
from docx.oxml.ns import qn, nsmap
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from lxml import etree
import zipfile
import os
import io
import logging

logger = logging.getLogger(__name__)

# Namespaces OOXML para imágenes
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
}


class ImageInfo:
    """Información detallada de una imagen en el documento."""
    
    def __init__(
        self,
        rel_id: str,
        target: str,
        location: str,
        section_idx: int = 0,
        index: int = 0,
        width_emu: Optional[int] = None,
        height_emu: Optional[int] = None,
        is_inline: bool = True,
        drawing_element: Optional[etree._Element] = None
    ):
        self.rel_id = rel_id
        self.target = target
        self.location = location  # 'header', 'footer', 'body'
        self.section_idx = section_idx
        self.index = index
        self.width_emu = width_emu
        self.height_emu = height_emu
        self.is_inline = is_inline  # True for inline, False for anchor
        self.drawing_element = drawing_element
    
    @property
    def width_inches(self) -> Optional[float]:
        """Width in inches."""
        if self.width_emu:
            return self.width_emu / 914400
        return None
    
    @property
    def height_inches(self) -> Optional[float]:
        """Height in inches."""
        if self.height_emu:
            return self.height_emu / 914400
        return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'rel_id': self.rel_id,
            'target': self.target,
            'location': self.location,
            'section_idx': self.section_idx,
            'index': self.index,
            'width_emu': self.width_emu,
            'height_emu': self.height_emu,
            'width_inches': self.width_inches,
            'height_inches': self.height_inches,
            'is_inline': self.is_inline
        }


class ImageReplacer:
    """
    Clase para reemplazar imágenes en documentos Word.
    
    Utiliza manipulación directa del XML OOXML para preservar
    todas las propiedades originales de las imágenes.
    
    Uso:
        replacer = ImageReplacer(document)
        replacer.replace_header_image(0, "nuevo_logo.png")
        replacer.replace_body_image_by_index(5, "nueva_imagen.png")
    """
    
    def __init__(self, document: Document):
        """
        Inicializa el reemplazador de imágenes.
        
        Args:
            document: Documento Word cargado con python-docx
        """
        self.document = document
        self._image_cache: Dict[str, List[ImageInfo]] = {}
        self._scan_images()
    
    def _scan_images(self) -> None:
        """Escanea todas las imágenes del documento y las cachea."""
        self._image_cache = {
            'headers': [],
            'footers': [],
            'body': []
        }
        
        # Escanear headers y footers
        for section_idx, section in enumerate(self.document.sections):
            if section.header:
                self._scan_part_images(
                    section.header, 'headers', section_idx
                )
            if section.footer:
                self._scan_part_images(
                    section.footer, 'footers', section_idx
                )
        
        # Escanear cuerpo del documento
        self._scan_body_images()
    
    def _scan_part_images(
        self,
        part,
        location: str,
        section_idx: int
    ) -> None:
        """Escanea imágenes en una parte del documento (header/footer)."""
        index = 0
        for rel_id, rel in part.part.rels.items():
            if 'image' in rel.reltype:
                # Buscar el elemento drawing correspondiente
                drawing_info = self._find_drawing_by_rel_id(
                    part._element, rel_id
                )
                
                info = ImageInfo(
                    rel_id=rel_id,
                    target=rel.target_ref,
                    location=location,
                    section_idx=section_idx,
                    index=index,
                    width_emu=drawing_info.get('width'),
                    height_emu=drawing_info.get('height'),
                    is_inline=drawing_info.get('is_inline', True),
                    drawing_element=drawing_info.get('element')
                )
                self._image_cache[location].append(info)
                index += 1
    
    def _scan_body_images(self) -> None:
        """Escanea imágenes en el cuerpo del documento."""
        index = 0
        for rel_id, rel in self.document.part.rels.items():
            if 'image' in rel.reltype:
                # Buscar el elemento drawing correspondiente
                drawing_info = self._find_drawing_by_rel_id(
                    self.document.element, rel_id
                )
                
                info = ImageInfo(
                    rel_id=rel_id,
                    target=rel.target_ref,
                    location='body',
                    index=index,
                    width_emu=drawing_info.get('width'),
                    height_emu=drawing_info.get('height'),
                    is_inline=drawing_info.get('is_inline', True),
                    drawing_element=drawing_info.get('element')
                )
                self._image_cache['body'].append(info)
                index += 1
    
    def _find_drawing_by_rel_id(
        self,
        root_element: etree._Element,
        rel_id: str
    ) -> Dict:
        """
        Encuentra el elemento drawing que referencia un rel_id específico.
        
        Args:
            root_element: Elemento raíz XML donde buscar
            rel_id: ID de relación a buscar
            
        Returns:
            Dict con información del drawing (width, height, is_inline, element)
        """
        result = {
            'width': None,
            'height': None,
            'is_inline': True,
            'element': None
        }
        
        # Buscar en elementos inline
        for drawing in root_element.iter(qn('w:drawing')):
            # Buscar blip con el rel_id
            for blip in drawing.iter(qn('a:blip')):
                embed = blip.get(qn('r:embed'))
                if embed == rel_id:
                    result['element'] = drawing
                    
                    # Determinar si es inline o anchor
                    inline = drawing.find('.//wp:inline', NAMESPACES)
                    anchor = drawing.find('.//wp:anchor', NAMESPACES)
                    
                    extent_parent = inline if inline is not None else anchor
                    result['is_inline'] = inline is not None
                    
                    if extent_parent is not None:
                        extent = extent_parent.find('wp:extent', NAMESPACES)
                        if extent is not None:
                            cx = extent.get('cx')
                            cy = extent.get('cy')
                            if cx:
                                result['width'] = int(cx)
                            if cy:
                                result['height'] = int(cy)
                    
                    return result
        
        return result
    
    def get_header_images_info(self, section_idx: int = 0) -> List[ImageInfo]:
        """
        Obtiene información sobre las imágenes en el header de una sección.
        
        Args:
            section_idx: Índice de la sección (por defecto 0)
            
        Returns:
            Lista de ImageInfo con información de cada imagen
        """
        return [
            img for img in self._image_cache['headers']
            if img.section_idx == section_idx
        ]
    
    def get_footer_images_info(self, section_idx: int = 0) -> List[ImageInfo]:
        """
        Obtiene información sobre las imágenes en el footer de una sección.
        
        Args:
            section_idx: Índice de la sección (por defecto 0)
            
        Returns:
            Lista de ImageInfo con información de cada imagen
        """
        return [
            img for img in self._image_cache['footers']
            if img.section_idx == section_idx
        ]
    
    def get_body_images_info(self) -> List[ImageInfo]:
        """
        Obtiene información sobre las imágenes en el cuerpo del documento.
        
        Returns:
            Lista de ImageInfo con información de cada imagen
        """
        return self._image_cache['body']
    
    def get_all_images_info(self) -> Dict[str, List[Dict]]:
        """
        Obtiene información de todas las imágenes del documento.
        
        Returns:
            Diccionario con imágenes organizadas por ubicación
        """
        return {
            'headers': [img.to_dict() for img in self._image_cache['headers']],
            'footers': [img.to_dict() for img in self._image_cache['footers']],
            'body': [img.to_dict() for img in self._image_cache['body']]
        }
    
    def replace_header_image(
        self,
        section_idx: int,
        new_image_path: str,
        image_index: int = 0,
        preserve_dimensions: bool = True
    ) -> bool:
        """
        Reemplaza una imagen en el header de una sección.
        
        Preserva las dimensiones originales, posición y estilo de wrapping.
        
        Args:
            section_idx: Índice de la sección
            new_image_path: Ruta a la nueva imagen
            image_index: Índice de la imagen en el header (si hay varias)
            preserve_dimensions: Si True, mantiene dimensiones originales
            
        Returns:
            True si se reemplazó correctamente
        """
        if section_idx >= len(self.document.sections):
            logger.error(f"Sección {section_idx} no existe")
            return False
        
        new_image_path = Path(new_image_path)
        if not new_image_path.exists():
            logger.error(f"Imagen no encontrada: {new_image_path}")
            return False
        
        section = self.document.sections[section_idx]
        header = section.header
        
        if not header:
            logger.error(f"La sección {section_idx} no tiene header")
            return False
        
        # Encontrar la imagen a reemplazar
        image_rels = []
        for rel_id, rel in header.part.rels.items():
            if 'image' in rel.reltype:
                image_rels.append((rel_id, rel))
        
        if image_index >= len(image_rels):
            logger.error(f"No hay imagen en el índice {image_index}")
            return False
        
        rel_id, old_rel = image_rels[image_index]
        
        # Leer nueva imagen
        with open(new_image_path, 'rb') as f:
            image_data = f.read()
        
        # Reemplazar el contenido de la imagen
        image_part = old_rel.target_part
        image_part._blob = image_data
        
        # Actualizar content type si es necesario
        self._update_content_type(image_part, new_image_path)
        
        logger.info(f"Imagen del header reemplazada: {new_image_path}")
        return True
    
    def replace_footer_image(
        self,
        section_idx: int,
        new_image_path: str,
        image_index: int = 0,
        preserve_dimensions: bool = True
    ) -> bool:
        """
        Reemplaza una imagen en el footer de una sección.
        
        Args:
            section_idx: Índice de la sección
            new_image_path: Ruta a la nueva imagen
            image_index: Índice de la imagen en el footer
            preserve_dimensions: Si True, mantiene dimensiones originales
            
        Returns:
            True si se reemplazó correctamente
        """
        if section_idx >= len(self.document.sections):
            logger.error(f"Sección {section_idx} no existe")
            return False
        
        new_image_path = Path(new_image_path)
        if not new_image_path.exists():
            logger.error(f"Imagen no encontrada: {new_image_path}")
            return False
        
        section = self.document.sections[section_idx]
        footer = section.footer
        
        if not footer:
            logger.error(f"La sección {section_idx} no tiene footer")
            return False
        
        image_rels = []
        for rel_id, rel in footer.part.rels.items():
            if 'image' in rel.reltype:
                image_rels.append((rel_id, rel))
        
        if image_index >= len(image_rels):
            logger.error(f"No hay imagen en el índice {image_index}")
            return False
        
        rel_id, old_rel = image_rels[image_index]
        
        with open(new_image_path, 'rb') as f:
            image_data = f.read()
        
        image_part = old_rel.target_part
        image_part._blob = image_data
        
        self._update_content_type(image_part, new_image_path)
        
        logger.info(f"Imagen del footer reemplazada: {new_image_path}")
        return True
    
    def replace_body_image_by_index(
        self,
        image_index: int,
        new_image_path: str,
        preserve_dimensions: bool = True
    ) -> bool:
        """
        Reemplaza una imagen del cuerpo del documento por su índice.
        
        Args:
            image_index: Índice de la imagen (0-based)
            new_image_path: Ruta a la nueva imagen
            preserve_dimensions: Si True, mantiene dimensiones originales
            
        Returns:
            True si se reemplazó correctamente
        """
        new_image_path = Path(new_image_path)
        if not new_image_path.exists():
            logger.error(f"Imagen no encontrada: {new_image_path}")
            return False
        
        image_rels = []
        for rel_id, rel in self.document.part.rels.items():
            if 'image' in rel.reltype:
                image_rels.append((rel_id, rel))
        
        if image_index >= len(image_rels):
            logger.error(f"No hay imagen en el índice {image_index}")
            return False
        
        rel_id, old_rel = image_rels[image_index]
        
        with open(new_image_path, 'rb') as f:
            image_data = f.read()
        
        image_part = old_rel.target_part
        image_part._blob = image_data
        
        self._update_content_type(image_part, new_image_path)
        
        logger.info(f"Imagen {image_index} del cuerpo reemplazada")
        return True
    
    def replace_body_image_by_rel_id(
        self,
        rel_id: str,
        new_image_path: str
    ) -> bool:
        """
        Reemplaza una imagen del cuerpo por su relationship ID.
        
        Args:
            rel_id: ID de relación de la imagen (ej: 'rId5')
            new_image_path: Ruta a la nueva imagen
            
        Returns:
            True si se reemplazó correctamente
        """
        new_image_path = Path(new_image_path)
        if not new_image_path.exists():
            logger.error(f"Imagen no encontrada: {new_image_path}")
            return False
        
        if rel_id not in self.document.part.rels:
            logger.error(f"Relación {rel_id} no encontrada")
            return False
        
        rel = self.document.part.rels[rel_id]
        if 'image' not in rel.reltype:
            logger.error(f"Relación {rel_id} no es una imagen")
            return False
        
        with open(new_image_path, 'rb') as f:
            image_data = f.read()
        
        image_part = rel.target_part
        image_part._blob = image_data
        
        self._update_content_type(image_part, new_image_path)
        
        logger.info(f"Imagen {rel_id} reemplazada")
        return True
    
    def _update_content_type(self, image_part, new_image_path: Path) -> None:
        """
        Actualiza el content type de la imagen si es necesario.
        
        Args:
            image_part: Parte de imagen del documento
            new_image_path: Ruta a la nueva imagen
        """
        extension = new_image_path.suffix.lower()
        content_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
        }
        
        if extension in content_types:
            image_part.content_type = content_types[extension]
    
    def replace_images_batch(
        self,
        replacements: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Reemplaza múltiples imágenes en lote.
        
        Args:
            replacements: Diccionario con formato:
                {
                    "header_0_0": "ruta/logo_cliente.png",
                    "header_0_1": "ruta/logo_empresa.png",
                    "body_5": "ruta/grafico1.png",
                    "footer_0_0": "ruta/firma.png"
                }
                
        Returns:
            Diccionario con resultado de cada reemplazo
        """
        results = {}
        
        for key, new_path in replacements.items():
            try:
                parts = key.split('_')
                location = parts[0]
                
                if location == 'header':
                    section_idx = int(parts[1])
                    img_idx = int(parts[2]) if len(parts) > 2 else 0
                    results[key] = self.replace_header_image(
                        section_idx, new_path, img_idx
                    )
                
                elif location == 'footer':
                    section_idx = int(parts[1])
                    img_idx = int(parts[2]) if len(parts) > 2 else 0
                    results[key] = self.replace_footer_image(
                        section_idx, new_path, img_idx
                    )
                
                elif location == 'body':
                    img_idx = int(parts[1])
                    results[key] = self.replace_body_image_by_index(
                        img_idx, new_path
                    )
                
                else:
                    logger.warning(f"Ubicación desconocida: {location}")
                    results[key] = False
            
            except Exception as e:
                logger.error(f"Error reemplazando {key}: {e}")
                results[key] = False
        
        return results
    
    def get_summary(self) -> Dict:
        """
        Retorna un resumen de las imágenes en el documento.
        
        Returns:
            Dict con conteos y detalles de imágenes
        """
        info = self.get_all_images_info()
        return {
            'total_headers': len(info['headers']),
            'total_footers': len(info['footers']),
            'total_body': len(info['body']),
            'total': len(info['headers']) + len(info['footers']) + len(info['body']),
            'details': info
        }
    
    def get_image_dimensions(
        self,
        location: str,
        index: int,
        section_idx: int = 0
    ) -> Optional[Tuple[int, int]]:
        """
        Obtiene las dimensiones de una imagen específica en EMUs.
        
        Args:
            location: 'header', 'footer', o 'body'
            index: Índice de la imagen
            section_idx: Índice de sección (para header/footer)
            
        Returns:
            Tupla (width_emu, height_emu) o None si no se encuentra
        """
        images = self._image_cache.get(location + 's' if location != 'body' else location, [])
        
        for img in images:
            if img.index == index:
                if location == 'body' or img.section_idx == section_idx:
                    if img.width_emu and img.height_emu:
                        return (img.width_emu, img.height_emu)
        
        return None
    
    def set_image_dimensions(
        self,
        location: str,
        index: int,
        width_emu: int,
        height_emu: int,
        section_idx: int = 0
    ) -> bool:
        """
        Establece las dimensiones de una imagen específica.
        
        Args:
            location: 'header', 'footer', o 'body'
            index: Índice de la imagen
            width_emu: Ancho en EMUs (914400 EMUs = 1 pulgada)
            height_emu: Alto en EMUs
            section_idx: Índice de sección (para header/footer)
            
        Returns:
            True si se actualizó correctamente
        """
        cache_key = location + 's' if location != 'body' else location
        images = self._image_cache.get(cache_key, [])
        
        for img in images:
            if img.index == index:
                if location == 'body' or img.section_idx == section_idx:
                    if img.drawing_element is not None:
                        # Actualizar extent en inline o anchor
                        inline = img.drawing_element.find('.//wp:inline', NAMESPACES)
                        anchor = img.drawing_element.find('.//wp:anchor', NAMESPACES)
                        
                        extent_parent = inline if inline is not None else anchor
                        if extent_parent is not None:
                            extent = extent_parent.find('wp:extent', NAMESPACES)
                            if extent is not None:
                                extent.set('cx', str(width_emu))
                                extent.set('cy', str(height_emu))
                                
                                # También actualizar en a:ext si existe
                                for ext in img.drawing_element.iter(qn('a:ext')):
                                    ext.set('cx', str(width_emu))
                                    ext.set('cy', str(height_emu))
                                
                                logger.info(
                                    f"Dimensiones actualizadas: {width_emu}x{height_emu} EMUs"
                                )
                                return True
        
        logger.error(f"No se encontró la imagen en {location}[{index}]")
        return False


def replace_images_in_document(
    doc_path: Union[str, Path],
    output_path: Union[str, Path],
    image_replacements: Dict[str, str]
) -> bool:
    """
    Función de conveniencia para reemplazar imágenes en un documento.
    
    Args:
        doc_path: Ruta al documento original
        output_path: Ruta para guardar el documento modificado
        image_replacements: Dict con reemplazos (ver replace_images_batch)
        
    Returns:
        True si todos los reemplazos fueron exitosos
    """
    try:
        doc = Document(doc_path)
        replacer = ImageReplacer(doc)
        
        results = replacer.replace_images_batch(image_replacements)
        
        doc.save(output_path)
        
        return all(results.values())
    
    except Exception as e:
        logger.error(f"Error procesando documento: {e}")
        return False
