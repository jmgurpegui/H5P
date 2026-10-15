#!/usr/bin/env python3
"""
Generador Maestro del Curso Interactivo H5P:
"Interpretación y Diagnosis de Esquemas Eléctricos del Automóvil"
Ubicación: EsquemasElectricosAutomocion/

Diseñado conforme a la especificación técnica de EducaMadrid (Moodle) y los
5 Pilares Pedagógicos de Aprendizaje Activo:
- Participación constante del estudiante y enriquecimiento multimedia.
- Andamiaje en 4 fases progresivas (InteractiveBook 1.7 con capítulos Column 1.16).
- Retroalimentación formativa inmediata y razonada en cada distractor.
- Gamificación estratégica contextualizada en diagnosis de taller.
- Trazabilidad y evaluación competencial para Formación Profesional.
- Accesibilidad Universal WCAG 2.1 AA / AAA (Slate 900, touch targets >= 44px, alt texts).
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PLANTILLA_DIR = os.path.join(PROJECT_ROOT, 'plantilla')

# Directorio de librerías H5P homologadas
POSSIBLE_LIB_DIRS = [
    os.path.join(PROJECT_ROOT, 'h5p_builder', 'h5p-libraries'),
    os.path.join(PLANTILLA_DIR, 'h5p-libraries'),
    os.path.join(SCRIPT_DIR, 'h5p-libraries'),
    r'\\wsl.localhost\Ubuntu\home\jmgurpegui\H5P\h5p_builder\h5p-libraries',
    '/home/jmgurpegui/H5P/h5p_builder/h5p-libraries'
]
LIB_DIR = None
for p in POSSIBLE_LIB_DIRS:
    if os.path.exists(p) and os.path.isdir(p):
        LIB_DIR = os.path.abspath(p)
        break

if not LIB_DIR:
    raise FileNotFoundError("No se encontró el directorio de librerías h5p-libraries.")

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
# 1. HELPERS DE ENVOLTORIO Y RESOLUCIÓN DE RECURSOS
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
    """Localiza y resuelve dinámicamente metadatos del logotipo institucional."""
    if search_dirs is None:
        search_dirs = [
            PLANTILLA_DIR,
            SCRIPT_DIR,
            os.path.join(PROJECT_ROOT, '.agents', 'skills', 'h5p-educamadrid', 'resources'),
            os.path.join(PLANTILLA_DIR, 'resources')
        ]

    candidates = [preferred_name, 'logo2026.png', 'logo2026.jpg', 'logo2026.bmp']
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

    ext = found_filename.split('.')[-1].lower() if found_filename else 'png'
    mime_map = {'bmp': 'image/bmp', 'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'}
    mime_type = mime_map.get(ext, 'image/png')

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
    """Genera el bloque nativo H5P.Image 1.1 con el logotipo institucional y alt text accesible."""
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

def create_image_section(rel_path, alt_text, title="Imagen Técnica", width=1200, height=800):
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
    """Genera un componente H5P.Accordion 1.0 para desglosar procedimientos extensos."""
    panels = []
    for p_title, p_html in panels_data:
        panels.append({
            "title": p_title,
            "content": {
                "library": "H5P.AdvancedText 1.1",
                "params": {"text": p_html},
                "subContentId": str(uuid.uuid4()),
                "metadata": {"title": p_title, "contentType": "Text", "license": "CC BY-SA"}
            }
        })
    return create_column_wrapper("H5P.Accordion 1.0", {"panels": panels}, title)

def create_checkpoint_section(title, intro_html):
    """Genera una parada pedagógica activa para consolidación y autorregulación."""
    html = f"""
    <div class="tech-checkpoint">
      <div class="tech-checkpoint-badge"><i class="fa fa-flag-checkered"></i> PARADA DE COMPRENSIÓN ACTIVA</div>
      <h3 style="margin-top:0.5rem; color:#0f172a; font-size:1.25rem;">{title}</h3>
      <div style="color:#1e293b; line-height:1.6;">{intro_html}</div>
    </div>
    """
    return create_text_section(html, f"Parada de Comprensión: {title}")

def create_active_challenge(title, scenario_html, steps, badge_text="Reto Práctico de Taller"):
    """Crea un reto pedagógico interactivo de taller con toma de decisiones."""
    steps_html = "".join([
        f'<div class="tech-challenge-step"><span class="step-num">{idx+1}</span><div><strong>{step_title}:</strong> {step_desc}</div></div>'
        for idx, (step_title, step_desc) in enumerate(steps)
    ])
    html = f"""
    <div class="tech-challenge">
      <div class="tech-challenge-badge"><i class="fa fa-wrench"></i> {badge_text}</div>
      <h3 style="margin-top:0.5rem; color:#0f172a; font-size:1.25rem;">{title}</h3>
      <div style="color:#1e293b; margin-bottom:1rem; line-height:1.6;">{scenario_html}</div>
      <div class="tech-challenge-steps">{steps_html}</div>
    </div>
    """
    return create_text_section(html, f"Reto: {title}")

def create_checklist_section(title, items):
    """Genera una lista de verificación táctil accesible (WCAG AAA, >=44px touch targets)."""
    items_html = "".join([
        f'<li class="tech-checklist-item"><label class="tech-check-label"><input type="checkbox" class="tech-checkbox" /> <span>{item_text}</span></label></li>'
        for item_text in items
    ])
    html = f"""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-tasks"></i> LISTA DE COTEJO TÁCTIL</div>
      <h3 style="margin-top:0.5rem; color:#0f172a; font-size:1.25rem;">{title}</h3>
      <ul class="tech-checklist">{items_html}</ul>
    </div>
    """
    return create_text_section(html, f"Checklist: {title}")

def create_multichoice_question(question_html, answers, title="Autocomprobación"):
    """Crea una actividad formativa H5P.MultiChoice 1.16 con retroalimentación razonada."""
    answers_formatted = []
    for text, is_correct, tip, feedback in answers:
        answers_formatted.append({
            "text": f"<div>{text}</div>",
            "correct": is_correct,
            "tipsAndFeedback": {
                "tip": f"<div>{tip}</div>" if tip else "",
                "chosenFeedback": f"<div>{feedback}</div>" if feedback else ""
            }
        })
    params = {
        "question": f"<div>{question_html}</div>",
        "answers": answers_formatted,
        "behaviour": {
            "singlePoint": False,
            "randomAnswers": True,
            "showSolutionsRequiresInput": True,
            "type": "auto",
            "confirmCheckDialog": False,
            "confirmRetryDialog": False,
            "autoCheck": True,
            "passPercentage": 100,
            "showScorePoints": True,
            "enableRetry": True,
            "enableSolutionsButton": True
        },
        "UI": {
            "checkAnswerButton": "Comprobar respuesta",
            "showSolutionButton": "Ver solución detallada",
            "tryAgainButton": "Reintentar para afianzar"
        }
    }
    return create_column_wrapper("H5P.MultiChoice 1.16", params, title)

def create_true_false_question(question_html, is_correct, title="Verificación Rápida", feedback_correct="", feedback_wrong=""):
    """Crea una actividad H5P.TrueFalse 1.8 para validación de criterios técnicos."""
    params = {
        "question": f"<div>{question_html}</div>",
        "correct": "true" if is_correct else "false",
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "confirmCheckDialog": False,
            "confirmRetryDialog": False,
            "autoCheck": True
        },
        "l10n": {
            "trueText": "Verdadero (Conforme a norma)",
            "falseText": "Falso (Contrario a norma)",
            "feedback": "Resultado de la comprobación:"
        }
    }
    return create_column_wrapper("H5P.TrueFalse 1.8", params, title)

def create_drag_text_activity(task_desc, text_template, distractors, title="Arrastre de Términos"):
    """Crea una actividad H5P.DragText 1.10 para arrastre de magnitudes y términos."""
    full_text = text_template
    if distractors:
        full_text += "\n\n" + " ".join([f"*{d}*" for d in distractors])
    params = {
        "taskDescription": f"<p>{task_desc}</p>",
        "textField": full_text,
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "instantFeedback": True,
            "enableCheckButton": True
        }
    }
    return create_column_wrapper("H5P.DragText 1.10", params, title)

def create_simulation_box(title, desc_html, button_text, url, icon="fa-video-camera"):
    """Crea una tarjeta accesible para enlazar a simuladores o vídeos de apoyo."""
    html = f"""
    <div class="tech-card" style="border-left: 5px solid #2563eb; background: #f8fafc;">
      <div class="tech-card-badge" style="background:#2563eb; color:#ffffff;"><i class="fa {icon}"></i> RECURSO INTERACTIVO</div>
      <h3 style="margin-top:0.5rem; color:#0f172a; font-size:1.25rem;">{title}</h3>
      <div style="color:#334155; line-height:1.6; margin-bottom:1rem;">{desc_html}</div>
      <div style="text-align:left;">
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="btn-sim" style="text-decoration:none; display:inline-block; background:#1d4ed8; color:#ffffff; padding:0.6rem 1.2rem; border-radius:6px; font-weight:600; font-size:0.95rem;">
          <i class="fa fa-external-link"></i> {button_text}
        </a>
      </div>
    </div>
    """
    return create_text_section(html, f"Recurso: {title}")

def create_didactic_sequence_chapter(title, phase1_intro, phase2_theory, phase3_practice, phase4_eval):
    """Construye un capítulo modular encapsulado en H5P.Column con la secuencia de 4 fases."""
    sections = [create_header_logo()]
    sections.extend(phase1_intro)
    sections.extend(phase2_theory)
    sections.extend(phase3_practice)
    sections.extend(phase4_eval)
    return {
        "library": "H5P.Column 1.16",
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": title,
            "contentType": "Column",
            "license": "CC BY-SA",
            "authors": [{"name": "Departamento de Formación Profesional - Automoción", "role": "Author"}]
        },
        "params": {
            "title": title,
            "content": sections
        }
    }


# =========================================================================
# 2. DEFINICIÓN DIDÁCTICA Y TÉCNICA DE LOS 4 CAPÍTULOS
# =========================================================================

def build_chapter_1():
    """Capítulo 1: Utilidad de la interpretación de esquemas eléctricos de vehículos"""
    # Fase 1: Motivación y Reto
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-bolt"></i> UNIDAD 1 · FORMACIÓN PROFESIONAL</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Utilidad de la Interpretación de Esquemas Eléctricos</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            Aprende a transformar horas de ensayo y error a ciegas en un procedimiento científico de diagnosis.
            En los vehículos modernos, con kilómetros de cableado y decenas de unidades de control interconectadas,
            el esquema eléctrico es el mapa de navegación indispensable para cualquier técnico electromecánico.
          </p>
        </div>
        """, "Introducción Unidad 1"),
        create_image_section("images/mapa_conceptual.jpg", "Mapa conceptual de la unidad didáctica de interpretación de esquemas eléctricos de automoción", "Mapa Conceptual General", 691, 735),
        create_active_challenge(
            title="El Dilema del Taller: ¿Sustituir piezas o Diagnosticar?",
            scenario_html="<p>Un vehículo llega al taller con un fallo intermitente en el encendido de los faros antiniebla delanteros y en el testigo del cuadro de instrumentos. En otro taller sustituyeron el interruptor y la bombilla sin éxito, con un coste elevado para el cliente. Antes de desmontar cualquier guarnecido, ¿cuál es el procedimiento metodológico?</p>",
            steps=[
                ("Paso 1 (Identificación)", "Consultar el esquema de detalle para conocer la línea de alimentación (fusible, relé intermedio y masa asociada)."),
                ("Paso 2 (Hipótesis)", "Determinar si la falla es común al actuador y al testigo, lo que acotaría el problema antes de la bifurcación del cableado."),
                ("Paso 3 (Medición no invasiva)", "Medir tensión y caída de tensión en los bornes de prueba sin perforar el aislamiento.")
            ],
            badge_text="Reto Inicial de Taller"
        )
    ]

    # Fase 2: Explicación interactiva
    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-book"></i> CONTENIDO TÉCNICO FUNDAMENTAL</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">1.1 Diagnosis de Averías Eléctricas</h3>
          <p style="color:#1e293b; line-height:1.6;">
            La interpretación de esquemas permite identificar los cuatro estados patológicos de un circuito:
          </p>
          <div class="tech-table-wrap">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Tipo de Avería</th>
                  <th>Comportamiento Eléctrico</th>
                  <th>Causa Frecuente</th>
                  <th>Método de Comprobación</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Circuito Abierto (Interrupción)</strong></td>
                  <td>Resistencia infinita (R = ∞ Ω). Intensidad nula (I = 0 A). Tensión de fuente presente hasta el punto de corte.</td>
                  <td>Cable seccionado, conector desenchufado, terminal desengarzado o fusible fundido.</td>
                  <td>Comprobación de continuidad sin tensión o medición de tensión paso a paso bajo carga.</td>
                </tr>
                <tr>
                  <td><strong>Cortocircuito a Masa</strong></td>
                  <td>Resistencia nula o casi nula (R ≈ 0 Ω). Intensidad máxima que funde el fusible de protección o desactiva la salida MOSFET.</td>
                  <td>Aislante rozado contra la chapa metálica de la carrocería o motor.</td>
                  <td>Medir resistencia a masa del tramo aislado desconectando carga y fuente.</td>
                </tr>
                <tr>
                  <td><strong>Cortocircuito a Positivo</strong></td>
                  <td>Unión involuntaria de dos conductores positivos independientes.</td>
                  <td>Cables derretidos juntos en el mazo por calor del escape o sobrecarga.</td>
                  <td>Aparición de tensión en un circuito apagado cuando se enciende otro cercano.</td>
                </tr>
                <tr>
                  <td><strong>Caída de Tensión Inadmisible</strong></td>
                  <td>Resistencia parásita de contacto en serie con la carga.</td>
                  <td>Sulfatación de bornes, terminales flojos, óxido de cobre interno.</td>
                  <td>Medición voltimétrica diferencial directamente sobre los extremos del conductor bajo carga.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="tech-formula-block">
            <span class="tech-formula">V<sub>caída</sub> = I × R<sub>contacto</sub> ≤ 0.2 V</span>
            <div class="tech-formula-desc">Regla de oro de automoción: En conexiones de potencia de 12 V, la caída de tensión en un conector o línea de masa bajo carga nunca debe superar 0.2 V.</div>
          </div>
        </div>
        """, "1.1 Diagnosis de Averías"),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-map-marker"></i> LOCALIZACIÓN PRÁCTICA</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">1.2 Localización de Componentes y Puntos de Medición</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Los esquemas eléctricos traducen la maraña física de cables en un mapa estructurado mediante coordenadas espaciales y códigos de conectores:
          </p>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem;">
            <li><strong>Cajas de Interconexión y Fusibles:</strong> Unidades como la <em>UCH</em> (Renault), <em>SAM</em> (Mercedes-Benz), <em>CJB/BJB</em> (Ford) o <em>BDC/FEM</em> (BMW) centralizan la distribución de potencia. Conocer su ubicación exacta ahorra horas de desmontaje.</li>
            <li><strong>Puntos de Masa de Carrocería:</strong> Más del 60% de los fallos eléctricos extraños son causados por masas oxidadas o flojas. Los esquemas indican su designación (ej. W10, G25, MAM) y zona concreta de fijación al chasis.</li>
            <li><strong>Puntos de Medición Seguros:</strong> Para comprobar señales en centralitas (ECU, ABS, BCM), se deben utilizar los pines de los conectores intermedios mediante agujas traseras (<em>back-probe</em>).</li>
          </ul>
          <div class="alert-box" style="border-left:4px solid #b91c1c; background:#fef2f2; padding:0.8rem; margin-top:0.8rem; border-radius:4px;">
            <strong style="color:#991b1b;"><i class="fa fa-exclamation-triangle"></i> ¡PROHIBICIÓN ESTRICTA DE TALLER!</strong>
            <p style="color:#7f1d1d; margin:0.4rem 0 0 0; font-size:0.95rem;">
              Jamás pinches el aislante de un cable automotriz con la aguja del multímetro. La perforación rompe la estanqueidad, permitiendo que la humedad y la sal del asfalto penetren por capilaridad, corroyendo el cobre por sulfatación verde y destruyendo el cable internamente meses después.
            </p>
          </div>
        </div>
        """, "1.2 Localización de Componentes"),
        create_simulation_box(
            title="Vídeo Práctico: ¿Cómo Leer Esquemas Eléctricos del Automóvil? (Parte 1)",
            desc_html="Visualiza la explicación en vídeo de PetrolheadGarage sobre la lógica de lectura de esquemas, alimentación de líneas 30/15 y localización de componentes en taller.",
            button_text="Ver Clase en YouTube (PetrolheadGarage)",
            url="https://www.youtube.com/watch?v=aw3jDyH8MbU"
        )
    ]

    # Fase 3: Práctica guiada
    phase3 = [
        create_checkpoint_section(
            title="Procedimiento Seguro de Medición Eléctrica",
            intro_html="Antes de realizar cualquier toma de tensión o continuidad en sistemas multiplexados, revisa la siguiente lista de verificación técnica."
        ),
        create_checklist_section(
            title="Checklist: 5 Reglas de Oro para Medir sin Averiar",
            items=[
                "Verificar tensión de reposo de la batería del vehículo (mínimo 12.4 V antes de iniciar pruebas).",
                "Comprobar fusibles midiendo tensión en sus dos puntos de prueba metálicos superiores sin extraerlos.",
                "Utilizar sondas de acupuntura traseras (back-probing) insertadas por la junta de goma estanca del conector.",
                "No aplicar el óhmetro jamás sobre un circuito que tenga tensión presente (destrucción del multímetro o disparo de airbags).",
                "Comprobar las caídas de tensión en bornes de masa con el circuito operando bajo carga nominal real."
            ]
        ),
        create_drag_text_activity(
            task_desc="Completa los principios fundamentales de la diagnosis eléctrica arrastrando los conceptos correspondientes a cada hueco:",
            text_template="En un *circuito abierto*, la resistencia es *infinita* y la intensidad que circula es nula. Por el contrario, un *cortocircuito a masa* provoca una resistencia cercana a cero y una corriente excesiva que funde el *fusible* de protección. La técnica de medición recomendada para no perforar el aislante se denomina *back-probing* y la caída de tensión en una conexión no debe superar los *0.2 V*.",
            distractors=["12 V", "cortocircuito a positivo", "óhmetro"],
            title="Práctica Guiada: Conceptos de Diagnosis"
        )
    ]

    # Fase 4: Evaluación formativa explicada
    phase4 = [
        create_multichoice_question(
            question_html="Al revisar un motor de arranque que gira lentamente, mides con el voltímetro entre el borne negativo de la batería y la carcasa metálica del motor durante el intento de arranque, obteniendo una lectura de <strong>1.8 V</strong>. ¿Cuál es la conclusión técnica?",
            answers=[
                ("Existe una caída de tensión inadmisible en el circuito de masa del motor (resistencia parásita en cable o tornillo).", True, "Recuerda la regla de caída máxima de tensión en masas de potencia.", "¡Excelente! Una masa correcta bajo carga debe registrar menos de 0.2 V. Un valor de 1.8 V roba potencia al motor de arranque y evidencia sulfatación o mala fijación del cable de masa a la carrocería."),
                ("La batería está completamente descargada y debe sustituirse de inmediato.", False, "Analiza entre qué puntos se colocaron las puntas del voltímetro.", "Incorrecto. Se está midiendo entre dos puntos que teóricamente deberían estar al mismo potencial (masa y negativo). Si hay 1.8 V de diferencia, la avería reside en la resistencia de unión del cable de masa, no necesariamente en el estado químico de la batería."),
                ("El motor de arranque tiene un cortocircuito interno a positivo.", False, "Si hubiera un cortocircuito a positivo se fundiría el fusible o ardería el cable.", "Incorrecto. Un cortocircuito a positivo generaría humo o dispararía protecciones masivas, no una pérdida de 1.8 V en el retorno de masa.")
            ],
            title="Autocomprobación 1.1: Diagnóstico de Caída de Tensión"
        ),
        create_true_false_question(
            question_html="¿Es admisible clavar las puntas afiladas del multímetro en el aislamiento plástico de un cable para tomar rápidamente una señal si luego se tapa con cinta aislante?",
            is_correct=False,
            title="Autocomprobación 1.2: Prácticas de Taller Seguras",
            feedback_correct="¡Correcto! Está taxativamente prohibido en manuales de fabricante. La perforación degrada el sellado estanco, provocando corrosión interna por salinidad y humedad que destruye el conductor.",
            feedback_wrong="Incorrecto. La cinta aislante no restaura la estanqueidad molecular original. Los fabricantes prohíben perforar cables y exigen sondas traseras (back-probes) o cajas de bornas (breakout boxes)."
        )
    ]

    return create_didactic_sequence_chapter(
        "Unidad 1: Utilidad y Diagnosis con Esquemas Eléctricos",
        phase1, phase2, phase3, phase4
    )


