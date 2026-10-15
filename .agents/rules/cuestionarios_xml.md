# Regla Psicométrica: Cuestionarios XML (Moodle XML) y Prevención de Patrones de Respuesta

Esta regla aplica a la creación, modificación, ampliación y validación de cualquier cuestionario o banco de preguntas en formato XML (Moodle XML `<quiz>`) y actividades de evaluación tipo test.

---

## 1. Principio Fundamental: Eliminación de Patrones y Sesgos

Queda **estrictamente prohibido** que exista cualquier patrón formal o sintáctico que permita al estudiante identificar la respuesta correcta sin dominar los contenidos técnicos.

### 🚫 El Sesgo de Longitud (*Length Bias / Length Cueing*)
En la generación de reactivos tipo test existe una tendencia habitual a redactar la respuesta correcta con mayor profusión de detalles, matices y aclaraciones, provocando que **la opción más larga sea casi siempre la correcta**.
* En los cuestionarios XML, **la respuesta correcta NUNCA debe ser sistemáticamente la más extensa o detallada**.
* Se debe garantizar una estricta **homogeneidad de longitud** (número similar de palabras y caracteres) entre la respuesta correcta y los distractores.

---

## 2. Directrices Operativas de Redacción de Opciones

1. **Equilibrio Cuantitativo y Cualitativo de Distractores**:
   - Si la respuesta correcta tiene 120 caracteres, los distractores deben rondar entre 100 y 140 caracteres.
   - Los distractores no pueden ser frases telegráficas o descartables por su brevedad mientras la correcta es un párrafo elaborado.
   - Todos los distractores deben formularse con el mismo nivel de precisión técnica, terminología especializada y rigor pedagógico.

2. **Alternancia Deliberada de Longitudes**:
   - En el conjunto del cuestionario, debe alternarse deliberadamente qué alternativa es la más extensa:
     - En unas preguntas, la correcta debe ser la más concisa y directa.
     - En otras preguntas, todas las opciones deben ser idénticas en longitud.
     - En otras preguntas, uno o varios distractores deben ser más largos y detallados que la correcta.
   - En ningún caso la opción correcta puede ser la más larga en más del **35-40%** de las preguntas multichoice del banco.

3. **Homogeneidad Gramatical y Sintáctica**:
   - Todas las opciones de una misma pregunta deben ser paralelas en estructura sintáctica: si una comienza con infinitivo verbal, todas deben comenzar con infinitivo verbal; si una es un sustantivo o sintagma nominal, todas deben serlo.
   - Evitar pistas gramaticales (como concordancia de género o número exclusiva con el enunciado).
   - Evitar modificadores absolutos en los distractores (*"siempre"*, *"nunca"*, *"en ningún caso"*) frente a matices cautelosos en la correcta (*"frecuentemente"*, *"generalmente"*).

4. **Separación entre Enunciado/Opción y Retroalimentación**:
   - No sobrecargar el texto de la opción `<answer><text>` con justificaciones explicativas para hacerla "irrefutable".
   - La justificación técnica detallada de por qué una opción es correcta o por qué es errónea debe residir exclusivamente en la etiqueta `<feedback><text>`, no en la alternativa visible.

5. **Barajado y Distribución Aleatoria**:
   - Configurar siempre `<shuffleanswers>1</shuffleanswers>` en preguntas de opción múltiple (`multichoice`) y emparejamiento (`matching`).
   - Distribuir de forma equitativa la posición de la respuesta correcta en el código XML (no colocar siempre la correcta en la primera posición `<answer fraction="100">`).

---

## 3. Validación y Control Automático

El script oficial `moodle_xml_builder.py` (`validar_moodle_xml`) audita la longitud relativa de las alternativas e informa del porcentaje de preguntas donde la opción correcta es la más extensa:
* Si el ratio supera el umbral admisible (> 50%), emite una **Advertencia Psicométrica de Sesgo de Longitud**.
* Antes de certificar un banco XML para producción en EducaMadrid o Moodle, se debe verificar que no existan patrones predecibles ni sesgos de longitud.
