#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Maestro del Curso Interactivo H5P y Banco Moodle XML:
"Circuitos de Alumbrado y Señalización del Automóvil"
Ubicación: CircuitosAlumbrado/

Desarrollado bajo el estándar técnico oficial de EducaMadrid (Moodle) y los
5 Pilares Pedagógicos de Aprendizaje Activo:
1. Participación activa del alumnado y enriquecimiento multimedia interactivo.
2. Andamiaje en 4 fases didácticas (InteractiveBook 1.7 con capítulos Column 1.16).
3. Retroalimentación inmediata con justificación pedagógica en cada distractor.
4. Gamificación estratégica contextualizada en diagnosis de taller y seguridad vial.
5. Desacoplamiento arquitectónico: H5P Formativo (visualización garantizada) + Cuestionario Moodle XML (Evaluación sumativa).
6. Accesibilidad Universal WCAG 2.1 AA / AAA y Diseño Responsive Móvil certificado.
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

sys.path.insert(0, PLANTILLA_DIR)
try:
    from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
except ImportError:
    # Fallback si no está en path
    sys.path.insert(0, os.path.join(PROJECT_ROOT, '.agents', 'skills', 'h5p-educamadrid', 'scripts'))
    from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml

# Directorio de librerías H5P homologadas
POSSIBLE_LIB_DIRS = [
    os.path.join(PROJECT_ROOT, 'h5p_builder', 'h5p-libraries'),
    os.path.join(PLANTILLA_DIR, 'h5p-libraries'),
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

def resolve_institutional_logo(preferred_name="logo2026.png"):
    """Localiza y resuelve dinámicamente metadatos del logotipo institucional."""
    search_dirs = [
        PLANTILLA_DIR,
        SCRIPT_DIR,
        os.path.join(PROJECT_ROOT, '.agents', 'skills', 'h5p-educamadrid', 'resources')
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
    width, height = (1600, 222)
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

def create_image_section(rel_path, alt_text, title="Imagen Técnica", width=1200, height=680):
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
            "autoCheck": False,
            "passPercentage": 100,
            "showScorePoints": True,
            "enableRetry": True,
            "enableSolutionsButton": True,
            "enableCheckButton": True
        },
        "media": {"disableImageZooming": False}
    }
    return create_column_wrapper("H5P.MultiChoice 1.16", params, title)

def create_true_false_question(question_html, correct_bool, feedback_correct, feedback_incorrect, title="Validación Técnica"):
    """Crea una comprobación formativa binaria H5P.TrueFalse 1.8."""
    params = {
        "question": f"<div>{question_html}</div>",
        "correct": "true" if correct_bool else "false",
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "confirmCheckDialog": False,
            "confirmRetryDialog": False,
            "autoCheck": False
        },
        "l10n": {
            "trueText": "Verdadero (Conforme a Norma)",
            "falseText": "Falso (No Conforme / Riesgo)",
            "feedback": "Resultado de la comprobación técnica"
        }
    }
    return create_column_wrapper("H5P.TrueFalse 1.8", params, title)

def create_drag_text_activity(task_description, text_with_drags, distractors="", title="Arrastre de Términos"):
    """Crea una actividad táctil H5P.DragText 1.10."""
    full_text = text_with_drags
    if distractors:
        full_text += f"\n\nDistractores adicionales: {distractors}"
    params = {
        "taskDescription": f"<p>{task_description}</p>",
        "textField": full_text,
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "autoCheck": False,
            "instantFeedback": False
        }
    }
    return create_column_wrapper("H5P.DragText 1.10", params, title)

def create_image_hotspots(img_rel_path, hotspots_data, title="Esquema Interactivo", alt_desc="Esquema de iluminación técnica", img_w=1200, img_h=680):
    """Crea un esquema interactivo H5P.ImageHotspots 1.10 con puntos de inspección."""
    hotspots = []
    for x, y, hs_title, hs_html in hotspots_data:
        hotspots.append({
            "x": x,
            "y": y,
            "title": hs_title,
            "header": hs_title,
            "content": [
                {
                    "library": "H5P.AdvancedText 1.1",
                    "params": {"text": hs_html},
                    "subContentId": str(uuid.uuid4()),
                    "metadata": {"title": hs_title, "contentType": "Text", "license": "CC BY-SA"}
                }
            ]
        })
    params = {
        "image": {
            "path": img_rel_path,
            "mime": "image/png" if img_rel_path.lower().endswith('.png') else "image/jpeg",
            "copyright": {"license": "U"},
            "width": img_w,
            "height": img_h
        },
        "hotspots": hotspots,
        "alt": alt_desc,
        "backgroundImageAltText": alt_desc
    }
    return create_column_wrapper("H5P.ImageHotspots 1.10", params, title)

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
# 2. DEFINICIÓN DIDÁCTICA Y TÉCNICA DE LOS 5 CAPÍTULOS
# =========================================================================

