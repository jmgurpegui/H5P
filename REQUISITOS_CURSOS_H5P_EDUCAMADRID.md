# Guía Técnica de Requisitos y Estándares para Cursos H5P en EducaMadrid y Moodle

Este documento establece la normativa técnica, de empaquetado, arquitectura semántica y sincronización con el Libro de Calificaciones que debe cumplir cualquier curso en formato H5P para garantizar un funcionamiento óptimo, sin errores de validación y sin bloqueos de pantalla en blanco en plataformas **Moodle** y el entorno **EducaMadrid**.

---

## 1. Restricciones de Seguridad y Archivos Multimedia (Whitelist de Moodle)

El validador de seguridad de Moodle (`H5PValidator.php`) inspecciona rigurosamente cada archivo alojado dentro del directorio `content/` del paquete `.h5p`.

### 1.1. Prohibición Estricta de Archivos Vectoriales `.svg` en `content/`
- **Motivo**: Moodle bloquea archivos `.svg` dentro de `content/` para prevenir vectores de inyección de código malicioso (*Stored XSS* en navegadores).
- **Norma obligatoria**: 
  - **PROHIBIDO** incluir archivos con extensión `.svg` dentro del directorio `content/` (por ejemplo, en `content/images/` o enlazados en el HTML de las páginas).
  - Todas las infografías, diagramas técnicos y esquemas vectoriales **deben rasterizarse a formato PNG o JPEG** en alta resolución (se recomienda ancho mínimo de 1200 a 1600 px con compresión optimizada).
  - Si un archivo SVG contiene entidades de caracteres HTML (como `&ge;` o `&le;`), deben normalizarse a entidades numéricas XML (`&#8805;`, `&#8804;`) o caracteres Unicode puros antes de la conversión rasterizada.
- **Excepción**: Los archivos `.svg` únicamente están permitidos dentro de las carpetas de las librerías del sistema (para iconos de biblioteca y tipografías).

### 1.2. Lista Blanca Oficial de Extensiones Admitidas
Cualquier archivo alojado en `content/` debe tener una de las siguientes extensiones permitidas:
```text
json, png, jpg, jpeg, gif, bmp, tif, tiff, eot, ttf, woff, woff2, otf,
webm, mp4, ogg, mp3, m4a, wav, txt, pdf, rtf, doc, docx, xls, xlsx,
ppt, pptx, odt, ods, odp, csv, diff, patch, swf, md, textile, vtt, webvtt, gltf, glb
```

---

## 2. Compatibilidad y Alineación de Librerías (`semantics.json`)

Moodle valida jerárquicamente que cada componente hijo esté explícitamente autorizado en el archivo `semantics.json` de la librería padre. Si se usa una versión menor superior a la admitida, la subida será rechazada con el error:
> *"La versión de la librería H5P [Librería] usada en este contenido no es válida. El contenido contiene [Versión], pero debería de ser [Versión Requerida]."*

### 2.1. Matriz de Versiones Homologada para Libros Interactivos

Para cursos completos maquetados con el estándar **`H5P.InteractiveBook`**:

| Librería | Versión Exigida | Rol en el Paquete |
| :--- | :--- | :--- |
| **`H5P.InteractiveBook`** | `1.7` (v1.7.5) | Contenedor principal (`mainLibrary`). |
| **`H5P.Column`** | **`1.16`** (v1.16.7) | Contenedor obligatorio de cada página/capítulo (exigido por el esquema de `InteractiveBook 1.7`). |
| **`H5P.QuestionSet`** | **`1.20`** (v1.20.31) | Cuestionario oficial integrado (exigido por el esquema de `Column 1.16`). |
| **`H5P.MultiChoice`** | `1.16` | Preguntas de opción múltiple con explicación y barajado. |
| **`H5P.TrueFalse`** | `1.8` | Autocomprobaciones de Verdadero / Falso. |
| **`H5P.AdvancedText`** | `1.1` | Bloques de texto HTML estructurado y responsive. |
| **`H5P.Accordion`** | `1.0` | Paneles desplegables para protocolos paso a paso. |
| **`H5P.Image`** | `1.1` | Despliegue de imágenes con soporte de accesibilidad. |
| **`H5P.Video`** | `1.6` | Vídeos integrados y píldoras audiovisuales. |
| **`FontAwesome`** | `4.5` | Iconografía del sistema. |
| **`H5P.JoubelUI`** | `1.3` | Componentes de interfaz de usuario. |
| **`H5P.FontIcons`** | `1.0` | Iconos de estado de verificación. |
| **`H5P.Transition`** | `1.0` | Animaciones de transición entre páginas. |
| **`H5P.Components`** | `1.0` | Componentes de portada y tarjetas. |
| **`jQuery.ui`** | `1.10` | Utilidades de maquetación interactiva. |

