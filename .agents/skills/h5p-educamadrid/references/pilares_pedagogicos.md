# Los 5 Pilares Pedagógicos de Aprendizaje Activo en H5P

Este documento establece la metodología pedagógica obligatoria para el diseño de Unidades de Trabajo y cursos interactivos en **EducaMadrid** y entornos **Moodle**.

---

## Esquema General del Modelo de Aprendizaje Activo

```
[1. Participación Constante] ➔ [2. Andamiaje en 4 Fases] ➔ [3. Retroalimentación Explicada] ➔ [4. Gamificación Didáctica] ➔ [5. Trazabilidad xAPI en Moodle]
```

---

## Pilar 1: Participación Constante del Estudiante y Enriquecimiento Multimedia

### El Problema de la Lectura Pasiva
Los contenidos virtuales que consisten en largos muros de texto estático o reproducción pasiva de vídeos lineales presentan bajas tasas de retención y desconexión cognitiva.

### La Solución Activa
En cada pantalla o sección del curso, el alumno debe interactuar directamente con el contenido:
1. **Manipulación de Conceptos con Arrastre (`H5P.DragText 1.10`)**:
   - El estudiante arrastra palabras, magnitudes o unidades para completar fórmulas o relaciones lógicas.
   - Activa la memoria motriz y la toma activa de decisiones.
2. **Imágenes Técnicas Enriquecidas (`H5P.ImageHotspots 1.10`)**:
   - En lugar de esquemas estáticos, los diagramas de taller se enriquecen con puntos interactivos de inspección.
   - El estudiante pulsa sobre componentes para explorar su función técnica, rangos de medición o precauciones.
3. **Vídeos Interactivos con Paradas Reflexivas (`H5P.InteractiveVideo 1.27`)**:
   - Vídeos alojados en la Mediateca de EducaMadrid con interrupciones automáticas que formulan preguntas clave antes de permitir continuar.

---

## Pilar 2: Estructuración Pedagógica Integrada (Andamiaje en 4 Fases)

### Contenedor Unificado
En lugar de dispersar recursos en el aula virtual de Moodle (un enlace web, un PDF, un foro y un cuestionario suelto), todo el itinerario se integra en un contenedor único y modular:
* **`H5P.InteractiveBook 1.7`**: Contenedor principal con menú lateral de navegación y seguimiento de progreso.
* **`H5P.Column 1.16`**: Contenedor obligatorio de cada capítulo o unidad temática.

### La Secuencia Didáctica Progresiva en 4 Fases
Cada capítulo o tema debe estructurarse obligatoriamente bajo esta progresión:

1. **Fase 1: Presentación Motivadora y Activación de Conocimientos Previos**:
   - Cabecera con insignia de módulo y banner destacado (`.tech-hero`).
   - Reto detonante inicial o dinamización lúdica para activar los esquemas mentales previos del alumno.
2. **Fase 2: Explicación Interactiva y Enriquecimiento**:
   - Exposición técnica concisa (máximo 2-3 párrafos seguidos).
   - Fórmulas matemáticas en HTML semántico + Unicode (<sub>, <sup>, `.tech-formula`).
   - Recursos visuales enriquecidos con hotspots interactivos.
3. **Fase 3: Práctica Guiada Activa y Exploración de Taller**:
   - Actividades de arrastre de términos técnicos (`H5P.DragText`).
   - Retos prácticos de taller y resolución de problemas reales (`.tech-challenge`).
   - Listas de cotejo táctiles para verificación procedimental (`.tech-checklist`).
   - Paneles colapsables (`H5P.Accordion`) para desglosar protocolos extensos.
4. **Fase 4: Evaluación Formativa Reflexiva**:
   - Pausa activa de comprensión (`.tech-checkpoint`).
   - Autocomprobaciones formativas (`H5P.MultiChoice`, `H5P.TrueFalse`) con retroalimentación razonada inmediata.

---

## Pilar 3: Retroalimentación Inmediata y Explicada

### Corrección Automática y Autorregulación
El alumno comprueba sus respuestas al instante mediante el botón "Comprobar", recibiendo feedback en el momento exacto en que mantiene activa su hipótesis mental.

