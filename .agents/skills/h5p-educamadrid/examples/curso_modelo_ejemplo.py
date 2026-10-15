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

    NOTA DE ARQUITECTURA EDUCAMADRID (DESACOPLAMIENTO OBLIGATORIO):
    En cursos estándar de producción para Moodle/EducaMadrid, NO se deben incrustar actividades DragText
    dentro del paquete H5P para evitar problemas de interacción táctil y scrolls involuntarios en smartphones,
    así como fallos de registro de calificaciones xAPI. Toda la evaluación práctica y sumativa se realiza
    mediante cuestionarios Moodle XML (mod_quiz). Se preserva esta función como referencia o para módulos locales.
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

def create_moodle_quiz_referral(chapter_num, title, summary_html):
    """
    Genera una tarjeta de síntesis y derivación directa al Cuestionario Oficial Sumativo Moodle XML.
    Alineado con el Pilar 5: Desacoplamiento de Formación (H5P) y Evaluación Oficial (Moodle XML)
    para garantizar 100% de fiabilidad en la trazabilidad y calificaciones del alumnado sin fallos xAPI en móviles.
    """
    html = f"""
    <div class="tech-checkpoint">
      <div class="tech-checkpoint-badge"><i class="fa fa-graduation-cap"></i> SÍNTESIS DE UNIDAD Y EVALUACIÓN</div>
      <h3 style="margin-top:0.5rem; color:#0f172a; font-size:1.3rem;">Capítulo {chapter_num}: {title}</h3>
      <div style="color:#1e293b; line-height:1.6; margin-bottom:1rem;">{summary_html}</div>
      <div class="alert-box alert-success" style="border-left: 4px solid #16a34a; background: #f0fdf4; padding: 1.1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <strong style="color: #15803d; font-size: 1.1rem; display: block; margin-bottom: 0.4rem;">
          <i class="fa fa-check-circle"></i> Unidad Formativa Completada
        </strong>
        <p style="color: #166534; margin: 0; line-height: 1.6; font-size: 0.95rem;">
          Has revisado todos los contenidos técnicos, esquemas y protocolos de este capítulo. 
          Para registrar tu calificación oficial de evaluación con validez académica y certificar tu progreso, accede al 
          <strong>Cuestionario Oficial de Evaluación en Moodle</strong> (módulo <code>mod_quiz</code>).
        </p>
      </div>
    </div>
    """
    return create_text_section(html, f"Síntesis Capítulo {chapter_num}")

# =========================================================================
# 3. PILAR 2: ESTRUCTURACIÓN PEDAGÓGICA INTEGRADA (ANDAMIAJE)
# =========================================================================

