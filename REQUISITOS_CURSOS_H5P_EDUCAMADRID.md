# Guía Técnica de Requisitos y Estándares para Cursos H5P en EducaMadrid y Moodle

Este documento consolida la **normativa técnica oficial**, directrices de empaquetado seguro, arquitectura semántica de datos, maquetación responsive, tratamiento de fórmulas físico-químicas/eléctricas, **los 5 pilares pedagógicos de aprendizaje activo** y **accesibilidad universal (WCAG 2.1 AA / AAA)** para la creación y distribución de paquetes `.h5p` homologados en **EducaMadrid** y entornos **Moodle**.

---

## 1. Introducción y Propósito

El módulo interactivo de Moodle (`mod_h5p` y el banco de contenidos integrado de la plataforma) aplica mecanismos de validación sintáctica, semántica y de seguridad informática notablemente más estrictos que el editor web de H5P.org.

El incumplimiento de estas especificaciones genera bloqueos comunes y fallos críticos:
1. **Errores de validación de extensiones (`not-in-whitelist`)**: Bloqueo absoluto del paquete al subirlo.
2. **Fuga de código CSS en pantalla (`CSS leakage`)**: Visualización de texto plano residual (ej. `tom: 2px solid #ner { font-family: ...`) en la cabecera por inyectar etiquetas `<style>` dentro de `H5P.AdvancedText`.
3. **Fórmulas matemáticas rotas**: Fórmulas con `$ ... $` o sintaxis LaTeX que se muestran como código fuente sin procesar debido a la ausencia de MathJax dentro del sandbox iframe de H5P.
4. **Pantallas en blanco (*White Screen of Death*)**: Excepciones de JavaScript (`TypeError: Cannot read properties of undefined`) por omitir el envoltorio obligatorio en `H5P.Column`.
5. **Ruptura de navegación lateral**: Falta de metadatos UUIDv4 (`subContentId`) o de títulos descriptivos (`metadata.title`).
6. **Contenido pasivo monótono**: Libros de texto planos que no desafían al alumno ni promueven la práctica activa reflexiva.
7. **Problemas de accesibilidad y contraste**: Textos ilegibles en pantallas con luz natural, botones táctiles diminutos para uso en taller o falta de soporte para lectores de pantalla.
8. **Ausencia de calificación en Moodle**: Incumplimiento del ciclo de sentencias xAPI hacia la tabla `mdl_grade_grades`.

Esta especificación detalla las directrices operativas que resuelven y anulan de raíz todos estos fallos.

---

## 2. Protocolo Obligatorio: Entrevista Inicial de Diagnóstico Curricular

Antes de programar o generar cualquier Unidad de Trabajo o recurso interactivo H5P, es obligatorio completar o verificar los siguientes parámetros clave para garantizar un ajuste pedagógico exacto:

```markdown
### 📋 Parámetros Clave para la Creación de la Unidad de Trabajo H5P:

1. **Tema del contenido**: [Insertar Tema, conceptos nucleares o destrezas técnicas]
2. **Asignatura y Nivel**: [Ej. 2º Bachillerato - Historia de España / 1º CFGM Electromecánica - Sistemas de Carga]
3. **Tipo de actividad / contenedor H5P**: [Ej. Interactive Book unificado / Question Set / Drag the Words / Image Hotspots / Single Choice Set]
4. **Cantidad de ítems**: [Ej. 10 preguntas / 8 huecos de arrastre / 2 capítulos / 4 puntos de inspección]
5. **Nivel cognitivo (Taxonomía de Bloom)**: [Recordar / Comprender / Aplicar / Analizar / Evaluar / Crear]
6. **Estrategia de Retroalimentación**: [Formativa con pistas y explicaciones ante error / Sumativa formal con nota xAPI]
7. **Recursos Multimedia**: [Esquemas PNG/JPG, vídeos en Mediateca EducaMadrid o simuladores externos]
```

---

## 3. Los 5 Pilares Pedagógicos y Técnicos para Cursos H5P

La creación de recursos H5P de calidad superior en Formación Profesional y enseñanza técnica se sustenta en 5 pilares obligatorios:

```
[1. Participación Constante] ➔ [2. Andamiaje Integrado (4 Fases)] ➔ [3. Retroalimentación Explicada] ➔ [4. Gamificación Didáctica] ➔ [5. Trazabilidad xAPI en Moodle]
```

