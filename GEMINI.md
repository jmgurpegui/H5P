# Reglas de Trabajo del Repositorio H5P & Cuestionarios Moodle XML

## Cuestionarios tipo XML (Moodle XML / Questionnaires)

1. **Sin patrones en las respuestas**:
   - Queda terminantemente prohibido que exista un patrón identificable en las opciones de respuesta que delate la opción correcta sin conocimiento de la materia.
2. **Prohibición del sesgo de longitud (*Length Bias*)**:
   - Evitar sistemáticamente que la respuesta más larga sea la correcta.
   - La opción correcta y los distractores deben tener una longitud y número de caracteres equilibrados y homogéneos.
   - Alternar de forma deliberada qué opción es más extensa (en algunas preguntas la correcta debe ser la más corta; en otras, homogénea; en otras, un distractor debe ser el más desarrollado).
3. **Calidad y plausibilidad de los distractores**:
   - Los distractores deben formularse con la misma sofisticación técnica, plausibilidad y estructura gramatical que la opción correcta.
   - Las explicaciones detalladas y razonadas pertenecen a la etiqueta `<feedback>`, no al texto visible de la opción `<answer>`.
4. **Aleatorización**:
   - Activar siempre `<shuffleanswers>1</shuffleanswers>` y alternar la posición de la respuesta correcta en el archivo XML.

## Cursos H5P 100% Formativos y Desacoplados (Arquitectura Oficial EducaMadrid)

1. **Desacoplamiento Estricto entre Formación (H5P) y Evaluación (Moodle XML)**:
   - Para garantizar que **el 100% de los alumnos registre la realización de los contenidos sin bloqueos ni fallos**, los cursos H5P (`InteractiveBook`) son exclusivamente **formativos y de consulta/estudio**.
   - **Prohibido incluir actividades evaluativas o prácticas con puntuación/arrastre dentro de los paquetes H5P** (tales como `H5P.MultiChoice`, `H5P.DragText`, `H5P.QuestionSet` o `H5P.TrueFalse`).
   - La evaluación formativa y sumativa oficial con validez académica se gestiona íntegramente a través de **cuestionarios Moodle XML (`mod_quiz`)**, garantizando que el Libro de Calificaciones registre con total fiabilidad los intentos y notas de cada estudiante sin depender del canal xAPI de H5P.
   - En cada capítulo de H5P, la Fase 4 concluye con un bloque de síntesis y derivación directa al cuestionario oficial en Moodle (`create_moodle_quiz_referral`).

2. **Optimización y Visualización Fluida en Dispositivos Móviles**:
   - Las actividades de arrastre (`DragText`) generan graves anomalías táctiles y scrolls involuntarios en pantallas táctiles de smartphones; su supresión en el paquete H5P erradica este fallo por completo.
   - En `InteractiveBook`, configurar siempre `"defaultTableOfContents": false` para evitar que el índice lateral cubra la pantalla y obstaculice la lectura inicial en teléfonos.
   - Mantener objetivos táctiles (*touch targets*) de al menos 44 x 44 px (WCAG 2.5.5) en listas de cotejo táctiles y botones de navegación.
   - Prohibido el uso de etiquetas `<style>` dentro de contenidos de texto (evita *CSS leakage*); todos los estilos responsive se inyectan en las hojas de estilo de las librerías base (`h5p-interactive-book.css` y `h5p-column.css`).

