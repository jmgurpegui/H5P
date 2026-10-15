#!/usr/bin/env python3
"""
Script Maestro de Plantilla: Generador de Cursos Interactivos H5P Homologados para EducaMadrid.
Implementa rigurosamente los 5 PILARES PEDAGÓGICOS Y TÉCNICOS:
1. Participación constante del estudiante: interacción continua, arrastre de elementos (DragText),
   toma de decisiones y enriquecimiento multimedia (Image Hotspots).
2. Estructuración pedagógica integrada (Andamiaje): Contenedor unificado (InteractiveBook 1.7) con
   secuencia didáctica de 4 fases (Motivación ➔ Explicación interactiva ➔ Práctica guiada ➔ Evaluación formativa).
3. Retroalimentación inmediata y explicada: justificación pedagógica en cada opción, pistas y reintentos.
4. Gamificación estratégica con propósito didáctico: dinamización lúdica para afianzar conceptos clave.
5. Integración con la evaluación y trazabilidad en Moodle: soporte xAPI y distinción de formatos didáctico vs evaluable.
"""

import os
import sys
import uuid
import json
import shutil
import zipfile

# Asegurar codificación UTF-8 en consola multiplataforma
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Rutas de referencia
CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTILLA_DIR = CURRENT_SCRIPT_DIR
for candidate in [
    CURRENT_SCRIPT_DIR,
    os.path.join(CURRENT_SCRIPT_DIR, 'plantilla'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', 'plantilla'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', '..', 'plantilla')
]:
    if os.path.exists(os.path.join(candidate, 'validar_h5p_educamadrid.py')) or os.path.exists(os.path.join(candidate, 'Plantilla_Curso_Modelo_EducaMadrid.h5p')):
        PLANTILLA_DIR = os.path.abspath(candidate)
        break

BASE_DIR = os.path.dirname(PLANTILLA_DIR)

# Resolución flexible del directorio de librerías H5P
POSSIBLE_LIB_DIRS = [
    os.path.join(PLANTILLA_DIR, 'h5p-libraries'),
    os.path.join(CURRENT_SCRIPT_DIR, 'h5p-libraries'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', 'h5p-libraries'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', '..', 'h5p-libraries'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', 'h5p_builder', 'h5p-libraries'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', '..', 'h5p_builder', 'h5p-libraries'),
    os.path.join(CURRENT_SCRIPT_DIR, '..', '..', '..', 'h5p_builder', 'h5p-libraries'),
    os.path.join(BASE_DIR, 'h5p_builder', 'h5p-libraries'),
    os.path.join(BASE_DIR, 'h5p-libraries'),
    r'\\wsl.localhost\Ubuntu\home\jmgurpegui\H5P\h5p_builder\h5p-libraries',
    '/home/jmgurpegui/H5P/h5p_builder/h5p-libraries'
]
LIB_DIR = None
for p in POSSIBLE_LIB_DIRS:
    if os.path.exists(p) and os.path.isdir(p):
        LIB_DIR = os.path.abspath(p)
        break