### Pilar 1: Participación Constante del Estudiante y Enriquecimiento Multimedia
* **Evitar la pasividad**: Queda expresamente desaconsejada la lectura pasiva de textos extensos o la simple visualización pasiva de vídeos lineales. El alumnado debe explorar, tomar decisiones, responder preguntas, arrastrar elementos e interactuar con el material en cada lección.
* **Enriquecimiento Multimedia Interactivo**:
  * **Imágenes Enriquecidas con Puntos de Inspección (`H5P.ImageHotspots 1.10`)**: Transforma fotografías de motores, placas de circuito o esquemas eléctricos en mapas interactivos donde cada punto despliega explicaciones detalladas y criterios de comprobación (`create_image_hotspots`).
  * **Manipulación Activa de Conceptos (`H5P.DragText 1.10`)**: El alumno arrastra términos técnicos, magnitudes, unidades o pasos lógicos para completar definiciones y deducciones (`create_drag_text_activity`).
  * **Vídeo Interactivo (`H5P.InteractiveVideo 1.27` / `H5P.Video 1.6`)**: Vídeos alojados en la Mediateca de EducaMadrid con interrupciones reflexivas y preguntas intercaladas que evitan el avance sin asimilación.

### Pilar 2: Estructuración Pedagógica Integrada (Andamiaje)
* **Contenedores Unificados**: En lugar de presentar recursos dispersos en el aula virtual (un PDF suelto, un vídeo en otro enlace, un cuestionario aparte), integrar la teoría, los ejemplos y las prácticas en un **único recurso estructurado**:
  * **`H5P.InteractiveBook 1.7`** como contenedor macro del curso (unidades modulares con tabla de contenidos lateral).
  * **`H5P.Column 1.16`** como contenedor estructurador de cada capítulo.
* **Secuencia Didáctica Progresiva en 4 Fases**: Cada unidad debe implementar la secuencia de andamiaje:
  1. *Fase 1: Presentación motivadora y activación*: Introducción visual (`tech-hero`), insignias de unidad y activación de conocimientos previos mediante un reto inicial o actividad gamificada.
  2. *Fase 2: Explicación interactiva*: Bloques concisos de teoría técnica maquetada, fórmulas semánticas normalizadas y recursos multimedia enriquecidos (`ImageHotspots`).
  3. *Fase 3: Práctica guiada activa*: Arrastre de magnitudes (`DragText`), retos de taller de toma de decisiones (`.tech-challenge`), listas de cotejo táctiles (`.tech-checklist`), protocolos en acordeón y laboratorios virtuales (`.sim-box`).
  4. *Fase 4: Evaluación formativa inmediata*: Autocomprobaciones (`MultiChoice`, `TrueFalse`) con retroalimentación pedagógica razonada en cada opción.

### Pilar 3: Retroalimentación Inmediata y Explicada
* **Corrección automática y autorregulación**: Las actividades deben ofrecer corrección instantánea al pulsar "Comprobar", permitiendo al estudiante verificar sus aciertos y errores en el momento de máximo enfoque mental.
* **Justificación pedagógica obligatoria**: Cada opción de respuesta debe incluir explicaciones razonadas:
  * Para la opción correcta: explicar **por qué** es la solución técnica adecuada y qué principio físico la avala.
  * Para cada distractor incorrecto: explicar **en qué consiste el error** cometido (ej. confundir intensidad con tensión, olvidar atenuar la sonda, no esperar la descarga de condensadores).
* **Pistas orientativas (`tips`)**: Proporcionar pistas previas para guiar el razonamiento sin regalar la solución.
* **Aprender del error**: Configurar siempre `enableRetry: true` y `enableSolutionsButton: true` para que el error sea una palanca de reflexión formativa, no un castigo.

### Pilar 4: Gamificación Estratégica con Propósito Didáctico
* **Dinamización lúdica planificada**: Incorporar mecánicas lúdicas (arrastre de términos `DragText`, juegos de memoria `MemoryGame`, emparejamiento de magnitudes) para activar conocimientos previos al inicio de la lección, romper la monotonía o realizar cierres atractivos.
* **Integración curricular orgánica**: La gamificación no es un adorno superficial aislado; forma parte orgánica de la narrativa técnica de la unidad (ej. "Reto previo: empareja cada magnitud con su unidad antes de conectar el osciloscopio").

