# Plantilla y Herramientas Maestras H5P para EducaMadrid (Moodle)

Esta carpeta contiene la **plantilla técnica integral**, especificaciones normativas, hoja de estilos accesible, validador automatizado y script generador para compilar cursos H5P y cuestionarios Moodle XML 100% compatibles con las Aulas Virtuales de **EducaMadrid** y entornos **Moodle**.

---

## Contenido de la Carpeta `plantilla/`

| Archivo / Recurso | Descripción y Utilidad |
| :--- | :--- |
| **`REQUISITOS_CURSOS_H5P_EDUCAMADRID.md`** | **Manual técnico y especificación oficial**: Arquitectura semántica, whitelist estricta, matriz de versiones de librerías, renderizado de fórmulas sin LaTeX, prevención de fugas de CSS, **los 5 pilares pedagógicos de aprendizaje activo** y **accesibilidad universal WCAG 2.1 AA / AAA**. |
| **`validar_h5p_educamadrid.py`** | **Script de certificación y validación automática**: Analiza cualquier paquete `.h5p` verificando extensiones en `content/`, clausura de librerías, anidamiento en `H5P.Column`, metadatos, detección de actividades activas (`MultiChoice`, `TrueFalse`, `DragText`, `ImageHotspots`), verificación de `alt` en imágenes y ausencia de LaTeX o fugas CSS. |
| **`generar_curso_plantilla.py`** | **Generador llave en mano con los 5 pilares pedagógicos**: Script en Python para compilar cursos H5P modelo listos para Moodle, incorporando cabecera oficial, secuencia de andamiaje en 4 fases, preguntas formativas intercaladas con feedback razonado, arrastre de términos (`DragText`), hotspots, retos de taller y checklist táctiles. |
| **`estilos_educamadrid.css`** | **Hoja de estilos CSS oficial accesible**: Clases optimizadas para tablets y smartphones con contraste certificado WCAG AAA (`.tech-hero`, `.tech-card`, `.tech-checkpoint`, `.tech-challenge`, `.tech-checklist`, `.alert-box`, `.tech-table`, `.tech-formula`, `.btn-sim`). |
| **`append_css_to_libraries.py`** | **Inyector limpio de CSS**: Inserta las reglas accesibles en las hojas de estilo de las librerías base de forma limpia y codificada en UTF-8. |
| **`logo2026.bmp` / `logo2026.png`** | **Logotipo institucional oficial** (Comunidad de Madrid - Unión Europea). El generador detecta y empaqueta automáticamente el archivo disponible (`.bmp`, `.png` o `.jpg`), con recomendación técnica oficial de usar `.png` por su soporte de canal alfa (transparencia) y compresión sin pérdidas. |
| **`Plantilla_Curso_Modelo_EducaMadrid.h5p`** | **Paquete H5P modelo precompilado y certificado**: Puedes subirlo directamente a cualquier Aula Virtual de EducaMadrid para comprobar su funcionamiento inmediato. |

---

## Los 5 Pilares Pedagógicos y Técnicos Homologados

1. **Participación Constante del Estudiante y Enriquecimiento Multimedia**:
   - Evitar lectura pasiva o simple visualización de vídeos. El alumno debe explorar, tomar decisiones, arrastrar elementos (`create_drag_text_activity`) e interactuar con esquemas enriquecidos (`create_image_hotspots`).
2. **Estructuración Pedagógica Integrada (Andamiaje en 4 Fases)**:
   - Contenedores unificados (`InteractiveBook 1.7` con capítulos `Column 1.16`).
   - Secuencia de andamiaje: *Fase 1 (Motivación/Activación)* ➔ *Fase 2 (Explicación interactiva)* ➔ *Fase 3 (Práctica guiada)* ➔ *Fase 4 (Evaluación formativa)* (`create_didactic_sequence_chapter`).
3. **Retroalimentación Inmediata y Explicada**:
   - Corrección automática con justificación pedagógica en cada opción: explica por qué es correcta y en qué consiste el fallo en las incorrectas (`create_multichoice_question`).
   - Pistas orientativas (`tips`) y reintentos ilimitados para aprender del error.
4. **Gamificación Estratégica con Propósito Didáctico**:
   - Dinamización lúdica integrada (arrastre de magnitudes, juegos de memoria, retos) para activar conocimientos previos o cerrar lecciones.
5. **Integración con la Evaluación y Trazabilidad en Moodle**:
   - Publicación como **Actividad H5P Nativa** para sincronizar con el Libro de Calificaciones (`Gradebook` vía xAPI).
   - Uso de incrustaciones para práctica autónoma y actividades nativas para evaluación sumativa.

---

## Cómo Validar un Paquete H5P

Para comprobar cualquier paquete `.h5p` antes de subirlo a Moodle, ejecuta desde la consola:

```bash
python3 plantilla/validar_h5p_educamadrid.py <ruta_del_paquete.h5p>
```

---

## Cómo Crear un Nuevo Curso Usando la Plantilla

1. **Definir los Parámetros Clave (Entrevista Inicial)**:
   - *Tema del contenido*: Título y conceptos nucleares.
   - *Asignatura y Nivel*: Ej. 2º Bachillerato - Historia de España / 1º CFGM Electromecánica.
   - *Tipo de actividad*: Interactive Book (4 fases), Question Set, Drag the Words, Image Hotspots.
   - *Cantidad de ítems*: Preguntas, huecos arrastrables, puntos de inspección o capítulos.
   - *Nivel cognitivo (Bloom)*: Recordar, Comprender, Aplicar, Analizar, Evaluar.
   - *Retroalimentación*: Formativa explicada con pistas / Sumativa con xAPI.
   - *Recursos multimedia*: Imágenes PNG/JPG, vídeos Mediateca EducaMadrid o simuladores.

2. Abre [`plantilla/generar_curso_plantilla.py`](generar_curso_plantilla.py) y ensambla los capítulos usando las funciones auxiliares homologadas:
   * `create_header_logo()`: Cabecera oficial accesible con resolución dinámica de logotipo (`logo2026.bmp` o `logo2026.png`).
   * `create_text_section(html, "Título")`: Texto maquetado de alto contraste.
   * `create_drag_text_activity(desc, texto, distractores, "Título")`: Arrastre interactivo de términos y magnitudes.
   * `create_image_hotspots(img, puntos, "Título")`: Esquema técnico interactivo con puntos de inspección.
   * `create_multichoice_question(preg, opciones, "Título")`: Autocomprobación activa con feedback pedagógico en cada alternativa.
   * `create_true_false_question(preg, valor, "Título")`: Validación rápida de criterios técnicos y de seguridad.
   * `create_checkpoint_section("Título", intro)`: Pausa activa visual de comprensión.
   * `create_active_challenge("Título", escenario, pasos)`: Reto de taller y toma de decisiones.
   * `create_checklist_section("Título", items)`: Lista de verificación táctil accesible (≥44px).
   * `create_accordion(paneles, "Título")`: Desplegables de protocolos técnicos.
   * `create_simulation_box(titulo, desc, boton, url)`: Enlace directo a laboratorios y simuladores interactivos.
   * `create_didactic_sequence_chapter(...)`: Montaje del capítulo completo en 4 fases didácticas.
2. Ejecuta el script:
   ```bash
   python3 plantilla/generar_curso_plantilla.py
   ```
3. El paquete `.h5p` resultante estará listo para subir directamente a EducaMadrid.
