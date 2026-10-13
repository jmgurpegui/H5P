# Entorno de Creación de Cursos H5P para EducaMadrid (Moodle)

Este repositorio contiene el **entorno oficial y plantilla homologada** para la creación, maquetación y validación de cursos interactivos H5P destinados a las Aulas Virtuales de **EducaMadrid** y entornos **Moodle**.

Garantiza el cumplimiento de las normativas de seguridad institucional, la **integración de los 5 pilares pedagógicos de aprendizaje activo** y las pautas de **accesibilidad universal (WCAG 2.1 AA / AAA)**.

---

## 📁 Estructura del Proyecto

```text
H5P/
├── REQUISITOS_CURSOS_H5P_EDUCAMADRID.md      # Especificación oficial EducaMadrid (Técnica, Pedagógica y Accesibilidad)
├── plantilla/                                # Toolkit y plantilla técnica maestra
│   ├── REQUISITOS_CURSOS_H5P_EDUCAMADRID.md  # Especificación técnica oficial, los 5 pilares y accesibilidad
│   ├── generar_curso_plantilla.py            # Generador y plantilla de código con helpers de los 5 pilares
│   ├── validar_h5p_educamadrid.py            # Validador de certificación EducaMadrid (whitelist, CSS, a11y)
│   ├── estilos_educamadrid.css               # Hoja de estilos accesible (WCAG AAA, táctil, fórmulas)
│   ├── append_css_to_libraries.py            # Inyector limpio de CSS en librerías base
│   ├── logo2026.png                          # Logotipo institucional oficial con transparencia (Comunidad de Madrid)
│   ├── logo2026.bmp                          # Logotipo complementario en formato BMP
│   ├── CC.png                                # Logotipo oficial Creative Commons
│   ├── Plantilla_Curso_Modelo_EducaMadrid.h5p# Paquete H5P modelo certificado y listo para Moodle (1.7 MB)
│   └── README.md                             # Documentación detallada de la plantilla
│
├── EsquemasElectricosAutomocion/             # Caso de éxito real: Curso interactivo de Formación Profesional
│   ├── Curso_Esquemas_Electricos_Automocion.h5p # Paquete H5P certificado listo para el Aula Virtual (2.0 MB)
│   ├── generar_curso_esquemas.py             # Script generador maestro con 4 capítulos y 13 actividades
│   ├── images/                               # Esquemas eléctricos y diagramas rasterizados de alta resolución
│   └── README.md                             # Guía curricular, unidades didácticas y normativa DIN
│
├── h5p_builder/
│   └── h5p-libraries/                        # Repositorio maestro de librerías oficiales H5P homologadas
│
└── .agents/
    └── skills/
        └── h5p-educamadrid/                  # Skill oficial para Agentes de IA (Gemini / Antigravity)
            ├── SKILL.md                      # Manual operativo con progressive disclosure
            ├── scripts/                      # Scripts ejecutables (generar, validar, inyectar)
            ├── resources/                    # Logos oficiales (2026, CC) y estilos CSS accesibles
            ├── references/                   # Documentación modular (pedagogía, técnica, a11y, entrevista)
            └── examples/                     # Implementaciones de referencia y paquete .h5p
```

---

## 🌟 Los 5 Pilares Pedagógicos de Aprendizaje Activo

1. **Participación Constante del Estudiante y Enriquecimiento Multimedia**:
   - Cero lectura pasiva o visualización lineal. El alumnado explora esquemas interactivos (`create_image_hotspots`), arrastra términos técnicos (`create_drag_text_activity`) y toma decisiones diagnósticas en cada lección.
2. **Estructuración Pedagógica Integrada (Andamiaje en 4 Fases)**:
   - Contenedor unificado (`InteractiveBook 1.7` con capítulos `Column 1.16`).
   - Secuencia de andamiaje: *Fase 1 (Motivación/Activación)* ➔ *Fase 2 (Explicación interactiva)* ➔ *Fase 3 (Práctica guiada)* ➔ *Fase 4 (Evaluación formativa)* (`create_didactic_sequence_chapter`).
3. **Retroalimentación Inmediata y Explicada**:
   - Corrección instantánea con justificación pedagógica en cada opción: explicación razonada de aciertos y análisis del error en opciones incorrectas (`create_multichoice_question`).
   - Pistas orientativas (`tips`) y reintentos ilimitados para aprender del error.
4. **Gamificación Estratégica con Propósito Didáctico**:
   - Dinamización lúdica planificada (arrastre de magnitudes, juegos de memoria, retos) integrada orgánicamente en la narrativa técnica.