### Pilar 5: Integración con la Evaluación y Trazabilidad en Moodle
* **Sincronización con el Libro de Calificaciones (`Gradebook`)**:
  * Para registrar calificaciones oficiales, intentos y analíticas de aprendizaje, el paquete debe publicarse en Moodle como **Actividad H5P Nativa** (`mod_h5p`), enviando sentencias xAPI (`completed`, `answered`, puntuación `result.score.raw` y `result.score.max`) hacia `mdl_grade_grades`.
* **Diferenciación estricta de formatos**:
  * **Incrustaciones (`iframe` o enlaces en libro/página)**: Para consulta, estudio autónomo a pie de taller y autocomprobación formativa no sumativa.
  * **Actividades H5P Nativas**: Para cursos con módulo evaluable integrado (`H5P.QuestionSet 1.20`) o cuestionarios oficiales generados con Moodle XML.

---

## 3. Normativa Técnica y Seguridad del Paquete `.h5p`

### 3.1. Restricciones de Seguridad en `content/` (Whitelist de Moodle)
El validador de Moodle (`H5PValidator.php`) examina individualmente cada fichero ubicado dentro del directorio `content/`:

1. **Prohibición estricta de SVG y ficheros ejecutables**:
   * **PROHIBIDO incluir archivos `.svg`** dentro del directorio `content/` (p. ej., `content/images/`) para prevenir inyecciones de código malicioso (*Stored XSS*).
   * **PROHIBIDO incluir archivos `.html` locales** dentro de `content/`.
2. **Rasterización obligatoria**:
   * Todo esquema eléctrico, diagrama o ilustración vectorial debe rasterizarse a formato **PNG o JPEG** en alta resolución (1200 a 1600 px).
3. **Simuladores Interactivos Externos**:
   * Alojarse en servidores seguros con protocolo HTTPS e integrarse mediante componentes de enlace seguro (`.sim-box`, `.btn-sim`) o `H5P.IFrameEmbed`.

#### Whitelist Oficial de Extensiones Admitidas en `content/`
```
json, png, jpg, jpeg, gif, bmp, tif, tiff, eot, ttf, woff, woff2, otf,
webm, mp4, ogg, mp3, m4a, wav, txt, pdf, rtf, doc, docx, xls, xlsx,
ppt, pptx, odt, ods, odp, csv, diff, patch, swf, md, textile, vtt, webvtt, gltf, glb
```

---

### 3.2. Matriz de Versiones Homologadas (`semantics.json`)
Para compilar cursos compatibles, deben incluirse exactamente las siguientes versiones homologadas:

| Librería H5P | Versión Requerida | Rol dentro del Paquete |
| :--- | :--- | :--- |
| **`H5P.InteractiveBook`** | **1.7** (v1.7.5) | Contenedor principal del curso (*mainLibrary*). |
| **`H5P.Column`** | **1.16** (v1.16.7) | Contenedor obligatorio de capítulo (exigido por InteractiveBook 1.7). |
| **`H5P.MultiChoice`** | **1.16** | Autocomprobaciones formativas con feedback razonado. |
| **`H5P.TrueFalse`** | **1.8** | Preguntas rápidas de Verdadero / Falso formativas. |
| **`H5P.DragText`** | **1.10** | Actividades de arrastre de conceptos y magnitudes. |
| **`H5P.ImageHotspots`**| **1.10** | Enriquecimiento interactivo de imágenes y esquemas. |
| **`H5P.Text`** | **1.1** | Bloques de texto simples para ventanas emergentes de hotspots. |
| **`H5P.Question`** | **1.5** | Base UI y motor de retroalimentación de preguntas. |
| **`H5P.QuestionSet`** | **1.20** (v1.20.31) | Cuestionario integrado para evaluación sumativa final. |
| **`H5P.AdvancedText`** | **1.1** | Bloques de texto HTML técnico maquetado y accesible. |
| **`H5P.Accordion`** | **1.0** | Paneles desplegables para protocolos de taller. |
| **`H5P.Image`** | **1.1** | Imágenes técnicas y cabeceras institucionales accesibles. |
| **`H5P.Video`** | **1.6** | Reproducción multimedia (vídeos pesados en Mediateca). |
| **`FontAwesome`** | **4.5** | Iconografía base de la interfaz de usuario. |
| **`H5P.JoubelUI`** | **1.3** | Componentes comunes de botones accesibles. |
| **`H5P.FontIcons`** | **1.0** | Iconos de estado de verificación. |
| **`H5P.Transition`** | **1.0** | Animaciones de navegación entre páginas. |
| **`jQuery.ui`** | **1.10** | Utilidades DOM y manipulación de arrastre. |