def build_chapter_1():
    """Capítulo 1: Circuitos de Alumbrado Principal (Posición, Cruce, Carretera y Automático)"""
    # Fase 1: Motivación y Reto
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-lightbulb-o"></i> CAPÍTULO 1 · ALUMBRADO PRINCIPAL</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Circuitos de Posición, Cruce, Carretera y Encendido Automático</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            El 90% de la información requerida para la toma de decisiones al volante se percibe mediante la vista.
            De noche, la capacidad visual se reduce al 20%, y el 42% de las muertes en carretera se concentran en condiciones de oscuridad (DGT / RACE).
            Dominar la arquitectura de los circuitos principales de iluminación y sus tecnologías ópticas (DE, Xenón, Matrix LED y Láser) es un pilar crítico en electromecánica.
          </p>
        </div>
        """, "Introducción Capítulo 1"),
        create_active_challenge(
            title="Reto de Taller: Deslumbramiento e Iluminación Asimétrica",
            scenario_html="<p>Un cliente acude al taller tras ser rechazado en la ITV por deslumbrar en luz de cruce con su vehículo equipado con proyectores Bixenón. El conductor afirma haber cambiado recientemente la lámpara D2S en otro taller. Además, en carretera de montaña nota que el haz no se ensancha a la derecha.</p>",
            steps=[
                ("Paso 1 (Inspección Óptica)", "Comprobar el montaje mecánico de la lámpara en el foco F1 del proyector elipsoidal DE y el estado del diafragma obturador a 15°."),
                ("Paso 2 (Verificación de Regulación)", "Verificar los sensores de inclinación de los ejes delantero y trasero y el actuador paso a paso del alcance luminoso."),
                ("Paso 3 (Alineación en Regloscopio)", "Medir con regloscopio a 25 m para certificar la línea de corte horizontal izquierda y la pendiente del 15% hacia el arcén derecho.")
            ],
            badge_text="Reto Inicial de Taller"
        )
    ]

    # Fase 2: Explicación interactiva
    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-book"></i> CONTENIDO TÉCNICO FUNDAMENTAL</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">1.1 Funciones Fotométricas y Arquitectura Óptica</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Los faros delanteros satisfacen tres requerimientos fotométricos normalizados internacionalmente (normativa ECE R112/R98/R48):
          </p>
          <div class="table-responsive">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Función Luminosa</th>
                  <th>Código Homologación</th>
                  <th>Intensidad Fotométrica</th>
                  <th>Principio Óptico y Distribución</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Luz de Posición Delantera</strong></td>
                  <td><code>A</code></td>
                  <td>4 a 125 cd (4–10 W)</td>
                  <td>Define la anchura y presencia del vehículo. Encendido ininterrumpido obligatorio con cruce y carretera.</td>
                </tr>
                <tr>
                  <td><strong>Luz de Cruce (Corto Alcance)</strong></td>
                  <td><code>C</code> / <code>HC</code> / <code>DC</code></td>
                  <td>20.000 a 150.000 cd en eje</td>
                  <td><strong>Haz asimétrico con elevación a 15°</strong> hacia el arcén derecho. Proyector elipsoidal DE con diafragma obturador.</td>
                </tr>
                <tr>
                  <td><strong>Luz de Carretera (Largo Alcance)</strong></td>
                  <td><code>R</code> / <code>HR</code> / <code>DR</code></td>
                  <td>Haz paralelo divergente</td>
                  <td>Emisor exactamente en el foco F de la parábola. En Bixenón el solenoide abate el obturador. Módulos láser activados a >60 km/h.</td>
                </tr>
                <tr>
                  <td><strong>Luz de Conducción Diurna (DRL)</strong></td>
                  <td><code>RL</code></td>
                  <td>400 a 1.200 cd</td>
                  <td>Encendido automático con contacto. Se atenúa (dimming) o apaga al conectar la luz de cruce o intermitente adyacente.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="alert-box alert-warning" style="margin-top:1rem;">
            <strong>¡Atención Técnica sobre DRL!</strong> Al circular por túneles o al anochecer solo con DRL encendidas, 
            <strong>los pilotos de posición traseros permanecen totalmente apagados</strong>, creando un riesgo severo de colisión por alcance en la zaga.
          </div>
        </div>
        """, "Funciones y Parámetros"),
        create_image_section("images/proyector_elipsoidal_de.png", "Esquema técnico del proyector elipsoidal DE con lámpara en F1, diafragma a 15 grados en F2 y huella proyectada", "Proyector Elipsoidal DE y Haz Asimétrico", 1200, 680),
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-cogs"></i> CONEXIONADO ELÉCTRICO Y SENSORES</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">1.2 Esquema de Relés DIN y Encendido Automático</h3>
          <p style="color:#1e293b; line-height:1.6;">
            En la arquitectura europea normalizada (DIN 72552), la alimentación de alta potencia de cruce y carretera se desacopla del mando del volante mediante relés automotrices:
          </p>
          <div class="tech-formula-block">
            Línea 30 (+Bat) ➔ Relé Cruce (Borne 30-87) ➔ Fusibles F1/F2 (10A c/u) ➔ Lámparas H7 / Balastos Xenón (56b)
            <br />
            Línea 15 (+Contacto) ➔ Mando Luces (Borne 56) ➔ Palanca Conmutadora ➔ Bobina Relé 86-85 ➔ Masa (31)
          </div>
          <p style="color:#1e293b; line-height:1.6;">
            El <strong>encendido automático de luces</strong> emplea un sensor crepuscular (fotorresistencia LDR o fototransistor) adherido a la zona superior del parabrisas. 
            La unidad BCM mide la señal analógica o por bus LIN y, al detectar una caída de iluminancia por debajo de un umbral programado (ej. entrada a túnel o puesta de sol), activa los transistores MOSFET o relés de potencia de las luces de cruce y posición simultáneamente.
          </p>
        </div>
        """, "Esquema y Relés"),
        create_image_section("images/esquema_alumbrado_reles.png", "Esquema eléctrico normalizado DIN con relés para alumbrado de cruce 56b y carretera 56a", "Circuito de Alumbrado con Relés Normalizados", 1200, 680)
    ]

    # Fase 3: Práctica guiada
    phase3 = [
        create_image_hotspots("images/proyector_elipsoidal_de.png", [
            (19, 47, "Foco F1: Fuente Luminosa", "<p>Posición donde se coloca la lámpara de descarga (Xenón D1S/D2S) o chip LED. El reflector elipsoidal concentra los rayos hacia el segundo foco.</p>"),
            (35, 47, "Foco F2: Diafragma Asimétrico", "<p>Lámina metálica colocada en el foco F2. Recorta el haz luminoso formando un plano horizontal a la izquierda y una elevación de 15° hacia la derecha.</p>"),
            (35, 80, "Solenoide Bixenón", "<p>Electroimán que abate el diafragma obturador hacia abajo cuando el conductor acciona la palanca de ráfagas o luces de carretera, dejando pasar el 100% del flujo luminoso.</p>"),
            (48, 47, "Lente Convergente (Lupa)", "<p>Lente plano-convexa o asférica que proyecta la imagen invertida del diafragma sobre la calzada, creando la línea de corte nítida.</p>"),
            (80, 50, "Corte a 15° para el Arcén", "<p>Normativa ECE: Ilumina hasta 75 metros por el margen derecho de la calzada para divisar peatones y señales sin deslumbrar a los vehículos en sentido contrario.</p>")
        ], "Exploración Interactiva: Componentes del Proyector DE"),
        create_drag_text_activity(
            task_description="Arrastra cada código de borne o parámetro de alumbrado a su definición correcta:",
            text_with_drags="El borne *56b* alimenta la luz de cruce o corto alcance.\nEl borne *56a* alimenta la luz de carretera o largo alcance.\nEl borne *58* corresponde al circuito de luces de posición y gálibo.\nEl ángulo de elevación del corte asimétrico europeo es de *15°*.\nEl código de homologación europeo de las luces diurnas obligatorias es *RL*.",
            distractors="*50* *31* *30°* *49*",
            title="Práctica de Bornes y Homologación de Alumbrado"
        )
    ]

    # Fase 4: Evaluación formativa
    phase4 = [
        create_checkpoint_section("Autocomprobación de Alumbrado Principal", "<p>Verifica tu comprensión de la óptica asimétrica y la normativa europea antes de continuar al sistema de señalización.</p>"),
        create_multichoice_question(
            question_html="¿Cuál es la función técnica de la elevación a 15° hacia el lado derecho en el haz de cruce asimétrico según normativa europea ECE?",
            answers=[
                (
                    "Iluminar a mayor distancia el arcén derecho y las señales de tráfico sin deslumbrar a los vehículos que circulan en sentido contrario.",
                    True,
                    "Piensa en la diferencia entre el lado por el que conducimos y el carril contrario.",
                    "¡Correcto! En países con circulación por la derecha, los 15° aumentan el alcance sobre el arcén hasta 75 metros manteniendo el lado izquierdo recortado."
                ),
                (
                    "Permitir que las luces de cruce alcancen la misma distancia que las luces de carretera.",
                    False,
                    "Comprueba el alcance de ambos tipos de faros.",
                    "Incorrecto. Las luces de cruce están limitadas para no deslumbrar; la elevación solo actúa en el margen derecho."
                ),
                (
                    "Compensar las vibraciones del motor en el soporte del faro.",
                    False,
                    "El ángulo responde a un diseño óptico y legal, no mecánico.",
                    "Incorrecto. Las vibraciones se aíslan mediante silentblocks y fijaciones elásticas."
                )
            ],
            title="Evaluación Formativa 1.1: Haz Asimétrico"
        ),
        create_true_false_question(
            question_html="Al circular de noche o dentro de un túnel con un vehículo moderno que solo lleva activadas las Luces de Conducción Diurna (DRL), los pilotos de posición traseros permanecen totalmente apagados, suponiendo un grave riesgo de accidente.",
            correct_bool=True,
            feedback_correct="¡Correcto! Las DRL solo iluminan hacia adelante durante el día. Por detrás el vehículo permanece a oscuras si el conductor o el sensor crepuscular no conecta las luces de cruce.",
            feedback_incorrect="Incorrecto. La normativa ECE R87 no activa los pilotos traseros con las DRL, por lo que la zaga queda desprotegida en condiciones de penumbra.",
            title="Validación Técnica 1.2: Seguridad con DRL"
        )
    ]

    return create_didactic_sequence_chapter(
        "Capítulo 1: Circuitos de Alumbrado Principal",
        phase1, phase2, phase3, phase4
    )


def build_chapter_2():
    """Capítulo 2: Señalización Óptica y Maniobra (Intermitencias, DRL, Freno y Marcha Atrás)"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-arrows-alt"></i> CAPÍTULO 2 · SEÑALIZACIÓN Y MANIOBRA</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Intermitencias, Emergencia, Frenado y Marcha Atrás</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            La señalización óptica comunica las intenciones del conductor a los demás usuarios.
            Los estudios de la NHTSA demostraron que el empleo de intermitentes ámbar en la zaga reduce hasta en un 28% los choques por alcance frente al color rojo americano.
            Analizaremos los circuitos de intermitencia, luces de freno adaptativas, modulación PWM y marcha atrás.
          </p>
        </div>
        """, "Introducción Capítulo 2"),
        create_active_challenge(
            title="Reto de Taller: Intermitencia Acelerada tras un Golpe Trasero",
            scenario_html="<p>Tras reparar un golpe en la aleta trasera izquierda de un vehículo, el cliente nota que al accionar el intermitente izquierdo la cadencia de parpadeo y el sonido del relé en el cuadro se duplica a más de 180 pulsaciones por minuto, mientras que el lado derecho parpadea al ritmo normal de 80 ppm.</p>",
            steps=[
                ("Paso 1 (Comprensión del Circuito)", "Recordar que la centralita o relé de intermitencia incorpora un circuito comparador de corriente de carga."),
                ("Paso 2 (Inspección Visual)", "Comprobar el piloto trasero izquierdo: la lámpara P21W está desconectada o su filamento roto, reduciendo el consumo nominal de 42W a solo 21W."),
                ("Paso 3 (Resolución)", "Sustituir la bombilla de 21W o reconectar el mazo de cables para restablecer el consumo y la frecuencia normal de 60-120 ppm.")
            ],
            badge_text="Reto de Taller: Diagnóstico de Carga"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-book"></i> PARÁMETROS DE SEÑALIZACIÓN ÓPTICA</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">2.1 Parámetros Reglamentarios y Señales PWM</h3>
          <p style="color:#1e293b; line-height:1.6;">
            Cada función de señalización responde a especificaciones estrictas recogidas en el Reglamento ECE R48:
          </p>
          <div class="table-responsive">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Función</th>
                  <th>Color Emisión</th>
                  <th>Intensidad Fotométrica</th>
                  <th>Comportamiento y Cadencia</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Intermitentes (Dirección)</strong></td>
                  <td>Ámbar (Europeo)</td>
                  <td>Alta potencia (21W / LED)</td>
                  <td>Cadencia fija obligatoria: <strong>60 a 120 destellos/minuto</strong> (1 a 2 Hz). Supervisión de carga.</td>
                </tr>
                <tr>
                  <td><strong>Luces de Emergencia (Warning)</strong></td>
                  <td>Ámbar simultáneo</td>
                  <td>Todos los indicadores</td>
                  <td>Alimentación permanente directa a <strong>Línea 30</strong>. Funciona con o sin llave de contacto.</td>
                </tr>
                <tr>
                  <td><strong>Luces de Freno Primarias</strong></td>
                  <td>Rojo continuo</td>
                  <td>60 a 185 cd</td>
                  <td>Activación inmediata por interruptor en pedal o sensor Hall en servofreno.</td>
                </tr>
                <tr>
                  <td><strong>Tercera Luz de Freno (CHMSL)</strong></td>
                  <td>Rojo continuo (S3)</td>
                  <td>Elevada en eje central</td>
                  <td>Obligatoria en la UE desde 1998. Desviación máxima permitida: 15 cm en portones asimétricos.</td>
                </tr>
                <tr>
                  <td><strong>Luz de Marcha Atrás</strong></td>
                  <td>Blanco continuo (AR)</td>
                  <td>Alta potencia</td>
                  <td>Activada mecánicamente por monocontacto en la caja de cambios al engranar marcha atrás.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <h4 style="color:#0f172a; margin-top:1.2rem;">Control por Modulación por Ancho de Pulso (PWM)</h4>
          <p style="color:#1e293b; line-height:1.6;">
            En los vehículos con electrónica de carrocería (BCM), una misma bombilla de filamento simple o conjunto de diodos LED realiza dos funciones mediante modulación PWM:
          </p>
          <div class="tech-formula-block">
            Función Luz de Posición Trasera ➔ Señal PWM con Duty Cycle al 15% - 20% (Luz suave de 4-10W)
            <br />
            Función Luz de Freno ➔ Señal PWM con Duty Cycle al 100% (Tensión continua de 12V, Brillo máximo de 21W)
          </div>
          <p style="color:#1e293b; line-height:1.6;">
            <strong>Frenado de Emergencia Adaptativo:</strong> Ante una deceleración violenta (>6 m/s² o disparo de ABS a >50 km/h), marcas como Mercedes-Benz o BMW hacen parpadear las luces de freno a alta frecuencia (3-5 Hz). Si el coche se detiene por completo, se disparan automáticamente las luces de emergencia (warning).
          </p>
        </div>
        """, "Señalización y PWM"),
        create_image_section("images/esquema_intermitencia_warning.png", "Esquema eléctrico normalizado de intermitencia y conmutador de luces de emergencia", "Circuito de Intermitencia y Warning", 1200, 680)
    ]

    phase3 = [
        create_checklist_section(
            "Protocolo de Inspección Pre-ITV: Señalización Exterior",
            [
                "Comprobar cadencia de intermitencia izquierda y derecha: 60 a 120 destellos/minuto.",
                "Verificar que las luces de emergencia (warning) funcionan con el contacto desconectado y llave fuera.",
                "Inspeccionar encendido de tercera luz de freno elevada y sincronización con pilotos traseros.",
                "Verificar conmutación de luz blanca de marcha atrás al engranar R con el contacto encendido.",
                "Comprobar ausencia de laca cuarteada en bombillas ámbar: la luz debe ser netamente ámbar, no blanca."
            ]
        ),
        create_drag_text_activity(
            task_description="Arrastra los términos técnicos a los huecos correspondientes sobre circuitos de señalización:",
            text_with_drags="La frecuencia de parpadeo de los intermitentes debe situarse reglamentariamente entre *60 y 120* destellos por minuto.\nLas luces de emergencia se alimentan directamente de la línea *30* de batería permanente.\nPara regular dos intensidades sobre una misma lámpara (posición y freno) se emplea modulación *PWM*.\nLa tercera luz de freno central obligatoria se identifica con el código *S3*.\nAl engranar la marcha atrás se enciende una luz de color *blanco* identificada con las siglas *AR*.",
            distractors="*15* *150 a 300* *rojo* *CAN*",
            title="Práctica de Señalización Óptica"
        )
    ]

    phase4 = [
        create_checkpoint_section("Autocomprobación de Señalización Óptica", "<p>Valida los conceptos de intermitencia, supervisión de carga y modulación PWM.</p>"),
        create_multichoice_question(
            question_html="¿Por qué la centralita de intermitencia duplica la frecuencia de parpadeo cuando se funde una de las bombillas de 21W?",
            answers=[
                (
                    "Porque el circuito incorpora una supervisión de corriente: al caer el consumo de la carga, el oscilador electrónico aumenta la frecuencia como aviso inmediato de avería al conductor.",
                    True,
                    "Relaciona la corriente consumida con el aviso al conductor.",
                    "¡Correcto! Es un chivato legal automático para alertar al conductor sin necesidad de pantallas digitales complejas."
                ),
                (
                    "Porque la batería suministra mayor voltaje al tener menos lámparas conectadas.",
                    False,
                    "El voltaje de la batería se mantiene regulado por el alternador.",
                    "Incorrecto. El alternador estabiliza la tensión a 14,2V; el cambio de frecuencia es una función calibrada en el circuito integrado."
                ),
                (
                    "Para evitar que el filamento de las demás bombillas se queme por sobrecalentamiento.",
                    False,
                    "Las bombillas están conectadas en paralelo.",
                    "Incorrecto. Al estar en paralelo, cada bombilla recibe la misma tensión con independencia de las demás."
                )
            ],
            title="Evaluación Formativa 2.1: Supervisión de Carga"
        ),
        create_true_false_question(
            question_html="El conmutador de luces de emergencia (warning) se alimenta exclusivamente de la Línea 15 (bajo llave de contacto) para impedir que se descargue la batería si el vehículo se abandona estacionado.",
            correct_bool=False,
            feedback_correct="¡Correcto! Es falso: el warning debe poder encenderse SIEMPRE, incluso sin llave y con el motor apagado, por lo que se alimenta directamente de la Línea 30 (+Bat).",
            feedback_incorrect="Incorrecto. La normativa exige que las luces de emergencia funcionen de forma permanente con alimentación directa de batería (Línea 30).",
            title="Validación Técnica 2.2: Alimentación del Warning"
        )
    ]

    return create_didactic_sequence_chapter(
        "Capítulo 2: Señalización Óptica y Maniobra",
        phase1, phase2, phase3, phase4
    )


