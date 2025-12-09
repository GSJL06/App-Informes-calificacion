# Test Images Folder

Esta carpeta contiene imágenes de prueba para reemplazar en las plantillas.

## Estructura de nombres

Los archivos deben seguir esta convención de nombres:

- `header_<section>_<index>.<ext>` - Imágenes para headers
- `body_<index>.<ext>` - Imágenes para el cuerpo del documento
- `footer_<section>_<index>.<ext>` - Imágenes para footers

### Ejemplos:

```
header_0_0.png    # Primera imagen del header de la primera sección
header_0_1.png    # Segunda imagen del header de la primera sección
body_0.png        # Primera imagen del cuerpo
body_1.png        # Segunda imagen del cuerpo
footer_0_0.png    # Primera imagen del footer de la primera sección
```

## Uso

```bash
python generar_informe.py \
    --plantilla templates/plantilla_desempeno.docx \
    --datos ejemplo_datos.json \
    --imagenes test_images/ \
    --output output/informe_generado.docx
```

## Formatos soportados

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)