#### Clausura Completa de Dependencias en `h5p.json`
El manifiesto `h5p.json` debe declarar **todas** las dependencias en `preloadedDependencies` y sus carpetas deben estar físicamente presentes en la raíz del archivo ZIP.

---

## 4. Visualización de Fórmulas Matemáticas y Magnitudes Eléctricas

1. **Prohibición estricta de LaTeX crudo**:
   * `H5P.AdvancedText 1.1` **no incluye MathJax ni KaTeX**. Prohibido usar `$ ... $`, `$$ ... $$` o `\text{}`.
2. **Estándar Oficial: HTML Semántico + Unicode**:
   * Subíndices: `<sub>` (ej. `V<sub>diff</sub>`, `V<sub>ADC</sub>`, `I<sub>carga</sub>`).
   * Superíndices: `<sup>` (ej. `10<sup>−9</sup> S`, `mm<sup>2</sup>`).
   * Símbolos Unicode: `×` (`&times;`), `−` (`&minus;`), `Ω` (`&Omega;`), `µ` (`&micro;`), `Δ` (`&Delta;`), `≥` (`&ge;`), `≤` (`&le;`).
3. **Clases CSS Normalizadas**:
   * Fórmulas en línea: `<span class="tech-formula">V = I × R</span>`.
   * Fórmulas destacadas en bloque:
     ```html
     <div class="tech-formula-block">
       <span class="tech-formula">V<sub>diff</sub> = V<sub>CAN-H</sub> − V<sub>CAN-L</sub> = 3.5 V − 1.5 V = <strong>2.0 V</strong></span>
       <div class="tech-formula-desc">Tensión diferencial calculada entre líneas del bus CAN.</div>
     </div>
     ```

---

## 5. Inyección de Estilos CSS y Prevención de Fugas (*CSS Leakage*)

* **Cero etiquetas `<style>` en HTML**: El sanitizador de H5P elimina las etiquetas `<style>` pero vuelca el código CSS interno como texto plano visible.
* **Inyección Homologada**: Los estilos se inyectan en los archivos `.css` de las librerías base mediante `append_css_to_libraries.py` usando delimitadores limpios:
  * `H5P.InteractiveBook-1.7/dist/h5p-interactive-book.css`
  * `H5P.Column-1.16/styles/h5p-column.css`

---

## 6. Cabecera Institucional Normalizada (`logo2026.bmp` / `logo2026.png`)

* Ubicación obligatoria en el ZIP: `content/images/<nombre_del_logo>`.
* Inserción como primer elemento de cada capítulo mediante el componente nativo **`H5P.Image 1.1`** con texto alternativo accesible (`alt="Comunidad de Madrid - Unión Europea - Formación Profesional Pública"`), garantizando que las rutas nunca fallen en Moodle.
* **Formatos y recomendaciones técnicas para logotipos**:
  * **PNG (`.png`) — Recomendado al 100%**: Soporta canal alfa para transparencia real (evita recuadros blancos sobre fondos tintados `#f8fafc` o modo oscuro), compresión sin pérdidas con textos/bordes nítidos y peso optimizado (~100-200 KB).
  * **BMP (`.bmp`) — Soportado pero no recomendado**: Permitido en la whitelist de Moodle, pero carece de canal alfa transparente (obliga a fondos opacos sólidos) y genera un peso de archivo significativamente mayor sin comprimir (~1.1 MB a 2 MB).
  * **SVG (`.svg`) — Prohibido**: Bloqueado de forma estricta por seguridad anti-XSS en el core de Moodle (`not-in-whitelist`).
  * El generador (`generar_curso_plantilla.py`) resuelve dinámicamente el archivo existente (`logo2026.bmp`, `logo2026.png` o `logo2026.jpg`), calculando automáticamente sus dimensiones reales y tipo MIME.

---

## 7. Arquitectura de Datos (`content.json`) y Prevención de Pantalla en Blanco

* **Anidamiento en `H5P.Column`**: Cada elemento en `params.content` debe envolverse obligatoriamente con `{"content": ..., "useSeparator": "auto"}`:
  ```json
  {
    "content": [
      {
        "content": {
          "library": "H5P.AdvancedText 1.1",
          "params": { "text": "<p>Contenido educativo...</p>" },
          "subContentId": "6b2a0c64-2db3-4318-9717-386d34bcf1b3",
          "metadata": { "title": "Unidad 1" }
        },
        "useSeparator": "auto"
      }
    ]
  }
  ```
