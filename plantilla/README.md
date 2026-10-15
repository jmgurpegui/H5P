# Plantilla y Herramientas Maestras H5P para EducaMadrid (Moodle)

Esta carpeta contiene la **plantilla técnica integral**, especificaciones normativas, hoja de estilos accesible, validador automatizado y script generador para compilar cursos H5P y cuestionarios Moodle XML 100% compatibles con las Aulas Virtuales de **EducaMadrid** y entornos **Moodle**.

---

## Contenido de la Carpeta `plantilla/`

| Archivo / Recurso | Descripción y Utilidad |
| :--- | :--- |
| **`REQUISITOS_CURSOS_H5P_EDUCAMADRID.md`** | **Manual técnico y especificación oficial**: Arquitectura semántica, whitelist estricta, matriz de versiones de librerías, renderizado de fórmulas sin LaTeX, prevención de fugas de CSS, **los 5 pilares pedagógicos de aprendizaje activo** y **accesibilidad universal WCAG 2.1 AA / AAA**. |
| **`validar_h5p_educamadrid.py`** | **Script de certificación y validación automática**: Analiza cualquier paquete `.h5p` verificando extensiones en `content/`, clausura de librerías, anidamiento en `H5P.Column`, metadatos, detección de actividades activas (`MultiChoice`, `TrueFalse`, `DragText`, `ImageHotspots`), verificación de `alt` en imágenes y ausencia de LaTeX o fugas CSS. |
| **`moodle_xml_builder.py`** | **Módulo generador y validador de cuestionarios Moodle XML**: Permite construir programáticamente bancos de preguntas sumativas (`multichoice`, `truefalse`, `matching`) con feedback explicativo, imágenes y categorías, además de validar la sintaxis XML. |
| **`evaluacion_modelo_moodle.xml`** | **Banco de preguntas modelo Moodle XML (10 preguntas)**: Cuestionario sumativo oficial listo para importar en el Banco de Preguntas de Moodle para la evaluación formal. |
| **`generar_curso_plantilla.py`** | **Generador llave en mano con los 5 pilares pedagógicos**: Script en Python para compilar cursos H5P modelo listos para Moodle, incorporando cabecera oficial, secuencia de andamiaje en 4 fases, preguntas formativas intercaladas con feedback razonado, arrastre de términos (`DragText`), hotspots, retos de taller y checklist táctiles. |
| **`estilos_educamadrid.css`** | **Hoja de estilos CSS oficial accesible y responsive**: Clases optimizadas para tablets y smartphones con contraste certificado WCAG AAA (`.tech-hero`, `.tech-card`, `.tech-checkpoint`, `.tech-challenge`, `.tech-checklist`, `.alert-box`, `.tech-table`, `.tech-formula`, `.btn-sim`) y media queries móviles. |
| **`append_css_to_libraries.py`** | **Inyector limpio de CSS**: Inserta las reglas accesibles en las hojas de estilo de las librerías base respetando las 1.646 líneas originales de layout responsive. |
| **`logo2026.bmp` / `logo2026.png`** | **Logotipo institucional oficial** (Comunidad de Madrid - Unión Europea). El generador detecta y empaqueta automáticamente el archivo disponible (`.bmp`, `.png` o `.jpg`), con recomendación técnica oficial de usar `.png` por su soporte de canal alfa (transparencia) y compresión sin pérdidas. |
| **`Plantilla_Curso_Modelo_EducaMadrid.h5p`** | **Paquete H5P modelo precompilado y certificado**: Puedes subirlo directamente a cualquier Aula Virtual de EducaMadrid para comprobar su funcionamiento inmediato. |

---

## Los 5 Pilares Pedagógicos y Técnicos Homologados

1. **Participación Constante del Estudiante y Enriquecimiento Multimedia**:
   - Evitar lectura pasiva o simple visualización de vídeos. El alumno debe explorar, tomar decisiones, arrastrar elementos (`create_drag_text_activity`) e interactuar con esquemas enriquecidos (`create_image_hotspots`).
