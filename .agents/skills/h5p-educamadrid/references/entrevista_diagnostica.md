# Protocolo de Entrevista Inicial de Diagnóstico Curricular

Antes de programar o generar cualquier Unidad de Trabajo, curso o actividad interactiva H5P, el agente o diseñador instruccional **debe confirmar o solicitar los siguientes parámetros clave** para garantizar un diseño pedagógico y técnico exacto.

---

## Plantilla de Parámetros Clave

```markdown
- Tema del contenido: [Insertar Tema, conceptos nucleares o destrezas técnicas]
- Asignatura y Nivel: [Ej. 2º Bachillerato - Historia de España / 1º CFGM Electromecánica - Sistemas de Carga]
- Tipo de actividad / contenedor H5P: [Ej. Interactive Book (4 fases) / Question Set / Drag the Words / Image Hotspots / Single Choice Set]
- Cantidad de ítems: [Ej. 2 capítulos con 10 preguntas / 8 huecos de arrastre / 4 puntos de inspección]
- Nivel cognitivo (Taxonomía de Bloom): [Recordar / Comprender / Aplicar / Analizar / Evaluar / Crear]
- Estrategia de Retroalimentación: [Formativa reflexiva con pistas y explicaciones ante error / Sumativa formal con nota xAPI]
- Recursos Multimedia: [Imágenes/esquemas PNG/JPG disponibles, vídeos en Mediateca EducaMadrid o laboratorios virtuales externos]
```

---

## Guía de Interpretación de Parámetros

### 1. Tema del Contenido y Resultados de Aprendizaje (RA)
* Concretar los conceptos nucleares, fórmulas físicas o protocolos de taller a trabajar.
* Si el contenido incluye procedimientos de seguridad o normativa laboral (EPIs, alta tensión), destacarlo para incluir alertas contextuales de seguridad.

### 2. Asignatura y Nivel Educativo
* **Formación Profesional (Ciclos Formativos Básicos, Medios y Superiores)**:
  * Enfoque altamente práctico: casos de diagnosis de averías, oscilogramas, esquemas eléctricos y protocolos de taller paso a paso.
* **Bachillerato y ESO**:
  * Enfoque conceptual, analítico y deductivo: mapas conceptuales, análisis de fuentes históricas, experimentos científicos o cálculo numérico.

### 3. Tipo de Actividad / Contenedor H5P
* **`H5P.InteractiveBook 1.7` (Recomendado)**: Contenedor integral para unidades completas de trabajo con menú lateral de navegación.
* **`H5P.Column 1.16`**: Contenedor modular obligatorio para cada capítulo del libro.
* **`H5P.DragText 1.10`**: Arrastre interactivo de términos, magnitudes y secuencias.
* **`H5P.ImageHotspots 1.10`**: Esquemas e imágenes técnicas enriquecidas con puntos interactivos de inspección.
* **`H5P.MultiChoice 1.16`**: Preguntas de opción múltiple con justificación pedagógica en cada alternativa.
* **`H5P.TrueFalse 1.8`**: Validación ágil de reglas críticas o criterios técnicos.
* **`H5P.QuestionSet 1.20`**: Batería de evaluación sumativa final vinculada al calificador.

### 4. Cantidad y Densidad de Ítems
* Aplicar la regla del andamiaje: intercalar una actividad formativa o reto de taller cada 2 o 3 párrafos de teoría técnica.

### 5. Nivel Cognitivo (Taxonomía de Bloom)
* **Recordar**: Términos técnicos, simbología, unidades de medida (ideal para `DragText` o `MemoryGame`).
* **Comprender**: Explicación de relaciones causa-efecto y funcionamiento de sistemas (`ImageHotspots` o `TrueFalse`).
* **Aplicar**: Resolución de ejercicios numéricos y aplicación de fórmulas (`MultiChoice` con cálculos).
* **Analizar**: Diagnóstico de fallos y toma de decisiones ante averías reales (`.tech-challenge`).

### 6. Estrategia de Retroalimentación
* **Formativa reflexiva**: Corrección inmediata, reintentos ilimitados (`enableRetry: true`), botón de solución (`enableSolutionsButton: true`) y feedback explicativo tanto para aciertos como para fallos.
* **Sumativa xAPI**: Preguntas evaluables finales con registro en el Libro de Calificaciones (`mdl_grade_grades`).

### 7. Recursos Multimedia
* Solo imágenes en formato **PNG** o **JPEG** (prohibido SVG en `content/`).
* Vídeos y audios alojados exclusivamente en la **Mediateca de EducaMadrid** para no saturar las cuotas de disco del servidor Moodle.