* **Metadatos obligatorios**: Identificador único UUIDv4 (`subContentId`) y título de navegación (`metadata.title`).

---

## 8. Guía de Accesibilidad Universal y Legibilidad de Textos (WCAG 2.1 AA / AAA)

* **Ratios de Contraste Cromático de Textos**:
  * Cuerpo de texto: `#0f172a` (Slate 900) sobre fondo blanco con ratio **> 13:1**.
  * Insignias (`.tech-badge`): Fondos de alto contraste con bordes nítidos y ratios **> 7:1 a 9:1**.
  * Cajas de alerta: Textos oscuros (`#450a0a`, `#451a03`, `#082f49`, `#052e16`) con ratios **> 9:1**.
* **Doble Señalización**: Todo estado se acompaña de iconos (`⚠️`, `📋`, `⚡`, `✓`) y textos contextuales.
* **Tipografía Accesible**: Tamaño base `1rem` (16px), interlineado `1.65` y texto alineado a la izquierda (cero texto justificado para prevenir barreras por dislexia).
* **Navegación por Teclado y Foco Visible**: Anillo de foco `:focus-visible` de 3px (`outline: 3px solid #0284c7; outline-offset: 3px;`).
* **Objetivos Táctiles**: Tamaño mínimo de **44 x 44 px** en botones y elementos interactivos para uso fluido con guantes en taller.
* **Textos Alternativos (`alt`)**: Toda imagen técnica exige descripción funcional del circuito u oscilograma.

---

## 9. Catálogo de Helpers en `plantilla/generar_curso_plantilla.py`

| Función Helper | Librería / Componente | Propósito Pedagógico y Técnico |
| :--- | :--- | :--- |
| `create_header_logo()` | `H5P.Image 1.1` | Inserta cabecera institucional oficial con alt text accesible. |
| `create_text_section(html, titulo)` | `H5P.AdvancedText 1.1` | Bloques de texto técnico de alto contraste y fórmulas semánticas. |
| `create_drag_text_activity(desc, texto, distractores, titulo)` | `H5P.DragText 1.10` | Manipulación y arrastre de conceptos técnicos a sus huecos. |
| `create_image_hotspots(img, puntos, titulo, alt)` | `H5P.ImageHotspots 1.10` | Enriquecimiento interactivo de imágenes con puntos de inspección. |
| `create_multichoice_question(preg, opciones, titulo)` | `H5P.MultiChoice 1.16` | Autocomprobación activa con justificación razonada en cada opción. |
| `create_true_false_question(preg, valor, titulo)` | `H5P.TrueFalse 1.8` | Validación ágil de reglas críticas de seguridad y criterios técnicos. |
| `create_checkpoint_section(titulo, intro)` | `.tech-checkpoint` | Pausa activa visual que predispone a la autocomprobación formativa. |
| `create_active_challenge(titulo, escenario, pasos)` | `.tech-challenge` | Reto práctico de taller y toma de decisiones ante averías. |
| `create_checklist_section(titulo, items)` | `.tech-checklist` | Lista de verificación táctil accesible (touch targets ≥44px). |
| `create_accordion(paneles, titulo)` | `H5P.Accordion 1.0` | Desplegables colapsables para protocolos extensos de taller. |
| `create_simulation_box(titulo, desc, btn, url)` | `.sim-box` / `.btn-sim` | Conexión directa a simuladores y laboratorios virtuales interactivos. |
| `create_didactic_sequence_chapter(...)` | `H5P.Column 1.16` | Ensambla un capítulo completo bajo la secuencia de andamiaje de 4 fases. |

---

## 10. Verificación Automatizada con `validar_h5p_educamadrid.py`

Antes de subir cualquier paquete a Moodle, certificar su cumplimiento mediante:

```bash
python3 plantilla/validar_h5p_educamadrid.py <nombre_paquete.h5p>
```

El script certifica automáticamente:
1. Whitelist estricta en `content/` (cero `.html`, cero `.svg`).
2. Clausura física completa de las 16 librerías en la raíz del ZIP.
3. Anidamiento reglamentario en `H5P.Column 1.16`.
4. Metadatos obligatorios UUIDv4 y `metadata.title`.
5. Ausencia de etiquetas `<style>` y delimitadores LaTeX crudos `$`.
6. Detección y contabilización de actividades de Aprendizaje Activo (`MultiChoice`, `TrueFalse`, `DragText`, `ImageHotspots`, `QuestionSet`).
7. Cumplimiento de accesibilidad básica (atributos `alt` no vacíos).