def build_chapter_3():
    """Capítulo 3: Alumbrado Especial y Confort Interior (Antiniebla e Interior)"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-eye-slash"></i> CAPÍTULO 3 · ALUMBRADO ESPECIAL E INTERIOR</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Circuitos de Iluminación Antiniebla y Confort del Habitáculo</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            Bajo niebla densa o nevadas, un haz mal orientado provoca un deslumbramiento por reflexión conocido como 'pared blanca'.
            Analizaremos el diseño óptico rasante de los faros antiniebla, los pilotos traseros de alta penetración (150-300 cd),
            sus enclavamientos eléctricos obligatorios y los sistemas temporizados del habitáculo.
          </p>
        </div>
        """, "Introducción Capítulo 3"),
        create_active_challenge(
            title="Reto de Taller: El Piloto Antiniebla Trasero Inoperativo",
            scenario_html="<p>Un cliente acude al taller porque su luz antiniebla trasera no enciende al pulsar el botón del salpicadero. El técnico novato comprueba la bombilla y el fusible F12, encontrándolos en perfecto estado. ¿Qué lógica eléctrica de seguridad ha omitido comprobar antes de desmontar el cableado?</p>",
            steps=[
                ("Paso 1 (Comprobación de Enclavamiento)", "Verificar si el conmutador general de luces está en posición de 'Cruce': la normativa UNECE exige que el antiniebla trasero no pueda encenderse solo con luces de posición."),
                ("Paso 2 (Inspección de la Piña de Remolque)", "En vehículos con enganche de remolque, verificar el microinterruptor interno de la base de 13 polos: si se queda atascado con suciedad, corta la masa del antiniebla del coche para evitar reflejos molestos en el remolque."),
                ("Paso 3 (Testigo en Cuadro)", "Comprobar el testigo amarillo auto en el cuadro de instrumentos para determinar si la orden sale de la BSI/UCH.")
            ],
            badge_text="Reto de Diagnosis: Enclavamiento de Seguridad"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-book"></i> NORMATIVA Y CARACTERÍSTICAS TÉCNICAS</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">3.1 Alumbrado Antiniebla y Reglamentación ECE R48</h3>
          <p style="color:#1e293b; line-height:1.6;">
            El alumbrado antiniebla está específicamente calculado para minimizar la dispersión de la luz producida por las gotas de agua en suspensión:
          </p>
          <div class="table-responsive">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Componente</th>
                  <th>Código Homologación</th>
                  <th>Color y Geometría</th>
                  <th>Prescripciones Técnicas y Legales</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Faros Antiniebla Delanteros</strong></td>
                  <td><code>B</code> o <code>F3</code></td>
                  <td>Blanco o Amarillo Selectivo. Haz plano y ancho.</td>
                  <td>Instalados en la parte baja del faldón. Prohibido su uso en pavimento mojado si no hay niebla (deslumbramiento por reflexión en charcos).</td>
                </tr>
                <tr>
                  <td><strong>Pilotos Antiniebla Traseros</strong></td>
                  <td><code>F</code> / <code>F1</code> / <code>F2</code></td>
                  <td>Rojo intenso (150 a 300 cd)</td>
                  <td>Obligatorio en Europa (uno central/lado izquierdo o dos simétricos). <strong>Separación mínima de 10 cm con luz de freno</strong> para no camuflarla.</td>
                </tr>
                <tr>
                  <td><strong>Iluminación Interior</strong></td>
                  <td>Confort</td>
                  <td>Blanco cálido / LED regulable</td>
                  <td>Temporización progresiva (fade-out) por BCM (2 min aprox.). Función 'Night Panel' para anular luces innecesarias de noche.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <h4 style="color:#0f172a; margin-top:1.2rem;">Lógica del Circuito de Interbloqueo Antiniebla</h4>
          <p style="color:#1e293b; line-height:1.6;">
            El circuito eléctrico del antiniebla trasero requiere por normativa un <strong>enclavamiento obligatorio</strong>: solo recibe corriente si las luces de cruce (56b) o los faros antiniebla delanteros (55) están previamente activados. Además, incorpora un testigo visual independiente en el cuadro de instrumentos de color amarillo auto (*Amber*) para evitar que el conductor lo deje encendido inadvertidamente al disiparse la niebla.
          </p>
        </div>
        """, "Antiniebla e Interior"),
        create_accordion([
            ("¿Por qué está prohibido el antiniebla delantero con lluvia sin niebla?",
             "<p>Sobre el asfalto mojado, la capa de agua actúa como un espejo plano reflectante. El haz ancho y rasante de los faros antiniebla rebota directamente hacia los ojos de los conductores que circulan en sentido contrario, multiplicando por diez el deslumbramiento.</p>"),
            ("Regla de los 10 cm entre Antiniebla Trasero y Freno (ECE R48)",
             "<p>La intensidad de un piloto antiniebla trasero (150-300 cd) es comparable a la de una luz de freno. Si estuvieran demasiado juntos, el conductor que circula detrás no distinguiría cuándo el vehículo frena, aumentando exponencialmente el riesgo de choque por alcance.</p>"),
            ("Atenuación Progresiva del Habitáculo (Theater Dimming)",
             "<p>Gestionada por la unidad de confort (BSI/UCH) mediante modulación PWM. Al cerrar las puertas, aplica una rampa decreciente en el ciclo de trabajo que apaga las luces suavemente. Al dar el contacto, se apagan de forma instantánea por seguridad.</p>")
        ], "Preguntas Clave y Normativa de Alumbrado Especial")
    ]

    phase3 = [
        create_drag_text_activity(
            task_description="Arrastra los requisitos normativos a sus correspondientes apartados:",
            text_with_drags="La separación mínima obligatoria entre el piloto antiniebla trasero y la luz de freno es de *10 cm*.\nLa intensidad luminosa de un piloto antiniebla trasero oscila entre *150 y 300* candelas.\nEl color del testigo del piloto antiniebla trasero en el cuadro es *amarillo auto*.\nEl código de homologación de los faros antiniebla delanteros es *B o F3*.\nLa iluminación interior temporizada del habitáculo se regula mediante señales *PWM*.",
            distractors="*5 cm* *verde* *RL* *12V continuo*",
            title="Práctica de Alumbrado Especial e Interior"
        )
    ]

    phase4 = [
        create_checkpoint_section("Autocomprobación de Alumbrado Especial", "<p>Comprueba los conceptos de enclavamiento antiniebla y ergonomía de iluminación interior.</p>"),
        create_multichoice_question(
            question_html="Según el Reglamento ECE R48, ¿por qué es obligatoria una separación física mínima de 10 cm entre la luz de freno y el piloto antiniebla trasero?",
            answers=[
                (
                    "Para evitar que la intensa luz del piloto antiniebla (150-300 cd) enmascare ópticamente la señal de frenado ante los conductores que circulan por detrás.",
                    True,
                    "Compara las intensidades lumínicas de ambas funciones.",
                    "¡Correcto! Debido a que ambas emiten luz roja de gran intensidad, una separación menor impediría percibir el encendido de los frenos en situaciones de baja visibilidad."
                ),
                (
                    "Para permitir que los cables no se crucen dentro del portalámparas.",
                    False,
                    "La normativa fija cotas de seguridad visual, no de cableado.",
                    "Incorrecto. Las razones son exclusivamente fotométricas y de seguridad vial."
                ),
                (
                    "Para reducir la temperatura acumulada en el interior de la tulipa de plástico.",
                    False,
                    "La temperatura se disipa por el volumen del piloto.",
                    "Incorrecto. Aunque la disipación térmica es importante, la cota de 10 cm es un requisito fotométrico de contraste visual."
                )
            ],
            title="Evaluación Formativa 3.1: Separación de Seguridad"
        ),
        create_true_false_question(
            question_html="El piloto antiniebla trasero puede encenderse de manera legal y autónoma cuando el vehículo circula únicamente con las luces de posición delanteras y traseras activadas.",
            correct_bool=False,
            feedback_correct="¡Correcto! Es falso: el circuito incorpora un enclavamiento obligatorio que exige tener encendidas las luces de cruce o los antinieblas delanteros.",
            feedback_incorrect="Incorrecto. La normativa europea prohíbe el encendido del antiniebla trasero sin que estén activas las luces de cruce o los faros antiniebla delanteros.",
            title="Validación Técnica 3.2: Enclavamiento Antiniebla"
        )
    ]

    return create_didactic_sequence_chapter(
        "Capítulo 3: Alumbrado Especial y Confort Interior",
        phase1, phase2, phase3, phase4
    )


def build_chapter_4():
    """Capítulo 4: Cálculo Electrotécnico y Regulación de Faros (Cálculos, Fusibles y Regloscopio)"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-calculator"></i> CAPÍTULO 4 · CÁLCULO Y REGULACIÓN</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Cálculo Electrotécnico, Fusibles y Regulación de Faros</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            En alumbrado automotriz, una caída de tensión de tan solo 0,5 V en el cableado disminuye el flujo luminoso de una lámpara un 15%, y 1,0 V de pérdida reduce su luz un 28%.
            Aprende a dimensionar conductores de cobre, seleccionar fusibles de protección y calibrar con precisión milimétrica los faros en el regloscopio.
          </p>
        </div>
        """, "Introducción Capítulo 4"),
        create_active_challenge(
            title="Reto de Cálculo: Instalación de Faros Supletorios de 110 W",
            scenario_html="<p>Un taller instala dos faros halógenos supletorios de 55 W cada uno (potencia total P = 110 W) en la defensa de un vehículo todoterreno. La longitud del cable desde la batería hasta los faros es de 4 metros (recorrido de ida). La caída de tensión admisible máxima se fija en ΔV = 0,3 V a 12 V de tensión nominal.</p>",
            steps=[
                ("Paso 1 (Cálculo de Intensidad)", "I = P / V = 110 W / 12 V = 9,17 A."),
                ("Paso 2 (Cálculo de Sección por Caída de Tensión)", "S = (2 · L · I) / (κ · ΔV) = (2 · 4 m · 9,17 A) / (56 · 0,3 V) = 73,36 / 16,8 = 4,36 mm² ➔ Normalizada comercial: 6 mm² (o 2,5 mm² por faro independiente)."),
                ("Paso 3 (Selección del Fusible)", "I_fusible = 1,25 · I_nom = 1,25 · 9,17 A = 11,46 A ➔ Fusible comercial normalizado: 15 A (Azul cielo tipo ATO).")
            ],
            badge_text="Reto Electrotécnico de Taller"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-book"></i> FÓRMULAS ELECTROTÉCNICAS Y METROLOGÍA</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">4.1 Dimensionado de Cables y Fusibles en Iluminación</h3>
          <p style="color:#1e293b; line-height:1.6;">
            En automoción, el cálculo de secciones de conductor de cobre se rige por dos criterios: <strong>densidad de corriente máxima admisible</strong> (calentamiento por efecto Joule) y <strong>caída de tensión máxima admisible</strong>:
          </p>
          <div class="tech-formula-block">
            Cálculo de Corriente: <strong>I = P / V</strong> [Amperios (A)]
            <br />
            Sección por Caída de Tensión: <strong>S = (2 · L · I) / (κ · ΔV)</strong> [mm²]
            <br />
            <span style="font-size:0.9rem; color:#475569;">Donde: L = longitud cable en m, κ = 56 m/(Ω·mm²) para cobre a temperatura de trabajo, ΔV = caída admisible (0,3V en faros principales, 0,5V en señalización).</span>
          </div>
          <div class="table-responsive">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Calibre Fusible (ATO/Mini)</th>
                  <th>Código de Color</th>
                  <th>Intensidad Máxima</th>
                  <th>Aplicación Típica en Alumbrado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>5 A</strong></td>
                  <td>Beige / Naranja claro</td>
                  <td>60 W a 12V</td>
                  <td>Luces de posición, luz de matrícula, iluminación de guantera.</td>
                </tr>
                <tr>
                  <td><strong>7,5 A</strong></td>
                  <td>Marrón</td>
                  <td>90 W a 12V</td>
                  <td>Luz antiniebla trasera individual, marcha atrás.</td>
                </tr>
                <tr>
                  <td><strong>10 A</strong></td>
                  <td>Rojo</td>
                  <td>120 W a 12V</td>
                  <td>Faro de cruce individual (55W) o carretera individual (60W).</td>
                </tr>
                <tr>
                  <td><strong>15 A</strong></td>
                  <td>Azul cielo</td>
                  <td>180 W a 12V</td>
                  <td>Pareja de faros antiniebla delanteros (2x55W) o luces de carretera conjuntas.</td>
                </tr>
                <tr>
                  <td><strong>20 A</strong></td>
                  <td>Amarillo</td>
                  <td>240 W a 12V</td>
                  <td>Línea principal de módulo BCM o circuito general de luces.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <h4 style="color:#0f172a; margin-top:1.2rem;">4.2 Regulación de Faros con Regloscopio</h4>
          <p style="color:#1e293b; line-height:1.6;">
            El regloscopio es el equipo metrológico de taller que reproduce la proyección del haz a una distancia de <strong>25 metros</strong> mediante una lente óptica colimadora:
          </p>
          <ul style="color:#1e293b; line-height:1.6;">
            <li><strong>Caída reglamentaria en turismos:</strong> Comprendida entre el <strong>-1,0% y el -1,5%</strong> respecto al centro óptico.</li>
            <li><strong>Efecto del desreglaje hacia arriba (+1%):</strong> Multiplica por <strong>20</strong> el nivel de deslumbramiento al tráfico contrario.</li>
            <li><strong>Efecto del desreglaje hacia abajo (-2,5%):</strong> Reduce a la mitad la distancia de visibilidad (apenas 30 metros de alcance).</li>
            <li><strong>Regulación Automática Dinámica Obligatoria:</strong> Exigida por normativa europea en faros con flujo superior a <strong>2.000 lúmenes</strong> (xenón de 35W y LED de alta potencia), empleando sensores de nivel en los ejes de suspensión y servomotores paso a paso.</li>
          </ul>
        </div>
        """, "Cálculos y Reglaje"),
        create_image_section("images/regloscopio_ajuste_faros.png", "Pantalla de proyección del regloscopio a 25 metros con cotas de inclinación de -1.0% a -1.5%", "Ajuste Óptico de Faros en Regloscopio", 1200, 680)
    ]

    phase3 = [
        create_drag_text_activity(
            task_description="Arrastra los valores numéricos y magnitudes al ejercicio de cálculo y reglaje:",
            text_with_drags="Una lámpara halógena de 55 W alimentada a 12 V consume una corriente de *4,58* A.\nLa caída de tensión máxima admisible en la línea positiva de un faro principal es de *0,3* V.\nEl regloscopio óptico reproduce la proyección del haz a una distancia equivalente de *25* metros.\nLa inclinación o caída reglamentaria del haz de cruce en turismos se sitúa entre *-1,0% y -1,5%*.\nUn desvío de +1% hacia arriba en el reglaje de un faro multiplica por *20* el deslumbramiento.",
            distractors="*9,17* *1,0* *50* *100*",
            title="Práctica de Cálculo Electrotécnico y Reglaje"
        )
    ]

    phase4 = [
        create_checkpoint_section("Autocomprobación de Cálculo y Reglaje", "<p>Valida tu capacidad para dimensionar instalaciones de iluminación y diagnosticar desajustes de faros.</p>"),
        create_multichoice_question(
            question_html="Si un proyector de luces de cruce se desajusta tan solo 1 grado hacia arriba (+1%) respecto a la cota recomendada por el fabricante, ¿cuál es la consecuencia técnica inmediata?",
            answers=[
                (
                    "El nivel de deslumbramiento hacia los conductores que circulan en sentido contrario se multiplica por 20.",
                    True,
                    "Revisa los estudios de fotometría vial del RACE sobre deslumbramiento.",
                    "¡Correcto! Un desvío de apenas +1% eleva el haz de corte claro-oscuro directamente a la altura de los ojos del conductor que viene de frente, cegándolo durante más de 3,6 segundos."
                ),
                (
                    "El alcance de visión del conductor aumenta a más de 300 metros sin efectos secundarios.",
                    False,
                    "El haz de cruce está diseñado para iluminar la calzada, no el horizonte.",
                    "Incorrecto. Aunque el haz apunte más arriba, la iluminancia en la calzada disminuye y provoca un deslumbramiento crítico ilegal."
                ),
                (
                    "El fusible de 10A se funde automáticamente por exceso de refracción.",
                    False,
                    "El ajuste mecánico del reflector no altera la corriente eléctrica de la lámpara.",
                    "Incorrecto. El reglaje de la parábola es un ajuste óptico-geométrico independiente del consumo eléctrico."
                )
            ],
            title="Evaluación Formativa 4.1: Desreglaje Óptico"
        ),
        create_true_false_question(
            question_html="Según el reglamento europeo ECE R48, los vehículos equipados con faros cuyo flujo luminoso supere los 2.000 lúmenes (como el xenón de 35W o LED potentes) deben equipar obligatoriamente sistema lavafaros y regulación automática del alcance luminoso.",
            correct_bool=True,
            feedback_correct="¡Correcto! Faros con más de 2.000 lm exigen obligatoriamente lavafaros de alta presión y regulador automático de altura conectado a sensores de suspensión.",
            feedback_incorrect="Incorrecto. La normativa europea fija en 2.000 lúmenes el umbral estricto a partir del cual el lavafaros y la regulación automática son obligatorios.",
            title="Validación Técnica 4.2: Umbral de 2.000 Lúmenes"
        )
    ]

    return create_didactic_sequence_chapter(
        "Capítulo 4: Cálculo Electrotécnico y Regulación de Faros",
        phase1, phase2, phase3, phase4
    )


