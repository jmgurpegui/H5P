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
* **Evitar la pasividad**: Queda expresamente desaconsejada la lectura pasiva de textos extensos o la simple visualización pasiva de vídeos lineales. El alumnado debe explorar esquemas de taller, tomar decisiones de diagnosis y seguir protocolos interactivos en cada lección.
* **Enriquecimiento Multimedia Interactivo**:
  * **Imágenes Técnicas en Alta Resolución (`H5P.Image 1.1`)**: Ilustraciones vectoriales rasterizadas o fotogramas 4K de taller nítidos (1200 a 1600 px) con texto alternativo descriptivo obligatorio.
  * **Puntos de Inspección Táctil (`H5P.ImageHotspots 1.10`)**: Transforma fotografías de componentes, placas de circuito o esquemas eléctricos en mapas interactivos donde cada punto despliega comprobaciones y tolerancias técnicas (`create_image_hotspots`).
  * **Retos de Taller y Toma de Decisiones (`.tech-challenge`)**: Casos reales de avería con toma de decisiones diagnósticas guiadas (`create_active_challenge`).
  * **Listas de Cotejo Táctiles (`.tech-checklist`)**: Checklists ergonómicos con áreas de pulsación mínimas de 44x44 px (WCAG 2.5.5) para certificar protocolos de seguridad y verificación (`create_checklist_section`).
  * **Protocolos Desplegables en Acordeón (`H5P.Accordion 1.0`)**: Desglose modular de pasos de taller sin saturar visualmente la pantalla (`create_accordion`).

### Pilar 2: Estructuración Pedagógica Integrada (Andamiaje en 4 Fases)
* **Contenedores Unificados**: En lugar de presentar recursos dispersos en el aula virtual, integrar la teoría, las figuras y los procedimientos de taller en un **único recurso estructurado**:
  * **`H5P.InteractiveBook 1.7`** como contenedor macro del curso (unidades modulares con tabla de contenidos lateral accesible y cerrada por defecto en móviles).
  * **`H5P.Column 1.16`** como contenedor estructurador de cada capítulo.
* **Secuencia Didáctica Progresiva en 4 Fases**: Cada unidad debe implementar la secuencia de andamiaje:
  1. *Fase 1: Presentación motivadora y activación*: Introducción visual (`.tech-hero`), insignias de unidad y activación conceptual previa.
  2. *Fase 2: Explicación interactiva*: Bloques concisos de teoría técnica maquetada, fórmulas semánticas normalizadas y recursos multimedia enriquecidos (`ImageHotspots`).
  3. *Fase 3: Práctica guiada activa*: Retos de taller (`.tech-challenge`), listas de cotejo táctiles (`.tech-checklist`), protocolos en acordeón y enlaces a laboratorios virtuales (`.sim-box`).
  4. *Fase 4: Consolidación y Derivación a Evaluación Oficial*: Tarjeta de síntesis de unidad (`.tech-checkpoint`) y remisión directa al cuestionario oficial en Moodle XML (`create_moodle_quiz_referral`).

### Pilar 3: Retroalimentación Inmediata y Explicada en Moodle XML
* **Ubicación en el Banco de Preguntas XML**: En la arquitectura desacoplada, la retroalimentación inmediata, explicada y razonada reside en los cuestionarios de Moodle XML (`mod_quiz`), no en actividades dentro del paquete H5P.
* **Justificación pedagógica obligatoria en `<feedback>`**:
  * Para la opción correcta: explicar **por qué** es la solución técnica adecuada y qué principio físico la avala.
  * Para cada distractor incorrecto: explicar **en qué consiste el error** cometido (ej. confundir intensidad con tensión, olvidar atenuar la sonda, no esperar la descarga de condensadores).
* **Aprender del error**: Configurar el cuestionario Moodle con intentos múltiples y retroalimentación diferida o interactiva con múltiples intentos para que el error sea una palanca de aprendizaje activo.

### Pilar 4: Dinamización y Retos Didácticos
* **Enfoque técnico motivador**: Incorporar retos de diagnosis de taller, checklists de comprobación previa y simuladores interactivos para activar conocimientos sin sobrecargar la pantalla con actividades de arrastre incompatibles con dispositivos móviles.