def build_chapter_2():
    """Capítulo 2: Tipos de esquemas eléctricos de vehículos"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-sitemap"></i> UNIDAD 2 · FORMACIÓN PROFESIONAL</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Tipos de Esquemas Eléctricos de Vehículos</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            Aprende a diferenciar y combinar los tres formatos esenciales de documentación técnica:
            esquemas de situación de componentes, esquemas generales de arquitectura y esquemas de detalle unifilares.
          </p>
        </div>
        """, "Introducción Unidad 2"),
        create_active_challenge(
            title="Reto: Seleccionar la Documentación Correcta",
            scenario_html="<p>El cliente de un taller indica que la luneta térmica trasera y el espejo retrovisor térmico derecho no desempañan. Dispones del manual de servicio oficial del vehículo. ¿En qué orden abres los tres tipos de esquemas para no perder tiempo?</p>",
            steps=[
                ("Fase A (Esquema General)", "Consultar el esquema general para comprobar si ambos actuadores comparten fusible, relé o pasarela electrónica común."),
                ("Fase B (Esquema de Detalle)", "Analizar el esquema de detalle tramo por tramo para verificar qué pines, conectores intermedios y colores de cable alimentan la luneta."),
                ("Fase C (Esquema de Situación)", "Abrir el esquema de situación para ubicar con exactitud el conector del pilar trasero y el punto de masa de la puerta.")
            ],
            badge_text="Estrategia Documental"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-cubes"></i> CLASIFICACIÓN TÉCNICA</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">Los 3 Tipos de Esquemas en la Documentación Automotriz</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Cada tipo de esquema responde a una pregunta diferente del electromecánico:
          </p>
          <div class="tech-table-wrap">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Tipo de Esquema</th>
                  <th>Pregunta a la que Responde</th>
                  <th>Características Principales</th>
                  <th>Uso en el Taller</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>1. De Situación de Componentes</strong></td>
                  <td><em>¿Dónde está físicamente la pieza en el coche?</em></td>
                  <td>Muestra gráficos en 3D, siluetas de la carrocería o fotografías reales del vano motor, salpicadero y taloneras con flechas y códigos.</td>
                  <td>Desmontar guarnecidos sin romper grapas y localizar masas, centralitas y conectores pasamuros.</td>
                </tr>
                <tr>
                  <td><strong>2. General (Arquitectura de Red)</strong></td>
                  <td><em>¿Cómo se distribuye la energía y la información global?</em></td>
                  <td>Diagrama de bloques de alto nivel. Muestra las redes de comunicación (CAN High/Low, LIN, FlexRay), las líneas maestras de potencia (+30, +15) y los módulos centrales.</td>
                  <td>Analizar fallos de comunicación entre calculadores y distribución de alimentación principal.</td>
                </tr>
                <tr>
                  <td><strong>3. De Detalle (Unifilar Desarrollado)</strong></td>
                  <td><em>¿Cómo se conecta exactamente cada pin y cable?</em></td>
                  <td>Representación lineal y funcional completa de un subsistema (ej. climatización, inyección). Positivo arriba, masa abajo. Muestra sección de cable, colores, relés y vías.</td>
                  <td>Medir tensiones, señales y continuidades pin a pin en el mazo de cables.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        """, "2.1 Clasificación de Esquemas"),
        create_image_section("images/esquema_mercedes_climatizacion.jpg", "Esquema de detalle de climatización automática de Mercedes-Benz con numeración de vías y conectores", "Ejemplo: Esquema de Detalle (Mercedes-Benz Climatización)", 691, 389),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-microchip"></i> DETALLE DE CONEXIONES</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">Análisis de un Esquema de Detalle Real</h3>
          <p style="color:#1e293b; line-height:1.6;">
            En la figura superior (Mercedes-Benz Clase C) podemos observar las claves de un esquema de detalle:
          </p>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem;">
            <li><strong>Módulos y Componentes:</strong> <code>N18</code> (teclado de calefacción automática), <code>A32</code> (unidad de reciclado de aire) y servomotores de trampillas <code>M2/5 a M2/21</code>.</li>
            <li><strong>Líneas de Alimentación y Masas:</strong> Borne <code>30</code> protegido por fusible <code>F34</code> (7.5 A), borne <code>31</code> con retorno a masa en talonera izquierda <code>W28/1</code> y talonera derecha <code>W28/2</code>.</li>
            <li><strong>Bus de Datos:</strong> Líneas trenzadas de comunicación <code>CAN-BH</code> (habitáculo alta) y <code>CAN-BL</code> (habitáculo baja) conectadas en el distribuidor <code>X30/6</code>.</li>
            <li><strong>Identificación de Cables:</strong> Sección y color, ej. <code>0.35 WHPK</code> (0.35 mm², blanco/rosa) o <code>0.75 RDBU</code> (0.75 mm², rojo/azul).</li>
          </ul>
        </div>
        """, "Análisis de Esquema de Detalle"),
        create_image_section("images/renault_uch_conectores.jpg", "Identificación de conectores modulares de la Unidad Central de Habitáculo (UCH) de Renault Mégane", "Ejemplo: Esquema de Módulo y Conectores (Renault UCH)", 691, 649)
    ]

    phase3 = [
        create_checkpoint_section(
            title="Lógica de Lectura Tramo a Tramo",
            intro_html="Un esquema de detalle nunca se lee al azar. Sigue siempre la corriente desde la fuente positiva superior hasta la masa inferior."
        ),
        create_accordion([
            ("Paso 1: Localización de la Fuente (+30 o +15)", "<p>Ubica en la parte superior del esquema la barra colectora de alimentación. Determina si el circuito opera con tensión permanente directa de batería (borne 30) o requiere llave de contacto (borne 15).</p>"),
            ("Paso 2: Elemento de Protección y Conmutación", "<p>Sigue la línea hacia abajo identificando el fusible de protección (valor en Amperios) y los contactos de relé o interruptores asociados.</p>"),
            ("Paso 3: Trayecto del Mazo y Conectores Intermedios", "<p>Anota los conectores intermedios (ej. R107, C202), el número de pin/vía de entrada y salida, así como la sección y color del cable.</p>"),
            ("Paso 4: El Actuador o Carga y su Retorno a Masa", "<p>Llega al componente consumidor (bombilla, servomotor, electroválvula) y continúa por el cable de retorno hasta el punto de masa atornillado a la carrocería (borne 31).</p>")
        ], "Protocolo de Lectura en 4 Pasos"),
        create_drag_text_activity(
            task_desc="Empareja cada necesidad diagnóstica con el tipo de esquema que debes consultar en el taller:",
            text_template="Para encontrar detrás de qué panel del pilar C se atornilla la masa W28/2, usamos el esquema de *situación*. Para verificar si la centralita de motor y el cuadro comparten la red de comunicación CAN, consultamos el esquema *general*. Para saber con qué pin, color y sección de cable se alimenta el inyector 1, recurrimos al esquema de *detalle*.",
            distractors=["diagrama de despiece", "manual de usuario"],
            title="Práctica Guiada: Selección de Esquemas"
        )
    ]

    phase4 = [
        create_multichoice_question(
            question_html="¿Qué información técnica fundamental <strong>NO</strong> proporciona un esquema eléctrico de detalle unifilar y debe buscarse en un esquema de situación?",
            answers=[
                ("La longitud real física del cable y la trayectoria espacial exacta del mazo dentro de la carrocería.", True, "El esquema de detalle simplifica la representación funcional sin escala métrica.", "¡Correcto! En los esquemas de detalle, las líneas se dibujan ortogonales por claridad funcional. Un cable de 20 cm se representa con la misma longitud que uno de 4 metros. La ruta real física y sus pasamuros se consultan en el esquema de situación."),
                ("El color del cable y su sección en milímetros cuadrados.", False, "Esta información sí está en el esquema de detalle.", "Incorrecto. Los esquemas de detalle indican expresamente la sección (ej. 0.75 mm²) y los códigos de color (ej. BNRD)."),
                ("El número de pin o vía en cada conector de la centralita.", False, "Los pines son el núcleo del esquema de detalle.", "Incorrecto. El número de vía en conectores y calculadores es precisamente uno de los datos principales del esquema de detalle.")
            ],
            title="Autocomprobación 2.1: Limitaciones y Alcance de Esquemas"
        ),
        create_true_false_question(
            question_html="¿En los esquemas eléctricos automotrices los relés e interruptores se representan siempre en su posición de reposo (sin corriente ni accionamiento)?",
            is_correct=True,
            title="Autocomprobación 2.2: Convención de Estado de Reposo",
            feedback_correct="¡Correcto! Es una norma internacional absoluta. Todos los componentes se representan en reposo mecánico y eléctrico (llave quitada, relés abiertos y pulsadores sin accionar).",
            feedback_wrong="Incorrecto. Si se dibujasen en estado activado generaría confusión sobre qué contactos son normalmente abiertos (NA) o normalmente cerrados (NC). Se dibujan siempre en reposo."
        )
    ]

    return create_didactic_sequence_chapter(
        "Unidad 2: Tipos de Esquemas Eléctricos del Automóvil",
        phase1, phase2, phase3, phase4
    )