### Justificación Pedagógica en Cada Opción
Queda prohibido el feedback genérico ("Correcto" o "Incorrecto"):
* **En la opción correcta**: Explica el principio físico, eléctrico o normativo que justifica técnicamente por qué es la solución idónea.
* **En las opciones incorrectas**: Explica con precisión el error conceptual o de cálculo cometido (ej. *"Has calculado la potencia en lugar de la caída de tensión"*, *"Olvidaste atenuar la sonda de osciloscopio provocando sobretensión"*).
* **Pistas orientativas (`tips`)**: Consejos pedagógicos previos que orientan la reflexión sin anticipar la respuesta.
* **El Error como Palanca de Aprendizaje**: Configuración obligatoria con `enableRetry: true` y `enableSolutionsButton: true`.

---

## Pilar 4: Gamificación Estratégica con Propósito Didáctico

* **Dinamización lúdica planificada**: Dinámicas de juego (arrastre de términos `DragText`, juegos de memoria `MemoryGame`, emparejamientos y crucigramas) diseñadas para activar la motivación y la agilidad mental.
* **Integración curricular orgánica**: La gamificación no es un adorno superfluo; forma parte de los objetivos de la unidad (ej. identificar simbología normalizada en un tiempo límite o emparejar magnitudes con sus unidades de medida).

---

## Pilar 5: Desacoplamiento Pedagógico: H5P Formativo y Evaluación Sumativa Moodle XML

### 1. Diagnóstico del Error de Registro en Moodle ("No intentado" / Pérdida de xAPI)
En aulas virtuales Moodle y EducaMadrid, cuando se exige una calificación dentro de un contenedor H5P (`InteractiveBook` o `Column`) para marcar la actividad como completada, se producen fallos recurrentes de registro en el alumnado:
* **Pérdida de eventos xAPI en navegadores móviles**: En smartphones (Safari iOS, Chrome Android), las restricciones de almacenamiento de terceros en `iframe` (*Third-Party Cookies / Storage Partitioning*) y los cortes intermitentes de red provocan que las sentencias `answered` o `completed` no lleguen al LRS de Moodle.
* **El puntaje de dominio anula el estado**: Si el alumno omite una sola pregunta formativa intercalada o no pulsa el botón final de envío en la última página, Moodle marca la actividad con estado **"No intentado"**, privándole del progreso de finalización.
* **Problemas ergonómicos en móviles con `DragText`**: En pantallas táctiles de smartphones, los elementos de arrastre colisionan con el scroll vertical de la página y las etiquetas resultan diminutas para interacción táctil con los dedos.

### 2. La Arquitectura Desacoplada Oficial (100% Confiabilidad y Ergonomía Móvil)

Para garantizar que el 100% de los alumnos registren su trabajo y cuenten con una experiencia fluida en cualquier dispositivo:

1. **Paquete H5P (100% Formativo e Ilustrado)**:
   - Se concibe exclusivamente como material de estudio interactivo, esquemas HD, puntos de inspección táctil (`ImageHotspots`), checklists táctiles (`tech-checklist`) y retos de taller.
   - **Prohibido incluir actividades puntuables o de arrastre** (`MultiChoice`, `DragText`, `TrueFalse`, `QuestionSet`) dentro de los paquetes de producción para evitar caídas de trazabilidad xAPI y fallos táctiles en smartphones.
   - La Fase 4 concluye con síntesis de unidad y remisión al Cuestionario Moodle XML (`create_moodle_quiz_referral`).
   - **Configuración de Finalización en Moodle**:
     - *Rastreo de finalización*: "Mostrar la actividad como completada cuando se cumplan las condiciones".
     - *Condición de finalización*: **"El estudiante debe ver esta actividad para completarla"** (marcada).
     - *Requerir calificación*: **Desactivada**.
     - *Aprobado obligatorio*: **Desactivado**.

2. **Cuestionario Sumativo Moodle Nativo (Banco Moodle XML)**:
   - La evaluación oficial calificable se traslada a la herramienta nativa de Moodle (**Cuestionario / `mod_quiz`**).
   - El profesorado importa el banco de preguntas estandarizado en formato **Moodle XML** (`plantilla/evaluacion_modelo_moodle.xml` o generado con `plantilla/moodle_xml_builder.py`).
   - **Ventajas críticas**:
     - Persistencia directa en base de datos Moodle sin depender de iframes ni xAPI.
     - Guardado automático pregunta a pregunta, navegación libre/secuencial y límite de tiempo.
     - Registro garantizado en el Libro de Calificaciones (`Gradebook`) para el 100% de los estudiantes.