def build_chapter_5():
    """Capítulo 5: Diagnosis y Localización de Averías (Redes, Drivers LED y Caídas de Tensión)"""
    phase1 = [
        create_text_section("""
        <div class="tech-hero">
          <div class="tech-badge"><i class="fa fa-stethoscope"></i> CAPÍTULO 5 · DIAGNOSIS EN TALLER</div>
          <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Diagnosis Avanzada, Redes Multiplexadas y Caídas de Tensión</h2>
          <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
            La evolución hacia faros Full LED matriciales y centralitas de red de a bordo (BCM) ha transformado la diagnosis.
            Ya no basta con cambiar una bombilla: los drivers electrónicos estabilizan corriente, supervisan filamentos en frío/caliente
            y registran códigos DTC ante anomalías térmicas o caídas de tensión por masas defectuosas.
          </p>
        </div>
        """, "Introducción Capítulo 5"),
        create_active_challenge(
            title="Reto de Taller: Faro Delantero con Iluminación Tenue y Parpadeo",
            scenario_html="<p>Un turismo moderno entra en el taller con el faro halógeno derecho alumbrando con un 30% menos de intensidad que el izquierdo. El cliente ya cambió la lámpara H7 pensando que estaba gastada, pero el problema persiste. El técnico conecta el multímetro digital para medir caídas de tensión en carga.</p>",
            steps=[
                ("Paso 1 (Medición de Caída en Línea Positiva V1)", "Colocar la punta roja en el borne positivo de la batería y la punta negra en el terminal positivo de la lámpara con las luces encendidas. Lectura: 0,12 V (Correcto, <0,3 V)."),
                ("Paso 2 (Medición de Caída en Línea de Masa V2)", "Colocar la punta negra en el borne negativo de la batería y la punta roja en el casquillo de masa de la lámpara. Lectura: 0,95 V (¡Inadmisible! Límite máximo: 0,1 V)."),
                ("Paso 3 (Localización y Reparación)", "Seguir el cable marrón de masa (Línea 31) hasta el tornillo de chasis en el paso de rueda derecho. Desmontar, lijar el óxido de cobre y apretar. Al repetir la prueba, la caída baja a 0,03 V y el faro recupera el 100% de brillo.")
            ],
            badge_text="Reto Metrológico de Taller"
        )
    ]

    phase2 = [
        create_text_section("""
        <div class="tech-card">
          <div class="tech-card-badge"><i class="fa fa-book"></i> ESTRATEGIAS DE DIAGNOSIS EN TALLER</div>
          <h3 style="color:#0f172a; margin-top:0.5rem;">5.1 Protocolos de Diagnosis Eléctrica y Electrónica</h3>
          <p style="color:#1e293b; line-height:1.6;">
            En los vehículos modernos, la diagnosis de iluminación se estructura en tres niveles técnicos:
          </p>
          <div class="table-responsive">
            <table class="tech-table">
              <thead>
                <tr>
                  <th>Nivel de Diagnosis</th>
                  <th>Herramienta de Medición</th>
                  <th>Parámetro Verificado</th>
                  <th>Criterio de Tolerancia / Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Caída de Tensión Positiva</strong></td>
                  <td>Voltímetro digital en paralelo (en carga)</td>
                  <td>Resistencia parásita en cables, fusibles y relés</td>
                  <td><strong>ΔV ≤ 0,3 V</strong> (Valores >0,5 V reducen el flujo un 15%).</td>
                </tr>
                <tr>
                  <td><strong>Caída de Tensión de Masa</strong></td>
                  <td>Voltímetro digital entre casquillo y borne (-)</td>
                  <td>Oxidación o aflojamiento en Línea 31 de chasis</td>
                  <td><strong>ΔV ≤ 0,1 V</strong> (Una masa con 0,9V roba tensión a la lámpara).</td>
                </tr>
                <tr>
                  <td><strong>Monitoreo de Red (BCM)</strong></td>
                  <td>Equipo de diagnosis OBD-II / Osciloscopio</td>
                  <td>Chequeo en frío (microimpulsos) y chequeo en caliente</td>
                  <td>Detección de bombilla fundida o circuito abierto con código DTC (ej. B1xxx).</td>
                </tr>
                <tr>
                  <td><strong>Drivers y Módulos LED</strong></td>
                  <td>Osciloscopio / Escáner</td>
                  <td>Señal PWM, corriente constante y temperatura juntura Tj</td>
                  <td>Protección electrónica: desconexión de la línea ante cortocircuito o sobrecalentamiento.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="alert-box alert-danger" style="margin-top:1rem;">
            <strong>Avería Química Frecuente (Directiva RoHS):</strong> Debido a la prohibición del uso de vidrio tintado con cadmio, 
            las bombillas ámbar actuales usan lacas superficiales. Con los ciclos térmicos, la laca se agrieta y se desprende, 
            emitiendo <strong>luz blanca en los intermitentes</strong> (defecto grave en ITV).
          </div>
        </div>
        """, "Protocolos de Diagnosis"),
        create_image_section("images/diagnosis_caida_tension.png", "Guía metrológica de medición de caída de tensión en línea positiva y masa con voltímetro en carga", "Método de Caída de Tensión en Taller", 1200, 680)
    ]

    phase3 = [
        create_checklist_section(
            "Lista de Cotejo Sistemática: Diagnosis de Alumbrado",
            [
                "1. Medición de tensión de batería en reposo (12.6V) y con motor en marcha (14.2V).",
                "2. Prueba de caída de tensión bajo carga (lámparas encendidas): verificar masa (≤0.1V) y positivo (≤0.3V).",
                "3. Lectura de códigos DTC de carrocería (serie B) en la BCM mediante puerto OBD-II.",
                "4. Inspección visual de bombillas ámbar para descartar desprendimiento de laca exterior.",
                "5. Verificación de transparencia en policarbonato: eliminar opacidad amarillenta por degradación UV mediante pulido y lacado."
            ]
        ),
        create_drag_text_activity(
            task_description="Arrastra cada concepto de diagnosis a su descripción correspondiente:",
            text_with_drags="La caída de tensión máxima admisible en el circuito de masa de un faro es de *0,1 V*.\nLa prueba de caída de tensión debe realizarse obligatoriamente con el circuito en *carga*.\nEl chequeo en *frío* envía microimpulsos imperceptibles para comprobar la continuidad del filamento apagado.\nLa directiva *RoHS* prohibió el empleo de cadmio en el cristal de las bombillas ámbar.\nLa unidad de control central que gestiona la iluminación en la red multiplexada se denomina *BCM*.",
            distractors="*0,5 V* *vacío* *caliente* *ISO*",
            title="Práctica de Diagnosis y Mantenimiento"
        )
    ]

    phase4 = [
        create_checkpoint_section("Autocomprobación de Diagnosis de Alumbrado", "<p>Valida los métodos metrológicos de localización de averías eléctricas en el vehículo.</p>"),
        create_multichoice_question(
            question_html="Al medir con el voltímetro entre el borne negativo (-) de la batería y el casquillo de masa de una lámpara H7 encendida, el instrumento marca 0,95 V. ¿Qué indica este resultado?",
            answers=[
                (
                    "Existe una resistencia parásita excesiva en la línea de masa (borne 31 oxidado o flojo) que está restando casi 1 voltio a la lámpara, provocando una pérdida de brillo superior al 25%.",
                    True,
                    "En una masa perfecta la caída debería ser prácticamente 0 V.",
                    "¡Correcto! La caída máxima admisible en masa es 0,1 V. Un valor de 0,95 V evidencia corrosión o mal contacto en el punto de anclaje al chasis."
                ),
                (
                    "La lámpara está funcionando correctamente porque el chasis tiene una tensión normal de 1 voltio.",
                    False,
                    "El chasis debe encontrarse al mismo potencial que el borne negativo de la batería.",
                    "Incorrecto. La masa debe ser idealmente 0 V; tener casi 1 voltio indica una caída parásita severa."
                ),
                (
                    "El alternador está sobrecargando el sistema y debe sustituirse.",
                    False,
                    "La medición es diferencial entre masa y negativo de batería.",
                    "Incorrecto. La medición se realiza entre dos puntos de masa; no evalúa la tensión del alternador."
                )
            ],
            title="Evaluación Formativa 5.1: Caída de Tensión en Masa"
        ),
        create_true_false_question(
            question_html="Para comprobar de forma fiable la caída de tensión en el cableado de un faro con el voltímetro, es indispensable que el circuito esté apagado y sin corriente para no quemar el fusible del multímetro.",
            correct_bool=False,
            feedback_correct="¡Correcto! Es falso: la caída de tensión solo existe cuando circula corriente por la resistencia del cable (Ley de Ohm: V = I · R). Con circuito apagado (I = 0 A), la caída medida será siempre 0 V, enmascarando la avería.",
            feedback_incorrect="Incorrecto. Sin corriente circulando (I = 0 A), no existe caída de tensión. La prueba exige obligatoriamente realizarse bajo carga con las luces encendidas.",
            title="Validación Técnica 5.2: Medición en Carga"
        )
    ]

    return create_didactic_sequence_chapter(
        "Capítulo 5: Diagnosis y Localización de Averías",
        phase1, phase2, phase3, phase4
    )


