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
