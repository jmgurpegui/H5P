---
name: h5p-educamadrid
description: >-
  Normas técnicas, empaquetado, arquitectura semántica, los 5 pilares pedagógicos de aprendizaje activo, protocolo de entrevista diagnóstica inicial y accesibilidad universal de paquetes H5P para EducaMadrid (Moodle). Usar siempre que se diseñe, edite, valide o empaquete un recurso o curso H5P destinado a Aulas Virtuales de EducaMadrid y Moodle, garantizando cumplimiento de la whitelist, resolución de errores 'not-in-whitelist', dependencias completas de librerías, diseño responsive (WCAG 2.1 AA/AAA), entrevista previa de parámetros clave, andamiaje en 4 fases, retroalimentación explicada, gamificación y trazabilidad xAPI en Formación Profesional y Bachillerato/Secundaria.
---

# H5P para EducaMadrid y Moodle: Skill Oficial para Gemini

Este skill capacita al agente para diseñar, maquetar, validar y empaquetar cursos y Unidades de Trabajo interactivas en formato **H5P**, garantizando el 100% de compatibilidad con las Aulas Virtuales de **EducaMadrid** (Moodle), el cumplimiento de la lista blanca (*whitelist*), la prevención de pantallas en blanco (*white screen of death*), los **5 pilares pedagógicos de aprendizaje activo** y la **accesibilidad universal (WCAG 2.1 AA / AAA)**.

---

## 📁 Estructura del Skill

```text
.agents/skills/h5p-educamadrid/
├── SKILL.md                  # Manual maestro de instrucciones operativas
├── scripts/                  # Scripts ejecutables y herramientas automatizadas
│   ├── generar_curso.py      # Generador y compilador de cursos H5P llave en mano
│   ├── validar_h5p.py        # Validador y certificador oficial EducaMadrid / Moodle
│   ├── inyectar_css.py       # Inyector limpio de hojas de estilo en librerías base
│   └── moodle_xml_builder.py # Generador y validador de bancos de preguntas Moodle XML
├── resources/                # Recursos y plantillas de diseño
│   ├── logo2026.png / .bmp   # Logotipo institucional oficial Comunidad de Madrid
│   ├── CC.png                # Logotipo oficial de licencia Creative Commons
│   └── estilos_educamadrid.css # Hoja de estilos accesible y responsive (WCAG AAA)
├── references/               # Documentación técnica y pedagógica detallada
│   ├── entrevista_diagnostica.md # Protocolo de preguntas clave iniciales
│   ├── pilares_pedagogicos.md # Los 5 pilares de aprendizaje activo y andamiaje
│   ├── requisitos_tecnicos.md # Normativa técnica, whitelist y semántica JSON
│   └── accesibilidad_wcag.md # Directrices WCAG 2.1 AA/AAA y diseño inclusivo
└── examples/                 # Implementaciones de referencia
    ├── curso_modelo_ejemplo.py # Código fuente de referencia para generar cursos
    ├── Plantilla_Curso_Modelo_EducaMadrid.h5p # Paquete modelo precompilado
    └── evaluacion_modelo_moodle.xml # Banco Moodle XML de evaluación sumativa
```

---

## 🚀 Flujo de Trabajo Operativo para el Agente

Cuando el usuario solicite crear, modificar o validar un recurso H5P, sigue estrictamente este procedimiento:

```
[Paso 1: Entrevista Inicial] ➔ [Paso 2: Andamiaje en 4 Fases] ➔ [Paso 3: Autoría con Helpers] ➔ [Paso 4: Validación Automática]
```

### Paso 1: Entrevista Inicial de Diagnóstico Curricular
Antes de generar código, confirma o solicita los **7 parámetros clave** (consulta [Guía de Entrevista](./references/entrevista_diagnostica.md)):

```markdown
- Tema del contenido: [Conceptos nucleares, fórmulas o destrezas técnicas]
- Asignatura y Nivel: [Ej. 2º Bachillerato - Historia / 1º CFGM Electromecánica]
- Tipo de actividad H5P: [Interactive Book (4 fases) / Question Set / Drag the Words / Image Hotspots / True-False]
- Cantidad de ítems: [Ej. 2 capítulos con 10 preguntas / 8 huecos de arrastre / 4 puntos de inspección]
- Nivel cognitivo (Bloom): [Recordar / Comprender / Aplicar / Analizar / Evaluar]
- Estrategia de Retroalimentación: [Formativa con pistas y explicaciones razonadas / Sumativa en Moodle XML]
- Recursos Multimedia: [Imágenes PNG/JPG disponibles, vídeos en Mediateca EducaMadrid]
```

