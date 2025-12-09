# Plantillas Refactorizadas - Guía de Uso

## Resumen

Este documento describe el sistema de plantillas dinámicas para generación de informes DOCX con soporte para:
- **Listas dinámicas**: Número variable de elementos bullet
- **Tablas dinámicas**: Número variable de filas
- **Placeholders escalares**: Valores de texto simples

## Placeholders por Plantilla

### plantilla_desempeno.docx

| Placeholder | Tipo | Descripción |
|-------------|------|-------------|
| `{{nombre_establecimiento}}` | Escalar | Nombre del establecimiento |
| `{{direccion}}` | Escalar | Dirección completa |
| `{{fecha_calificacion}}` | Escalar | Fecha de calificación |
| `{{numero_informe}}` | Escalar | Número de informe |
| `{{dispositivos}}` | Lista | Array de dispositivos en prueba |
| `{{responsables}}` | Tabla | Array de objetos con nombre, telefono, correo |

### plantilla_diseno.docx

| Placeholder | Tipo | Descripción |
|-------------|------|-------------|
| `{{nombre_establecimiento}}` | Escalar | Nombre del establecimiento |
| `{{titulo}}` | Escalar | Título del sistema |
| `{{fecha_firma}}` | Escalar | Fecha de firma |
| `{{equipos_calibrados}}` | Tabla | Array de equipos calibrados |

### plantilla_instalacion.docx

| Placeholder | Tipo | Descripción |
|-------------|------|-------------|
| `{{nombre_establecimiento}}` | Escalar | Nombre del establecimiento |
| `{{fecha_calificacion}}` | Escalar | Fecha de calificación |
| `{{pruebas_realizadas}}` | Lista | Array de pruebas realizadas |

### plantilla_operacion.docx

| Placeholder | Tipo | Descripción |
|-------------|------|-------------|
| `{{nombre_establecimiento}}` | Escalar | Nombre del establecimiento |
| `{{observaciones}}` | Lista | Array de observaciones |

## Estructura JSON Esperada

### Valores Escalares
```json
{
  "nombre_establecimiento": "Clínica San Rafael",
  "direccion": "Avenida Principal 456",
  "fecha_calificacion": "15/12/2024"
}
```

### Listas Dinámicas
```json
{
  "dispositivos": [
    "PRF196 NEVERA MED. FAST TRACK-P2-TA",
    "PRF250 NEVERA MED. BODEGA FARM. E8-PB1-TB",
    "PRF251 NEVERA MED. BODEGA FARM. E8-PB1-TC"
  ]
}
```

### Tablas Dinámicas
```json
{
  "responsables": [
    {
      "nombre": "Centro de monitoreo",
      "telefono": "6012345678",
      "correo": "monitoreo@clinica.com"
    },
    {
      "nombre": "Yesid Hoyos",
      "telefono": "3101234567",
      "correo": "yhoyos@clinica.com"
    }
  ]
}
```

## Guía de Migración

### Desde Formato Antiguo

**Antes (hardcoded):**
```
Listado de dispositivos en prueba
- PRF196 NEVERA MED. FAST TRACK-P2-TA
- PRF250 NEVERA MED. BODEGA FARM. E8-PB1-TB
```

**Después (placeholder):**
```
Listado de dispositivos en prueba
{{dispositivos}}
```

**JSON correspondiente:**
```json
{
  "dispositivos": [
    "PRF196 NEVERA MED. FAST TRACK-P2-TA",
    "PRF250 NEVERA MED. BODEGA FARM. E8-PB1-TB"
  ]
}
```

### Tablas con Datos Mixtos

**Antes:**
| Nombre | Teléfono | Correo |
|--------|----------|--------|
| Centro de monitoreo | {{telefono_monitoreo}} | |
| Darío Rojas | 3164433168 | |

**Después:**
| Nombre | Teléfono | Correo |
|--------|----------|--------|
| {{responsables.nombre}} | {{responsables.telefono}} | {{responsables.correo}} |

## Uso del Script de Refactorización

### Analizar Plantillas
```bash
# Analizar todas las plantillas
python refactorizar_plantillas.py --analizar

# Analizar una plantilla específica
python refactorizar_plantillas.py --plantilla templates/plantilla_desempeno.docx --analizar

# Guardar análisis en JSON
python refactorizar_plantillas.py --analizar --output-json analisis.json
```

### Auto-Refactorizar
```bash
# Refactorizar con backup automático
python refactorizar_plantillas.py --plantilla templates/plantilla_desempeno.docx --auto-refactor

# Modo dry-run (sin cambios)
python refactorizar_plantillas.py --plantilla templates/plantilla_desempeno.docx --auto-refactor --dry-run
```

## Generación de Informes

```bash
# Generar informe con datos completos
python generar_informe.py \
  --plantilla templates/plantilla_desempeno.docx \
  --datos ejemplo_datos_completo.json \
  --output informe_generado.docx

# Con imágenes
python generar_informe.py \
  --plantilla templates/plantilla_desempeno.docx \
  --datos ejemplo_datos_completo.json \
  --imagenes mis_imagenes/ \
  --output informe_final.docx
```

## Troubleshooting

### Lista no se expande
- Verificar que el placeholder esté exactamente como `{{nombre_lista}}`
- Verificar que el JSON contenga un array de strings
- Revisar logs con `--verbose`

### Tabla no genera filas
- Verificar que la fila plantilla tenga placeholders con formato `{{array.campo}}`
- Verificar que el JSON contenga array de objetos con los campos correctos

### Formato perdido
- El sistema preserva estilos de párrafo
- Para tablas, el formato de la primera fila de datos se replica

### Placeholder no reemplazado
- Verificar que el nombre coincida exactamente (case-sensitive)
- Usar `--info` para ver placeholders detectados:
  ```bash
  python generar_informe.py --plantilla template.docx --info
  ```

## Archivos de Referencia

- [`ejemplo_datos_completo.json`](ejemplo_datos_completo.json) - Ejemplo completo con todos los campos
- [`ejemplo_datos.json`](ejemplo_datos.json) - Ejemplo básico (solo escalares)
- [`refactorizar_plantillas.py`](refactorizar_plantillas.py) - Script de análisis y refactorización
- [`generar_informe.py`](generar_informe.py) - Script de generación de informes