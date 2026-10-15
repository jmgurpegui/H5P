# Entorno de Creación de Cursos H5P para EducaMadrid (Moodle)

Este repositorio contiene el **entorno oficial y plantilla homologada** para la creación, maquetación y validación de cursos interactivos H5P destinados a las Aulas Virtuales de **EducaMadrid** y entornos **Moodle**.

Garantiza el cumplimiento de las normativas de seguridad institucional, la **integración de los 5 pilares pedagógicos de aprendizaje activo** y las pautas de **accesibilidad universal (WCAG 2.1 AA / AAA)**.

---

## 📁 Estructura del Proyecto

```text
H5P/
├── REQUISITOS_CURSOS_H5P_EDUCAMADRID.md      # Especificación oficial EducaMadrid (Técnica, Pedagógica y Accesibilidad)
├── build.py                                  # Script maestro de compilación, inyección CSS y validación
├── plantilla/                                # Toolkit y plantilla técnica maestra
│   ├── REQUISITOS_CURSOS_H5P_EDUCAMADRID.md  # Especificación técnica oficial, los 5 pilares y accesibilidad
│   ├── generar_curso_plantilla.py            # Generador y plantilla de código con helpers de los 5 pilares
│   ├── validar_h5p_educamadrid.py            # Validador de certificación EducaMadrid (whitelist, CSS, a11y)
│   ├── moodle_xml_builder.py                 # Generador y validador de bancos de preguntas Moodle XML
│   ├── evaluacion_modelo_moodle.xml          # Banco de preguntas modelo sumativo para Moodle (10 preguntas)
│   ├── estilos_educamadrid.css               # Hoja de estilos accesible y responsive (WCAG AAA, táctil, fórmulas)
│   ├── append_css_to_libraries.py            # Inyector limpio de CSS en librerías base (preserva 1.646 líneas)
│   ├── logo2026.png                          # Logotipo institucional oficial con transparencia (Comunidad de Madrid)
│   ├── logo2026.bmp                          # Logotipo complementario en formato BMP
│   ├── CC.png                                # Logotipo oficial Creative Commons
│   ├── Plantilla_Curso_Modelo_EducaMadrid.h5p# Paquete H5P modelo certificado y listo para Moodle (1.7 MB)
│   └── README.md                             # Documentación detallada de la plantilla
│
├── EsquemasElectricosAutomocion/             # Caso de éxito real: Curso interactivo de Formación Profesional
│   ├── Curso_Esquemas_Electricos_Automocion.h5p # Paquete H5P certificado listo para el Aula Virtual (2.0 MB)
│   ├── evaluacion_esquemas_electricos.xml    # Banco sumativo oficial Moodle XML para el curso (20 preguntas)
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
            ├── scripts/                      # Scripts ejecutables (generar, validar, inyectar, moodle_xml)
            ├── resources/                    # Logos oficiales (2026, CC) y estilos CSS accesibles
            ├── references/                   # Documentación modular (pedagogía, técnica, a11y, entrevista)
            └── examples/                     # Implementaciones de referencia, paquete .h5p y banco .xml
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
5. **Desacoplamiento Pedagógico: H5P Formativo + Moodle XML Sumativo**:
   - **Solución al error de registro en Moodle ("No intentado")**: En navegadores móviles y redes móviles, exigir calificación dentro del iframe H5P provoca pérdidas de eventos xAPI. Se establece la separación oficial:
     - **H5P Formativo**: Se sube al aula virtual configurando la finalización de actividad con **"El estudiante debe ver esta actividad para completarla"** (sin requerir calificación). Garantiza el 100% de éxito en el registro de finalización.
     - **Moodle XML Sumativo**: Las pruebas evaluativas con nota oficial para el Calificador se gestionan mediante **Cuestionarios nativos de Moodle (`mod_quiz`)**, importando los archivos Moodle XML provistos (`plantilla/evaluacion_modelo_moodle.xml` y `EsquemasElectricosAutomocion/evaluacion_esquemas_electricos.xml`).

---

## 🚀 Cómo Crear y Compilar Cursos con `build.py`

El script maestro [`build.py`](build.py) centraliza todas las operaciones de compilación, inyección y validación:

```bash
# Compilar y certificar el curso modelo de la plantilla
python3 build.py

# Compilar y certificar el curso completo de Esquemas Eléctricos
python3 build.py esquemas

# Compilar todos los cursos del repositorio
python3 build.py todos

# Validar todos los bancos de preguntas Moodle XML del repositorio
python3 build.py xml

# Inyectar estilos CSS accesibles y responsive en las librerías base
python3 build.py css

# Validar cualquier paquete .h5p existente
python3 build.py validar <ruta_al_paquete.h5p>
```

---

## 📱 Optimización para Dispositivos Móviles

Para garantizar una experiencia visual y funcional impecable en smartphones y tablets (desde 360px de ancho):
1. **Cajón lateral cerrado por defecto (`defaultTableOfContents: false`)**: Impide que el menú lateral ocupe el 100% de la pantalla al abrir el recurso en móviles.
2. **Progreso textual (`progressType: "textual"`)**: Sustituye la hilera de círculos (que se solapan o desbordan) por texto adaptativo "Página X de Y".
3. **Contenedores de ancho flexible**: `max-width: 100%` y `box-sizing: border-box` en todos los contenedores `.h5p-interactive-book`, tarjetas (`.tech-card`) y héroes (`.tech-hero`).
4. **Desplazamiento táctil suave**: Bloques de fórmulas (`.tech-formula-block`) y tablas (`.tech-table`) configurados con `overflow-x: auto` y `-webkit-overflow-scrolling: touch`.
5. **Objetivos táctiles adaptados**: Todos los botones y selectores interactivos cuentan con un área mínima de **44 × 44 px** según directrices WCAG 2.1 AAA.

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