### Paso 2: Aplicación de los 5 Pilares Pedagógicos
Diseña el contenido asegurando la participación constante del estudiante (consulta [Pilares Pedagógicos](./references/pilares_pedagogicos.md)):
1. **Participación activa**: Cero muros de texto pasivo; interacción continua (arrastrar términos, explorar hotspots).
2. **Andamiaje en 4 fases**:
   - *Fase 1*: Motivación y activación previa (reto inicial o gamificación).
   - *Fase 2*: Explicación interactiva (máximo 2-3 párrafos con fórmulas semánticas y hotspots).
   - *Fase 3*: Práctica guiada (arrastre de términos `DragText`, casos de taller `.tech-challenge` y checklists táctiles).
   - *Fase 4*: Evaluación formativa (preguntas con feedback razonado inmediato).
3. **Retroalimentación explicada**: Toda opción de respuesta justifica técnicamente por qué es válida o en qué consiste el fallo (`chosenFeedback`).
4. **Gamificación estratégica**: Dinamización lúdica integrada orgánicamente en el tema.
5. **Desacoplamiento Formativo H5P + Sumativo Moodle XML**:
   - **Cursos H5P 100% Formativos**: Para evitar fallos en el registro de calificaciones ("No intentado" o pérdida de sentencias xAPI en móviles por bloqueo de cookies o iframes) y problemas de arrastre táctil en smartphones, **está prohibido incluir actividades puntuables o de arrastre (`MultiChoice`, `DragText`, `TrueFalse`, `QuestionSet`) dentro de los paquetes H5P de producción**.
   - **Fase 4 de Andamiaje**: Concluye con un bloque didáctico de síntesis y derivación directa al Cuestionario Moodle XML (`create_moodle_quiz_referral`).
   - **Finalización en Moodle**: El recurso H5P se configura con **"El estudiante debe ver esta actividad para completarla"** (100% fiable para todos los alumnos).
   - **Evaluación Sumativa Oficial**: Se canaliza a través de **Cuestionarios Moodle (`mod_quiz`)** a partir del banco de preguntas XML generado con `moodle_xml_builder.py`.
   - **Regla Psicométrica contra Patrones y Sesgo de Longitud (*Length Bias*)**:
     * Queda estrictamente prohibido que la respuesta correcta sea sistemáticamente la más extensa o detallada.
     * La opción correcta y los distractores deben mantener una longitud y estructura sintáctica homogénea (±15-20% de caracteres).
     * Alternar deliberadamente qué alternativa es la más larga o concisa (en algunas preguntas la correcta debe ser la más breve; en otras, los distractores deben ser más desarrollados).
     * Los distractores deben poseer alta plausibilidad y rigor técnico idéntico a la correcta.
     * Las justificaciones explicativas pertenecen a la retroalimentación (`<feedback>`), no al cuerpo de la alternativa (`<answer>`).
     * Activar siempre `<shuffleanswers>1</shuffleanswers>` y alternar la posición de las claves de respuesta.
     * **Sin etiquetas `<p>` ni `</p>` innecesarias (Norma Picuino / Test)**: Las preguntas de test XML no necesitan `<p>` ni `</p>`. El texto del enunciado (`<questiontext>`), opciones (`<answer>`) y retroalimentaciones (`<feedback>`) deben redactarse en texto limpio y directo sin envoltorios `<p>...</p>`, preservando únicamente formato inline (`<strong>`, `<sub>`, `<sup>`, `<code>`) cuando sea técnicamente indispensable (referencia técnica: [https://github.com/picuino/test](https://github.com/picuino/test)).

### Paso 3: Reglas Técnicas, Accesibilidad Universal y Optimización Móvil
Cumple estrictamente los estándares técnicos y de accesibilidad (consulta [Requisitos Técnicos](./references/requisitos_tecnicos.md) y [Accesibilidad WCAG](./references/accesibilidad_wcag.md)):
* **Whitelist estricta**: Cero archivos `.html` y cero `.svg` en `content/`. Diagramas rasterizados a **PNG** o **JPEG**.
* **Fórmulas sin LaTeX**: Prohibido usar `$ ... $`. Usar HTML semántico y Unicode (`<sub>`, `<sup>`, `.tech-formula`, `.tech-formula-block`).
* **Cero etiquetas `<style>` en HTML**: Estilos inyectados en librerías base para evitar fugas de código CSS en pantalla.
* **Diseño Responsive para Móviles**:
  - `behaviour.defaultTableOfContents: false` en `InteractiveBook` para evitar que el índice tape la pantalla en móviles.
  - `behaviour.progressType: "textual"` para evitar desbordamientos de círculos de progreso en pantallas estrechas (≤480px).
  - Tablas y fórmulas envueltas con desplazamiento horizontal táctil suave (`overflow-x: auto; -webkit-overflow-scrolling: touch;`).
* **Contraste WCAG AAA**: Texto Slate 900 (`#0f172a`) sobre blanco (> 13:1), insignias y alertas con ratios > 7:1 a 9:1.
* **Objetivos táctiles**: Botones y elementos interactivos con tamaño mínimo de **44 x 44 px**.
* **Textos alternativos `alt`**: Toda imagen técnica exige descripción funcional obligatoria.
* **Anidamiento en `H5P.Column`**: Todo elemento debe envolverse con `{"content": ..., "useSeparator": "auto"}` y contar con `subContentId` (UUIDv4) y `metadata.title`.

---

## 🛠️ Catálogo de Helpers en `scripts/generar_curso.py`

| Función Helper | Librería / Módulo | Utilidad en el Diseño |
| :--- | :--- | :--- |
| `create_header_logo()` | `H5P.Image 1.1` | Inserta cabecera institucional oficial con resolución dinámica de logo (`.bmp`, `.png`, `.jpg`). |
| `create_text_section(html, titulo)` | `H5P.AdvancedText 1.1` | Bloques de texto técnico de alto contraste y fórmulas semánticas. |
| `create_component_spec_card(...)` | `.tech-spec-grid` | Ficha técnica de sensor/actuador de Automoción (valores nominales, pinout DIN 72552, osciloscopio). |
| `create_diagnostic_table(titulo, filas)` | `.tech-table` | Tabla metrológica de diagnosis en taller (Síntoma ➔ Medición ➔ Valores ➔ Acción correctiva). |
| `create_video_section(url, titulo)` | `H5P.Video 1.6` | Reproductor nativo de vídeos técnicos demostrativos (YouTube / Mediateca EducaMadrid). |
| `create_image_hotspots(img, puntos, titulo, alt)` | `H5P.ImageHotspots 1.10` | Enriquecimiento interactivo de imágenes con puntos de inspección táctiles. |
| `create_moodle_quiz_referral(num, titulo, resumen)` | `.tech-checkpoint` | Tarjeta de síntesis de unidad y derivación oficial a evaluación en Moodle XML. |
| `create_checkpoint_section(titulo, intro)` | `.tech-checkpoint` | Pausa activa visual y recordatorio conceptual de unidad. |
| `create_active_challenge(titulo, escenario, pasos)` | `.tech-challenge` | Reto práctico de taller y toma de decisiones ante averías. |
| `create_checklist_section(titulo, items)` | `.tech-checklist` | Lista de cotejo táctil accesible (touch targets ≥44px). |
| `create_accordion(paneles, titulo)` | `H5P.Accordion 1.0` | Paneles desplegables colapsables para protocolos extensos. |
| `create_simulation_box(titulo, desc, btn, url)` | `.sim-box` / `.btn-sim` | Conexión directa a simuladores y laboratorios virtuales. |
| `create_didactic_sequence_chapter(...)` | `H5P.Column 1.16` | Ensamblado del capítulo en la secuencia progresiva de 4 fases. |
| `build_h5p_package(...)` | Empaquetador | Compila físicamente el archivo `.h5p` con sus 18 librerías homologadas. |

---

## 🔍 Verificación Automatizada con `scripts/validar_h5p.py`

Para certificar la compatibilidad del paquete antes de entregarlo al usuario o subirlo a Moodle:

```bash
python3 .agents/skills/h5p-educamadrid/scripts/validar_h5p.py <paquete.h5p>
```

El script certifica:
1. Whitelist estricta en `content/` (cero `.html`, cero `.svg`) y en todas las carpetas de librerías empaquetadas (cero `.scss`, `.yml`, `LICENSE` sin extensión o dotfiles que provoquen `package-validation-failed:not-in-whitelist` en Lumi y Moodle).
2. Clausura física completa de las librerías homologadas en el ZIP.
3. Anidamiento reglamentario en `H5P.Column 1.16`.
4. Metadatos obligatorios UUIDv4 y `metadata.title`.
5. Ausencia de fugas de etiquetas `<style>` y delimitadores LaTeX crudos `$`.
6. Detección y contabilización de actividades de Aprendizaje Activo.
7. Cumplimiento de accesibilidad básica (`alt` no vacíos en imágenes).