# =========================================================================
# 3. EMPAQUETADOR MAESTRO H5P Y GENERADOR MOODLE XML
# =========================================================================

def build_h5p_course(destination_h5p_path):
    """Compila físicamente el paquete .h5p con sus 16 librerías homologadas."""
    print(f"📦 Compilando curso H5P en: {destination_h5p_path}")
    print(f"📁 Copiando 16 librerías base desde: {LIB_DIR}")

    temp_build_dir = os.path.join(SCRIPT_DIR, "temp_h5p_build")
    if os.path.exists(temp_build_dir):
        shutil.rmtree(temp_build_dir)
    os.makedirs(temp_build_dir, exist_ok=True)

    # 1. Copiar librerías homologadas
    for item in os.listdir(LIB_DIR):
        src = os.path.join(LIB_DIR, item)
        dst = os.path.join(temp_build_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)

    # 2. Copiar imágenes técnicas y logo
    content_images_dir = os.path.join(temp_build_dir, "content", "images")
    os.makedirs(content_images_dir, exist_ok=True)

    logo_info = resolve_institutional_logo()
    if logo_info["src_path"] and os.path.exists(logo_info["src_path"]):
        shutil.copy2(logo_info["src_path"], os.path.join(content_images_dir, logo_info["filename"]))
        print(f"✓ Logotipo institucional empaquetado: {logo_info['filename']}")

    local_images_dir = os.path.join(SCRIPT_DIR, "images")
    if os.path.exists(local_images_dir):
        for img_file in os.listdir(local_images_dir):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                shutil.copy2(os.path.join(local_images_dir, img_file), os.path.join(content_images_dir, img_file))
                print(f"✓ Imagen técnica empaquetada: content/images/{img_file}")

    # 3. Ensamblar los 5 capítulos
    print("🔨 Ensamblando los 5 capítulos con andamiaje pedagógico...")
    chapters = [
        build_chapter_1(),
        build_chapter_2(),
        build_chapter_3(),
        build_chapter_4(),
        build_chapter_5()
    ]

    # 4. Generar content.json con optimización responsive móvil
    content_json = {
        "showCoverPage": False,
        "bookCover": {
            "coverDescription": "Curso Interactivo Oficial de Circuitos de Alumbrado y Señalización del Automóvil",
            "coverMedium": {}
        },
        "chapters": chapters,
        "behaviour": {
            "defaultTableOfContents": False,  # Cajón lateral cerrado en móviles
            "progressType": "textual",        # Progreso textual adaptativo (sin desbordamiento)
            "progressAuto": True,
            "displaySummary": True
        },
        "l10n": {
            "read": "Iniciar estudio",
            "displayTOC": "Mostrar índice de capítulos",
            "hideTOC": "Ocultar índice de capítulos",
            "nextPage": "Capítulo siguiente",
            "previousPage": "Capítulo anterior",
            "navigateToTop": "Volver arriba"
        }
    }

    with open(os.path.join(temp_build_dir, "content", "content.json"), "w", encoding="utf-8") as f:
        json.dump(content_json, f, ensure_ascii=False, indent=2)

    # 5. Generar h5p.json
    h5p_json = {
        "title": "Circuitos de Alumbrado y Señalización del Automóvil",
        "language": "es",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["div"],
        "license": "CC BY-SA",
        "defaultLanguage": "es",
        "preloadedDependencies": HOMOLOGATED_DEPENDENCIES,
        "authors": [{"name": "Departamento de Formación Profesional - Automoción", "role": "Author"}]
    }

    with open(os.path.join(temp_build_dir, "h5p.json"), "w", encoding="utf-8") as f:
        json.dump(h5p_json, f, ensure_ascii=False, indent=2)

    # 6. Comprimir en ZIP con extensión .h5p
    if os.path.exists(destination_h5p_path):
        os.remove(destination_h5p_path)

    with zipfile.ZipFile(destination_h5p_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_build_dir):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_file = os.path.relpath(abs_file, temp_build_dir)
                zip_out.write(abs_file, rel_file)

    shutil.rmtree(temp_build_dir)
    pkg_size_mb = os.path.getsize(destination_h5p_path) / (1024 * 1024)
    print(f"\n✅ Paquete H5P generado con éxito: {destination_h5p_path} ({pkg_size_mb:.2f} MB)")