def build_chapter_3():
    """Capítulo 3: Simbología empleada en los esquemas eléctricos de vehículos"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-tags"></i> UNIDAD 3 · FORMACIÓN PROFESIONAL</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Simbología Normalizada y Códigos de Bornes</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            Domina la Norma DIN 72552, el código internacional de designación de terminales y la simbología
            gráfica de componentes eléctricos para diagnosticar cualquier vehículo sin riesgo de avería.
          </p>
        </div>
        """, "Introducción Unidad 3"),
        create_active_challenge(
            title="El Riesgo de Invertir Bornes en un Relé",
            scenario_html="<p>Un operario novato sustituye un relé estándar por otro relé que incorpora un diodo supresor de picos inductivos en paralelo con la bobina. Al conectarlo, invierte accidentalmente las conexiones de los bornes 85 y 86. ¿Qué ocurre de inmediato en el circuito?</p>",
            steps=[
                ("Efecto Físico", "El diodo queda polarizado en sentido directo entre positivo y negativo."),
                ("Consecuencia", "Se crea un cortocircuito franco a través del diodo."),
                ("Daño en Taller", "Se destruye el transistor de control de la centralita electrónica o se funde el fusible de control de inyección.")
            ],
            badge_text="Caso Crítico de Seguridad"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-certificate"></i> NORMA DIN 72552</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">3.1 Designación Normalizada de Bornes y Terminales</h3>
          <p style="color:#1e293b; line-height:1.6;">
            La norma DIN 72552 asigna un número invariable a cada función eléctrica en el automóvil:
          </p>
          <div class="tech-table-wrap">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Borne DIN</th>
                  <th>Función Eléctrica</th>
                  <th>Estado de Conmutación</th>
                  <th>Color Típico (Norma Alemana)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>30</strong></td>
                  <td>Positivo directo desde batería (Alimentación permanente).</td>
                  <td>Siempre con tensión (+12 V / +24 V).</td>
                  <td>Rojo (RD / RT)</td>
                </tr>
                <tr>
                  <td><strong>15</strong></td>
                  <td>Positivo conmutado tras llave de contacto (Encendido / Ignición).</td>
                  <td>Tensión presente en posición CONTACTO y ARRANQUE.</td>
                  <td>Negro (BK / SW) o Verde (GN)</td>
                </tr>
                <tr>
                  <td><strong>31</strong></td>
                  <td>Masa / Retorno a negativo de batería (Chasis).</td>
                  <td>Potencial 0 V de referencia de masa.</td>
                  <td>Marrón (BN / BR)</td>
                </tr>
                <tr>
                  <td><strong>50</strong></td>
                  <td>Mando del motor de arranque.</td>
                  <td>Tensión únicamente durante la fase de START.</td>
                  <td>Rojo/Negro o Violeta</td>
                </tr>
                <tr>
                  <td><strong>X o 75</strong></td>
                  <td>Positivo conmutado de accesorios y climatización.</td>
                  <td>Activo en contacto, pero <strong>se desconecta durante el arranque</strong> para reservar energía.</td>
                  <td>Negro/Amarillo</td>
                </tr>
                <tr>
                  <td><strong>1</strong></td>
                  <td>Señal de encendido / Negativo de bobina de encendido.</td>
                  <td>Pulsos de conmutación a masa.</td>
                  <td>Verde</td>
                </tr>
                <tr>
                  <td><strong>85</strong></td>
                  <td>Extremo negativo o de control de la bobina del relé.</td>
                  <td>Conmutado a masa por interruptor o UCE.</td>
                  <td>Marrón o según UCE</td>
                </tr>
                <tr>
                  <td><strong>86</strong></td>
                  <td>Extremo positivo de excitación de la bobina del relé.</td>
                  <td>Alimentado desde borne 15 o borne 30.</td>
                  <td>Negro o Rojo</td>
                </tr>
                <tr>
                  <td><strong>87</strong></td>
                  <td>Contacto de salida de potencia del relé (Normalmente Abierto, NA).</td>
                  <td>Alimenta la carga cuando la bobina está excitada.</td>
                  <td>Varía según consumidor</td>
                </tr>
                <tr>
                  <td><strong>87a</strong></td>
                  <td>Contacto normalmente cerrado (NC) en relés inversores.</td>
                  <td>Conduce en reposo, se abre al excitar el relé.</td>
                  <td>Varía según consumidor</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        """, "3.1 Norma DIN 72552"),
        create_image_section("images/tabla_colores_multimarca.jpg", "Tabla comparativa de códigos y denominación de colores de cables en diferentes fabricantes de automóviles", "Tabla Comparativa de Colores de Cables Multimarca", 691, 519),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-paint-brush"></i> CÓDIGOS DE COLOR</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">3.2 Códigos de Color de Conductores y Simbología Especial</h3>
          <p style="color:#1e293b; line-height:1.6;">
            A diferencia de la instalación eléctrica doméstica, en automoción cada grupo automovilístico utiliza abreviaturas en su propio idioma:
          </p>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem;">
            <li><strong>Abreviaturas en Inglés (Ford, Nissan, etc.):</strong> <code>BK</code> (Negro), <code>BN</code> (Marrón), <code>BU</code> (Azul), <code>GN</code> (Verde), <code>GY</code> (Gris), <code>OG</code> (Naranja), <code>RD</code> (Rojo), <code>WH</code> (Blanco), <code>YE</code> (Amarillo).</li>
            <li><strong>Abreviaturas en Francés (Renault, PSA):</strong> <code>NO</code> (Noir/Negro), <code>MR/MA</code> (Marron), <code>BE</code> (Bleu), <code>VE</code> (Vert), <code>GR</code> (Gris), <code>OR</code> (Orange), <code>RG</code> (Rouge), <code>BA</code> (Blanc), <code>JA/JN</code> (Jaune), <code>VJ</code> (Vert-Jaune).</li>
            <li><strong>Abreviaturas en Alemán (BMW, Grupo VAG):</strong> <code>SW</code> (Schwarz), <code>BR</code> (Braun), <code>BL</code> (Blau), <code>GN</code> (Grün), <code>GR</code> (Grau), <code>RT</code> (Rot), <code>WS</code> (Weiß), <code>GE</code> (Gelb).</li>
          </ul>
          <div class="tech-formula-block">
            <span class="tech-formula">S = (2 × L × I) / (γ × V<sub>caída</sub>)</span>
            <div class="tech-formula-desc">Fórmula de sección mínima del cable: L = longitud (m), I = intensidad (A), γ = conductividad del cobre (56 m/(Ω·mm²)), V<sub>caída</sub> = 0.2 V máximo.</div>
          </div>
        </div>
        """, "3.2 Códigos de Color Multimarca")
    ]

    phase3 = [
        create_checkpoint_section(
            title="Consolidación de Bornes DIN y Funciones",
            intro_html="Comprueba tu dominio de la norma DIN arrastrando los bornes normalizados a su función correspondiente."
        ),
        create_drag_text_activity(
            task_desc="Arrastra el número de borne DIN correspondiente a cada definición técnica:",
            text_template="El borne *30* suministra positivo directo permanente de batería. El borne *15* alimenta los sistemas activos con el contacto puesto. La conexión a masa del chasis es el borne *31*. El solenoide de arranque se activa mediante el borne *50*. En un relé convencional, la bobina se energiza entre los bornes *85* y *86*, mientras que el contacto de potencia cierra entre *30* y *87*. El borne *X* desconecta los consumidores pesados durante el arranque.",
            distractors=["87a", "1", "15a"],
            title="Práctica Guiada: Bornes DIN 72552"
        )
    ]

    phase4 = [
        create_multichoice_question(
            question_html="¿Por qué la línea de alimentación de accesorios y climatización está conectada al <strong>borne X (o borne 75)</strong> en lugar de conectarse directamente al borne 15?",
            answers=[
                ("Para desconectar temporalmente las cargas de confort durante el arranque y destinar toda la capacidad de la batería al motor de arranque.", True, "Piensa en el consumo del motor de arranque.", "¡Exacto! El motor de arranque puede demandar entre 150 A y 400 A. Al girar la llave a la posición 50 (START), el relé de descarga de accesorios corta el borne X/75 para evitar caídas excesivas de tensión y proteger la electrónica sensible."),
                ("Porque el borne X suministra corriente alterna para los motores de climatización.", False, "En automoción el sistema de distribución es de corriente continua.", "Incorrecto. Los vehículos operan en corriente continua; el alternador rectifica la corriente antes de inyectarla a la red."),
                ("Para evitar que la climatización funcione si el motor no ha alcanzado 90 ºC.", False, "Eso lo gestiona el calculador de climatización, no el borne de contacto.", "Incorrecto. La temperatura del motor la gestiona la UCE por software, no la desconexión del borne X.")
            ],
            title="Autocomprobación 3.1: Función del Borne X/75"
        ),
        create_true_false_question(
            question_html="¿En un esquema eléctrico alemán (BMW o VAG), un cable con la designación <strong>0.5 BR</strong> corresponde a un cable de positivo conmutado bajo llave?",
            is_correct=False,
            title="Autocomprobación 3.2: Códigos Alemanes de Color",
            feedback_correct="¡Correcto! En los esquemas de marcas alemanas, 'BR' significa Braun (Marrón), que representa obligatoriamente la conexión a masa (borne 31). El positivo conmutado se designaría con SW (Schwarz) o RT/SW.",
            feedback_wrong="Incorrecto. En la normativa alemana, 'BR' (Braun / Marrón) es invariablemente masa (0 V). Confundirlo con un positivo en el taller provocará un cortocircuito grave."
        )
    ]

    return create_didactic_sequence_chapter(
        "Unidad 3: Simbología Normalizada y Códigos DIN",
        phase1, phase2, phase3, phase4
    )