HOMOLOGATED_DEPENDENCIES = [
    {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
    {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
    {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
    {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
    {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
    {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
    {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
    {"machineName": "H5P.DragText", "majorVersion": 1, "minorVersion": 10},
    {"machineName": "H5P.Text", "majorVersion": 1, "minorVersion": 1},
    {"machineName": "H5P.ImageHotspots", "majorVersion": 1, "minorVersion": 10},
    {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
    {"machineName": "H5P.Accordion", "majorVersion": 1, "minorVersion": 0},
    {"machineName": "H5P.Image", "majorVersion": 1, "minorVersion": 1},
    {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
    {"machineName": "H5P.Column", "majorVersion": 1, "minorVersion": 16},
    {"machineName": "H5P.InteractiveBook", "majorVersion": 1, "minorVersion": 7}
]

# =========================================================================
# 1. HELPERS DE ENVOLTORIO Y MAQUETACIÓN BASE
# =========================================================================

def create_column_wrapper(library_str, params_dict, title_str="Sección"):
    """Envuelve cualquier componente hijo dentro del contenedor exigido por H5P.Column 1.16."""
    return {
        "content": {
            "library": library_str,
            "params": params_dict,
            "subContentId": str(uuid.uuid4()),
            "metadata": {
                "title": title_str,
                "contentType": library_str.split()[0].replace('H5P.', ''),
                "license": "CC BY-SA"
            }
        },
        "useSeparator": "auto"
    }

def resolve_institutional_logo(preferred_name="logo2026.png", search_dirs=None):
    """
    Localiza y resuelve metadatos del logotipo institucional 2026.
    Soporta extensiones admitidas por la whitelist de Moodle: .png, .jpg / .jpeg, .bmp.
    Detecta automáticamente dimensiones (width, height) y tipo MIME adecuado.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if search_dirs is None:
        search_dirs = [
            PLANTILLA_DIR,
            current_dir,
            os.path.join(current_dir, 'resources'),
            os.path.join(current_dir, '..', 'resources'),
            os.path.join(current_dir, '..', 'plantilla'),
            os.path.join(current_dir, '..', '.agents', 'skills', 'h5p-educamadrid', 'resources'),
            os.path.join(current_dir, '..', '..', '.agents', 'skills', 'h5p-educamadrid', 'resources')
        ]

    candidates = []
    if preferred_name:
        candidates.append(preferred_name)
    for name in ['logo2026.png', 'logo2026.jpg', 'logo2026.jpeg', 'logo2026.bmp']:
        if name not in candidates:
            candidates.append(name)

    found_path = None
    found_filename = None
    for c_name in candidates:
        for s_dir in search_dirs:
            if s_dir and os.path.isdir(s_dir):
                candidate_path = os.path.abspath(os.path.join(s_dir, c_name))
                if os.path.exists(candidate_path):
                    found_path = candidate_path
                    found_filename = c_name
                    break
        if found_path:
            break

    ext = found_filename.split('.')[-1].lower() if found_filename else 'bmp'
    mime_map = {
        'bmp': 'image/bmp',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'
    }
    mime_type = mime_map.get(ext, 'image/bmp')

    width, height = (1391, 192) if ext == 'bmp' else (1600, 222)
    if found_path:
        try:
            from PIL import Image
            with Image.open(found_path) as im:
                width, height = im.size
        except Exception:
            pass

    return {
        "src_path": found_path,
        "filename": found_filename or "logo2026.png",
        "rel_path": f"images/{found_filename or 'logo2026.png'}",
        "mime": mime_type,
        "width": width,
        "height": height,
        "alt": "Comunidad de Madrid - Unión Europea - Formación Profesional Pública"
    }

def create_header_logo():
    """Genera el bloque nativo H5P.Image 1.1 con el logotipo institucional 2026 y alt text accesible."""
    logo = resolve_institutional_logo()
    return create_column_wrapper("H5P.Image 1.1", {
        "contentName": "Image",
        "file": {
            "path": logo["rel_path"],
            "mime": logo["mime"],
            "copyright": {"license": "U"},
            "width": logo["width"],
            "height": logo["height"]
        },
        "alt": logo["alt"]
    }, "Cabecera Institucional EducaMadrid")

def create_image_section(rel_path, alt_text, title="Imagen Técnica", width=1600, height=800):
    """Crea un bloque nativo H5P.Image 1.1 homologado con alt text descriptivo obligatorio."""
    return create_column_wrapper("H5P.Image 1.1", {
        "contentName": "Image",
        "file": {
            "path": rel_path,
            "mime": "image/png" if rel_path.lower().endswith('.png') else "image/jpeg",
            "copyright": {"license": "U"},
            "width": width,
            "height": height
        },
        "alt": alt_text,
        "title": title
    }, title)

def create_text_section(html_content, title="Bloque Didáctico"):
    """Genera un bloque de texto técnico en H5P.AdvancedText 1.1."""
    return create_column_wrapper("H5P.AdvancedText 1.1", {"text": html_content}, title)

def create_accordion(panels_data, title="Protocolo Desplegable"):
    """
    Genera un componente H5P.Accordion 1.0 para desglosar procedimientos extensos.
    panels_data: lista de tuplas (titulo_panel, contenido_html)
    """
    h5p_panels = []
    for p_title, p_html in panels_data:
        h5p_panels.append({
            "title": p_title,
            "content": {
                "library": "H5P.AdvancedText 1.1",
                "params": {"text": p_html},
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "title": p_title,
                    "contentType": "AdvancedText",
                    "license": "CC BY-SA"
                }
            }
        })
    return create_column_wrapper("H5P.Accordion 1.0", {"panels": h5p_panels, "hTag": "h3"}, title)

# =========================================================================
# 2. PILAR 1: PARTICIPACIÓN CONSTANTE Y ENRIQUECIMIENTO MULTIMEDIA
# =========================================================================

def create_drag_text_activity(task_description_html, text_field_str, distractors_str=None, title="Actividad de Arrastre de Conceptos"):
    """
    Genera una actividad interactiva de arrastre de términos H5P.DragText 1.10.
    Permite al alumno manipular conceptos, fórmulas o secuencias arrastrando elementos a sus casillas.
    text_field_str: Las palabras a arrastrar se encierran entre asteriscos (ej. '*intensidad*').
                    Se pueden incluir pistas con dos puntos (ej. '*tensión:voltaje en voltios*').
    distractors_str: Palabras de distracción incorrectas entre asteriscos (ej. '*potencia* *vatio*').
    """
    params = {
        "taskDescription": f"<p>{task_description_html}</p>",
        "textField": text_field_str,
        "distractors": distractors_str or "",
        "overallFeedback": [
            {
                "from": 0,
                "to": 99,
                "feedback": "Revisa los conceptos y las relaciones de magnitudes. Vuelve a intentarlo para afianzar el conocimiento."
            },
            {
                "from": 100,
                "to": 100,
                "feedback": "¡Excelente! Has asociado y ordenado todos los términos técnicos con total precisión."
            }
        ],
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
            "instantFeedback": False
        },
        "l10n": {
            "checkAnswer": "Comprobar respuestas",
            "tryAgain": "Reintentar actividad",
            "showSolution": "Mostrar soluciones",
            "dropZoneIndex": "Zona de destino @index.",
            "empty": "Vacío",
            "contains": "Contiene @piece",
            "ariaDraggableIndex": "@index de @count elementos arrastrables.",
            "tipLabel": "Mostrar pista",
            "scoreBarLabel": "Has obtenido :num de :total puntos"
        }
    }
    return create_column_wrapper("H5P.DragText 1.10", params, title)

def create_image_hotspots(image_rel_path, hotspots_data, title="Esquema Interactivo con Puntos de Inspección", alt_text="Esquema técnico interactivo", icon="plus", color="#0284c7"):
    """
    Genera un recurso multimedia interactivo H5P.ImageHotspots 1.10.
    Convierte una imagen o esquema técnico pasivo en una experiencia interactiva de exploración.
    hotspots_data: lista de diccionarios:
      [
        {
          "x": float (coordenada horizontal 0-100),
          "y": float (coordenada vertical 0-100),
          "header": "Título del Punto",
          "text": "<p>Contenido explicativo técnico...</p>"
        }
      ]
    """
    hotspots = []
    for h in hotspots_data:
        hotspots.append({
            "position": {
                "x": h.get("x", 50.0),
                "y": h.get("y", 50.0),
                "legacyPositioning": False
            },
            "alwaysFullscreen": False,
            "header": h.get("header", "Punto de Inspección"),
            "content": [
                {
                    "library": "H5P.Text 1.1",
                    "params": {
                        "text": h.get("text", "")
                    },
                    "subContentId": str(uuid.uuid4())
                }
            ]
        })

    params = {
        "image": {
            "path": image_rel_path,
            "mime": "image/png" if image_rel_path.lower().endswith('.png') else "image/jpeg",
            "copyright": {"license": "U"},
            "width": 1600,
            "height": 900
        },
        "backgroundImageAltText": alt_text,
        "iconType": "icon",
        "icon": icon,
        "color": color,
        "hotspots": hotspots
    }
    return create_column_wrapper("H5P.ImageHotspots 1.10", params, title)

def create_simulation_box(title, description, button_text, url):
    """Genera una caja interactiva para enlazar a simuladores y laboratorios virtuales externos seguros."""
    html = f"""
    <div class="sim-box">
      <h3>⚡ {title}</h3>
      <p>{description}</p>
      <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn-sim" role="button">
        {button_text} &nbsp;↗
      </a>
    </div>
    """
    return create_text_section(html, f"Simulador: {title}")

# =========================================================================
# 3. PILAR 2: ESTRUCTURACIÓN PEDAGÓGICA INTEGRADA (ANDAMIAJE)
# =========================================================================

def create_didactic_sequence_chapter(title, phase1_intro, phase2_theory_interactive, phase3_guided_practice, phase4_formative_eval):
    """
    Construye un capítulo modular con la secuencia pedagógica progresiva completa de 4 fases:
    - Fase 1 (Motivación): Activación de conocimientos previos / Reto inicial / Gamificación.
    - Fase 2 (Explicación): Teoría interactiva con enriquecimiento multimedia (Image Hotspots / Fórmulas).
    - Fase 3 (Práctica Guiada): Exploración activa (DragText / Retos de taller / Checklists / Acordeones).
    - Fase 4 (Evaluación Formativa): Autocomprobación reflexiva con retroalimentación inmediata y explicada.
    """
    sections = [create_header_logo()]
    sections.extend(phase1_intro)
    sections.extend(phase2_theory_interactive)
    sections.extend(phase3_guided_practice)
    sections.extend(phase4_formative_eval)
    return create_chapter(title, sections)

def create_chapter(title, sections):
    """Crea un capítulo modular encapsulado en H5P.Column 1.16."""
    return {
        "library": "H5P.Column 1.16",
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": title,
            "contentType": "Column",
            "license": "CC BY-SA",
            "authors": [{"name": "Departamento de Formación Profesional"}]
        },
        "params": {
            "title": title,
            "content": sections
        }
    }

# =========================================================================
# 4. PILAR 3: RETROALIMENTACIÓN INMEDIATA Y EXPLICADA
# =========================================================================

def create_multichoice_question(question_html, answers, title="Autocomprobación Formativa", single_point=False, randomize=True):
    """
    Genera una autocomprobación interactiva H5P.MultiChoice 1.16 con justificación pedagógica en cada opción.
    answers: lista de diccionarios:
      [
        {
          "text": "Opción...",
          "correct": True/False,
          "chosenFeedback": "Por qué es correcta o por qué es errónea...",
          "tip": "Pista orientativa que guía el razonamiento..."
        }
      ]
    """
    formatted_answers = []
    for a in answers:
        if isinstance(a, dict):
            text = a.get('text', '')
            correct = bool(a.get('correct', False))
            tip = a.get('tip', '')
            chosen = a.get('chosenFeedback', '')
            not_chosen = a.get('notChosenFeedback', '')
        elif isinstance(a, (list, tuple)):
            text = a[0]
            correct = bool(a[1])
            chosen = a[2] if len(a) > 2 else ''
            tip = a[3] if len(a) > 3 else ''
            not_chosen = ''
        else:
            continue

        item = {
            "text": f"<div>{text}</div>",
            "correct": correct,
            "tipsAndFeedback": {
                "tip": tip,
                "chosenFeedback": f"<div>{chosen}</div>" if chosen else "",
                "notChosenFeedback": f"<div>{not_chosen}</div>" if not_chosen else ""
            }
        }
        formatted_answers.append(item)

    params = {
        "question": f"<p>{question_html}</p>",
        "answers": formatted_answers,
        "overallFeedback": [
            {
                "from": 0,
                "to": 99,
                "feedback": "Repasa la justificación técnica explicada en la solución y reintenta la actividad para afianzar el concepto."
            },
            {
                "from": 100,
                "to": 100,
                "feedback": "¡Excelente! Has asimilado con solvencia el criterio técnico y su aplicación diagnóstica."
            }
        ],
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
            "type": "auto",
            "singlePoint": single_point,
            "randomAnswers": randomize,
            "showSolutionsRequiresInput": True,
            "confirmCheckDialog": False,
            "confirmRetryDialog": False,
            "autoCheck": False
        },
        "UI": {
            "checkAnswerButton": "Comprobar respuesta",
            "showSolutionButton": "Mostrar solución explicada",
            "tryAgainButton": "Reintentar actividad",
            "tipsLabel": "Pistas y retroalimentación",
            "scoreBarLabel": "Has obtenido :num de :total puntos",
            "tipAvailable": "Pista disponible",
            "feedbackAvailable": "Retroalimentación disponible",
            "readFeedback": "Leer retroalimentación",
            "wrongAnswer": "Respuesta incorrecta",
            "correctAnswer": "Respuesta correcta",
            "shouldCheck": "Debería haber sido marcada",
            "shouldNotCheck": "No debería haber sido marcada",
            "noInput": "Por favor, selecciona una opción antes de comprobar.",
            "a11yCheck": "Comprobar las respuestas seleccionadas. Se mostrará si son correctas o erróneas con su justificación técnica.",
            "a11yShowSolution": "Mostrar la solución y la argumentación de la respuesta correcta.",
            "a11yRetry": "Reintentar la actividad desde el principio para reforzar el aprendizaje activo."
        }
    }

    return create_column_wrapper("H5P.MultiChoice 1.16", params, title)

def create_true_false_question(question_html, is_correct, title="Verificación Rápida", tip="", feedback_correct="", feedback_wrong=""):
    """
    Genera una pregunta rápida de Verdadero/Falso H5P.TrueFalse 1.8 para fijar axiomas o criterios de seguridad.
    """
    correct_str = "true" if is_correct else "false"

    params = {
        "question": f"<p>{question_html}</p>",
        "correct": correct_str,
        "l10n": {
            "trueText": "Verdadero",
            "falseText": "Falso",
            "score": "Has obtenido @score de @total puntos",
            "checkAnswer": "Comprobar",
            "submitAnswer": "Enviar",
            "showSolutionButton": "Mostrar solución",
            "tryAgain": "Reintentar",
            "wrongAnswerMessage": feedback_wrong or "Respuesta incorrecta. Analiza las condiciones de seguridad o la magnitud indicada.",
            "correctAnswerMessage": feedback_correct or "¡Correcto! Has identificado el criterio técnico adecuado.",
            "scoreBarLabel": "Puntuación obtenida: :num de :total puntos",
            "a11yCheck": "Comprobar la respuesta.",
            "a11yShowSolution": "Mostrar la solución y la justificación.",
            "a11yRetry": "Reintentar la pregunta."
        },
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True,
            "confirmCheckDialog": False,
            "confirmRetryDialog": False,
            "autoCheck": False
        }
    }

    return create_column_wrapper("H5P.TrueFalse 1.8", params, title)

def create_checkpoint_section(title, intro_text, badge_text="Pausa Activa de Comprensión"):
    """Crea una pausa activa visual que predispone al alumno a verificar su entendimiento."""
    html = f"""
    <div class="tech-checkpoint">
      <div class="tech-checkpoint-header">
        <span class="tech-badge badge-blue">{badge_text}</span>
        <h4>{title}</h4>
      </div>
      <p>{intro_text}</p>
    </div>
    """
    return create_text_section(html, f"Pausa Activa: {title}")

# =========================================================================
# 5. PILAR 4: GAMIFICACIÓN ESTRATÉGICA Y RETOS PRÁCTICOS
# =========================================================================

def create_active_challenge(title, scenario_html, steps, badge_text="Reto Práctico de Taller"):
    """Genera un reto de toma de decisiones o resolución de averías (Problem-Based Learning)."""
    steps_html = ""
    for s in steps:
        if isinstance(s, (list, tuple)):
            steps_html += f"""
            <div class="tech-challenge-step">
              <strong>{s[0]}:</strong> {s[1]}
            </div>
            """
        else:
            steps_html += f"""
            <div class="tech-challenge-step">{s}</div>
            """

    html = f"""
    <div class="tech-challenge">
      <span class="tech-badge badge-purple">{badge_text}</span>
      <h4>{title}</h4>
      <div>{scenario_html}</div>
      <div style="margin-top: 12px;">
        {steps_html}
      </div>
    </div>
    """
    return create_text_section(html, f"Reto: {title}")

def create_checklist_section(title, items, intro_text=None):
    """Genera una lista de cotejo activa con áreas táctiles accesibles (>=44px)."""
    intro_part = f"<p>{intro_text}</p>" if intro_text else ""
    items_html = ""
    for idx, item in enumerate(items, 1):
        items_html += f"""
        <li class="tech-checklist-item">
          <span class="tech-check-icon" aria-hidden="true">#{idx}</span>
          <span>{item}</span>
        </li>
        """

    html = f"""
    <div class="tech-card">
      <h3>📋 {title}</h3>
      {intro_part}
      <ul class="tech-checklist">
        {items_html}
      </ul>
    </div>
    """
    return create_text_section(html, f"Checklist: {title}")

# =========================================================================
# 6. EMPAQUETADOR MAESTRO Y COMPILACIÓN DEL ARCHIVO .H5P
# =========================================================================

def build_h5p_package(output_path, title, book_cover_title, book_cover_desc, chapters, extra_images=None):
    """Compila físicamente el archivo ZIP final con estructura, accesibilidad y dependencias certificadas."""
    build_dir = os.path.join(PLANTILLA_DIR, "_build_tmp")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    content_dir = os.path.join(build_dir, 'content')
    images_dir = os.path.join(content_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # 1. Copiar librerías
    for dep in HOMOLOGATED_DEPENDENCIES:
        folder_name = f"{dep['machineName']}-{dep['majorVersion']}.{dep['minorVersion']}"
        src_path = os.path.join(LIB_DIR, folder_name)
        dst_path = os.path.join(build_dir, folder_name)
        if os.path.exists(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            print(f"⚠️ Aviso: Librería no encontrada en {src_path}")

    # 2. Copiar logo institucional
    logo = resolve_institutional_logo()
    if logo.get("src_path") and os.path.exists(logo["src_path"]):
        shutil.copy2(logo["src_path"], os.path.join(images_dir, logo["filename"]))
        print(f"✓ Logotipo institucional copiado: {logo['filename']} ({logo['width']}x{logo['height']} px, {logo['mime']})")
    else:
        print("⚠️ Aviso: No se encontró archivo de logotipo institucional en los directorios de búsqueda.")

    # 3. Copiar imágenes adicionales si existen
    if extra_images:
        for src, rel in extra_images:
            if os.path.exists(src):
                dst = os.path.join(content_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

    # 4. Construir content.json
    content_data = {
        "showCoverPage": True,
        "bookCover": {
            "coverTitle": book_cover_title,
            "coverDescription": book_cover_desc,
            "coverMedium": {
                "params": {
                    "contentName": "Image",
                    "file": {
                        "path": logo["rel_path"],
                        "mime": logo["mime"],
                        "copyright": {"license": "U"},
                        "width": logo["width"],
                        "height": logo["height"]
                    },
                    "alt": "Portada Oficial EducaMadrid - Formación Profesional Pública"
                },
                "library": "H5P.Image 1.1",
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "contentType": "Image",
                    "license": "CC BY-SA",
                    "title": "Portada Institucional"
                }
            }
        },
        "chapters": chapters,
        "behaviour": {
            "defaultTableOfContents": False,
            "progressIndicators": True,
            "progressType": "textual"
        }
    }

    with open(os.path.join(content_dir, 'content.json'), 'w', encoding='utf-8') as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)

    # 5. Construir h5p.json
    h5p_manifest = {
        "title": title,
        "language": "es",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["div"],
        "license": "CC BY-SA",
        "authors": [{"name": "Profesorado de Formación Profesional y Tecnología"}],
        "preloadedDependencies": HOMOLOGATED_DEPENDENCIES
    }

    with open(os.path.join(build_dir, 'h5p.json'), 'w', encoding='utf-8') as f:
        json.dump(h5p_manifest, f, ensure_ascii=False, indent=2)

    # 6. Empaquetar ZIP
    if os.path.exists(output_path):
        os.remove(output_path)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, build_dir)
                zipf.write(abs_path, rel_path)

    shutil.rmtree(build_dir)
    print(f"\n✅ Paquete H5P generado: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")


# =========================================================================
# EJEMPLO MAESTRO: CURSO MODELO QUE INTEGRA LOS 5 PILARES PEDAGÓGICOS
# =========================================================================
if __name__ == '__main__':
    ejemplo_pkg = os.path.join(PLANTILLA_DIR, "Plantilla_Curso_Modelo_EducaMadrid.h5p")

    # ---------------------------------------------------------------------
    # CAPÍTULO 0: SEGURIDAD, DESENERGIZACIÓN Y PARTICIPACIÓN CONSTANTE
    # Secuencia didáctica de 4 fases (Andamiaje)
    # ---------------------------------------------------------------------
    # Fase 1: Motivación y activación
    c0_fase1_intro = [
        create_text_section("""
        <div class="tech-hero">
          <h2>Módulo Formativo: Fundamentos Técnicos y Seguridad en Taller</h2>
          <p>Curso interactivo estructurado bajo el modelo de aprendizaje activo y diseño accesible (WCAG 2.1 AA / AAA), optimizado para tablets, smartphones y ordenadores de taller.</p>
          <div class="tech-badge-container">
            <span class="tech-badge badge-blue">Formación Profesional FP</span>
            <span class="tech-badge badge-green">EducaMadrid Moodle Ready</span>
            <span class="tech-badge badge-yellow">WCAG 2.1 AA Accesible</span>
            <span class="tech-badge badge-purple">Aprendizaje Activo</span>
          </div>
        </div>
        """, "Presentación del Módulo")
    ]

    # Fase 2: Explicación interactiva y regla crítica
    c0_fase2_explicacion = [
        create_text_section("""
        <div class="alert-box alert-danger">
          <h4>⚠️ REGLA CRÍTICA DE SEGURIDAD ELÉCTRICA: CÁLCULO DE PROTECCIÓN</h4>
          <p>Comprobación obligatoria antes de conectar instrumentación de medida a bornes de potencia:</p>
          <div class="tech-formula-block" style="background: #ffffff; border: 1px solid #fecaca; border-left: 6px solid #dc2626; color: #450a0a;">
            <span class="tech-formula" style="color: #7f1d1d; background: #fee2e2; border-color: #dc2626;">V<sub>instrumento</sub> = V<sub>circuito</sub> / 20</span>
            <div class="tech-formula-desc" style="color: #450a0a;">
              Para un pico inducido de 400 V ÷ 20 = <strong>20 V</strong> (margen seguro &lt; 30 V para el osciloscopio).
            </div>
          </div>
        </div>
        """, "Regla de Seguridad Eléctrica")
    ]

    # Fase 3: Práctica guiada activa (Reto de taller y toma de decisiones)
    c0_fase3_practica = [
        create_active_challenge(
            title="Protocolo de Desenergización en Vehículo Híbrido",
            scenario_html="<p>Un vehículo llega al taller con testigo de avería en el sistema de alta tensión. Antes de intervenir en el inversor, el técnico debe garantizar tensión nula de servicio aplicando el protocolo de seguridad laboral.</p>",
            steps=[
                ("Paso 1 (EPIs)", "Equiparse con guantes dieléctricos Clase 0 (1000 V) y pantalla facial de protección antes de acercarse al puente de servicio."),
                ("Paso 2 (Desconexión)", "Retirar el conector de servicio (Service Plug) y custodiarlo bajo candado de consignación LOTO."),
                ("Paso 3 (Espera activa)", "Esperar 10 minutos para la descarga completa de los condensadores de filtrado del inversor."),
                ("Paso 4 (Verificación)", "Medir tensión residual con multímetro categoría CAT III 1000 V asegurando lectura < 12 V.")
            ],
            badge_text="Reto Práctico de Taller"
        )
    ]

    # Fase 4: Evaluación formativa inmediata con retroalimentación explicada
    c0_fase4_evaluacion = [
        create_true_false_question(
            question_html="¿Es seguro conectar directamente una sonda de osciloscopio 1X sin atenuación a un circuito de potencia donde pueden inducirse picos superiores a 300 V?",
            is_correct=False,
            title="Autocomprobación 1: Seguridad en Medición",
            feedback_correct="¡Correcto! Una sonda 1X no atenúa la señal e introduciría 300 V directamente en el convertidor analógico del equipo, provocando su destrucción inmediata y severo riesgo para el operario.",
            feedback_wrong="Incorrecto. Una sonda 1X somete el canal de entrada a la totalidad de la tensión sin atenuar. Debe emplearse siempre una sonda atenuadora 10X o 20X con categoría de seguridad CAT III o superior."
        )
    ]

    capitulo_0 = create_didactic_sequence_chapter(
        "Tema 0: Seguridad y Desenergización",
        c0_fase1_intro,
        c0_fase2_explicacion,
        c0_fase3_practica,
        c0_fase4_evaluacion
    )

    # ---------------------------------------------------------------------
    # CAPÍTULO 1: MEDIDAS ELÉCTRICAS, ARRASTRE DE ELEMENTOS Y DIAGNOSIS
    # ---------------------------------------------------------------------
    # Fase 1: Motivación y activación lúdica previa (Gamificación didáctica)
    c1_fase1_intro = [
        create_checkpoint_section(
            title="Activación de Conceptos: Relaciones de Magnitudes",
            intro_text="Antes de calcular caídas de tensión en el taller, demuestra que dominas la correlación entre magnitudes, unidades y fórmulas fundamentales arrastrando cada término a su lugar.",
            badge_text="Activación Previa Gamificada"
        ),
        # Dinamización lúdica: Actividad de arrastre de términos (Pilar 1 y 4)
        create_drag_text_activity(
            task_description_html="Arrastra cada término técnico y unidad al hueco correspondiente de la definición:",
            text_field_str="La Ley de Ohm establece que la diferencia de potencial o *tensión:Medida en voltios* es igual al producto de la *intensidad:Flujo de corriente* por la *resistencia:Oposición al paso de electrones*. En el Sistema Internacional, la resistencia se mide en *ohmios* y la frecuencia en *hercios*.",
            distractors_str="*vatios* *faradios* *julios*",
            title="Actividad Interactiva: Arrastre de Magnitudes y Unidades"
        )
    ]

    # Fase 2: Explicación técnica interactiva con fórmulas semánticas
    c1_fase2_explicacion = [
        create_text_section("""
        <div class="tech-card">
          <h3>Relación Matemática y Ley de Ohm Aplicada al Diagnóstico</h3>
          <p>En el análisis de sensores y actuadores con señales periódicas en osciloscopio:</p>
          <div class="tech-formula-block">
            <span class="tech-formula">f = 1 / T</span> &nbsp;&nbsp;|&nbsp;&nbsp; <span class="tech-formula">T = 1 / f</span>
            <div class="tech-formula-desc">
              Relación entre Frecuencia (Hz) y Período (s). Para T = 2 ms (0.002 s) → f = 1 ÷ 0.002 s = <strong>500 Hz</strong>
            </div>
          </div>
          <p>Caída de tensión en conexiones con resistencia parásita (<span class="tech-formula">ΔV = I × R</span>):</p>
          <div class="tech-formula-block">
            <span class="tech-formula">ΔV<sub>contacto</sub> = I<sub>servicio</sub> × R<sub>contacto</sub></span>
            <div class="tech-formula-desc">
              Con una corriente de 10 A y 0.2 Ω de resistencia parásita en un borne: 10 A × 0.2 Ω = <strong>2.0 V de caída</strong>
            </div>
          </div>
        </div>
        """, "Fundamentos de Medición y Ley de Ohm")
    ]

    # Fase 3: Práctica guiada activa con checklist táctil, acordeón y simulador
    c1_fase3_practica = [
        create_checklist_section(
            title="Lista de Cotejo: Verificación Rápida de Línea de Alimentación",
            items=[
                "Comprobar tensión de batería en reposo (> 12.4 V para certificar al menos 75% de carga química).",
                "Inspeccionar visualmente ausencia de sulfatación, holguras o apriete defectuoso en bornes.",
                "Medir caída de tensión entre borne y terminal de cable bajo consumo dinámico (< 0.2 V admisible).",
                "Verificar continuidad y calidad de masa a chasis con polímetro calibrado."
            ],
            intro_text="Procedimiento estructurado que todo técnico debe certificar antes de declarar un componente como defectuoso:"
        ),
        create_accordion([
            ("Paso 1: Preparación del Instrumento de Medición", "<p>Asegurar categoría de seguridad CAT III o superior. Inspeccionar el estado de las puntas de prueba y el fusible cerámico interno.</p>"),
            ("Paso 2: Medición Bajo Carga Dinámica Real", "<p>Nunca medir la resistencia con el circuito desconectado como único criterio; la prueba definitiva de caída de tensión requiere que el circuito esté circulando su corriente nominal de trabajo.</p>")
        ], "Protocolo Guiado de Taller"),
        create_simulation_box(
            title="Laboratorio Virtual de Circuitos DC y Ley de Ohm",
            description="Experimenta en tiempo real variando resistencias parásitas y visualizando caídas de tensión en un entorno interactivo accesible.",
            button_text="Abrir Simulador Interactivo",
            url="https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_all.html"
        )
    ]

    # Fase 4: Evaluación formativa reflexiva con retroalimentación explicada en cada opción
    c1_fase4_evaluacion = [
        create_checkpoint_section(
            title="Pausa Activa de Comprensión: Demuestra tu Criterio Numérico",
            intro_text="Responde a la siguiente autocomprobación formativa para verificar si sabes calcular con soltura la caída de tensión en una línea real de vehículo.",
            badge_text="Autocomprobación Formativa"
        ),
        create_multichoice_question(
            question_html="Si una bomba de combustible demanda <strong>8 A</strong> en pleno funcionamiento y el borne positivo presenta una resistencia parásita por corrosión de <strong>0.5 Ω</strong>, ¿cuál será la caída de tensión en dicho borne y qué tensión recibirá la bomba si la batería entrega 12.6 V?",
            answers=[
                {
                    "text": "Caída de 4.0 V; la bomba recibe 8.6 V.",
                    "correct": True,
                    "chosenFeedback": "¡Exacto! Aplicando la Ley de Ohm: ΔV = 8 A × 0.5 Ω = 4.0 V. Por tanto, V_bomba = 12.6 V − 4.0 V = 8.6 V. Una pérdida crítica que provocará caída de presión y fallos graves de inyección.",
                    "tip": "Aplica la Ley de Ohm: ΔV = I × R, y luego resta dicha caída a la tensión de la batería."
                },
                {
                    "text": "Caída de 2.0 V; la bomba recibe 10.6 V.",
                    "correct": False,
                    "chosenFeedback": "Incorrecto. 8 A × 0.5 Ω = 4.0 V, no 2.0 V. Revisa la multiplicación de la corriente por la resistencia.",
                    "tip": "Multiplica 8 por 0.5 con atención."
                },
                {
                    "text": "Caída de 0.5 V; la bomba recibe 12.1 V.",
                    "correct": False,
                    "chosenFeedback": "Incorrecto. 0.5 Ω es el valor óhmico de la resistencia parásita, no los voltios de caída. Debes multiplicar la resistencia por los 8 amperios de intensidad.",
                    "tip": "No confundas el valor de la resistencia (Ω) con la caída de tensión producida (V)."
                }
            ],
            title="Autocomprobación Formativa: Caída de Tensión y Diagnóstico",
            single_point=True,
            randomize=True
        )
    ]

    capitulo_1 = create_didactic_sequence_chapter(
        "Tema 1: Medición, Relaciones y Diagnóstico",
        c1_fase1_intro,
        c1_fase2_explicacion,
        c1_fase3_practica,
        c1_fase4_evaluacion
    )

    capitulos = [capitulo_0, capitulo_1]

    build_h5p_package(
        output_path=ejemplo_pkg,
        title="Plantilla Oficial de Curso Interactivo EducaMadrid",
        book_cover_title="Curso Interactivo Homologado EducaMadrid",
        book_cover_desc="Plantilla técnica maestra para Formación Profesional en EducaMadrid y Moodle. Integración de los 5 pilares pedagógicos de aprendizaje activo, andamiaje, retroalimentación y accesibilidad WCAG 2.1 AA.",
        chapters=capitulos
    )

    # Validar automáticamente la plantilla generada
    try:
        from validar_h5p import validate_h5p
        validate_h5p(ejemplo_pkg)
    except ImportError:
        try:
            from validar_h5p_educamadrid import validate_h5p
            validate_h5p(ejemplo_pkg)
        except ImportError:
            import importlib.util
            for val_name in ['validar_h5p.py', 'validar_h5p_educamadrid.py']:
                for v_dir in [CURRENT_SCRIPT_DIR, PLANTILLA_DIR]:
                    v_path = os.path.join(v_dir, val_name)
                    if os.path.exists(v_path):
                        spec = importlib.util.spec_from_file_location("val_mod", v_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        mod.validate_h5p(ejemplo_pkg)
                        break