def generar_evaluacion_alumbrado_xml(output_xml_path):
    """Genera el banco sumativo de 25 preguntas técnicas Moodle XML para el Calificador."""
    builder = MoodleXMLBuilder()
    builder.set_category("Circuitos de Alumbrado y Senalizacion - Evaluacion Sumativa Oficial")

    # 1. Haz asimétrico
    builder.add_multichoice(
        "ALUM_P01_MC_Corte_Asimetrico_15",
        "<p>En la normativa europea ECE para faros de cruce, ¿cuál es la razón técnica y geométrica de la elevación a 15° en el lado derecho de la línea de corte claro-oscuro?</p>",
        [
            {"text": "Aumentar el alcance visual sobre el arcén derecho y las señales de tráfico hasta 75 metros, manteniendo recortado el lado izquierdo para evitar el deslumbramiento a los conductores que circulan en sentido contrario.", "fraction": 100, "feedback": "¡Correcto! En países con circulación por la derecha, el corte a 15° optimiza la seguridad sin deslumbrar."},
            {"text": "Compensar la inclinación de la carrocería en curvas cerradas a la derecha.", "fraction": 0, "feedback": "Incorrecto. Para la iluminación en curva se emplean sistemas direccionales dinámicos o luces de giro (cornering)."},
            {"text": "Permitir que la lámpara halógena opere con menor temperatura en el lado izquierdo.", "fraction": 0, "feedback": "Incorrecto. La temperatura depende del filamento y el diseño del bulbo, no del corte óptico."},
            {"text": "Facilitar el reglaje manual sin necesidad de regloscopio.", "fraction": 0, "feedback": "Incorrecto. El regloscopio es estrictamente necesario para ajustar tanto la horizontal como el ángulo a 15°."}
        ],
        general_feedback="<p>Normativa ECE R112/R98: Haz asimétrico a 15° hacia el arcén derecho.</p>"
    )

    # 2. Proyector DE
    builder.add_multichoice(
        "ALUM_P02_MC_Proyector_Elipsoidal_DE",
        "<p>¿En qué punto geométrico del proyector elipsoidal DE (tres elipsoides) se ubica el diafragma obturador que genera la línea de corte claro-oscuro?</p>",
        [
            {"text": "En el segundo foco geométrico (F2) del reflector elipsoidal, donde convergen los rayos reflejados antes de atravesar la lente convergente.", "fraction": 100, "feedback": "¡Correcto! La lámpara se ubica en F1 y el diafragma en F2."},
            {"text": "En el primer foco geométrico (F1), justo en el centro de la descarga de gas.", "fraction": 0, "feedback": "Incorrecto. En F1 se sitúa la fuente luminosa (filamento, arco de xenón o chip LED)."},
            {"text": "En la superficie exterior de la lente de policarbonato.", "fraction": 0, "feedback": "Incorrecto. La lente exterior es transparente y lisa."},
            {"text": "En el interior del casquillo metálico del conector.", "fraction": 0, "feedback": "Incorrecto. El diafragma es un componente óptico interno."}
        ],
        general_feedback="<p>Proyector elipsoidal DE: F1 = Lámpara, F2 = Diafragma obturador, Lente = Proyección invertida.</p>"
    )

    # 3. Bixenón Solenoide
    builder.add_truefalse(
        "ALUM_P03_TF_Bixenon_Solenoide",
        "<p>En un sistema de faros Bixenón con un único proyector elipsoidal por lado, el cambio de luz de cruce a luz de carretera se efectúa mediante un solenoide electromecánico que abate la pantalla obturadora para permitir el paso del 100% del haz luminoso.</p>",
        True,
        feedback_true="¡Correcto! Una única lámpara de xenón realiza ambas funciones abatiendo la pantalla con un electroimán en milisegundos.",
        feedback_false="Incorrecto. Los proyectores Bixenón emplean una pantalla móvil gobernada por solenoide o motor eléctrico.",
        general_feedback="<p>Bixenón: Pantalla levantada = Cruce asimétrico / Pantalla abatida = Carretera total.</p>"
    )

    # 4. Umbral 2000 lm Lavafaros
    builder.add_multichoice(
        "ALUM_P04_MC_Umbral_2000lm_Regulacion",
        "<p>Según el Reglamento europeo ECE R48, ¿a partir de qué flujo luminoso es obligatorio que el vehículo incorpore sistema de limpieza de faros (lavafaros) y regulación automática del alcance luminoso?</p>",
        [
            {"text": "A partir de 2.000 lúmenes por proyector (como en las lámparas de xenón de 35W con 3.200 lm).", "fraction": 100, "feedback": "¡Correcto! Por debajo de 2.000 lm (ej. xenón D8S de 25W o LED estándar) están exentos."},
            {"text": "A partir de 1.000 lúmenes.", "fraction": 0, "feedback": "Incorrecto. Las lámparas halógenas H7 emiten unos 1.500 lm y no requieren lavafaros."},
            {"text": "A partir de 5.000 lúmenes.", "fraction": 0, "feedback": "Incorrecto. 5.000 lm es una cifra muy superior a la permitida en automoción."},
            {"text": "Únicamente en faros con tecnología láser.", "fraction": 0, "feedback": "Incorrecto. Aplica a cualquier fuente que supere 2.000 lm."}
        ],
        general_feedback="<p>ECE R48: Flujo > 2.000 lm exige regulación automática y lavafaros.</p>"
    )

    # 5. DRL y Túneles
    builder.add_truefalse(
        "ALUM_P05_TF_DRL_Tuneles_Peligro",
        "<p>Al circular en condiciones de baja visibilidad o en túneles con las Luces de Conducción Diurna (DRL) encendidas, los pilotos de posición traseros permanecen apagados, creando un grave riesgo de colisión por alcance en la parte posterior del vehículo.</p>",
        True,
        feedback_true="¡Correcto! Las DRL solo activan proyectores delanteros. De noche o en túneles se debe conectar el alumbrado de cruce para iluminar la zaga.",
        feedback_false="Incorrecto. La normativa ECE R87 no enciende las luces traseras con las DRL, dejando la zaga completamente a oscuras.",
        general_feedback="<p>Seguridad con DRL: No sustituyen a la luz de cruce; la zaga permanece apagada.</p>"
    )

    # 6. Cadencia Intermitentes
    builder.add_multichoice(
        "ALUM_P06_MC_Cadencia_Intermitencia_Reglamentaria",
        "<p>¿Cuál es la cadencia de parpadeo reglamentaria que debe mantener el sistema de intermitencia de dirección en todo momento según la normativa internacional?</p>",
        [
            {"text": "Entre 60 y 120 destellos por minuto (1 a 2 Hz).", "fraction": 100, "feedback": "¡Correcto! Es el intervalo legal exacto fijado por ECE R48."},
            {"text": "Entre 30 y 60 destellos por minuto.", "fraction": 0, "feedback": "Incorrecto. Una cadencia tan lenta retrasaría la advertencia de maniobra."},
            {"text": "Exactamente 180 destellos por minuto.", "fraction": 0, "feedback": "Incorrecto. 180 ppm es una cadencia anómala que indica bombilla fundida."},
            {"text": "Entre 20 y 40 destellos por minuto.", "fraction": 0, "feedback": "Incorrecto. Demasiado lento e inseguro."}
        ],
        general_feedback="<p>Frecuencia de intermitencia normalizada: 60 - 120 pulsaciones por minuto.</p>"
    )

    # 7. Warning Línea 30
    builder.add_truefalse(
        "ALUM_P07_TF_Warning_Linea_30",
        "<p>El circuito de las luces de emergencia (warning) se alimenta permanentemente desde la Línea 30 (+Bat) para garantizar su accionamiento inmediato incluso con el motor apagado y la llave de contacto retirada.</p>",
        True,
        feedback_true="¡Correcto! La señalización de peligro debe estar operativa en cualquier situación de avería o inmovilización del vehículo.",
        feedback_false="Incorrecto. El warning se conecta a Línea 30 directa de batería precisamente para no depender de la llave.",
        general_feedback="<p>Línea 30 directa de batería: Garantiza funcionamiento permanente del warning.</p>"
    )

    # 8. Modulación PWM
    builder.add_multichoice(
        "ALUM_P08_MC_Modulacion_PWM_Pilotos",
        "<p>¿Qué tecnología electrónica permite que un mismo grupo óptico LED o bombilla realice la función de luz de posición (4W) y luz de freno (21W) sobre el mismo filamento o chip?</p>",
        [
            {"text": "Modulación por Ancho de Pulso (PWM), variando el ciclo de trabajo (duty cycle) para regular la tensión eficaz y el brillo emitido.", "fraction": 100, "feedback": "¡Correcto! Al 15-20% genera luz de posición y al 100% luz de freno."},
            {"text": "Un transformador electromagnético reductor de 230V a 12V.", "fraction": 0, "feedback": "Incorrecto. En continua de 12V no se usan transformadores convencionales."},
            {"text": "Una resistencia variable accionada mecánicamente por el pedal de acelerador.", "fraction": 0, "feedback": "Incorrecto. Se gestiona de forma electrónica digital por la BCM."},
            {"text": "Un divisor resistivo térmico que disipa la energía en forma de calor.", "fraction": 0, "feedback": "Incorrecto. Sería altamente ineficiente y provocaría sobrecalentamiento."}
        ],
        general_feedback="<p>PWM: Control eficiente de potencia luminosa variando el tiempo de conducción.</p>"
    )

    # 9. Separación Antiniebla Freno 10 cm
    builder.add_multichoice(
        "ALUM_P09_MC_Separacion_Antiniebla_Freno",
        "<p>Según el Reglamento ECE R48, ¿cuál es la distancia física mínima obligatoria que debe existir entre la superficie iluminada del piloto antiniebla trasero y la luz de freno?</p>",
        [
            {"text": "100 mm (10 cm).", "fraction": 100, "feedback": "¡Correcto! Impide que la intensa luz del antiniebla enmascare la señal de parada."},
            {"text": "25 mm (2,5 cm).", "fraction": 0, "feedback": "Incorrecto. Demasiado cerca; confundiría al conductor trasero."},
            {"text": "500 mm (50 cm).", "fraction": 0, "feedback": "Incorrecto. No cabría en turismos compactos."},
            {"text": "No existe separación mínima reglamentada.", "fraction": 0, "feedback": "Incorrecto. La separación de 10 cm es mandatoria en homologación europea."}
        ],
        general_feedback="<p>ECE R48: Separación mínima de 10 cm entre antiniebla trasero y luz de freno.</p>"
    )

    # 10. Intensidad Antiniebla Trasero
    builder.add_multichoice(
        "ALUM_P10_MC_Intensidad_Antiniebla_Trasero",
        "<p>¿Cuál es el rango de intensidad luminosa normalizado en Europa para los pilotos antiniebla traseros?</p>",
        [
            {"text": "Entre 150 y 300 candelas.", "fraction": 100, "feedback": "¡Correcto! Es una luz de gran penetración visual para niebla densa."},
            {"text": "Entre 4 y 10 candelas.", "fraction": 0, "feedback": "Incorrecto. Ese es el rango de una luz de posición ordinaria."},
            {"text": "Entre 20.000 y 50.000 candelas.", "fraction": 0, "feedback": "Incorrecto. Esa intensidad corresponde a los faros de cruce o carretera."},
            {"text": "Exactamente 1.000 candelas.", "fraction": 0, "feedback": "Incorrecto. Deslumbraría masivamente a los vehículos cercanos."}
        ],
        general_feedback="<p>Piloto antiniebla trasero: 150 a 300 candelas de alta penetración.</p>"
    )

    # 11. Caída de Tensión Admisible Faros
    builder.add_multichoice(
        "ALUM_P11_MC_Caida_Tension_Faros_Principales",
        "<p>En el circuito de alimentación de los faros principales de cruce y carretera, ¿cuál es la caída de tensión máxima admisible en la línea positiva para evitar pérdidas severas de flujo luminoso?</p>",
        [
            {"text": "ΔV ≤ 0,3 V (o máximo 0,5 V en condiciones extremas).", "fraction": 100, "feedback": "¡Correcto! Una pérdida de 0,5V reduce el flujo un 15%; 1V de caída lo reduce un 28%."},
            {"text": "ΔV ≤ 2,5 V.", "fraction": 0, "feedback": "Incorrecto. A 2,5V de caída el faro apenas emitiría una luz amarillenta inútil."},
            {"text": "ΔV ≤ 4,0 V.", "fraction": 0, "feedback": "Incorrecto. Inadmisible en una red automotriz de 12V."},
            {"text": "No importa la caída mientras el fusible no se funda.", "fraction": 0, "feedback": "Incorrecto. La eficacia luminosa depende drásticamente de la tensión en bornes."}
        ],
        general_feedback="<p>Criterio de cálculo en automoción: ΔV ≤ 0,3V en faros principales.</p>"
    )

    # 12. Cálculo de Intensidad I = P / V
    builder.add_multichoice(
        "ALUM_P12_MC_Calculo_Intensidad_Halogena",
        "<p>¿Cuál es la corriente eléctrica que consumen dos lámparas halógenas H7 de 55 W cada una conectadas en paralelo a una batería de 12 V?</p>",
        [
            {"text": "Aproximadamente 9,17 A (P_total = 110 W; I = 110 / 12 = 9,166 A).", "fraction": 100, "feedback": "¡Correcto! I = P / V = (55 + 55) / 12 = 9,17 A."},
            {"text": "4,58 A.", "fraction": 0, "feedback": "Incorrecto. 4,58 A es el consumo de una sola bombilla."},
            {"text": "18,33 A.", "fraction": 0, "feedback": "Incorrecto. Has multiplicado la potencia por dos erróneamente."},
            {"text": "1,2 A.", "fraction": 0, "feedback": "Incorrecto. Revisa la Ley de Joule: I = P / V."}
        ],
        general_feedback="<p>I = P_total / V = 110 W / 12 V = 9,17 A.</p>"
    )

    # 13. Caída Regloscopio Turismos
    builder.add_multichoice(
        "ALUM_P13_MC_Inclinacion_Regloscopio_Turismos",
        "<p>¿Cuál es el porcentaje de inclinación o caída descendente reglamentaria del haz de cruce para un turismo estándar en el regloscopio?</p>",
        [
            {"text": "Entre el -1,0% y el -1,5% (generalmente -1,2% marcado en el proyector).", "fraction": 100, "feedback": "¡Correcto! Equivale a descender entre 25 y 37,5 cm a una distancia de 25 metros."},
            {"text": "0,0% perfectamente horizontal.", "fraction": 0, "feedback": "Incorrecto. Un haz horizontal causaría deslumbramiento con el cabeceo del vehículo."},
            {"text": "Entre el -3,5% y el -5,0%.", "fraction": 0, "feedback": "Incorrecto. Ese valor se reserva para camiones pesados muy elevados."},
            {"text": "+1,5% ascendente.", "fraction": 0, "feedback": "Incorrecto. Provocaría un deslumbramiento masivo ilegal."}
        ],
        general_feedback="<p>Regloscopio en turismos: Inclinación descendente de -1,0% a -1,5%.</p>"
    )

    # 14. Desreglaje +1% Deslumbramiento
    builder.add_multichoice(
        "ALUM_P14_MC_Efecto_Desreglaje_Deslumbramiento",
        "<p>Según los estudios de fotometría vial del RACE, ¿qué consecuencia tiene un desajuste de tan solo +1% hacia arriba en el reglaje de los faros de cruce?</p>",
        [
            {"text": "Multiplica por 20 el nivel de deslumbramiento hacia los conductores que circulan en sentido contrario.", "fraction": 100, "feedback": "¡Correcto! Eleva la línea de corte directamente hacia los ojos del conductor que viene de frente."},
            {"text": "Reduce el consumo de la batería un 20%.", "fraction": 0, "feedback": "Incorrecto. El reglaje mecánico no modifica la potencia eléctrica."},
            {"text": "Duplica la vida útil de la lámpara halógena.", "fraction": 0, "feedback": "Incorrecto. La durabilidad depende del filamento y la tensión."},
            {"text": "No produce ningún efecto apreciable en carretera.", "fraction": 0, "feedback": "Incorrecto. Es una de las causas principales de siniestralidad nocturna."}
        ],
        general_feedback="<p>Desreglaje +1% arriba = Deslumbramiento x20 / Desreglaje -2,5% abajo = Pérdida 50% alcance.</p>"
    )

    # 15. Caída de Tensión Masa 0,1V
    builder.add_multichoice(
        "ALUM_P15_MC_Caida_Tension_Masa_Tolerancia",
        "<p>Al diagnosticar una masa deficiente (Línea 31) en el casquillo de un faro con el voltímetro digital bajo carga, ¿cuál es el valor máximo admisible de caída de tensión?</p>",
        [
            {"text": "V_masa ≤ 0,1 V (idealmente < 0,05 V).", "fraction": 100, "feedback": "¡Correcto! Una lectura superior indica óxido, sulfatación o terminal flojo en el chasis."},
            {"text": "V_masa ≤ 1,5 V.", "fraction": 0, "feedback": "Incorrecto. 1,5V de caída en masa provocaría una pérdida crítica de luminosidad."},
            {"text": "V_masa = 12,0 V.", "fraction": 0, "feedback": "Incorrecto. 12V en masa indicaría una interrupción total del circuito (circuito abierto)."},
            {"text": "No se puede medir la masa con voltímetro.", "fraction": 0, "feedback": "Incorrecto. La medición de caída de tensión en masa en paralelo es el método estrella de taller."}
        ],
        general_feedback="<p>Límite metrológico en masa: V_masa ≤ 0,1V bajo carga.</p>"
    )

    # 16. Chequeo en Frío BCM
    builder.add_multichoice(
        "ALUM_P16_MC_Chequeo_Frio_BCM",
        "<p>¿En qué consiste el procedimiento de 'chequeo en frío' que realiza la unidad BCM sobre las lámparas del vehículo?</p>",
        [
            {"text": "En enviar microimpulsos de tensión de muy corta duración con la lámpara apagada para verificar la continuidad eléctrica del filamento sin llegar a encenderlo.", "fraction": 100, "feedback": "¡Correcto! Si no hay retorno de corriente, registra el fallo en el cuadro antes de accionar el mando."},
            {"text": "En enfriar el faro mediante ventiladores antes de encenderlo.", "fraction": 0, "feedback": "Incorrecto. La refrigeración es térmica, no un protocolo de chequeo eléctrico."},
            {"text": "En medir la temperatura ambiental del paragolpes.", "fraction": 0, "feedback": "Incorrecto. Es una prueba eléctrica de diagnóstico de lámpara."},
            {"text": "En desconectar la batería cuando hace frío.", "fraction": 0, "feedback": "Incorrecto. No tiene relación técnica."}
        ],
        general_feedback="<p>Chequeo en frío: Microimpulsos para medir continuidad con la lámpara apagada.</p>"
    )

    # 17. Desprendimiento Laca Ámbar RoHS
    builder.add_truefalse(
        "ALUM_P17_TF_Desprendimiento_Laca_Ambar",
        "<p>Debido a la prohibición del vidrio dopado con cadmio por la directiva europea RoHS, las bombillas ámbar de señalización actuales emplean lacas superficiales que pueden cuartearse con los ciclos térmicos, provocando que el intermitente emita luz blanca ilegal (defecto grave en ITV).</p>",
        True,
        feedback_true="¡Correcto! Es una de las averías más frecuentes en inspección técnica y exige sustituir la bombilla de inmediato.",
        feedback_false="Incorrecto. La pérdida de laca exterior es un fallo real y extendido tras la directiva medioambiental RoHS.",
        general_feedback="<p>Directiva RoHS: La degradación de la laca en bombillas ámbar provoca emisión de luz blanca ilegal.</p>"
    )

    # 18. Medición en Carga
    builder.add_truefalse(
        "ALUM_P18_TF_Medicion_En_Carga_Obligatoria",
        "<p>La medición voltimétrica de caídas de tensión en conductores, relés y masas debe realizarse obligatoriamente con el circuito encendido y consumiendo corriente (en carga), ya que con el circuito apagado (I = 0 A) la caída de tensión es matemáticamente cero.</p>",
        True,
        feedback_true="¡Correcto! Ley de Ohm: ΔV = I · R. Si no circula intensidad (I = 0), la caída de tensión en la resistencia parásita no se manifiesta.",
        feedback_false="Incorrecto. Sin corriente circulando es imposible detectar resistencias de contacto parásitas con el voltímetro.",
        general_feedback="<p>Regla de oro metrológica: Medir caídas de tensión SIEMPRE en carga.</p>"
    )

    # 19. Sensores Regulación Altura
    builder.add_multichoice(
        "ALUM_P19_MC_Sensores_Inclinacion_Suspension",
        "<p>¿Qué sensores y componentes integran el sistema de regulación automática dinámica del alcance luminoso en faros de xenón o LED de alta gama?</p>",
        [
            {"text": "Sensores de nivel (inductivos o resistivos) en los ejes delantero y trasero unidos por bieletas a la suspensión, calculador electrónico y servomotores paso a paso en los faros.", "fraction": 100, "feedback": "¡Correcto! Miden la inclinación de la carrocería en milisegundos compensando carga, aceleraciones y frenadas."},
            {"text": "Un acelerómetro en el salpicadero y cables mecánicos Bowden hasta los reflectores.", "fraction": 0, "feedback": "Incorrecto. Los cables mecánicos corresponden a reguladores manuales arcaicos."},
            {"text": "Cámaras ultrasónicas en las llantas de las cuatro ruedas.", "fraction": 0, "feedback": "Incorrecto. Se emplean sensores de ángulo en los brazos de suspensión."},
            {"text": "Un barómetro que mide la presión de inflado de los neumáticos.", "fraction": 0, "feedback": "Incorrecto. Eso corresponde al sistema TPMS de presión de neumáticos."}
        ],
        general_feedback="<p>Regulación automática dinámica: Sensores de altura en suspensión + Calculador + Motores paso a paso.</p>"
    )

    # 20. Luces Adaptativas Curvas
    builder.add_multichoice(
        "ALUM_P20_MC_Luces_Curvas_Estatica_Dinamica",
        "<p>¿Cuál es la diferencia técnica entre la luz de giro estática (cornering light) y la luz de curvas dinámica (faros direccionales)?</p>",
        [
            {"text": "La luz estática enciende a baja velocidad (<40 km/h) el antiniebla o lámpara lateral al poner el intermitente; la luz dinámica hace pivotar el proyector principal horizontalmente hasta 15° mediante un motor paso a paso.", "fraction": 100, "feedback": "¡Correcto! La estática ilumina cruces y giros cerrados; la dinámica acompaña el trazado de la carretera en velocidad."},
            {"text": "La luz estática solo funciona de día y la dinámica de noche.", "fraction": 0, "feedback": "Incorrecto. Ambas están diseñadas para conducción nocturna o túneles."},
            {"text": "La luz dinámica sustituye a las luces de freno traseras.", "fraction": 0, "feedback": "Incorrecto. Son sistemas frontales de visibilidad de calzada."},
            {"text": "No existe diferencia; son dos nombres comerciales para el mismo sistema.", "fraction": 0, "feedback": "Incorrecto. Son arquitecturas electromecánicas completamente distintas."}
        ],
        general_feedback="<p>Luz de giro estática = Lámpara lateral a baja velocidad / Luz dinámica = Pivotado de lente en carretera.</p>"
    )

    # 21. Tercera Luz S3 Desviación
    builder.add_truefalse(
        "ALUM_P21_TF_Tercera_Luz_Desviacion_15cm",
        "<p>En vehículos comerciales con portón trasero de apertura asimétrica (dos puertas batientes), la normativa europea ECE R48 autoriza que la tercera luz de freno elevada (S3) se desplace como máximo 15 cm respecto al eje de simetría central del vehículo.</p>",
        True,
        feedback_true="¡Correcto! Se contempla esta excepción geométrica exclusiva de 15 cm en furgones de carga.",
        feedback_false="Incorrecto. La normativa ECE R48 permite específicamente una tolerancia de hasta 15 cm en portones asimétricos.",
        general_feedback="<p>ECE R48: Tolerancia máxima de 15 cm en tercera luz de freno en portones asimétricos.</p>"
    )

    # 22. Color Luces Marcha Atrás
    builder.add_multichoice(
        "ALUM_P22_MC_Color_Marcha_Atras_AR",
        "<p>En el marco reglamentario internacional vigente, ¿de qué color debe ser obligatoriamente la luz de marcha atrás (código AR)?</p>",
        [
            {"text": "Color blanco continuo.", "fraction": 100, "feedback": "¡Correcto! Advierte de la maniobra de retroceso e ilumina el entorno posterior."},
            {"text": "Color ámbar fijo.", "fraction": 0, "feedback": "Incorrecto. Aunque fue admitido en algunos países en el siglo XX, hoy es blanco estricto."},
            {"text": "Color rojo de alta intensidad.", "fraction": 0, "feedback": "Incorrecto. El rojo se reserva para posición, freno y antiniebla trasero."},
            {"text": "Color azul intermitente.", "fraction": 0, "feedback": "Incorrecto. El azul está reservado a vehículos de policía y emergencias."}
        ],
        general_feedback="<p>Luz de marcha atrás AR: Color blanco continuo obligatorio.</p>"
    )

    # 23. Bornes Normalizados DIN
    builder.add_matching(
        "ALUM_P23_Matching_Bornes_DIN_Alumbrado",
        "<p>Relaciona cada borne normalizado según la norma DIN 72552 con su función específica en el circuito de alumbrado y señalización:</p>",
        [
            ("Borne 56b", "Salida de alimentación para luz de cruce (corto alcance)"),
            ("Borne 56a", "Salida de alimentación para luz de carretera (largo alcance)"),
            ("Borne 58", "Circuito de luces de posición, gálibo e iluminación de mandos"),
            ("Borne 49a", "Salida pulsante intermitente desde el relé hacia el mando")
        ],
        general_feedback="<p>Norma DIN 72552: 56b = Cruce, 56a = Carretera, 58 = Posición, 49a = Intermitente pulsante.</p>"
    )

    # 24. Códigos Homologación ECE
    builder.add_matching(
        "ALUM_P24_Matching_Codigos_Homologacion_ECE",
        "<p>Empareja cada código de homologación europeo grabado en los grupos ópticos con su función reglamentaria:</p>",
        [
            ("RL", "Luz de conducción diurna (Daytime Running Light)"),
            ("AR", "Luz de marcha atrás"),
            ("B o F3", "Faro antiniebla delantero"),
            ("S3", "Tercera luz de freno central elevada")
        ],
        general_feedback="<p>Códigos ECE: RL = Diurna, AR = Marcha atrás, B/F3 = Antiniebla delantero, S3 = 3ª luz freno.</p>"
    )

    # 25. Requisitos de Seguridad Xenón
    builder.add_multichoice(
        "ALUM_P25_MC_Seguridad_Alta_Tension_Xenon",
        "<p>Durante la manipulación o sustitución de una lámpara de xenón en el taller, ¿por qué es obligatorio desconectar la batería o el conector del faro antes de intervenir?</p>",
        [
            {"text": "Porque el cebador o transformador de encendido genera un pico de alta tensión de 20.000 a 30.000 V (20-30 kV) que supone riesgo mortal de electrocución.", "fraction": 100, "feedback": "¡Correcto! El arco eléctrico inicial requiere hasta 30 kV para ionizar el gas xenón."},
            {"text": "Para evitar que el gas xenón se escape a la atmósfera.", "fraction": 0, "feedback": "Incorrecto. La ampolla de cuarzo es hermética y no se abre."},
            {"text": "Porque la bombilla de xenón funciona con imanes de neodimio permanentes.", "fraction": 0, "feedback": "Incorrecto. No contiene imanes."},
            {"text": "Para resetear el cuentakilómetros del vehículo.", "fraction": 0, "feedback": "Incorrecto. No tiene relación con el odómetro."}
        ],
        general_feedback="<p>Seguridad en faros de descarga: Pico de cebado de 20 a 30 kV. Desconectar siempre la alimentación antes de intervenir.</p>"
    )

    builder.save_xml(output_xml_path)
    validar_moodle_xml(output_xml_path)


if __name__ == '__main__':
    dest_pkg = os.path.join(SCRIPT_DIR, "Curso_Circuitos_Alumbrado_Automocion.h5p")
    build_h5p_course(dest_pkg)

    # Generar y validar banco sumativo Moodle XML
    xml_path = os.path.join(SCRIPT_DIR, "evaluacion_circuitos_alumbrado.xml")
    generar_evaluacion_alumbrado_xml(xml_path)