2. **Estructuración Pedagógica Integrada (Andamiaje en 4 Fases)**:
   - Contenedores unificados (`InteractiveBook 1.7` con capítulos `Column 1.16`).
   - Secuencia de andamiaje: *Fase 1 (Motivación/Activación)* ➔ *Fase 2 (Explicación interactiva)* ➔ *Fase 3 (Práctica guiada)* ➔ *Fase 4 (Evaluación formativa)* (`create_didactic_sequence_chapter`).
3. **Retroalimentación Inmediata y Explicada**:
   - Corrección automática con justificación pedagógica en cada opción: explica por qué es correcta y en qué consiste el fallo en las incorrectas (`create_multichoice_question`).
   - Pistas orientativas (`tips`) y reintentos ilimitados para aprender del error.
4. **Gamificación Estratégica con Propósito Didáctico**:
   - Dinamización lúdica integrada (arrastre de magnitudes, juegos de memoria, retos) para activar conocimientos previos o cerrar lecciones.
5. **Desacoplamiento Arquitectónico (H5P Formativo + Moodle XML Sumativo)**:
   - **H5P Formativo**: Estudio autónomo, andamiaje y autocomprobación interactiva. En Moodle, se configura el rastreo de finalización con **"El estudiante debe ver esta actividad para completarla"** (sin requerir calificación ni aprobado obligatorio). Esto resuelve de raíz los fallos de registro ("No intentado") en móviles y navegadores con bloqueo de cookies de terceros en iframe.
   - **Moodle XML Sumativo**: La evaluación oficial calificable se traslada a la herramienta nativa **Cuestionario (`mod_quiz`)** de Moodle, importando los bancos XML generados. Esto garantiza guardado automático, persistencia en base de datos y registro infalible en el Calificador (`Gradebook`) para el 100% del alumnado.

---

## 📱 Optimización para Dispositivos Móviles

Se han incorporado correcciones críticas para garantizar que el recurso sea perfectamente usable en smartphones y tablets (desde 360px de ancho):
1. **Cajón lateral cerrado por defecto (`defaultTableOfContents: false`)**: El índice no bloquea la pantalla al abrir el libro en teléfonos.
2. **Progreso textual (`progressType: "textual"`)**: Muestra "Página X de Y" en lugar de puntos de progreso que se desbordan o solapan.
3. **Objetivos táctiles adaptados**: Botones interactivos con área táctil mínima de 44 × 44 px.
4. **Desplazamiento horizontal táctil**: Tablas y bloques de fórmulas envueltos con `overflow-x: auto` y `-webkit-overflow-scrolling: touch`.
5. **Imágenes y recursos flexibles**: `max-width: 100%; height: auto;` para evitar cualquier desbordamiento horizontal.

---

## Cómo Validar y Generar los Recursos

### 1. Validar un Paquete H5P
```bash
python3 plantilla/validar_h5p_educamadrid.py <ruta_del_paquete.h5p>
```

### 2. Generar el Paquete H5P de la Plantilla
```bash
python3 plantilla/generar_curso_plantilla.py
```

### 3. Validar los Bancos de Preguntas Moodle XML
```bash
python3 -c "import moodle_xml_builder as m; print(m.validar_moodle_xml('evaluacion_modelo_moodle.xml'))"
```

---

## 📥 Cómo Importar el Banco Moodle XML en el Aula Virtual

1. Entra en tu curso de Moodle / EducaMadrid y accede a **Banco de preguntas** en la administración del curso.
2. Selecciona la pestaña **Importar**.
3. En *Formato de archivo*, selecciona **Formato Moodle XML**.
4. Arrastra el archivo `evaluacion_modelo_moodle.xml` al área de subida y pulsa **Importar**.
5. Las preguntas quedarán categorizadas y listas para añadirse a cualquier **Cuestionario** (`mod_quiz`) con calificación automática.