### 2.2. Clausura Total de Dependencias en `h5p.json`
El manifiesto `h5p.json` debe declarar **todas** las dependencias directas e indirectas de cada una de las librerías incluidas. Por ejemplo, dado que `H5P.Components` requiere `jQuery.ui 1.10`, esta última debe figurar tanto en `h5p.json` como con su carpeta correspondiente (`jQuery.ui-1.10/`) en la raíz del archivo ZIP.

---

## 3. Estructura Interna del Contenido (`content.json`) y Prevención de Pantallas en Blanco

Uno de los errores más críticos que provocan que el contenido se registre pero se muestre en blanco es un fallo en la estructura interna de anidamiento de datos en JavaScript.

### 3.1. Anidamiento Obligatorio en `H5P.Column`
En `H5P.Column`, la lista `params.content` **no acepta directamente los objetos ejecutables**. Cada elemento debe envolverse como un grupo que contenga la propiedad `content` y la propiedad `useSeparator`:

```json
// CORRECTO (Funciona al 100%):
{
  "content": [
    {
      "content": {
        "library": "H5P.AdvancedText 1.1",
        "params": {
          "text": "<p>Contenido técnico maquetado...</p>"
        },
        "subContentId": "6b2a0c64-2db3-4318-9717-386d34bcf1b3",
        "metadata": {
          "title": "Teoría: Procedimiento de Diagnosis"
        }
      },
      "useSeparator": "auto"
    }
  ]
}
```

```json
// INCORRECTO (Genera pantalla en blanco en Moodle):
{
  "content": [
    {
      "library": "H5P.AdvancedText 1.1",
      "params": { "text": "<p>Contenido...</p>" }
    }
  ]
}
```
*Consecuencia del formato incorrecto*: El método `H5P.Column.prototype.attach()` evalúa `content.content.library`. Al ser `content.content` indefinido, lanza un `TypeError: Cannot read properties of undefined (reading 'library')`, deteniendo por completo el script y dejando el iframe en blanco.

### 3.2. Metadatos Obligatorios (`subContentId` y `metadata.title`)
El menú lateral de navegación (`SideBar`) y el indexador de capítulos (`PageContent`) de `H5P.InteractiveBook` requieren que **cada sección ejecutable** posea:
1. **`subContentId`**: Identificador UUIDv4 único generado programáticamente.
2. **`metadata.title`**: Título de la sección como cadena de texto. Si un elemento carece de `metadata.title`, el sidebar arroja:
   `TypeError: Cannot read properties of undefined (reading 'title')`.

---

## 4. Sincronización con el Libro de Calificaciones de Moodle / EducaMadrid

Para que la calificación obtenida por el alumno se guarde de forma automática en la base de datos de calificaciones de Moodle (`mdl_grade_grades`), deben cumplirse los siguientes estándares:

### 4.1. Emisión de Sentencias xAPI
- **Cuestionario Final (`H5P.QuestionSet`)**:
  - Emite automáticamente sentencias xAPI de tipo `answered` y `completed` con los campos `result.score.raw` (puntos obtenidos) y `result.score.max` (puntos posibles).
  - Debe configurarse con `passPercentage: 70` (o la nota de corte deseada, ej. 50% o 70%).
  - Al hacer clic en *"Finalizar y Guardar en Calificaciones"* o *"Enviar Calificación a Moodle"*, el runtime de Moodle captura el evento xAPI y actualiza el calificador.