def build_chapter_4():
    """Capítulo 4: Estudio de esquemas eléctricos de fabricantes (Mercedes-Benz, Ford, Renault, BMW)"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-car"></i> UNIDAD 4 · FORMACIÓN PROFESIONAL</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Estudio de Esquemas Eléctricos por Fabricantes</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            Aprende a interpretar los dialectos propios de los cuatro grandes fabricantes:
            Mercedes-Benz (sistema SAM y códigos W/N), Ford (sistema de cuadrículas y circuitos),
            Renault (código numérico universal y UCH) y BMW (sistema ISTA y WDS).
          </p>
        </div>
        """, "Introducción Unidad 4"),
        create_active_challenge(
            title="Reto de Taller Multimarca: Decodificación Cruzada",
            scenario_html="<p>En un taller multimarca entran simultáneamente cuatro vehículos con averías eléctricas. Debes identificar la UCE de inyección y el punto de masa en la documentación de cada fabricante. ¿Cómo se denominan en cada marca?</p>",
            steps=[
                ("Mercedes-Benz", "UCE motor: N3/10. Masas designadas con la letra W (ej. W10 masa batería, W28/1 talonera). Cable de masa: BN (Braun)."),
                ("Ford", "UCE motor: PCM / A147. Masas designadas con G (Ground, ej. G25, G1001). Empalmes con S (Splice). Cable: código alfanumérico (ej. 91-PG30A.75BK/WH)."),
                ("Renault", "UCE motor: Código puramente numérico '120'. UCH habitáculo: '645'. Conectores: PE1, PP1 con colores BA, GR, NO."),
                ("BMW", "UCE motor: DME/DDE. Conectores siempre con la letra X (ej. X11004, X60001). Cable de masa: BR (Braun), positivo directo: RT (Rot).")
            ],
            badge_text="Competencia Multimarca"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-shield"></i> FABRICANTE 1 · MERCEDES-BENZ</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">Particularidades de los Esquemas de Mercedes-Benz</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Mercedes estructura sus esquemas mediante arquitectura de módulos SAM y códigos de letra estandarizados:
          </p>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem;">
            <li><strong>Letras de Componentes:</strong> <code>N</code> = Unidades de control / calculadores electrónicos (ej. N10/1 SAM delantero, N73 clausor EZS). <code>W</code> = Puntos de masa atornillados al chasis (ej. W10 masa de batería, W19 salpicadero). <code>K</code> = Relés. <code>F</code> = Fusibles. <code>X</code> = Conectores. <code>M</code> = Motores y actuadores.</li>
            <li><strong>Designación de Vías y Conectores:</strong> Los conectores llevan letra y número (ej. Conector A, vía 14). Los empalmes internos de mazos se indican con fracciones cuadradas como <code>27/35z2</code>.</li>
            <li><strong>Redes Multiplexadas:</strong> Identificadas como <code>CAN-BH</code> (Bus CAN de habitáculo - alta) y <code>CAN-BL</code> (Bus CAN de habitáculo - baja).</li>
          </ul>
        </div>
        """, "Mercedes-Benz"),
        create_image_section("images/ford_esquema_nomenclatura.jpg", "Esquema eléctrico de Ford mostrando la nomenclatura de cables, conectores C, empalmes S y masas G", "Particularidades de Esquemas Ford (Nomenclatura y Cuadrícula)", 676, 718),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-car"></i> FABRICANTE 2 · FORD</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">Particularidades de los Esquemas de Ford</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Ford utiliza un sistema de cuadrícula con celdas y una fórmula de designación de cables muy estructurada:
          </p>
          <div class="tech-table-wrap">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Ejemplo de Cable Ford</th>
                  <th>Segmento del Código</th>
                  <th>Significado Técnico</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td rowspan="4"><code>91-PG30A.75BK/WH</code></td>
                  <td><strong>91</strong></td>
                  <td>Número del circuito eléctrico principal.</td>
                </tr>
                <tr>
                  <td><strong>PG</strong></td>
                  <td>Código de función del circuito (PG = Señal de velocidad del vehículo y régimen de motor).</td>
                </tr>
                <tr>
                  <td><strong>.75</strong></td>
                  <td>Sección transversal del conductor en mm² (0.75 mm²).</td>
                </tr>
                <tr>
                  <td><strong>BK/WH</strong></td>
                  <td>Color base <strong>Negro (BK)</strong> con traza longitudinal de color <strong>Blanco (WH)</strong>.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem; margin-top:0.8rem;">
            <li><strong>Letras de Conexión:</strong> <code>C</code> = Conectores (ej. C202, C190). <code>S</code> = Empalmes soldados (*Splices*, ej. S64, S4). <code>G</code> = Masas de carrocería (*Ground*, ej. G25, G1001). <code>P</code> = Cajas de distribución de potencia (ej. P91 BJB).</li>
            <li><strong>Cajas de Unión:</strong> <em>BJB</em> (Battery Junction Box en vano motor) y <em>CJB / GEM</em> (Central Junction Box en habitáculo).</li>
          </ul>
        </div>
        """, "Ford"),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-diamond"></i> FABRICANTE 3 · RENAULT</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">Particularidades de los Esquemas de Renault</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Renault prescinde de letras para componentes y utiliza un <strong>código numérico universal de 3 o 4 dígitos</strong>:
          </p>
          <div class="tech-table-wrap">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Código Renault</th>
                  <th>Componente Asignado</th>
                  <th>Código Renault</th>
                  <th>Componente Asignado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>120</strong></td>
                  <td>Calculador de inyección de motor</td>
                  <td><strong>103</strong></td>
                  <td>Alternador</td>
                </tr>
                <tr>
                  <td><strong>645</strong></td>
                  <td>Calculador del habitáculo (UCH)</td>
                  <td><strong>104</strong></td>
                  <td>Contactor de arranque (Clausor)</td>
                </tr>
                <tr>
                  <td><strong>597</strong></td>
                  <td>Caja de fusibles y relés del motor (UPC)</td>
                  <td><strong>107</strong></td>
                  <td>Batería</td>
                </tr>
                <tr>
                  <td><strong>260 / 1016</strong></td>
                  <td>Caja de fusibles del habitáculo</td>
                  <td><strong>163</strong></td>
                  <td>Motor de arranque</td>
                </tr>
              </tbody>
            </table>
          </div>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem; margin-top:0.8rem;">
            <li><strong>Conectores Modulares UCH:</strong> Denominados <code>PE</code> (Pequeña electrónica) y <code>PP</code> (Potencia), identificados visualmente por colores: <code>BA</code> (Blanco), <code>GR</code> (Gris) y <code>NO</code> (Negro).</li>
            <li><strong>Prefijos de Alimentación:</strong> <code>BP</code> = Positivo protegido tras fusible. <code>AP</code> = Positivo accesorio tras llave de contacto. <code>M</code> = Masa.</li>
          </ul>
        </div>
        """, "Renault"),
        create_image_section("images/bmw_esquema_luneta.jpg", "Esquema de luneta térmica de BMW mostrando relé K13, fusible F46 y conectores X", "Particularidades de Esquemas BMW (Sistema ISTA/WDS)", 676, 545),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-dashboard"></i> FABRICANTE 4 · BMW</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">Particularidades de los Esquemas de BMW</h3>
          <p style="color:#1e293b; line-height:1.6;">
            BMW utiliza los sistemas ISTA y WDS con una rigurosa codificación alemana de conectores y señales:
          </p>
          <ul style="color:#1e293b; line-height:1.7; padding-left:1.2rem;">
            <li><strong>Conectores con la Letra X:</strong> Todos los conectores llevan la letra <code>X</code> seguida de 4 a 6 dígitos (ej. <code>X11004</code> conector de relé, <code>X18284</code> conector de luneta, <code>X608</code> conector de climatizador).</li>
            <li><strong>Colores de Cables en Alemán:</strong> <code>BR</code> = Braun (Marrón, SIEMPRE masa), <code>RT</code> = Rot (Rojo, SIEMPRE positivo 30), <code>SW</code> = Schwarz (Negro), <code>BL</code> = Blau (Azul), <code>GE</code> = Gelb (Amarillo), <code>WS</code> = Weiß (Blanco). Bicolores: <code>WS/GE</code> (Blanco con traza amarilla para bus K_CAN_H).</li>
            <li><strong>Señales Específicas:</strong> <code>30&lt;46</code> = Terminal 30 alimentado a través del fusible 46. <code>31L</code> = Retorno de masa de circuitos de carga.</li>
          </ul>
        </div>
        """, "BMW"),
        create_simulation_box(
            title="Vídeo Práctico: ¿Cómo Leer Esquemas de Centralitas de Motor? (Parte 2)",
            desc_html="Continúa la formación con el análisis avanzado de PetrolheadGarage sobre pines de ECU, sensores y actuadores en esquemas de fabricantes.",
            button_text="Ver Clase en YouTube (PetrolheadGarage)",
            url="https://www.youtube.com/watch?v=bNECe8JhzJQ"
        )
    ]

    phase3 = [
        create_checkpoint_section(
            title="Síntesis Comparativa Multimarca",
            intro_html="Consulta este desplegable para traducir rápidamente términos entre los cuatro fabricantes estudiados."
        ),
        create_accordion([
            ("Tabla de Equivalencias de Unidades Centrales", """
            <p><strong>Mercedes-Benz:</strong> Módulo SAM (Signal Acquisition and Actuation Module, N10/1).</p>
            <p><strong>Ford:</strong> Módulo GEM / BCM (Generic Electronic Module / Body Control Module) y CJB.</p>
            <p><strong>Renault:</strong> Módulo UCH (Unidad Central de Habitáculo, código 645) y UPC (código 597).</p>
            <p><strong>BMW:</strong> Módulo FEM (Front Electronic Module) / BDC (Body Domain Controller) / Gateway A4010.</p>
            """),
            ("Tabla de Equivalencias de Designación de Masas", """
            <p><strong>Mercedes-Benz:</strong> Letra W seguida de número (ej. W10, W28/1). Cable marrón (BN).</p>
            <p><strong>Ford:</strong> Letra G (Ground, ej. G25, G1001). Cable negro o negro/color.</p>
            <p><strong>Renault:</strong> Código alfanumérico (ej. MAM masa salpicadero) o prefijo M. Cable negro (NO).</p>
            <p><strong>BMW:</strong> Borne 31 o terminales X con retorno a chasis. Cable marrón (BR).</p>
            """),
            ("Regla de Colores de Masa vs Positivo en Marcas Alemanas", """
            <p>En Mercedes-Benz y BMW (norma alemana DIN):</p>
            <ul>
              <li><strong>MARRÓN (BN / BR):</strong> SIEMPRE es masa (0 V, borne 31).</li>
              <li><strong>ROJO (RD / RT):</strong> SIEMPRE es positivo permanente (12 V, borne 30).</li>
              <li>¡Nunca asumas que el negro (BK/SW) es masa en un vehículo alemán, pues suele ser positivo de contacto o señal!</li>
            </ul>
            """)
        ], "Guía Rápida de Traducción Multimarca"),
        create_drag_text_activity(
            task_desc="Arrastra cada código o término técnico al fabricante automovilístico correspondiente:",
            text_template="En los esquemas de *Mercedes-Benz*, la letra W designa los puntos de masa y N las centralitas. En los esquemas de *Ford*, el código 91-PG30A.75BK/WH indica sección y colores en cuadrícula con masas designadas por la letra G. En los esquemas de *Renault*, el número 120 identifica la UCE de inyección y el 645 la unidad de habitáculo UCH. En los esquemas de *BMW*, todos los conectores se designan con la letra X y el cable marrón (BR) es siempre la masa.",
            distractors=["Grupo VAG", "Toyota"],
            title="Práctica Guiada: Identificación Multimarca"
        )
    ]

    phase4 = [
        create_multichoice_question(
            question_html="En el esquema de un Ford Fiesta observas el cable marcado como <strong>15-DA2 .35 GN/BU</strong>. ¿Cómo se interpreta correctamente este conductor?",
            answers=[
                ("Cable del circuito 15-DA2, con sección de 0.35 mm², color base verde (GN) y traza azul (BU).", True, "Aplica el patrón de codificación de conductores de Ford.", "¡Correcto! En Ford: prefijo = número y función de circuito (15-DA2), decimal = sección en mm² (.35 = 0.35 mm²), primer color = verde dominante (GN), segundo color tras la barra = traza azul (BU)."),
                ("Cable alimentado por el borne 15 de 15 Amperios, calibre 35 AWG, color gris/blanco.", False, "Revisa la abreviatura GN y BU en inglés.", "Incorrecto. .35 representa 0.35 mm² de sección métrica, y GN/BU corresponde a Green/Blue (Verde/Azul)."),
                ("Cable de masa directa con fusible de 35 A y aislamiento ignífugo.", False, "Recuerda que en Ford la masa se designa con G.", "Incorrecto. Las masas en Ford se indican con G y color negro (BK).")
            ],
            title="Autocomprobación 4.1: Decodificación de Cables Ford"
        ),
        create_multichoice_question(
            question_html="En la documentación de un Renault Clio, el esquema indica que la señal del sensor de PMS llega al <strong>componente 120</strong> desde el <strong>conector R107</strong>. ¿A qué componente físico se refiere el número 120?",
            answers=[
                ("Al calculador electrónico de inyección de motor (UCE).", True, "Consulta la tabla de códigos universales de Renault.", "¡Exacto! El código 120 es la designación numérica universal de Renault para la centralita de inyección del motor (mientras que 645 es la UCH y 597 la UPC)."),
                ("Al motor de arranque.", False, "El motor de arranque tiene el código 163.", "Incorrecto. El motor de arranque en Renault se designa con el código 163 (y el alternador con el 103)."),
                ("A la batería del vehículo.", False, "La batería tiene el código 107.", "Incorrecto. La batería en los esquemas de Renault tiene asignado el código 107.")
            ],
            title="Autocomprobación 4.2: Códigos Numéricos Renault"
        ),
        create_true_false_question(
            question_html="En un esquema de BMW (sistema ISTA), ¿un cable de color <strong>SW (Schwarz)</strong> corresponde obligatoriamente a la masa de carrocería como ocurre en el cableado doméstico?",
            is_correct=False,
            title="Autocomprobación 4.3: Regla Alemana de Masa",
            feedback_correct="¡Correcto! Falso. En la norma alemana (BMW, Mercedes-Benz, VAG), la masa es SIEMPRE el color marrón (BR / Braun). El color negro (SW / Schwarz) se utiliza para positivos de contacto (borne 15) o líneas de mando.",
            feedback_wrong="Incorrecto. En los vehículos alemanes, conectar un cable negro (SW) a masa creará un cortocircuito mortal para la instalación. La masa en Alemania es SIEMPRE marrón (BR / Braun)."
        )
    ]

    return create_didactic_sequence_chapter(
        "Unidad 4: Estudio de Esquemas Eléctricos por Fabricantes",
        phase1, phase2, phase3, phase4
    )


