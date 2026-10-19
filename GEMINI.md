# Reglas de Trabajo del Repositorio H5P & Cuestionarios Moodle XML (FP Automoción)

## 1. Política de Repositorio en GitHub (Exclusivamente Plantilla)

- En el repositorio de GitHub (`jmgurpegui/H5P`) **solo se mantiene y sincroniza la plantilla maestra** (`plantilla/`, `h5p_builder/`, `.agents/`, `build.py` y documentación técnica).
- **Prohibido subir carpetas de cursos concretos ni paquetes `.h5p` de cursos específicos a GitHub**.
- Para iniciar un curso nuevo en local, utiliza `python3 build.py nuevo <NombreCurso> "Título del Curso"`.

## 2. Cuestionarios tipo XML (Moodle XML / Questionnaires)

1. **Sin patrones en las respuestas**:
   - Queda terminantemente prohibido que exista un patrón identificable en las opciones de respuesta que delate la opción correcta sin conocimiento de la materia.
2. **Prohibición bidireccional del sesgo de longitud (*Length Bias*)**:
   - Evitar tanto que la respuesta más larga sea sistemáticamente la correcta (> 45 %) como que nunca lo sea (0 %).
   - En bancos con $\ge 5$ preguntas `multichoice`, la opción correcta debe ser la más larga en una proporción equilibrada (**entre el 15 % y el 40 %** de las preguntas, idealmente ~25 %).
   - La opción correcta y los distractores deben tener una longitud y número de caracteres equilibrados y homogéneos (±20 %).
3. **Calidad y plausibilidad de los distractores**:
   - Los distractores deben formularse con la misma sofisticación técnica, plausibilidad y estructura gramatical que la opción correcta.
   - Las explicaciones detalladas y razonadas pertenecen a la etiqueta `<feedback>`, no al texto visible de la opción `<answer>`.
4. **Aleatorización y rotación de posición en el XML**:
   - Activar siempre `<shuffleanswers>1</shuffleanswers>` y distribuir equitativamente la posición de la respuesta correcta (`A, B, C, D`) en el archivo XML (`MoodleXMLBuilder.add_multichoice` lo realiza automáticamente).
5. **Tipología enriquecida para FP de Automoción**:
   - Combinar preguntas de opción múltiple (`add_multichoice`), problemas de cálculo numérico de taller con tolerancia y unidades (`add_numerical`), identificación directa de bornes DIN / códigos ECE en respuesta corta (`add_shortanswer`), emparejamiento (`add_matching`) y verdadero/falso (`add_truefalse`).
6. **Sin etiquetas `<p>` y `</p>` innecesarias (Norma Picuino / Test)**:
   - Las preguntas de test XML no necesitan `<p>` ni `</p>`.
   - El texto del enunciado (`<questiontext>`), opciones de respuesta (`<answer>`) y retroalimentaciones (`<feedback>`) deben redactarse en texto limpio y directo sin envoltorios `<p>...</p>`, evitando espaciados y desajustes visuales indeseados en la interfaz de Moodle. Se preserva únicamente marcado semántico inline (`<strong>`, `<sub>`, `<sup>`, `<code>`) cuando sea técnicamente imprescindible.
   - Norma técnica oficial de referencia: https://github.com/picuino/test.

## 3. Cursos H5P 100% Formativos y Desacoplados (Arquitectura Oficial EducaMadrid)

1. **Desacoplamiento Estricto entre Formación (H5P) y Evaluación (Moodle XML)**:
   - Para garantizar que **el 100 % de los alumnos registre la realización de los contenidos sin bloqueos ni fallos**, los cursos H5P (`InteractiveBook`) son exclusivamente **formativos y de consulta/estudio**.
   - **Prohibido incluir actividades evaluativas o prácticas con puntuación/arrastre dentro de los paquetes H5P** (tales como `H5P.MultiChoice`, `H5P.DragText`, `H5P.QuestionSet` o `H5P.TrueFalse`).
   - La evaluación formativa y sumativa oficial con validez académica se gestiona íntegramente a través de **cuestionarios Moodle XML (`mod_quiz`)**.
   - En cada capítulo de H5P, utilizar los helpers técnicos de Automoción (`create_component_spec_card`, `create_diagnostic_table`, `create_active_challenge`, `create_checklist_section`, `create_accordion`, `create_video_section`) y cerrar la Fase 4 con `create_moodle_quiz_referral`.

2. **Optimización Móvil y Alto Contraste (Cero Textos Claros)**:
   - Prohibido usar colores de texto claros, pálidos o de bajo contraste. El texto principal emplea siempre `#0f172a` (ratio > 13:1 sobre fondo blanco).
   - En `InteractiveBook`, configurar siempre `"defaultTableOfContents": false` y `"progressType": "textual"`.
   - Mantener objetivos táctiles (*touch targets*) de al menos 44 x 44 px (WCAG 2.5.5).
   - Prohibido el uso de etiquetas `<style>` dentro de contenidos de texto (evita *CSS leakage*); todos los estilos responsive se inyectan en las hojas de estilo de las librerías base (`python3 build.py css`).

3. **Whitelist Estricta en Librerías H5P (Compatibilidad Lumi Desktop y Moodle)**:
   - Los paquetes `.h5p` no deben incluir jamás archivos de desarrollo listados en `.h5pignore` ni archivos sin extensión o fuera de la *whitelist* de H5P dentro de las carpetas de librerías.
   - Todo curso debe empaquetarse invocando `build_h5p_package()` de `plantilla/generar_curso_plantilla.py` y certificarse con `validar_h5p_educamadrid.py`.

## 4. Arquitectura de Cursos: Contenido en YAML y Lógica en Python

1. **Separación de Responsabilidades**:
   - El contenido pedagógico (secuencia en 4 fases, fichas técnicas, cuadros de diagnosis, listas de verificación) y el banco de preguntas se redactan en **`contenido_curso.yaml`** (o `plantilla/contenido_modelo.yaml`).
   - La lógica de empaquetado, dependencias de librerías, generación de `subContentId` con `uuid.uuid4()`, rotación y control de sesgo psicométrico corre en **Python** (`yaml_course_builder.py`).
2. **Metadatos y Licenciamiento Homologado**:
   - Autoría obligatoria: `"FP Madrid profesor JM Gurpegui"`.
   - Licencia: `"CC BY-NC-SA"`, versión `"4.0"`, idioma `"es"`.
3. **Pipeline de Imágenes con Pillow**:
   - Toda imagen ubicada en `images/` se optimiza automáticamente: ancho máximo de 1280 px, compresión JPEG a calidad 82 (o PNG optimizado), y sanitización de nombres de archivo (sin tildes, ñ ni caracteres especiales).

## 5. Compilación de Simuladores Interactivos HTML (Whitelist Safe)

1. **Incrustación Segura sin Error 'not-in-whitelist'**:
   - Para integrar simuladores HTML (osciloscopios Rigol, multímetros Fluke, bancos de diagnosis) en EducaMadrid, utiliza:
     ```bash
     python3 build.py simuladores <carpeta_o_archivo.html>
     ```
   - El compilador `h5p_builder/compilar_simulador.py` incrusta el código HTML en `content/content.json` y `iframe-embed.js` lo ejecuta vía Blob URL / `srcdoc` local.
   - Prohibido dejar archivos `.html` sueltos dentro de la carpeta `content/` del ZIP (evita el bloqueo estricto de Moodle al importar).