- **Libro Interactivo (`H5P.InteractiveBook`)**:
  - Consolida tanto las comprobaciones intermedias como el cuestionario final.
  - Al llegar al capítulo de resumen final, el botón *"Enviar Informe y Calificación a Moodle"* transmite el estado global del curso.

### 4.2. Configuración Recomendada de la Actividad en Moodle
Al publicar el recurso en el aula virtual de EducaMadrid:
- **Calificación**:
  - *Tipo de calificación*: Puntuación.
  - *Puntuación máxima*: 10 (o 100 según el criterio del departamento).
  - *Calificación para aprobar*: 7 (o 70 si la escala es 100).
- **Opciones de intento**:
  - *Habilitar seguimiento de intentos*: **Sí** (imprescindible para el registro de intentos).
  - *Método de calificación*: Calificación más alta (o Último intento).

---

## 5. Diseño Pedagógico y Estándares para Formación Profesional (FP)

Para garantizar un valor educativo riguroso y adaptado al currículo de FP (especialmente en automoción y áreas técnicas):

1. **Estructura Modular Clara**:
   - **Tema 0 / Portada**: Presentación del curso, guía didáctica, Resultados de Aprendizaje (RA) y Criterios de Evaluación oficiales.
   - **Temas Teórico-Prácticos**: Unidades con desarrollo técnico, normativo y procedimental.
   - **Desplegables Técnicos (Acordeones)**: Protocolos paso a paso de taller, diagnosis con polímetro / osciloscopio, medidas de seguridad y gestión ambiental.
   - **Autocomprobaciones Formativas**: Mínimo 1 cuestión interactiva (MultiChoice o True/False) al final de cada tema para retroalimentación formativa inmediata (no penalizadora).
   - **Mediateca Técnica**: Enlaces a normativas vigentes, reglamentos europeos (F-Gas UE 2024/573, SIGAUS, UNE-EN 50110), manuales de taller y simuladores.
   - **Evaluación Final Calificada**: Capítulo exclusivo con batería de preguntas oficiales conectadas al libro de calificaciones.

2. **Calidad de los Cuestionarios**:
   - **Bolsa de preguntas representativa**: Mínimo 40-50 preguntas técnicas redactadas con fundamento real de taller.
   - **Muestreo aleatorio (`poolSize`)**: Seleccionar automáticamente 20 supuestos por intento para evitar el aprendizaje mecánico o la copia.
   - **Barajado de alternativas (`randomAnswers: true`)**: Las respuestas correctas deben alternar de manera aleatoria y equitativa entre A, B, C y D.
   - **Retroalimentación formativa y explicada**: Cada opción debe justificar técnicamente el motivo del acierto o del error (ej. citando la norma UNE, el artículo de ley o el principio físico/mecánico).

---

## 6. Procedimiento de Verificación y Compilación Automatizada

Antes de subir cualquier archivo `.h5p` a EducaMadrid, se debe someter a una suite de validación automatizada:

```bash
# 1. Ejecutar el compilador y validador
python3 build_h5p.py

# 2. Comprobar que no existen archivos fuera de whitelist en content/
python3 -c "
import zipfile
wl = {'json','png','jpg','jpeg','gif','bmp','tif','tiff','eot','ttf','woff','woff2','otf','webm','mp4','ogg','mp3','m4a','wav','txt','pdf','rtf','doc','docx','xls','xlsx','ppt','pptx','odt','ods','odp','csv','diff','patch','swf','md','textile','vtt','webvtt','gltf','glb'}
for pkg in ['Curso_Logistica_y_Organizacion_del_Taller.h5p', 'UT1_ODS_y_Agenda_2030_Taller_Madrid.h5p']:
    with zipfile.ZipFile(pkg) as zf:
        bad = [f for f in zf.namelist() if f.startswith('content/') and not f.endswith('/') and f.split('.')[-1].lower() not in wl]
        assert not bad, f'Errores de whitelist en {pkg}: {bad}'
print('✓ Todos los archivos en content/ cumplen la lista blanca de Moodle.')
"
```

Cumpliendo con estas directrices, cualquier curso interactivo H5P garantizará una experiencia fluida, compatible, accesible y perfectamente integrada con la evaluación oficial en EducaMadrid.
