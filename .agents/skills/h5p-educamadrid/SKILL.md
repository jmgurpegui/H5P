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
   - Para evitar errores de rastreo ("No intentado" en móviles por pérdida de sentencias xAPI en iframes), el H5P se configura en Moodle con la condición de finalización **"El estudiante debe ver esta actividad para completarla"** (sin nota requerida).
   - La evaluación sumativa oficial se gestiona mediante un **Cuestionario Moodle nativo (`mod_quiz`)** a partir del banco de preguntas exportado con `moodle_xml_builder.py`.

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
| `create_drag_text_activity(desc, texto, distractores, titulo)` | `H5P.DragText 1.10` | Manipulación y arrastre interactivo de conceptos a sus casillas. |
| `create_image_hotspots(img, puntos, titulo, alt)` | `H5P.ImageHotspots 1.10` | Enriquecimiento interactivo de imágenes con puntos de inspección. |
| `create_multichoice_question(preg, opciones, titulo)` | `H5P.MultiChoice 1.16` | Autocomprobación activa con justificación pedagógica en cada opción. |
| `create_true_false_question(preg, valor, titulo)` | `H5P.TrueFalse 1.8` | Validación rápida de reglas de seguridad o criterios técnicos. |
| `create_checkpoint_section(titulo, intro)` | `.tech-checkpoint` | Pausa activa visual que predispone a la autocomprobación. |
| `create_active_challenge(titulo, escenario, pasos)` | `.tech-challenge` | Reto práctico de taller y toma de decisiones ante averías. |
| `create_checklist_section(titulo, items)` | `.tech-checklist` | Lista de cotejo táctil accesible (touch targets ≥44px). |
| `create_accordion(paneles, titulo)` | `H5P.Accordion 1.0` | Paneles desplegables colapsables para protocolos extensos. |
| `create_simulation_box(titulo, desc, btn, url)` | `.sim-box` / `.btn-sim` | Conexión directa a simuladores y laboratorios virtuales. |
| `create_didactic_sequence_chapter(...)` | `H5P.Column 1.16` | Ensamblado del capítulo en la secuencia progresiva de 4 fases. |
| `build_h5p_package(...)` | Empaquetador | Compila físicamente el archivo `.h5p` con sus 16 librerías. |

---

## 🔍 Verificación Automatizada con `scripts/validar_h5p.py`

Para certificar la compatibilidad del paquete antes de entregarlo al usuario o subirlo a Moodle:

```bash
python3 .agents/skills/h5p-educamadrid/scripts/validar_h5p.py <paquete.h5p>
```

El script certifica:
1. Whitelist estricta en `content/` (cero `.html`, cero `.svg`).
2. Clausura física completa de las 16 librerías homologadas en el ZIP.
3. Anidamiento reglamentario en `H5P.Column 1.16`.
4. Metadatos obligatorios UUIDv4 y `metadata.title`.
5. Ausencia de fugas de etiquetas `<style>` y delimitadores LaTeX crudos `$`.
6. Detección y contabilización de actividades de Aprendizaje Activo.
7. Cumplimiento de accesibilidad básica (`alt` no vacíos en imágenes).