def create_didactic_sequence_chapter(title, phase1_intro, phase2_theory_interactive, phase3_guided_practice, phase4_formative_eval):
    """
    Construye un capítulo modular con la secuencia pedagógica progresiva completa de 4 fases:
    - Fase 1 (Motivación): Activación de conocimientos previos / Reto inicial.
    - Fase 2 (Explicación): Teoría interactiva con enriquecimiento multimedia (Image Hotspots / Fórmulas).
    - Fase 3 (Práctica Guiada): Exploración activa (Retos de taller / Checklists táctiles / Acordeones).
    - Fase 4 (Consolidación / Evaluación): Síntesis de unidad y remisión al Cuestionario Moodle XML.
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
            "authors": [{"name": "Departamento de Formación Profesional", "role": "Author"}]
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

    NOTA DE ARQUITECTURA EDUCAMADRID (DESACOPLAMIENTO OBLIGATORIO):
    En cursos estándar de producción, la evaluación (formativa o sumativa con calificación) NO se incrusta
    dentro del paquete H5P para evitar fallos de registro de calificaciones (xAPI) y bloqueos en dispositivos
    móviles. Toda evaluación oficial se gestiona mediante cuestionarios Moodle XML (mod_quiz). Se preserva esta
    función como referencia para módulos locales o paquetes específicos.
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

    NOTA DE ARQUITECTURA EDUCAMADRID (DESACOPLAMIENTO OBLIGATORIO):
    En cursos estándar de producción, no se deben incluir preguntas TrueFalse internas dentro del InteractiveBook
    para evitar anomalías de finalización xAPI en Moodle y navegadores móviles. La evaluación se realiza mediante Moodle XML.
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
        "authors": [{"name": "Profesorado de Formación Profesional y Tecnología", "role": "Author"}],
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
def generar_evaluacion_modelo_xml(output_xml_path):
    """Genera y valida el banco de preguntas Moodle XML oficial desacoplado de la plantilla."""
    try:
        from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
    except ImportError:
        sys.path.insert(0, PLANTILLA_DIR)
        from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml

    builder = MoodleXMLBuilder("Plantilla Oficial EducaMadrid - Evaluacion Sumativa")

    # P1: Desacoplamiento de H5P y XML (Opciones equilibradas ~100-130 caracteres)
    builder.add_multichoice(
        "P01_Desacoplamiento_Evaluacion",
        "<p>¿Por qué la normativa oficial de EducaMadrid recomienda separar los contenidos interactivos H5P del cuestionario sumativo oficial en Moodle XML?</p>",
        [
            {
                "text": "Garantizar el registro infalible en Moodle y evitar pérdidas de sentencias xAPI o bloqueos en móviles.",
                "fraction": 100,
                "feedback": "¡Correcto! El criterio de visualización en Moodle es 100% infalible, mientras que la nota sumativa se gestiona con fiabilidad absoluta mediante los cuestionarios nativos Moodle Quiz (mod_quiz)."
            },
            {
                "text": "Cumplir la normativa que prohíbe evaluar contenidos interactivos directamente en los módulos técnicos de Formación Profesional.",
                "fraction": 0,
                "feedback": "Incorrecto. H5P dispone de MultiChoice y QuestionSet, pero las sentencias xAPI dependen de conexión estable y cookies de terceros que a menudo fallan en móviles."
            },
            {
                "text": "Reducir el tamaño de descarga del paquete H5P en el navegador y minimizar el consumo de ancho de banda en servidores EducaMadrid.",
                "fraction": 0,
                "feedback": "Incorrecto. Moodle integra H5P nativamente, pero el calificador xAPI no es recomendable como único filtro de superación."
            },
            {
                "text": "Impedir que el alumnado repita las actividades formativas más de una vez durante el transcurso del curso académico en el aula.",
                "fraction": 0,
                "feedback": "Incorrecto. Aunque el XML es ligero, el motivo primordial es la robustez en el registro de calificaciones (mdl_grade_grades)."
            }
        ],
        general_feedback="<p>El desacoplamiento garantiza que la práctica autónoma sea formativa y la evaluación sumativa se gestione de forma nativa e infalible en Moodle.</p>"
    )

    # P2: Contraste WCAG 2.1 AAA (Opciones equilibradas ~80-100 caracteres)
    builder.add_multichoice(
        "P02_Contraste_WCAG_AAA",
        "<p>Según las directrices de accesibilidad universal WCAG 2.1 nivel AAA para entornos educativos, ¿cuál es el ratio de contraste mínimo exigido para el texto principal?</p>",
        [
            {
                "text": "Al menos 7:1 para garantizar lectura sin fatiga visual en cualquier soporte.",
                "fraction": 100,
                "feedback": "¡Correcto! El nivel AAA exige un ratio mínimo de 7:1 para texto estándar, lo que garantiza lectura sin fatiga visual en talleres con luz natural o dispositivos móviles."
            },
            {
                "text": "Al menos 4.5:1 exigido exclusivamente para textos estándar en nivel de conformidad intermedio AA.",
                "fraction": 0,
                "feedback": "Incorrecto. 4.5:1 es el umbral mínimo del nivel AA, pero el estándar técnico oficial EducaMadrid adopta el estándar superior AAA (>= 7:1)."
            },
            {
                "text": "Al menos 3:1 válido únicamente para componentes interactivos de gran escala y tipografías decorativas.",
                "fraction": 0,
                "feedback": "Incorrecto. 3:1 solo es admisible para texto de gran tamaño (>= 24px) o componentes de interfaz de usuario en nivel AA."
            },
            {
                "text": "Cualquier valor numérico libre siempre que se mantengan los colores corporativos de la institución.",
                "fraction": 0,
                "feedback": "Incorrecto. El contraste debe certificarse matemáticamente mediante luminancia relativa."
            }
        ],
        general_feedback="<p>El estándar AAA previene la exclusión de alumnos con baja visión o daltonismo.</p>"
    )

    # P3: Whitelist de Moodle (Distractor más largo ~61 caracteres, correcta ~54 caracteres)
    builder.add_multichoice(
        "P03_Whitelist_Moodle_Seguridad",
        "<p>¿Qué formatos de archivo están estrictamente prohibidos dentro del directorio content/ de un paquete H5P para prevenir el error 'not-in-whitelist'?</p>",
        [
            {
                "text": "Archivos vectoriales .svg y documentos locales .html.",
                "fraction": 100,
                "feedback": "¡Correcto! Moodle bloquea archivos SVG y HTML locales en content/ para neutralizar ataques de inyección de código malicioso (Stored XSS). Todos los diagramas deben rasterizarse a PNG o JPEG."
            },
            {
                "text": "Archivos de mapa de bits comprimidos en formato .png y .jpg.",
                "fraction": 0,
                "feedback": "Incorrecto. PNG y JPEG son formatos plenamente admitidos y recomendados por la whitelist oficial."
            },
            {
                "text": "Grabaciones de audio en .mp3 y tipografías web .woff2.",
                "fraction": 0,
                "feedback": "Incorrecto. El audio y las fuentes web forman parte de la lista blanca admitida."
            },
            {
                "text": "Estructuras de metadatos del paquete en formato .json.",
                "fraction": 0,
                "feedback": "Incorrecto. content.json es el núcleo semántico indispensable del paquete H5P."
            }
        ],
        general_feedback="<p>H5PValidator.php rechaza cualquier paquete con extensiones fuera de la whitelist oficial.</p>"
    )

    # P4: Andamiaje pedagógico (Opciones equilibradas ~80-100 caracteres)
    builder.add_multichoice(
        "P04_Andamiaje_Cuatro_Fases",
        "<p>¿Cuál es la secuencia didáctica progresiva en 4 fases que estructura cada unidad interactiva según el modelo de Aprendizaje Activo?</p>",
        [
            {
                "text": "1. Motivación activa ➔ 2. Explicación ➔ 3. Práctica guiada ➔ 4. Autocomprobación.",
                "fraction": 100,
                "feedback": "¡Correcto! Esta progresión pedagógica activa conocimientos previos, expone teoría concisa, ejercita la toma de decisiones y consolida el aprendizaje."
            },
            {
                "text": "1. Examen inicial ➔ 2. Lectura lineal teórica ➔ 3. Descanso pautado ➔ 4. Entrega de informe final.",
                "fraction": 0,
                "feedback": "Incorrecto. El andamiaje pedagógico exige preparación y práctica antes de la evaluación."
            },
            {
                "text": "1. Práctica de taller ➔ 2. Dudas en el foro ➔ 3. Examen sumativo ➔ 4. Repetición de la evaluación.",
                "fraction": 0,
                "feedback": "Incorrecto. La práctica sin andamiaje ni explicación previa genera frustración y abandono."
            },
            {
                "text": "1. Visionado de vídeo ➔ 2. Descarga de manual ➔ 3. Cuestionario externo ➔ 4. Calificación final.",
                "fraction": 0,
                "feedback": "Incorrecto. Este enfoque fragmentado dispersa la atención del estudiante; el modelo oficial unifica la secuencia."
            }
        ],
        general_feedback="<p>El andamiaje en 4 fases sustituye los muros de texto pasivo por interacción cognitiva continua.</p>"
    )

    # P5: Touch targets en dispositivos móviles (Correcta es la más corta ~62 caracteres, distractores ~74 caracteres)
    builder.add_multichoice(
        "P05_Touch_Targets_Moviles",
        "<p>Para garantizar que los contenidos sean perfectamente accesibles y utilizables en smartphones y tablets (incluso con guantes en taller), ¿qué dimensión mínima deben tener los objetivos táctiles?</p>",
        [
            {
                "text": "44 x 44 píxeles como dimensión ergonómica mínima (WCAG 2.5.5).",
                "fraction": 100,
                "feedback": "¡Correcto! 44 x 44 px es el tamaño mínimo ergonómico para interacción táctil con el pulgar o dedos enguantados."
            },
            {
                "text": "Al menos 60 x 60 píxeles obligatorios exclusivamente en pantallas grandes.",
                "fraction": 0,
                "feedback": "Incorrecto. Un botón de 20x20 px provoca toques accidentales y fallos constantes en pantallas pequeñas."
            },
            {
                "text": "Un máximo de 24 x 24 píxeles para aprovechar el espacio útil de pantalla.",
                "fraction": 0,
                "feedback": "Incorrecto. Incumple totalmente las pautas de accesibilidad móvil."
            },
            {
                "text": "El ancho estricto del texto visible sin necesidad de márgenes de toque.",
                "fraction": 0,
                "feedback": "Incorrecto. Los elementos táctiles exigen áreas de pulsación mínimas independientes del texto."
            }
        ],
        general_feedback="<p>Los botones, casillas de arrastre y opciones de test deben respetar siempre touch targets >= 44x44 px.</p>"
    )

    # P6: Fórmulas matemáticas (Distractores más largos ~103 caracteres, correcta ~101 caracteres)
    builder.add_multichoice(
        "P06_Formulas_HTML_Semantico",
        "<p>¿Por qué está prohibido utilizar delimitadores LaTeX crudos ($ ... $) en los textos de H5P?</p>",
        [
            {
                "text": "Porque H5P.AdvancedText no incorpora MathJax por defecto y mostraría el código fuente sin formatear.",
                "fraction": 100,
                "feedback": "¡Correcto! Se debe utilizar siempre HTML semántico y Unicode (<sub>, <sup>, .tech-formula), asegurando renderizado inmediato y accesible."
            },
            {
                "text": "Porque el compilador de LaTeX genera incompatibilidades críticas con los sistemas operativos móviles.",
                "fraction": 0,
                "feedback": "Incorrecto. LaTeX es multiplataforma, pero requiere motores de renderizado que no residen en el sandbox de H5P."
            },
            {
                "text": "Porque la sintaxis matemática LaTeX vulnera los protocolos de seguridad de datos del servidor Moodle.",
                "fraction": 0,
                "feedback": "Incorrecto. Las fórmulas son esenciales en enseñanzas técnicas y científicas."
            },
            {
                "text": "Porque su procesamiento incrementa exponencialmente el peso del archivo comprimido superando la cuota.",
                "fraction": 0,
                "feedback": "Incorrecto. El texto plano no añade peso, el fallo es puramente visual y de renderizado."
            }
        ],
        general_feedback="<p>El estándar HTML semántico + Unicode garantiza compatibilidad universal en tablets, móviles y lectores de pantalla.</p>"
    )

    # P7: Verdadero / Falso - Inyección de estilos
    builder.add_truefalse(
        "P07_TF_Inyeccion_Estilos_CSS",
        "<p>¿Es una práctica correcta insertar etiquetas &lt;style&gt; dentro de los bloques de contenido de H5P para aplicar estilos personalizados?</p>",
        False,
        feedback_true="Incorrecto. El sanitizador de H5P elimina las etiquetas &lt;style&gt; pero expone el código CSS como texto plano residual visible en pantalla (CSS leakage).",
        feedback_false="¡Correcto! Es falso. Los estilos accesibles deben inyectarse limpiamente en las hojas de estilo de las librerías base (h5p-interactive-book.css y h5p-column.css).",
        general_feedback="<p>La inyección en librerías base previene fugas de código y unifica el tema visual.</p>"
    )

    # P8: Verdadero / Falso - Menú en móviles
    builder.add_truefalse(
        "P08_TF_Menu_Table_Of_Contents_Movil",
        "<p>Para optimizar la visualización en dispositivos móviles, se recomienda configurar 'defaultTableOfContents: false' en InteractiveBook para evitar que el índice lateral cubra el contenido al abrir el curso.</p>",
        True,
        feedback_true="¡Correcto! Al configurar defaultTableOfContents: false, el estudiante ve directamente la portada y el tema en su teléfono, pudiendo desplegar el menú táctilmente cuando lo desee.",
        feedback_false="Incorrecto. Si defaultTableOfContents es true, el menú ocupa toda la pantalla en smartphones y bloquea la visualización del contenido.",
        general_feedback="<p>El diseño responsive exige que el menú no obstruya la lectura inicial en pantallas reducidas.</p>"
    )

    # P9: Verdadero / Falso - El error formativo
    builder.add_truefalse(
        "P09_TF_Error_Como_Palanca",
        "<p>En la modalidad de formación interactiva H5P, las autocomprobaciones deben configurarse con reintentos habilitados (enableRetry: true) y justificación pedagógica en cada opción para aprender del error.</p>",
        True,
        feedback_true="¡Correcto! El Aprendizaje Activo convierte el error en una oportunidad formativa y no en un elemento punitivo.",
        feedback_false="Incorrecto. Bloquear reintentos en actividades formativas genera frustración y contradice los pilares pedagógicos.",
        general_feedback="<p>La autorregulación del estudiante se fomenta con feedback inmediato y posibilidad de reintento.</p>"
    )

    # P10: Emparejamiento - Fases del Andamiaje
    builder.add_matching(
        "P10_Emparejamiento_Fases_Andamiaje",
        "<p>Relaciona cada una de las 4 fases de la secuencia didáctica progresiva con su componente o finalidad pedagógica:</p>",
        [
            ("Fase 1: Activación y Motivación", "Reto detonante inicial y cabecera institucional (.tech-hero)"),
            ("Fase 2: Explicación Interactiva", "Teoría concisa, fórmulas semánticas y puntos de inspección (ImageHotspots)"),
            ("Fase 3: Práctica Guiada Activa", "Arrastre de magnitudes (DragText), retos de taller y checklists táctiles"),
            ("Fase 4: Evaluación Formativa", "Autocomprobación con retroalimentación razonada inmediata (.tech-checkpoint)")
        ],
        general_feedback="<p>Las 4 fases articulan el aprendizaje activo desde la motivación inicial hasta la consolidación formativa.</p>"
    )

    builder.save_xml(output_xml_path)
    validar_moodle_xml(output_xml_path)

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

    # Fase 4: Consolidación pedagógica y derivación a evaluación oficial Moodle XML
    c0_fase4_evaluacion = [
        create_moodle_quiz_referral(
            0,
            "Seguridad y Desenergización",
            "<p>Has analizado los protocolos obligatorios de desenergización en alta tensión y la regla crítica de cálculo de protección para osciloscopios y multímetros de taller. La verificación formal de conocimientos y el registro oficial en el Libro de Calificaciones se efectúan a través del cuestionario oficial Moodle XML.</p>"
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
    # CAPÍTULO 1: MEDIDAS ELÉCTRICAS, RELACIONES Y DIAGNOSIS
    # ---------------------------------------------------------------------
    # Fase 1: Motivación y activación conceptual
    c1_fase1_intro = [
        create_checkpoint_section(
            title="Activación de Conceptos: Relaciones de Magnitudes",
            intro_text="Antes de diagnosticar caídas de tensión y fallos de alimentación en el taller, repasa los fundamentos conceptuales y las relaciones matemáticas clave que rigen los circuitos de potencia.",
            badge_text="Activación de Conceptos Clave"
        ),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-bolt"></i> RECORDATORIO CONCEPTUAL</div>
          <h4 style="margin-top:0.4rem; color:#0f172a;">Parámetros Eléctricos Críticos en Diagnosis</h4>
          <ul style="margin:0; padding-left:1.2rem; color:#1e293b; line-height:1.7;">
            <li><strong>Diferencia de Potencial (Tensión - V):</strong> Medida en voltios (V). Fuerza impulsora de las cargas.</li>
            <li><strong>Intensidad de Corriente (I):</strong> Medida en amperios (A). Caudal de electrones que atraviesa un conductor.</li>
            <li><strong>Resistencia Eléctrica (R):</strong> Medida en ohmios (Ω). Oposición al flujo eléctrico; las resistencias parásitas provocan pérdidas térmicas inadmisibles.</li>
            <li><strong>Frecuencia de Señal (f):</strong> Medida en hercios (Hz). Ciclos por segundo en señales periódicas, inductivas y de sensores Hall.</li>
          </ul>
        </div>
        """, "Recordatorio de Magnitudes")
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

    # Fase 4: Consolidación pedagógica y derivación a evaluación oficial Moodle XML
    c1_fase4_evaluacion = [
        create_moodle_quiz_referral(
            1,
            "Medición, Relaciones y Diagnóstico",
            "<p>Has completado el análisis de la Ley de Ohm aplicada a caídas de tensión parásitas, verificación bajo consumo real con multímetro y protocolos de comprobación de líneas de alimentación. Para registrar tu evaluación oficial en el Libro de Calificaciones, realiza el cuestionario Moodle XML correspondiente.</p>"
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

    # 6. Compilar paquete H5P interactivo (Modalidad Formativa)
    build_h5p_package(
        output_path=ejemplo_pkg,
        title="Plantilla Oficial de Curso Interactivo EducaMadrid",
        book_cover_title="Curso Interactivo Homologado EducaMadrid",
        book_cover_desc="Plantilla técnica maestra para Formación Profesional en EducaMadrid y Moodle. Integración de los 5 pilares pedagógicos de aprendizaje activo, andamiaje, retroalimentación y accesibilidad WCAG 2.1 AA.",
        chapters=capitulos
    )

    # 7. Generar Banco de Preguntas Oficial Moodle XML (Modalidad Sumativa Desacoplada)
    eval_xml_path = os.path.join(PLANTILLA_DIR, "evaluacion_modelo_moodle.xml")
    generar_evaluacion_modelo_xml(eval_xml_path)

    # 8. Validar automáticamente el paquete H5P generado
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