# =========================================================================
# 3. COMPILADOR Y EMPAQUETADOR MAESTRO DEL ARCHIVO .H5P
# =========================================================================

def build_h5p_course(output_path):
    """Compila y empaqueta el curso H5P completo."""
    build_dir = os.path.join(SCRIPT_DIR, '_build_temp')
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    content_dir = os.path.join(build_dir, 'content')
    images_dir = os.path.join(content_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    print(f"📦 Compilando curso H5P en: {output_path}")

    # 1. Copiar librerías homologadas
    print(f"📁 Copiando 16 librerías base desde: {LIB_DIR}")
    for dep in HOMOLOGATED_DEPENDENCIES:
        folder_name = f"{dep['machineName']}-{dep['majorVersion']}.{dep['minorVersion']}"
        src_path = os.path.join(LIB_DIR, folder_name)
        dst_path = os.path.join(build_dir, folder_name)
        if os.path.exists(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            raise FileNotFoundError(f"Librería requerida no encontrada: {src_path}")

    # 2. Copiar logo institucional
    logo = resolve_institutional_logo()
    if logo.get("src_path") and os.path.exists(logo["src_path"]):
        shutil.copy2(logo["src_path"], os.path.join(images_dir, logo["filename"]))
        print(f"✓ Logotipo institucional empaquetado: {logo['filename']} ({logo['width']}x{logo['height']} px, {logo['mime']})")
    else:
        print("⚠️ Aviso: No se encontró archivo de logotipo.")

    # 3. Copiar imágenes técnicas del curso
    course_images_dir = os.path.join(SCRIPT_DIR, 'images')
    if os.path.exists(course_images_dir):
        for img_file in os.listdir(course_images_dir):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src_img = os.path.join(course_images_dir, img_file)
                dst_img = os.path.join(images_dir, img_file)
                shutil.copy2(src_img, dst_img)
                print(f"✓ Imagen técnica empaquetada: content/images/{img_file}")

    # 4. Construir los 4 capítulos didácticos
    print("🔨 Ensamblando los 4 capítulos con andamiaje pedagógico...")
    chapters = [
        build_chapter_1(),
        build_chapter_2(),
        build_chapter_3(),
        build_chapter_4()
    ]

    # 5. Generar content/content.json
    content_data = {
        "showCoverPage": True,
        "bookCover": {
            "coverTitle": "Interpretación y Diagnosis de Esquemas Eléctricos del Automóvil",
            "coverDescription": "Curso Técnico Interactivo para Formación Profesional (CFGM Electromecánica y CFGS Automoción). Dominio de esquemas unifilares y de situación, arquitectura de redes multiplexadas, simbología DIN 72552 y manuales multimarca (Mercedes-Benz, Ford, Renault y BMW). Incluye andamiaje en 4 fases, retos de taller y autocomprobación activa.",
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
                    "alt": "Portada Oficial EducaMadrid - Formación Profesional de Automoción"
                },
                "library": "H5P.Image 1.1",
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "contentType": "Image",
                    "license": "CC BY-SA",
                    "title": "Portada Institucional EducaMadrid"
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

    # 6. Generar h5p.json
    h5p_manifest = {
        "title": "Interpretación y Diagnosis de Esquemas Eléctricos del Automóvil",
        "language": "es",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["iframe"],
        "license": "CC BY-SA",
        "preloadedDependencies": HOMOLOGATED_DEPENDENCIES,
        "authors": [{"name": "Departamento de Formación Profesional - Automoción", "role": "Author"}]
    }

    with open(os.path.join(build_dir, 'h5p.json'), 'w', encoding='utf-8') as f:
        json.dump(h5p_manifest, f, ensure_ascii=False, indent=2)

    # 7. Empaquetar archivo ZIP .h5p
    if os.path.exists(output_path):
        os.remove(output_path)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, build_dir)
                zipf.write(abs_path, rel_path)

    shutil.rmtree(build_dir)
    pkg_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Paquete H5P generado con éxito: {output_path} ({pkg_size_mb:.2f} MB)")

    # 8. Certificación oficial con validador de EducaMadrid
    try:
        from validar_h5p import validate_h5p
        validate_h5p(output_path)
    except ImportError:
        try:
            from validar_h5p_educamadrid import validate_h5p
            validate_h5p(output_path)
        except ImportError:
            import importlib.util
            for val_dir in [PLANTILLA_DIR, SCRIPT_DIR, os.path.join(PROJECT_ROOT, '.agents', 'skills', 'h5p-educamadrid', 'scripts')]:
                for v_name in ['validar_h5p.py', 'validar_h5p_educamadrid.py']:
                    v_path = os.path.join(val_dir, v_name)
                    if os.path.exists(v_path):
                        spec = importlib.util.spec_from_file_location("val_mod", v_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        mod.validate_h5p(output_path)
                        break

def generar_evaluacion_esquemas_xml(output_xml_path):
    """Genera y valida el banco oficial de preguntas Moodle XML de Esquemas Eléctricos del Automóvil."""
    try:
        from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
    except ImportError:
        sys.path.insert(0, PLANTILLA_DIR)
        from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml

    builder = MoodleXMLBuilder("Esquemas Electricos del Automovil - Evaluacion Sumativa Oficial")

    # 1. Metodología deductiva
    builder.add_multichoice(
        "EE_P01_Metodologia_Cuatro_Estados",
        "<p>Durante la diagnosis eléctrica de un circuito de inyección o alumbrado, ¿cuáles son los cuatro estados fundamentales que puede presentar un conductor o componente?</p>",
        [
            {
                "text": "Circuito abierto, cortocircuito a masa, cortocircuito a positivo y caída de tensión por resistencia indebida.",
                "fraction": 100,
                "feedback": "¡Correcto! Cualquier avería eléctrica automotriz se clasifica rigurosamente en uno de estos 4 estados para deducir la causa raíz."
            },
            {
                "text": "Circuito en corriente continua pura, circuito alterno rectificado, circuito mixto serie-paralelo y circuito trifásico del alternador.",
                "fraction": 0,
                "feedback": "Incorrecto. Esos son tipos de corriente o topologías de red, no estados de diagnóstico de averías."
            },
            {
                "text": "Circuito cerrado funcional, fusible de protección fundido por sobrecarga térmica, relé excitado y batería con densidad química baja.",
                "fraction": 0,
                "feedback": "Incorrecto. Esos son síntomas o condiciones puntuales de componentes, no la clasificación analítica de un circuito."
            },
            {
                "text": "Resistencia de aislamiento baja, resistencia de contacto media, resistencia de carga nominal y circuito abierto con valor infinito.",
                "fraction": 0,
                "feedback": "Incorrecto. No distingue entre fallos a masa, cortocircuitos a positivo o caídas de tensión bajo carga."
            }
        ],
        general_feedback="<p>La metodología de los 4 estados es la base del diagnóstico técnico sin sustitución empírica de piezas.</p>"
    )

    # 2. Caída de tensión admisible
    builder.add_multichoice(
        "EE_P02_Caida_Tension_Admisible",
        "<p>En una línea de potencia de automoción (alimentación de bombas o relés), ¿cuál es la caída de tensión parásita máxima admisible bajo carga real de trabajo?</p>",
        [
            {
                "text": "Menor o igual a 0.2 V (o máximo 0.5 V en arranque).",
                "fraction": 100,
                "feedback": "¡Correcto! Una caída de tensión mayor a 0.2 V en cables de alimentación o masa revela corrosión, terminal flojo o sulfatación en empalmes."
            },
            {
                "text": "Entre 1.5 V y 3.0 V en cualquier línea de alimentación protegida por fusible estándar.",
                "fraction": 0,
                "feedback": "Incorrecto. Una caída de 1.5 V a 3 V provocaría mal funcionamiento de calculadores o pérdida de potencia en actuadores."
            },
            {
                "text": "Exactamente 0.000 V independientemente de la longitud del cable o la corriente de carga.",
                "fraction": 0,
                "feedback": "Incorrecto. Todo conductor real de cobre presenta una mínima resistencia óhmica (R = ρ·L/S)."
            },
            {
                "text": "Hasta un 50% de la tensión nominal de la batería medida en vacío con motor detenido.",
                "fraction": 0,
                "feedback": "Incorrecto. Eso equivaldría a dejar el componente con solo 6 V, inutilizándolo."
            }
        ],
        general_feedback="<p>Vcaída = I × R. Debe medirse siempre en circuito cerrado con los consumidores encendidos.</p>"
    )

    # 3. Back-probing
    builder.add_multichoice(
        "EE_P03_Tecnica_Back_Probing",
        "<p>¿Cuál es la técnica reglamentaria y segura para medir tensiones o señales con multímetro/osciloscopio en un conector sin dañar el cableado?</p>",
        [
            {
                "text": "Técnica de agujas traseras (back-probing) insertadas por el retén de goma posterior.",
                "fraction": 100,
                "feedback": "¡Correcto! Perforar el aislante con pinzas cocodrilo o alfileres destruye la estanqueidad, permitiendo la entrada de humedad que oxida el cobre internamente."
            },
            {
                "text": "Perforar el aislante de PVC del cable con pinzas de cocodrilo afiladas para hacer contacto directo.",
                "fraction": 0,
                "feedback": "Incorrecto. Esta práctica provoca corrosión galvánica verde oculta (*cobre sulfatado*) con averías intermitentes graves."
            },
            {
                "text": "Seccionar transversalmente el conductor para medir en el extremo pelado y empalmar con cinta aislante.",
                "fraction": 0,
                "feedback": "Incorrecto. Rompe la integridad del mazo y altera las secciones y apantallamientos de la red CAN."
            },
            {
                "text": "Desconectar el mazo de cables del calculador con el motor en marcha y medir directamente en las clavijas.",
                "fraction": 0,
                "feedback": "Incorrecto. Desconectar una ECU bajo tensión genera picos inductivos que pueden quemar sus etapas de potencia."
            }
        ],
        general_feedback="<p>El back-probing con agujas flexibles preserva la estanqueidad de los conectores modulares de automoción.</p>"
    )

    # 4. Borne 30 DIN 72552
    builder.add_multichoice(
        "EE_P04_Borne_30_DIN",
        "<p>Según la norma DIN 72552 de codificación de bornes en el automóvil, ¿qué indica el Borne 30?</p>",
        [
            {
                "text": "Alimentación positiva permanente directa de batería (+Bat).",
                "fraction": 100,
                "feedback": "¡Correcto! El Borne 30 mantiene alimentados componentes que requieren memoria permanente (ECU, reloj, cierres o alarmas)."
            },
            {
                "text": "Línea de retorno a masa del chasis conectada al polo negativo de la batería del vehículo.",
                "fraction": 0,
                "feedback": "Incorrecto. La masa del chasis según DIN 72552 es el Borne 31."
            },
            {
                "text": "Positivo bajo llave de contacto que solo suministra corriente en posición de encendido.",
                "fraction": 0,
                "feedback": "Incorrecto. El positivo tras llave de contacto es el Borne 15."
            },
            {
                "text": "Línea de excitación temporal que activa el solenoide del motor de arranque al girar la llave.",
                "fraction": 0,
                "feedback": "Incorrecto. El mando de activación del arranque es el Borne 50."
            }
        ],
        general_feedback="<p>Borne 30 = Positivo directo batería. En esquemas alemanes suele ser de color rojo (RT).</p>"
    )

    # 5. Borne 15 DIN 72552
    builder.add_multichoice(
        "EE_P05_Borne_15_DIN",
        "<p>¿Qué función cumple la línea señalizada como Borne 15 en los esquemas eléctricos normalizados?</p>",
        [
            {
                "text": "Positivo conmutado tras llave de contacto (ignición activada).",
                "fraction": 100,
                "feedback": "¡Correcto! El Borne 15 solo suministra 12 V cuando la llave está en posición de contacto/marcha (KL 15)."
            },
            {
                "text": "Alimentación positiva permanente directa desde el borne positivo de la batería sin fusible previo.",
                "fraction": 0,
                "feedback": "Incorrecto. Ese es el Borne 30."
            },
            {
                "text": "Retorno de masa general hacia el borne negativo de batería y a los puntos estructurales del chasis.",
                "fraction": 0,
                "feedback": "Incorrecto. La masa es el Borne 31."
            },
            {
                "text": "Línea de alta tensión secundaria generada por la bobina de encendido hacia las bujías del motor.",
                "fraction": 0,
                "feedback": "Incorrecto. Las líneas de alta tensión se identifican como 4 o 4a en bobinas clásicas."
            }
        ],
        general_feedback="<p>Borne 15 = Positivo conmutado (+15). En esquemas alemanes suele ser negro (SW) o amarillo/negro.</p>"
    )

    # 6. Borne 31 DIN 72552
    builder.add_multichoice(
        "EE_P06_Borne_31_DIN",
        "<p>¿Qué representa el Borne 31 en la normalización internacional de esquemas eléctricos?</p>",
        [
            {
                "text": "Línea de retorno a masa conectada al polo negativo y al chasis.",
                "fraction": 100,
                "feedback": "¡Correcto! El Borne 31 cierra el circuito de todos los consumidores de vuelta al polo negativo."
            },
            {
                "text": "Tensión de carga rectificada suministrada por el alternador hacia la batería del automóvil.",
                "fraction": 0,
                "feedback": "Incorrecto. El solenoide de arranque es el Borne 50."
            },
            {
                "text": "Salida conmutada de potencia del relé para alimentar faros de carretera y luneta térmica.",
                "fraction": 0,
                "feedback": "Incorrecto. Las salidas de relé son los bornes 87 u 87a."
            },
            {
                "text": "Línea de excitación positiva enviada al solenoide del motor de arranque durante el encendido.",
                "fraction": 0,
                "feedback": "Incorrecto. La salida del alternador a batería es B+ o Borne 30."
            }
        ],
        general_feedback="<p>Borne 31 = Retorno a masa. En fabricantes alemanes siempre se identifica con color marrón (BR).</p>"
    )

    # 7. Borne 50 DIN 72552
    builder.add_multichoice(
        "EE_P07_Borne_50_DIN",
        "<p>Al girar la llave de contacto a la posición START (arranque), ¿qué borne DIN recibe alimentación temporal de excitación?</p>",
        [
            {
                "text": "Borne 50 (excita el solenoide de arranque durante el giro de llave).",
                "fraction": 100,
                "feedback": "¡Correcto! El Borne 50 solo tiene 12 V durante los segundos en que se acciona el arranque."
            },
            {
                "text": "Borne 30, suministrando corriente permanente ininterrumpida directamente desde la batería.",
                "fraction": 0,
                "feedback": "Incorrecto. El Borne 30 es permanente y siempre tiene 12 V."
            },
            {
                "text": "Borne 31, cerrando el circuito de masa exclusivo para el motor eléctrico del motor de arranque.",
                "fraction": 0,
                "feedback": "Incorrecto. Borne 31 es masa permanente."
            },
            {
                "text": "Borne X / 75, derivando corriente auxiliar a los accesorios de confort durante la fase de arranque.",
                "fraction": 0,
                "feedback": "Incorrecto. El Borne X precisamente se desconecta durante el arranque para reservar batería."
            }
        ],
        general_feedback="<p>Borne 50 = Mando de arranque activado por clausor o por relé gobernado por la ECU.</p>"
    )

    # 8. Borne X / 75
    builder.add_multichoice(
        "EE_P08_Borne_X_Accesorios",
        "<p>¿Qué comportamiento característico tiene la línea de Borne X (o borne 75) en los vehículos modernos?</p>",
        [
            {
                "text": "Alimenta accesorios y se desconecta en el arranque para reservar batería.",
                "fraction": 100,
                "feedback": "¡Correcto! El relé de descarga de contacto X apaga elementos pesados para que el motor de arranque disponga del 100% de la energía disponible en la batería."
            },
            {
                "text": "Permanece conectado de forma continua incluso con la llave de contacto retirada del vehículo.",
                "fraction": 0,
                "feedback": "Incorrecto. Eso descargaría la batería rápidamente."
            },
            {
                "text": "Suministra alimentación auxiliar exclusivamente cuando el vehículo supera los 50 km/h de velocidad.",
                "fraction": 0,
                "feedback": "Incorrecto. Es un circuito eléctrico de confort gestionado por llave o calculador de carrocería."
            },
            {
                "text": "Constituye el canal principal de comunicación digital multiplexada para las centralitas del bus CAN.",
                "fraction": 0,
                "feedback": "Incorrecto. El bus CAN utiliza líneas de par trenzado CAN-H y CAN-L, no Borne X."
            }
        ],
        general_feedback="<p>Borne X / 75 = Línea de accesorios con descarga en arranque.</p>"
    )

    # 9. Relé 85 y 86
    builder.add_multichoice(
        "EE_P09_Rele_Bornes_Control",
        "<p>En un relé electromagnético automotriz estándar de 4 o 5 patillas, ¿qué bornes corresponden a los extremos de la bobina de excitación?</p>",
        [
            {
                "text": "Bornes 85 y 86.",
                "fraction": 100,
                "feedback": "¡Correcto! Los bornes 85 y 86 alimentan el electroimán interno que desplaza el inducido móvil de potencia."
            },
            {
                "text": "Bornes 30 y 87.",
                "fraction": 0,
                "feedback": "Incorrecto. 30 y 87 son los contactos del circuito de potencia (alta corriente)."
            },
            {
                "text": "Bornes 15 y 31.",
                "fraction": 0,
                "feedback": "Incorrecto. Son bornes de alimentación del vehículo, no las designaciones de las patillas del relé."
            },
            {
                "text": "Bornes 87 y 87a.",
                "fraction": 0,
                "feedback": "Incorrecto. Son las salidas normalmente abierta (NO) y normalmente cerrada (NC) del contacto de potencia."
            }
        ],
        general_feedback="<p>85 (generalmente masa o mando por transistor) y 86 (positivo de mando).</p>"
    )

    # 10. Relé 30 y 87
    builder.add_multichoice(
        "EE_P10_Rele_Bornes_Potencia",
        "<p>¿Qué bornes de un relé normalizado DIN conectan el circuito de potencia que alimenta directamente a los consumidores (faros, bomba de combustible, luneta térmica)?</p>",
        [
            {
                "text": "Borne 30 (entrada de potencia) y Borne 87 (salida al consumidor).",
                "fraction": 100,
                "feedback": "¡Correcto! El contacto 30-87 soporta intensidades de 20 A a 40 A, conmutadas por la débil corriente de la bobina (aprox. 150-200 mA)."
            },
            {
                "text": "Bornes 85 y 86, que forman el circuito de control de baja intensidad de la bobina electromagnética.",
                "fraction": 0,
                "feedback": "Incorrecto. Son los bornes de la bobina de control."
            },
            {
                "text": "Bornes 50 y 31, que comunican directamente el solenoide del motor de arranque con la masa del chasis.",
                "fraction": 0,
                "feedback": "Incorrecto. 50 es arranque y 31 es masa."
            },
            {
                "text": "Bornes 15 y 85, que enlazan el positivo de contacto con el transistor de conmutación de la centralita.",
                "fraction": 0,
                "feedback": "Incorrecto. No forman un par de conmutación de potencia."
            }
        ],
        general_feedback="<p>30 = Entrada potencia / 87 = Salida normalmente abierta hacia consumidor.</p>"
    )

    # 11. Diodo supresor en relés
    builder.add_multichoice(
        "EE_P11_Diodo_Supresor_Transitorios",
        "<p>¿Cuál es la finalidad de instalar un diodo supresor de transitorios en paralelo inverso entre los bornes 85 y 86 de la bobina de un relé?</p>",
        [
            {
                "text": "Neutralizar el pico de alta tensión inductiva al desconectar la bobina.",
                "fraction": 100,
                "feedback": "¡Correcto! Al cortar la corriente en un inductor, la tensión puede elevarse bruscamente a 70-100 V con polaridad invertida. El diodo la deriva en bucle seguro."
            },
            {
                "text": "Aumentar la velocidad de giro y el par mecánico del motor de arranque durante el encendido del motor.",
                "fraction": 0,
                "feedback": "Incorrecto. No tiene relación con el par del motor de arranque."
            },
            {
                "text": "Evitar que la bobina consuma corriente eléctrica cuando el relé se encuentra plenamente activado.",
                "fraction": 0,
                "feedback": "Incorrecto. La bobina sigue consumiendo corriente según la ley de Ohm (I = V/R)."
            },
            {
                "text": "Permitir la conexión accidental del relé con polaridad invertida sin causar daños al bobinado interno.",
                "fraction": 0,
                "feedback": "Incorrecto. Al revés: si se invierte la polaridad con diodo, se provoca un cortocircuito directo que quema el fusible o el transistor."
            }
        ],
        general_feedback="<p>El diodo supresor es vital cuando los relés son excitados por módulos electrónicos (BCM, ECU, SAM).</p>"
    )

    # 12. Colorimetría alemana
    builder.add_multichoice(
        "EE_P12_Colorimetria_Alemana",
        "<p>En la documentación técnica de fabricantes alemanes (Grupo VAG, BMW, Mercedes-Benz, Porsche), ¿qué significado tienen los colores de cable MARRÓN (BR / Braun) y ROJO (RT / Rot)?</p>",
        [
            {
                "text": "MARRÓN es masa (Borne 31) y ROJO es positivo permanente (Borne 30).",
                "fraction": 100,
                "feedback": "¡Correcto! Es una regla invariable en el esquema alemán: Brown (BR) = Masa / Rot (RT) = Positivo (+30)."
            },
            {
                "text": "MARRÓN es positivo conmutado bajo llave y ROJO es línea de masa conectada directamente al chasis.",
                "fraction": 0,
                "feedback": "Incorrecto. ¡Peligro de cortocircuito! Nunca confundir la norma alemana donde el marrón es masa directa."
            },
            {
                "text": "MARRÓN es señal analógica de sensor y ROJO es canal de audio para los altavoces del habitáculo.",
                "fraction": 0,
                "feedback": "Incorrecto. Son las dos líneas maestras de potencia del vehículo."
            },
            {
                "text": "Ambos colores se alternan de forma indistinta según la serie y año de fabricación del fabricante.",
                "fraction": 0,
                "feedback": "Incorrecto. La colorimetría alemana sigue una estricta normalización DIN."
            }
        ],
        general_feedback="<p>Marrón (BR) = Borne 31 (Masa). Rojo (RT) = Borne 30 (+ permanente).</p>"
    )

    # 13. Mercedes-Benz SAM
    builder.add_multichoice(
        "EE_P13_Mercedes_Modulos_SAM",
        "<p>En los esquemas de Mercedes-Benz, ¿qué designación reciben las cajas de fusibles y módulos inteligentes de adquisición de señales, y qué letra identifica los puntos de masa?</p>",
        [
            {
                "text": "Módulos SAM (N10/1, N10/2) y la letra 'W' para masas de carrocería.",
                "fraction": 100,
                "feedback": "¡Correcto! N = Módulos de control / W = Conexiones de masa de chasis en la nomenclatura Mercedes-Benz."
            },
            {
                "text": "Módulos UCH para el habitáculo del vehículo y la letra 'M' para identificar las tomas de masa.",
                "fraction": 0,
                "feedback": "Incorrecto. UCH es la denominación exclusiva de Renault."
            },
            {
                "text": "Módulos BCM para las luces y carrocería y la letra 'G' para señalizar los puntos de toma a masa.",
                "fraction": 0,
                "feedback": "Incorrecto. La letra 'G' para masas corresponde a Ford."
            },
            {
                "text": "Módulos BSI con arquitectura multiplexada y la letra 'E' para definir las conexiones a carrocería.",
                "fraction": 0,
                "feedback": "Incorrecto. BSI es la arquitectura del grupo Stellantis / PSA."
            }
        ],
        general_feedback="<p>Mercedes: SAM (Signal Acquisition Module), N = calculadores, W = masas, X = conectores.</p>"
    )

    # 14. Ford Nomenclatura
    builder.add_multichoice(
        "EE_P14_Ford_Nomenclatura_Circuitos",
        "<p>En un esquema unifilar de Ford, en el código de cable '91-PG30A 0.75 BK/WH', ¿qué indican '0.75' y 'BK/WH'?</p>",
        [
            {
                "text": "0.75 mm² de sección de cobre; color base NEGRO (BK) y traza BLANCA (WH).",
                "fraction": 100,
                "feedback": "¡Correcto! En Ford la primera sigla es el color predominante del cable y la segunda es la línea de traza identificativa."
            },
            {
                "text": "0.75 amperios de intensidad máxima admisible y aislamiento monocromático de color blanco puro.",
                "fraction": 0,
                "feedback": "Incorrecto. 0.75 es la sección transversal del hilo conductor en milímetros cuadrados."
            },
            {
                "text": "0.75 voltios de caída de tensión teórica y cable con apantallamiento trenzado contra parásitos.",
                "fraction": 0,
                "feedback": "Incorrecto. BK/WH representa Black/White en inglés internacional."
            },
            {
                "text": "0.75 metros de longitud geométrica de cableado desde el conector hasta el punto de empalme.",
                "fraction": 0,
                "feedback": "Incorrecto. Los esquemas no indican la longitud física del cable sino su calibre geométrico."
            }
        ],
        general_feedback="<p>Sección en mm² + Código de color en inglés internacional (BK=Black, WH=White, RD=Red, etc.).</p>"
    )

    # 15. Renault Sistema Numérico
    builder.add_multichoice(
        "EE_P15_Renault_Sistema_Numerico",
        "<p>¿Cuál es la particularidad del sistema de numeración universal de componentes en los esquemas eléctricos de Renault?</p>",
        [
            {
                "text": "Cada componente técnico tiene un número universal fijo (120=inyección, 645=UCH).",
                "fraction": 100,
                "feedback": "¡Correcto! En Renault no importa el modelo de vehículo (Clio, Megane, Master); el número 120 siempre identifica el calculador de motor."
            },
            {
                "text": "Los números se asignan por orden aleatorio de montaje según la secuencia en la cadena de producción.",
                "fraction": 0,
                "feedback": "Incorrecto. Renault utiliza una enciclopedia numérica universal fija."
            },
            {
                "text": "Cada número indica la tensión máxima en voltios que tolera el aislamiento del componente en trabajo.",
                "fraction": 0,
                "feedback": "Incorrecto. Son códigos unívocos de identificación topográfica."
            },
            {
                "text": "Solo se numeran los fusibles de la caja de fusibles, designándose el resto con nombres en francés.",
                "fraction": 0,
                "feedback": "Incorrecto. Todos los calculadores, motores y sensores poseen código numérico estándar."
            }
        ],
        general_feedback="<p>Renault: 120 = Inyección, 645 = UCH (habitáculo), 597 = UPC (motor), 103 = Alternador.</p>"
    )

    # 16. Renault Colores Conectores
    builder.add_multichoice(
        "EE_P16_Renault_Conectores_Colores",
        "<p>En la documentación técnica de Renault, ¿qué indican las abreviaturas 'BA', 'GR', 'NO' y 'MR' al lado de un conector modular?</p>",
        [
            {
                "text": "El color plástico del conector en francés: Blanco (BA), Gris (GR), Negro (NO), Marrón (MR).",
                "fraction": 100,
                "feedback": "¡Correcto! En Renault los conectores de las centralitas son modulares de 16, 32 o 48 vías identificados por su color físico para evitar errores de inserción."
            },
            {
                "text": "El nivel de riesgo eléctrico homologado para los operarios del taller: Bajo, Grave, Nocivo y Mortal.",
                "fraction": 0,
                "feedback": "Incorrecto. Hacen referencia exclusiva al color visual de la carcasa del conector."
            },
            {
                "text": "El tipo de bus de datos utilizado en el conector: Básico (BA), Gradual (GR), Normal (NO) y Rápido (MR).",
                "fraction": 0,
                "feedback": "Incorrecto. La comunicación se especifica por el protocolo (CAN, LIN, K-Line)."
            },
            {
                "text": "Las iniciales de las plantas de fabricación de la alianza automotriz donde se ensambló cada componente.",
                "fraction": 0,
                "feedback": "Incorrecto. Son nombres de colores en francés."
            }
        ],
        general_feedback="<p>BA=Blanc, GR=Gris, NO=Noir, MR=Marron, JA=Jaune (Amarillo), VE=Vert (Verde), RG=Rouge (Rojo).</p>"
    )

    # 17. BMW ISTA
    builder.add_multichoice(
        "EE_P17_BMW_ISTA_Conectores",
        "<p>En el sistema de esquemas interactivos de BMW (ISTA / WDS), ¿con qué letra se identifican unívocamente todos los conectores eléctricos?</p>",
        [
            {
                "text": "Con la letra 'X' seguida de un número de identificación (ej. X11004).",
                "fraction": 100,
                "feedback": "¡Correcto! En BMW la 'X' designa cualquier conector, permitiendo localizar en el visor 3D el pinout y su fotografía real."
            },
            {
                "text": "Con la letra 'B' seguida del modelo de la carrocería y el código del año de homologación del chasis.",
                "fraction": 0,
                "feedback": "Incorrecto. En BMW la 'B' se reserva para sensores (transductores), no para conectores."
            },
            {
                "text": "Con la letra 'C' de conector y dos dígitos indicando la cantidad de cables alojados en el interior.",
                "fraction": 0,
                "feedback": "Incorrecto. La designación estándar alemana de conectores de interconexión es 'X'."
            },
            {
                "text": "Con la letra 'W' de cableado seguida de la letra identificativa del módulo electrónico correspondiente.",
                "fraction": 0,
                "feedback": "Incorrecto. 'W' en algunos sistemas alemanes designa mazo de cables o masa (en Mercedes)."
            }
        ],
        general_feedback="<p>BMW: X = Conectores (X13*1V, X11004), A = Centralitas, B = Sensores, Y = Actuador, F = Fusible, K = Relé.</p>"
    )

    # 18. TF Desconexión Batería
    builder.add_truefalse(
        "EE_P18_TF_Desconexion_Bateria_Masa",
        "<p>Al desconectar la batería del vehículo antes de una intervención eléctrica compleja en el taller, debe retirarse siempre en primer lugar el borne NEGATIVO (-) para evitar riesgos de cortocircuito con la herramienta contra la carrocería.</p>",
        True,
        feedback_true="¡Correcto! Si la llave metálica toca la chapa mientras se afloja el borne negativo, no ocurre nada porque ambos tienen el mismo potencial (0 V). En cambio, si se afloja primero el positivo y la herramienta toca masa, se produce un cortocircuito violento con chispazo.",
        feedback_false="Incorrecto. Retirar primero el borne positivo supone un riesgo crítico de cortocircuito accidental con la herramienta sobre el chasis.",
        general_feedback="<p>Regla de oro de seguridad en taller: Desconectar primero el negativo (-) / Conectar último el negativo (-).</p>"
    )

    # 19. TF Osciloscopio Inyectores
    builder.add_truefalse(
        "EE_P19_TF_Atenuacion_Sonda_Osciloscopio",
        "<p>Al medir la señal de mando de un inyector inductivo common-rail o de gasolina con el osciloscopio, es obligatorio utilizar una sonda atenuadora 10:1 o 20:1 para proteger el canal de entrada contra picos inductivos que pueden superar los 80 V.</p>",
        True,
        feedback_true="¡Correcto! Al cerrarse el inyector, la bobina genera un pico de tensión inducida de hasta 80-100 V. Si se mide con escala directa 1:1 en un canal limitado a 20 o 50 V, se destruye el conversor analógico-digital (ADC) del osciloscopio.",
        feedback_false="Incorrecto. Omitir la sonda atenuadora en cargas inductivas provoca la avería irreversible de la tarjeta de adquisición del osciloscopio.",
        general_feedback="<p>Proteger siempre el osciloscopio con atenuador al medir inyectores, solenoides o electroválvulas PWM.</p>"
    )

    # 20. Matching Bornes DIN
    builder.add_matching(
        "EE_P20_Matching_Bornes_DIN72552",
        "<p>Relaciona cada borne normalizado según la norma DIN 72552 con su circuito correspondiente en el vehículo:</p>",
        [
            ("Borne 30", "Positivo directo permanente de batería (+12V constante)"),
            ("Borne 15", "Positivo conmutado tras llave de contacto (ignición)"),
            ("Borne 31", "Retorno de masa directa a negativo y carrocería"),
            ("Borne 50", "Mando de activación del motor de arranque (posición START)")
        ],
        general_feedback="<p>La normalización DIN 72552 es el lenguaje común de los esquemas eléctricos en todo el mundo.</p>"
    )

    builder.save_xml(output_xml_path)
    validar_moodle_xml(output_xml_path)


if __name__ == '__main__':
    dest_pkg = os.path.join(SCRIPT_DIR, "Curso_Esquemas_Electricos_Automocion.h5p")
    build_h5p_course(dest_pkg)
    
    # Generar y certificar el banco sumativo Moodle XML oficial
    xml_path = os.path.join(SCRIPT_DIR, "evaluacion_esquemas_electricos.xml")
    generar_evaluacion_esquemas_xml(xml_path)