### Pilar 5: Desacoplamiento de Formación (H5P) y Evaluación Oficial (Moodle XML)

#### El Problema de la Trazabilidad y Calificaciones en H5P
En Moodle / EducaMadrid, vincular la finalización de un paquete H5P complejo a una calificación de aprobado o sentencias xAPI genera frecuentes bloqueos para el alumnado:
* **Fuga de sentencias xAPI**: En dispositivos móviles (especialmente iOS/Safari y Chrome Android), las restricciones de cookies de terceros, bloqueos de iframes o microcortes de red provocan que las sentencias xAPI (`completed`, `passed`) no lleguen al servidor Moodle.
* **Sobreescritura por puntaje de dominio**: Si Moodle tiene activado *"El puntaje de dominio anula el estado"* (*Mastery score overrides status*), un estudiante que complete la lectura y práctica pero no supere el corte de un cuestionario interno figura como **"No intentado"** o **"No superado"**, anulando su progreso formativo.
* **Problemas ergonómicos en móviles con actividades de arrastre (`DragText`)**: En pantallas táctiles de smartphones, los elementos de arrastre colisionan con el gesto de scroll vertical de la página y las etiquetas resultan diminutas para interacción con los dedos.

#### La Solución Oficial Homologada: Cursos H5P 100% Formativos y Cuestionarios Moodle XML
Para garantizar que **el 100% de los alumnos registre la realización de los contenidos sin errores** y disfrute de una experiencia fluida en smartphones y tablets:
1. **El paquete H5P es 100% Formativo**: Queda expresamente prohibido incluir actividades puntuables o de arrastre (`H5P.MultiChoice`, `H5P.DragText`, `H5P.TrueFalse`, `H5P.QuestionSet`) dentro de los cursos H5P de producción.
2. **La evaluación se realiza íntegramente en Moodle XML**: Toda la evaluación sumativa y calificación académica se canaliza a través de cuestionarios nativos de Moodle (`mod_quiz`) importados desde el banco XML oficial.

```
┌─────────────────────────────────────────────────────────────┐
│  1. CONTENIDO EDUCATIVO Y PRÁCTICA ACTIVA (H5P INTERACTIVO) │
│  - Paquete .h5p en H5P.InteractiveBook 1.7 (100% formativo) │
│  - Andamiaje en 4 fases, esquemas HD y checklists táctiles  │
│  - Sin DragText ni cuestionarios internos (cero fallos)     │
│  - Finalización Moodle: "El estudiante debe VER la          │
│    actividad para completarla" (100% FIABLE)                │
└─────────────────────────────────────────────────────────────┘
                              +
┌─────────────────────────────────────────────────────────────┐
│  2. EVALUACIÓN SUMATIVA OFICIAL (CUESTIONARIO MOODLE XML)   │
│  - Banco oficial exportado en formato Moodle XML (<quiz>)   │
│  - Cuestionario nativo de Moodle (mod_quiz)                 │
│  - Intentos, temporizador y registro en mdl_grade_grades    │
│  - Soporte offline y app móvil Moodle sin fallos de xAPI    │
└─────────────────────────────────────────────────────────────┘
```

1. **Configuración en el Aula Virtual (EducaMadrid)**:
   * **Actividad H5P (`mod_h5p`)**: Subir el archivo `.h5p`. En la sección *Finalización de actividad*, seleccionar:
     * *Rastreo de finalización*: **Mostrar la actividad como completada cuando se cumplan las condiciones**.
     * *Requerir ver*: **El estudiante debe ver esta actividad para completarla**.
     * *Requerir calificación*: **Desmarcado**.
     *(Esto garantiza el tic verde de realización a todo alumno que trabaje el tema).*
   * **Cuestionario de Evaluación (`mod_quiz`)**:
     * Importar el archivo XML del curso (*Banco de preguntas -> Importar -> Moodle XML*).
     * Crear el cuestionario sumativo oficial (*Añadir cuestionario*), asignando calificación para aprobar (ej. 5.0).
     * En *Finalización de actividad*: Marcar **El estudiante debe recibir una calificación para completar esta actividad** y/o calificación de aprobado.
     *(Moodle almacena los intentos directamente en base de datos nativa con fiabilidad total).*