5. **Integración con la Evaluación y Trazabilidad en Moodle**:
   - Publicación como **Actividad H5P Nativa** para registrar calificaciones y progreso vía xAPI en el Calificador (`mdl_grade_grades`).
   - Incrustaciones para práctica autónoma y actividades nativas para evaluación sumativa.

---

## 🚀 Cómo Crear un Nuevo Curso H5P

1. **Completar la Entrevista Inicial de Diagnóstico**:
   Antes de generar el código, definir o confirmar:
   * **Tema del contenido**: Título y conceptos nucleares.
   * **Asignatura y Nivel**: Ej. 2º Bachillerato - Historia de España / 1º CFGM Electromecánica.
   * **Tipo de actividad**: Interactive Book (4 fases), Question Set, Drag the Words, Image Hotspots.
   * **Cantidad de ítems**: Preguntas, huecos arrastrables, puntos de inspección o capítulos.
   * **Nivel cognitivo (Bloom)**: Recordar, Comprender, Aplicar, Analizar, Evaluar.
   * **Retroalimentación**: Formativa explicada con pistas / Sumativa con xAPI.
   * **Recursos multimedia**: Imágenes PNG/JPG, vídeos Mediateca EducaMadrid o simuladores.

2. **Editar o duplicar el script de plantilla**:
   Abre [`plantilla/generar_curso_plantilla.py`](plantilla/generar_curso_plantilla.py) y construye los temas con los helpers homologados:
   * `create_header_logo()`: Cabecera oficial accesible con `logo2026.png`.
   * `create_text_section(html, titulo)`: Texto de alto contraste con fórmulas semánticas.
   * `create_drag_text_activity(desc, texto, distractores, titulo)`: Arrastre interactivo de términos y magnitudes.
   * `create_image_hotspots(img, puntos, titulo, alt)`: Esquema interactivo con puntos de inspección.
   * `create_multichoice_question(preg, opciones, titulo)`: Autocomprobación activa con justificación razonada en cada opción.
   * `create_true_false_question(preg, valor, titulo)`: Validación rápida de seguridad o axiomas técnicos.
   * `create_checkpoint_section(titulo, intro)`: Pausa activa visual de comprensión.
   * `create_active_challenge(titulo, escenario, pasos)`: Reto de diagnosis y toma de decisiones.
   * `create_checklist_section(titulo, items)`: Lista de verificación táctil accesible (≥44px).
   * `create_accordion(paneles, titulo)`: Desplegables de protocolos de taller.
   * `create_simulation_box(titulo, desc, boton, url)`: Enlace directo a laboratorios y simuladores virtuales.
   * `create_didactic_sequence_chapter(...)`: Ensamblado del capítulo en 4 fases de andamiaje.

3. **Compilar y validar paquetes con `build.py`**:
   ```bash
   # Compilar y certificar el curso modelo de la plantilla
   python3 build.py

   # Compilar y certificar el curso completo de Esquemas Eléctricos
   python3 build.py esquemas

   # Compilar todos los cursos del repositorio
   python3 build.py todos

   # Validar cualquier paquete .h5p existente
   python3 build.py validar <ruta_al_paquete.h5p>
   ```

4. **Validación manual directa**:
   ```bash
   python3 plantilla/validar_h5p_educamadrid.py <nombre_paquete.h5p>
   ```

---

## 🔒 Reglas Técnicas y Accesibilidad Obligatorias

1. **Accesibilidad Universal y Legibilidad (WCAG 2.1 AA / AAA)**:
   * Contraste certificado (> 7:1 en badges y > 9:1 en alertas y tarjetas).
   * Tamaño táctil mínimo de 44 x 44 px en botones y elementos interactivos.
   * Foco de navegación por teclado visible (`:focus-visible`).
   * Textos alternativos descriptivos obligatorios en todas las imágenes (`alt`).
   * Prohibido el texto justificado; siempre alineación a la izquierda.
2. **Whitelist Estricta en `content/`**: Cero archivos `.html` y cero `.svg` dentro de `content/`. Todos los esquemas deben ser imágenes rasterizadas (`.png` o `.jpg`).
3. **Fórmulas Matemáticas y Eléctricas**: Cero LaTeX crudo (`$ ... $`). Emplear **HTML semántico y Unicode** (`<sub>`, `<sup>`, `.tech-formula`, `.tech-formula-block`).
4. **Cero etiquetas `<style>` en HTML**: Los estilos globales se inyectan en las librerías base mediante `append_css_to_libraries.py`.
5. **Anidamiento en `H5P.Column`**: Cada elemento debe envolverse con `{"content": ..., "useSeparator": "auto"}` y contar con `subContentId` (UUIDv4) y `metadata.title`.