2. **Requisitos Psicométricos y Prevención del Sesgo de Longitud en Cuestionarios XML**:
   * **Prohibición de patrones**: Queda prohibido cualquier patrón o pista formal que revele la respuesta correcta sin conocimiento del contenido.
   * **Erradicación del sesgo de longitud (*Length Bias*)**: La opción correcta **NUNCA** debe ser sistemáticamente la más extensa. Las opciones deben ser homogéneas en número de caracteres y palabras (±15-20%).
   * **Alternancia deliberada**: En el cómputo del banco, alternar deliberadamente preguntas donde la correcta sea más breve, homogénea o más larga. El porcentaje de preguntas donde la correcta es la más larga no debe exceder el 35-40%.
   * **Plausibilidad de distractores**: Los distractores deben formularse con el mismo nivel de rigor técnico y estructura sintáctica.
   * **Aislamiento de la justificación**: Las explicaciones detalladas deben ubicarse en la etiqueta `<feedback>`, no en el texto de la opción `<answer>`.
   * **Barajado**: Usar `<shuffleanswers>1</shuffleanswers>` y alternar las posiciones de las opciones en el XML.
   * **Sin etiquetas `<p>` ni `</p>` innecesarias (Norma Picuino / Test)**:
     Las preguntas de test XML no necesitan `<p>` ni `</p>`. El texto del enunciado (`<questiontext>`), opciones de respuesta (`<answer>`) y retroalimentaciones (`<feedback>`) deben redactarse en texto limpio y directo sin envoltorios `<p>...</p>`, evitando espaciados y desajustes visuales indeseados en la interfaz de Moodle (referencia técnica oficial: [https://github.com/picuino/test](https://github.com/picuino/test)). Se preserva únicamente marcado semántico inline (`<strong>`, `<sub>`, `<sup>`, `<code>`) cuando sea técnicamente imprescindible.

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

#### Metadatos de Autoría Obligatorios (`authors` y `role`)
Si se incluye el campo `authors` en `h5p.json` o en los metadatos de los capítulos (`metadata.authors`), cada entrada de autor **debe ser obligatoriamente un objeto con las propiedades `name` y `role`**:
```json
"authors": [
  {
    "name": "Departamento de Formación Profesional - Automoción",
    "role": "Author"
  }
]
```
> [!WARNING]
> Si se omite la clave `"role"` en algún autor (ej. `[{"name": "..."}]`), el validador oficial de Moodle/EducaMadrid bloqueará la subida del paquete con el error:  
> **«La propiedad requerida role está faltando de h5p.json. El archivo principal h5p.json no es válido.»**  
> Valores válidos según la especificación H5P: `"Author"`, `"Editor"`, `"Licensee"`, `"Originator"`, `"Other"`.

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

## 8. Guía de Accesibilidad Universal y Adaptación Móvil (WCAG 2.1 AAA & Smartphones)

* **Ratios de Contraste Cromático de Textos**:
  * Cuerpo de texto: `#0f172a` (Slate 900) sobre fondo blanco con ratio **> 13:1**.
  * Insignias (`.tech-badge`): Fondos de alto contraste con bordes nítidos y ratios **> 7:1 a 9:1**.
  * Cajas de alerta: Textos oscuros (`#450a0a`, `#451a03`, `#082f49`, `#052e16`) con ratios **> 9:1**.
* **Doble Señalización**: Todo estado se acompaña de iconos (`⚠️`, `📋`, `⚡`, `✓`) y textos contextuales.
* **Tipografía Accesible**: Tamaño base `1rem` (16px), interlineado `1.65` y texto alineado a la izquierda (cero texto justificado para prevenir barreras por dislexia).
* **Navegación por Teclado y Foco Visible**: Anillo de foco `:focus-visible` de 3px (`outline: 3px solid #0284c7; outline-offset: 3px;`).
* **Objetivos Táctiles**: Tamaño mínimo de **44 x 44 px** en botones y elementos interactivos para uso fluido con guantes en taller.
* **Textos Alternativos (`alt`)**: Toda imagen técnica exige descripción funcional del circuito u oscilograma.

### 8.1. Reglas Técnicas de Visualización en Dispositivos Móviles (Smartphones y Tablets)
Para resolver los reportes de mala visualización o desbordamiento en teléfonos móviles de los estudiantes:
1. **Contención de Viewport**: Declaración universal `box-sizing: border-box` en todos los componentes para evitar que padding o bordes sobrepasen el 100% del ancho de la pantalla.
2. **Fórmulas y Tablas sin Desbordamiento**: Tanto `.tech-formula-block` como `.table-responsive` cuentan con scroll horizontal táctil suave (`-webkit-overflow-scrolling: touch; overflow-x: auto; max-width: 100%;`).
3. **Imágenes Flexibles**: Las ilustraciones técnicas escalan con `max-width: 100% !important; height: auto !important; object-fit: contain;`.
4. **Menú Lateral No Intrusivo**: En `H5P.InteractiveBook 1.7`, se configura `"defaultTableOfContents": false`. Esto evita que el cajón del índice cubra toda la pantalla al abrir el libro en un teléfono de 360-390 px de ancho. El estudiante puede abrir el menú pulsando el botón flotante en cualquier momento.
5. **Indicadores Textuales**: En lugar de puntos de progreso diminutos que desbordan la pantalla (`progressType: "dots"`), se emplea formato textual accesible (`progressType: "textual"`).
6. **Librerías Base Íntegras**: Se inyectan las hojas de estilo sin truncar los 1.646 estilos base de `H5P.InteractiveBook-1.7` encargados del comportamiento responsive del contenedor.

---

## 9. Catálogo de Helpers y Herramientas

| Función / Herramienta | Módulo / Script | Propósito Pedagógico y Técnico |
| :--- | :--- | :--- |
| `create_header_logo()` | `H5P.Image 1.1` | Inserta cabecera institucional oficial con alt text accesible. |
| `create_text_section(html, titulo)` | `H5P.AdvancedText 1.1` | Bloques de texto técnico de alto contraste y fórmulas semánticas. |
| `create_drag_text_activity(...)` | `H5P.DragText 1.10` | Manipulación y arrastre de conceptos técnicos a sus huecos. |
| `create_image_hotspots(img, puntos, ...)`| `H5P.ImageHotspots 1.10` | Enriquecimiento interactivo de imágenes con puntos de inspección. |
| `create_multichoice_question(...)` | `H5P.MultiChoice 1.16` | Autocomprobación activa con justificación razonada en cada opción. |
| `create_true_false_question(...)` | `H5P.TrueFalse 1.8` | Validación ágil de reglas críticas de seguridad y criterios técnicos. |
| `create_checkpoint_section(...)` | `.tech-checkpoint` | Pausa activa visual que predispone a la autocomprobación formativa. |
| `create_active_challenge(...)` | `.tech-challenge` | Reto práctico de taller y toma de decisiones ante averías. |
| `create_checklist_section(...)` | `.tech-checklist` | Lista de verificación táctil accesible (touch targets ≥44px). |
| `create_accordion(paneles, titulo)` | `H5P.Accordion 1.0` | Desplegables colapsables para protocolos extensos de taller. |
| `create_simulation_box(...)` | `.sim-box` / `.btn-sim` | Conexión directa a simuladores y laboratorios virtuales interactivos. |
| `create_didactic_sequence_chapter(...)` | `H5P.Column 1.16` | Ensambla un capítulo completo bajo la secuencia de andamiaje de 4 fases. |
| `MoodleXMLBuilder` | `moodle_xml_builder.py` | Generador oficial de bancos de preguntas Moodle XML con retroalimentación (multichoice, truefalse, matching, numerical, shortanswer, ddimageortext). |
| `build_ddimageortext_xml(...)` | `moodle_xml_builder.py` | Generador directo de preguntas de arrastrar y soltar sobre imagen con fondo en Base64. |
| `validar_moodle_xml(xml)` | `moodle_xml_builder.py` | Validador y certificador automático de bancos de preguntas Moodle XML. |

---

## 10. Verificación Automatizada y Flujo de Trabajo

### Compilación y Validación de Paquetes
```bash
# Compilar todo el ecosistema (H5P Formativo + Moodle XML Sumativo)
python3 build.py todos

# Validar paquetes H5P
python3 build.py validar <nombre_paquete.h5p>

# Validar bancos Moodle XML
python3 build.py xml
```

El validador de H5P certifica:
1. Whitelist estricta en `content/` (cero `.html`, cero `.svg`).
2. Clausura física completa de las 16 librerías en la raíz del ZIP.
3. Anidamiento reglamentario en `H5P.Column 1.16`.
4. Metadatos obligatorios UUIDv4 y `metadata.title`.
5. Ausencia de etiquetas `<style>` y delimitadores LaTeX crudos `$`.
6. Detección y contabilización de actividades de Aprendizaje Activo.
7. Cumplimiento de accesibilidad básica (atributos `alt` no vacíos).

El validador de Moodle XML certifica:
1. Conformidad con esquema estándar `<quiz>`.
2. Opciones de respuesta con fracciones equilibradas (100% en correctas).
3. Retroalimentación pedagógica explicada para aciertos y fallos.
4. Control psicométrico de sesgo de longitud (auditoría de homogeneidad y alerta si la opción correcta es sistemáticamente la más extensa).
5. Limpieza de etiquetas `<p>` y `</p>` redundantes según la norma [https://github.com/picuino/test](https://github.com/picuino/test).
6. Validación exhaustiva de preguntas de arrastrar sobre imagen (`ddimageortext`): comprobación de imagen de fondo `<file>` en Base64, etiquetas `<drag>` y zonas de caída `<drop>` con coordenadas `<xleft>` y `<ytop>`.

---

## 11. Arquitectura Desacoplada: Contenido en YAML + Lógica en Python

Para agilizar la producción de cursos y permitir que el profesorado se centre en el rigor técnico y pedagógico sin lidiar con sintaxis de programación o comillas escapadas:
1. **Archivo `contenido_curso.yaml`**: Define los metadatos (autoría `"FP Madrid profesor JM Gurpegui"`, licencia `"CC BY-NC-SA 4.0"`), la secuencia de 4 fases por unidad y las preguntas de evaluación.
2. **Compilador Python (`yaml_course_builder.py`)**:
   - Ensambla automáticamente el paquete `.h5p` (`InteractiveBook`) formativo.
   - Genera el banco de preguntas Moodle XML (`mod_quiz`) sumativo.
   - Optimiza las imágenes de la carpeta `images/` con Pillow (ancho máx 1280 px, calidad 82).
   - Genera UUIDv4 reales y valida ambos productos contra los estándares de EducaMadrid.
3. **Inicio rápido de curso**:
   ```bash
   python3 build.py nuevo MiCurso "Título del Curso"
   python3 build.py MiCurso
   ```

---

## 12. Compilador de Simuladores Interactivos HTML (Whitelist Safe)

Los simuladores de taller desarrollados en HTML/JS (osciloscopios digitales, polímetros, tableros de relés) pueden empaquetarse directamente como recursos H5P independientes listos para Moodle:
```bash
# Compilar un simulador individual o una carpeta completa de simuladores
python3 build.py simuladores <carpeta_o_archivo.html>
```
* **Mecanismo de Seguridad Anti-Rechazo Moodle**: Moodle EducaMadrid rechaza archivos `.html` dentro de `content/` (`not-in-whitelist`). El compilador `h5p_builder/compilar_simulador.py` incrusta el código HTML dentro de `content/content.json` y la librería `H5P.IFrameEmbed 1.0` lo instancia en el navegador mediante Blob URL / `srcdoc` local seguro. Cero archivos `.html` sueltos en `content/`.

