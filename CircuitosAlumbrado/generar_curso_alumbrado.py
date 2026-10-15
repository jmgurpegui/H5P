#!/usr/bin/env python3
"""
Generador Maestro del Curso H5P: Circuitos de Alumbrado y Señalización del Automóvil.
Curso Interactivo Homologado para Formación Profesional en Automoción (EducaMadrid).

ARQUITECTURA PEDAGÓGICA Y TÉCNICA DESACOPLADA:
1. Paquete H5P 100% Formativo e Ilustrado (InteractiveBook 1.7):
   - Exposición didáctica interactiva, esquemas técnicos y figuras de referencia 4K extraídas del vídeo de taller.
   - Sin actividades evaluativas o de arrastre internas (eliminación de DragText y MultiChoice en H5P) para
     evitar problemas de registro de realización en Moodle y garantizar máxima fluidez táctil en smartphones.
   - Trazabilidad y finalización en Moodle 100% fiable: "El estudiante debe ver la actividad para completarla".
2. Evaluación Sumativa Oficial Centralizada en Moodle XML:
   - Banco de 25 preguntas psicométricamente calibradas (sin sesgo de longitud, opciones balanceadas, barajado aleatorio).
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

# Rutas del entorno
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTILLA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "plantilla"))
if not os.path.exists(PLANTILLA_DIR):
    PLANTILLA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "plantilla"))

LIB_DIR = os.path.join(SCRIPT_DIR, "..", "h5p_builder", "h5p-libraries")
if not os.path.exists(LIB_DIR):
    LIB_DIR = os.path.join(PLANTILLA_DIR, "h5p-libraries")

# Importar validador y generador de Moodle XML
sys.path.insert(0, PLANTILLA_DIR)
from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
from validar_h5p_educamadrid import validate_h5p

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
    {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
    {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
    {"machineName": "H5P.Column", "majorVersion": 1, "minorVersion": 16},
    {"machineName": "H5P.InteractiveBook", "majorVersion": 1, "minorVersion": 7}
]


# =========================================================================
# 1. HELPERS DE MAQUETACIÓN RESPONSIVE H5P
# =========================================================================

def resolve_institutional_logo():
    """Localiza y valida el logotipo institucional homologado de EducaMadrid."""
    candidates = [
        os.path.join(SCRIPT_DIR, "images", "logo2026.png"),
        os.path.join(PLANTILLA_DIR, "logo2026.png"),
        os.path.join(SCRIPT_DIR, "images", "logo_educamadrid.png"),
        os.path.join(SCRIPT_DIR, "logo2026.png")
    ]
    for path in candidates:
        if os.path.exists(path):
            fname = os.path.basename(path)
            return {
                "rel_path": f"images/{fname}",
                "src_path": os.path.abspath(path),
                "filename": fname,
                "width": 800,
                "height": 180,
                "alt": "Comunidad de Madrid - Consejería de Educación, Ciencia y Universidades (EducaMadrid)"
            }
    return {
        "rel_path": "images/logo2026.png",
        "src_path": None,
        "filename": "logo2026.png",
        "width": 800,
        "height": 180,
        "alt": "EducaMadrid - Formación Profesional"
    }

def create_column_wrapper(library_str, params_dict, title_str="Sección"):
    """Envuelve cualquier elemento hijo en H5P.Column 1.16."""
    return {
        "content": {
            "library": library_str,
            "params": params_dict,
            "subContentId": str(uuid.uuid4()),
            "metadata": {
                "title": title_str,
                "contentType": library_str.split()[0].replace('H5P.', ''),
                "license": "CC BY-SA",
                "authors": [{"name": "Departamento de Formación Profesional - Automoción", "role": "Author"}]
            }
        },
        "useSeparator": "auto"
    }

def create_header_logo():
    """Genera el bloque institucional en la cabecera de cada capítulo."""
    logo = resolve_institutional_logo()
    return create_column_wrapper("H5P.Image 1.1", {
        "contentName": "Image",
        "file": {
            "path": logo["rel_path"],
            "mime": "image/png",
            "copyright": {"license": "U"},
            "width": logo["width"],
            "height": logo["height"]
        },
        "alt": logo["alt"]
    }, "Cabecera Institucional EducaMadrid")

def create_image_section(rel_path, alt_text, title="Imagen Técnica", width=None, height=None):
    """Crea un bloque nativo H5P.Image 1.1 homologado con alt text descriptivo obligatorio y dimensiones automáticas."""
    if width is None or height is None:
        local_path = os.path.join(SCRIPT_DIR, rel_path)
        if os.path.exists(local_path):
            try:
                from PIL import Image
                with Image.open(local_path) as img:
                    width, height = img.size
            except Exception:
                width, height = (1200, 680)
        else:
            width, height = (1200, 680)
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

def create_video_section(video_url, title="Vídeo Técnico Demostrativo"):
    """Crea un bloque nativo H5P.Video 1.6 homologado para incrustación de vídeo técnico."""
    return create_column_wrapper("H5P.Video 1.6", {
        "sources": [
            {
                "path": video_url,
                "mime": "video/YouTube"
            }
        ],
        "visuals": {
            "fit": True,
            "controls": True
        },
        "playback": {
            "autoplay": False,
            "loop": False
        }
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
                "metadata": {
                    "title": p_title,
                    "contentType": "Text",
                    "license": "CC BY-SA",
                    "authors": [{"name": "Departamento de Formación Profesional - Automoción", "role": "Author"}]
                }
            }
        })
    return create_column_wrapper("H5P.Accordion 1.0", {"panels": panels}, title)

def create_active_challenge(title, scenario_html, steps, badge_text="Reto Práctico de Taller"):
    """Crea un reto pedagógico contextualizado de taller con toma de decisiones diagnósticas."""
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

def create_image_hotspots(img_rel_path, hotspots_data, title="Esquema Técnico Interactivo", img_w=1200, img_h=680, alt_desc="Esquema con puntos de inspección"):
    """Genera un componente H5P.ImageHotspots 1.10 para exploración táctil."""
    hotspots = []
    for x, y, hs_title, hs_html in hotspots_data:
        hotspots.append({
            "position": {"x": x, "y": y},
            "header": hs_title,
            "content": [
                {
                    "library": "H5P.Text 1.1",
                    "params": {"text": hs_html},
                    "subContentId": str(uuid.uuid4()),
                    "metadata": {
                        "title": hs_title,
                        "contentType": "Text",
                        "license": "CC BY-SA",
                        "authors": [{"name": "Departamento de Formación Profesional - Automoción", "role": "Author"}]
                    }
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

def create_moodle_quiz_referral(chapter_num, title, summary_html):
    """Genera una tarjeta de síntesis y derivación directa al Cuestionario Oficial Sumativo Moodle XML."""
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
          Has revisado todos los contenidos técnicos, esquemas y figuras de referencia de este capítulo. 
          Para registrar tu calificación oficial de evaluación sumativa con validez académica, accede al 
          <strong>Cuestionario Oficial de Evaluación en Moodle</strong> (módulo <code>mod_quiz</code>).
        </p>
      </div>
    </div>
    """
    return create_text_section(html, f"Síntesis Capítulo {chapter_num}")

def create_didactic_chapter(title, sections):
    """Construye un capítulo modular encapsulado en H5P.Column con cabecera y secciones formativas."""
    full_sections = [create_header_logo()]
    full_sections.extend(sections)
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
            "content": full_sections
        }
    }


# =========================================================================
# 2. DEFINICIÓN DIDÁCTICA Y TÉCNICA DE LOS 5 CAPÍTULOS ILUSTRADOS
# =========================================================================

def build_chapter_1():
    """Capítulo 1: Alumbrados de Posición, Cruce y Carretera y su Conmutación"""
    sections = []

    # 1. Motivación y Reto
    sections.append(create_text_section("""
    <div class="tech-hero">
      <div class="tech-badge"><i class="fa fa-lightbulb-o"></i> CAPÍTULO 1 · ALUMBRADO PRINCIPAL</div>
      <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Circuitos de Posición, Cruce, Carretera y Encendido Automático</h2>
      <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
        El 90% de la información requerida para la toma de decisiones al volante se percibe mediante la vista.
        De noche, la capacidad visual se reduce al 20%, y el 42% de los accidentes mortales se concentran en condiciones de oscuridad.
        Dominar la arquitectura de los circuitos principales de iluminación, su distribución en el vehículo, normativas de homologación y tecnologías ópticas es un pilar crítico en electromecánica.
      </p>
    </div>
    """, "Introducción Capítulo 1"))

    sections.append(create_active_challenge(
        title="Reto de Taller: Deslumbramiento e Iluminación Asimétrica",
        scenario_html="<p>Un cliente acude al taller tras ser rechazado en la ITV por deslumbrar en luz de cruce con su vehículo equipado con proyectores Bixenón. El conductor afirma haber cambiado recientemente la lámpara D2S en otro taller. Además, en carretera de montaña nota que el haz no se ensancha hacia el arcén derecho.</p>",
        steps=[
            ("Paso 1 (Inspección Mecánica y Óptica)", "Comprobar el asentamiento de la lámpara en el foco F1 del proyector elipsoidal DE y el estado del diafragma obturador a 15°."),
            ("Paso 2 (Verificación de Regulación)", "Verificar los sensores de inclinación en los ejes de suspensión y el servomotor de corrección automática del alcance luminoso."),
            ("Paso 3 (Alineación en Regloscopio)", "Medir con regloscopio óptico a 25 m para certificar la línea de corte horizontal izquierda y la elevación del 15% hacia el arcén.")
        ],
        badge_text="Reto Inicial de Taller"
    ))

    # 2. Explicación Técnica e Imágenes de Referencia
    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-book"></i> DISTRIBUCIÓN DE FUENTES DE LUZ</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">1.1 Distribución y Tipología Normalizada de Lámparas en el Automóvil</h3>
      <p style="color:#1e293b; line-height:1.6;">
        El diseño luminotécnico del vehículo integra fuentes de luz adaptadas a las funciones de alumbrado (ver la carretera) y señalización (ser visto y advertir maniobras). La siguiente figura de referencia muestra la disposición perimétrica de las lámparas reglamentarias en la carrocería:
      </p>
    </div>
    """, "Distribución de Lámparas"))

    sections.append(create_image_section(
        "images/figura_distribucion_lamparas_vehiculo.png",
        "Figura 5.6: Ejemplo de lámparas empleadas para alumbrado y señalización en el vehículo (luces de cruce, posición, intermitencia, freno, antiniebla)",
        "Distribución Perimétrica de Lámparas en el Vehículo",
        1210, 1440
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-certificate"></i> HOMOLOGACIÓN Y NORMAS ECE</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">1.2 Marcado de Homologación ECE en Lámparas Halógenas</h3>
      <p style="color:#1e293b; line-height:1.6;">
        La normativa europea ECE R37 establece la obligatoriedad de que toda lámpara comercializada para automoción incorpore en su casquillo metálico la información reglamentaria indeleble:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Marca del fabricante y denominación internacional:</strong> H1, H4, H7, etc.</li>
        <li><strong>Tensión y potencia nominal:</strong> Ej. 12 V 55 W.</li>
        <li><strong>País de homologación:</strong> Letra 'E' en círculo acompañada del código del país (ej. <code>E1</code> Alemania, <code>E9</code> España, <code>E2</code> Francia).</li>
        <li><strong>Símbolo 'U':</strong> Indica emisión de radiación UV reducida, imprescindible para no amarillear los dispersores termoplásticos de policarbonato.</li>
        <li><strong>Marcado 'DOT':</strong> Cumplimiento para el mercado estadounidense (Department of Transportation).</li>
      </ul>
    </div>
    """, "Marcado de Homologación"))

    sections.append(create_image_section(
        "images/figura_marcado_lampara_h7.png",
        "Figura 5.38: Ejemplo de inscripción y marcado de homologación en casquillo de lámpara H7 de Osram",
        "Marcado Reglamentario en Casquillo de Lámpara H7",
        894, 894
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-eye"></i> ÓPTICA GEOMÉTRICA DE FAROS</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">1.3 Principios de Reflexión y Formación del Haz Asimétrico</h3>
      <p style="color:#1e293b; line-height:1.6;">
        El diseño del reflector define la dirección del haz luminoso respecto a la fuente:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Foco geométrico coincidente con la fuente (F):</strong> Los rayos reflejados salen paralelos (luz de carretera).</li>
        <li><strong>Foco situado antes de la fuente:</strong> Los rayos reflejados son convergentes.</li>
        <li><strong>Foco situado después de la fuente:</strong> Los rayos reflejados son divergentes.</li>
      </ul>
      <p style="color:#1e293b; line-height:1.6;">
        En el <strong>haz de cruce europeo</strong>, una pantalla antideslumbrante colocada bajo el filamento bloquea los rayos inferiores que deslumbrarían hacia arriba, proyectando una línea de corte horizontal nítida a la izquierda y una elevación asimétrica a 15° hacia el arcén derecho.
      </p>
    </div>
    """, "Óptica de Faros"))

    sections.append(create_image_section(
        "images/figura_optica_paraboloides_haz.png",
        "Figuras 5.42, 5.43, 5.44: Principios de reflexión óptica en reflectores paraboloides (rayos paralelos, convergentes y divergentes)",
        "Reflexión Óptica en Reflectores Paraboloides",
        1180, 350
    ))

    sections.append(create_image_section(
        "images/figura_optica_pantalla_cruce.png",
        "Figura 5.46: Faro con lámpara de doble filamento y pantalla antideslumbrante para haz de cruce",
        "Formación del Haz Asimétrico con Pantalla de Cruce",
        880, 460
    ))

    sections.append(create_image_section(
        "images/figura_faro_elipsoidal_de.png",
        "Figura 5.47 y 5.48: Óptica de proyector elipsoidal DE y reflectores de geometría libre Free Form (FF)",
        "Proyector Elipsoidal DE y Tecnología Free Form (FF)",
        1180, 480
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-cogs"></i> CONEXIONADO DE POTENCIA DIN 72552</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">1.4 Esquema Eléctrico con Relés y Fusibles Independientes</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Para evitar caídas de tensión en el mando del conductor y prevenir fallos catastróficos, la instalación eléctrica de alumbrado principal desacopla el mando de los circuitos de potencia mediante relés automotrices:
      </p>
      <div class="tech-formula-block">
        Línea 30 (+Bat) ➔ Contactos Relé (30-87) ➔ Fusibles F1/F2 (10A c/u) ➔ Lámparas Cruce (Borne 56b)
        <br />
        Línea 15 (+Contacto) ➔ Mando Luces (Borne 56) ➔ Conmutador ➔ Bobina Relé (86-85) ➔ Masa (Borne 31)
      </div>
    </div>
    """, "Esquema Eléctrico"))

    sections.append(create_image_section(
        "images/esquema_alumbrado_reles.png",
        "Esquema eléctrico normalizado DIN con relés para alumbrado de cruce 56b y carretera 56a",
        "Circuito de Alumbrado con Relés Normalizados DIN",
        335, 597
    ))

    # 3. Protocolo Técnico de Taller
    sections.append(create_image_hotspots("images/proyector_elipsoidal_de.png", [
        (19, 47, "Foco F1: Fuente Luminosa", "<p>Lámpara halógena, de xenón o emisor LED ubicada en el primer foco de la elipse reflectante.</p>"),
        (35, 47, "Foco F2: Diafragma Asimétrico", "<p>Pantalla obturadora colocada en el segundo foco que perfila el corte asimétrico europeo a 15°.</p>"),
        (35, 80, "Solenoide Bixenón", "<p>Electroimán que abate el diafragma hacia abajo al activar las luces de carretera, dejando pasar el haz total.</p>"),
        (48, 47, "Lente Proyectora Convergente", "<p>Lente asférica que proyecta la imagen invertida del diafragma nítidamente sobre la calzada.</p>"),
        (80, 50, "Alcance en Arcén Derecho", "<p>Ilumina hasta 75 metros por el margen derecho sin deslumbrar a los vehículos que se aproximan de frente.</p>")
    ], "Exploración Interactiva: Componentes del Proyector DE"))

    sections.append(create_accordion([
        ("Comprobación de Caída de Tensión en Faros Principales",
         "<p>Con el motor en marcha y luces encendidas, medir con multímetro en paralelo: la caída entre el borne (+) de batería y el borne de la lámpara debe ser <strong>ΔV ≤ 0,3 V</strong>. En masa (borne negativo de lámpara a borne (-) de batería) debe ser <strong>ΔV ≤ 0,1 V</strong>.</p>"),
        ("Sustitución Segura de Lámparas Halógenas H7",
         "<p>Nunca tocar el cristal de cuarzo directamente con los dedos: las grasas de la piel se carbonizan por el calor extremo (>600 °C) provocando puntos calientes y la rotura prematura de la ampolla. Utilizar guantes limpios de nitrilo o papel limpio.</p>"),
        ("Verificación del Mando de Luces y Bornes DIN",
         "<p>Borne 30: +12V permanente. Borne 15: +12V bajo contacto. Borne 56: Entrada al conmutador de cruce/carretera. Borne 56a: Salida a carretera. Borne 56b: Salida a cruce. Borne 58: Posición.</p>")
    ], "Protocolos de Taller: Alumbrado Principal"))

    sections.append(create_checklist_section(
        "Puntos de Control Pre-ITV: Alumbrado Principal",
        [
            "Verificar encendido simultáneo de luces de posición delanteras y traseras con cruce y carretera.",
            "Comprobar corte asimétrico nítido en ambos proyectores sin difuminado ni sombras anormales.",
            "Asegurar funcionamiento del testigo azul de luz de carretera en el cuadro de mandos.",
            "Inspeccionar estado de los dispersores de policarbonato: ausencia de opacidad y fisuras."
        ]
    ))

    # 4. Síntesis y Derivación a Moodle XML
    sections.append(create_moodle_quiz_referral(
        1, "Circuitos de Alumbrado Principal",
        "<p>Has estudiado la tipología de lámparas automotrices, el marcado de homologación ECE R37, los fundamentos ópticos del haz asimétrico de 15° y el conexionado de potencia con relés DIN 72552.</p>"
    ))

    return create_didactic_chapter("Capítulo 1: Alumbrados de Posición, Cruce y Carretera", sections)


def build_chapter_2():
    """Capítulo 2: Señalización Óptica y Maniobra (Intermitencias, DRL, Freno y Marcha Atrás)"""
    sections = []

    # 1. Motivación y Reto
    sections.append(create_text_section("""
    <div class="tech-hero">
      <div class="tech-badge"><i class="fa fa-arrows-alt"></i> CAPÍTULO 2 · SEÑALIZACIÓN Y MANIOBRA</div>
      <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Intermitencias, Emergencia, Frenado y Marcha Atrás</h2>
      <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
        La señalización óptica comunica las intenciones del conductor a los demás usuarios de la vía.
        Los estudios de la NHTSA demostraron que el empleo de intermitentes ámbar en la zaga reduce hasta en un 28% los choques por alcance frente al color rojo.
        Analizaremos los circuitos de intermitencia con supervisión de carga, luces de freno adaptativas, modulación PWM, tecnología Matrix LED y faros láser.
      </p>
    </div>
    """, "Introducción Capítulo 2"))

    sections.append(create_active_challenge(
        title="Reto de Taller: Intermitencia Acelerada tras un Golpe Trasero",
        scenario_html="<p>Tras reparar un golpe en la aleta trasera izquierda de un vehículo, el cliente nota que al accionar el intermitente izquierdo la cadencia de parpadeo y el sonido del relé en el cuadro se duplica a más de 180 pulsaciones por minuto, mientras que el lado derecho parpadea al ritmo normal de 80 ppm.</p>",
        steps=[
            ("Paso 1 (Comprensión del Circuito)", "Recordar que el relé de intermitencia incorpora un circuito comparador de corriente para supervisión de carga."),
            ("Paso 2 (Inspección del Piloto)", "Comprobar el piloto trasero izquierdo: la lámpara P21W está desconectada o fundida, reduciendo el consumo nominal de 42W a 21W."),
            ("Paso 3 (Resolución)", "Sustituir la bombilla de 21W o reparar el mazo de cables para restablecer el consumo y la frecuencia normal de 60-120 ppm.")
        ],
        badge_text="Reto de Taller: Diagnóstico de Carga"
    ))

    # 2. Explicación Técnica e Imágenes de Referencia
    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-book"></i> CIRCUITOS DE INTERMITENCIA Y WARNING</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">2.1 Esquema Eléctrico y Reglamentación ECE R48</h3>
      <p style="color:#1e293b; line-height:1.6;">
        La normativa fija una cadencia obligatoria de <strong>60 a 120 destellos por minuto</strong> (1 a 2 Hz). El conmutador de luces de emergencia (warning) se alimenta permanentemente de la <strong>Línea 30 (+Bat)</strong> para funcionar incluso con la llave de contacto quitada y el vehículo estacionado.
      </p>
    </div>
    """, "Intermitencia y Warning"))

    sections.append(create_image_section(
        "images/esquema_intermitencia_warning.png",
        "Esquema eléctrico normalizado de intermitencia y conmutador de luces de emergencia con relé DIN 49, 49a y masa 31",
        "Circuito Eléctrico de Intermitencia y Emergencia (Warning)",
        496, 618
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-sliders"></i> MODULACIÓN PWM EN SEÑALIZACIÓN</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">2.2 Control por Modulación por Ancho de Pulso (PWM)</h3>
      <p style="color:#1e293b; line-height:1.6;">
        En la electrónica de carrocería (BCM), una misma fuente luminosa (bombilla de un polo o módulo LED) asume dos funciones variando el ciclo de trabajo de la señal cuadrada PWM:
      </p>
      <div class="tech-formula-block">
        Luz de Posición Trasera ➔ Señal PWM con Duty Cycle al 25% (Brillo tenue, consumo reducido)
        <br />
        Luz de Frenado ➔ Señal PWM con Duty Cycle al 100% (Tensión continua completa de 12V, máxima intensidad)
      </div>
    </div>
    """, "Señales PWM"))

    sections.append(create_image_section(
        "images/figura_senales_pwm_senalizacion.png",
        "Figura 5.132: Señales de modulación PWM con distintos ciclos de trabajo (0%, 25%, 50%, 75%, 100%) aplicadas a señalización vehicular",
        "Modulación PWM en Pilotos Traseros de Señalización",
        1180, 540
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-car"></i> SEGURIDAD ACTIVA</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">2.3 Luces de Freno Adaptativas de Emergencia</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Los sistemas de frenado adaptativo modulan la señal luminosa trasera en función de la deceleración registrada por los sensores del ABS/ESP:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Frenada moderada:</strong> Se encienden los segmentos primarios de freno de manera convencional.</li>
        <li><strong>Frenada más enérgica:</strong> Se ilumina una superficie ampliada del piloto aumentando el número de ledes activos.</li>
        <li><strong>Frenada de emergencia (a fondo / disparo ABS >50 km/h):</strong> Las luces de freno parpadean a alta frecuencia (3-5 Hz). Si el vehículo se detiene totalmente, se activan automáticamente los intermitentes de emergencia (warning).</li>
      </ul>
    </div>
    """, "Freno Adaptativo"))

    sections.append(create_image_section(
        "images/figura_luces_freno_adaptativo.png",
        "Figuras 5.134, 5.135, 5.136: Comportamiento de las luces de freno adaptativas según la energía de deceleración",
        "Luces de Freno Adaptativas según Intensidad de Frenada",
        1180, 420
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-microchip"></i> TECNOLOGÍA LED Y LÁSER</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">2.4 Faros Full LED, Matrix LED e Iluminación Láser de Alta Eficiencia</h3>
      <p style="color:#1e293b; line-height:1.6;">
        La tecnología LED para faros principales se basa en módulos multichip de alta potencia sobre sustratos cerámicos, refrigerados activamente.
      </p>
      <p style="color:#1e293b; line-height:1.6;">
        Los faros <strong>Matrix LED</strong> emplean matrices de diodos controlados individualmente mediante multiplexado por la unidad electrónica. Al circular de noche, la cámara frontal detecta otros vehículos y apaga selectivamente solo los ledes que deslumbrarían al conductor contrario, manteniendo iluminado el resto de la escena con luz de carretera ininterrumpida.
      </p>
      <p style="color:#1e293b; line-height:1.6;">
        Los <strong>faros láser</strong> alcanzan hasta <strong>600 metros</strong> de proyección (el doble que un LED convencional). Tres diodos láser emiten luz azul monocromática que atraviesa un prisma y una lente de fósforo fluorescente, convirtiéndola en luz blanca pura (5.500 K) extremadamente brillante y segura.
      </p>
    </div>
    """, "Matrix LED y Láser"))

    sections.append(create_image_section(
        "images/figura_tecnologia_faros_led.png",
        "Evolución y módulos de tecnología de faros Full LED para automoción: matriz de ledes, disipador térmico y proyectores elipsoidales",
        "Tecnología y Módulos de Faros LED en Automoción",
        2560, 1439
    ))

    sections.append(create_image_section(
        "images/figura_despiece_faro_matrix_led.png",
        "Figura 5.90: Componentes y despiece de un faro Matrix LED de Audi (módulos multichip, disipadores, ventilador y UCE)",
        "Arquitectura y Despiece de Faro Matrix LED",
        1180, 540
    ))

    sections.append(create_image_section(
        "images/figura_faro_laser_alcance_comparativa.png",
        "Figura 5.109: Comparativa de alcance fotométrico entre haz halógeno, cruce LED, carretera LED y luz láser (600 m)",
        "Alcance Fotométrico Comparativo de Tecnologías de Iluminación",
        1160, 290
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-video-camera"></i> VÍDEO TÉCNICO DE REFERENCIA · HELLA TECH WORLD</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">Vídeo Demostrativo de Taller: Sustitución y Calibración de Faro Matrix LED</h3>
      <p style="color:#1e293b; line-height:1.6;">
        En este vídeo técnico oficial del canal de referencia <strong>HELLA TECH WORLD</strong> (fabricante líder en iluminación automotriz), se demuestra el protocolo completo de sustitución de un faro Matrix LED en taller, incluyendo precauciones electrostáticas (ESD), verificación de buses y codificación de unidades de control:
      </p>
    </div>
    """, "Vídeo HELLA Matrix LED"))

    sections.append(create_video_section(
        "https://www.youtube.com/watch?v=wAoESig-TzQ",
        "HELLA TECH WORLD: Sustitución de un faro Matrix LED"
    ))

    # 3. Protocolos de Taller
    sections.append(create_accordion([
        ("Diagnosis de Intermitencia Rápida (Cadencia >120 ppm)",
         "<p>Indica caída de consumo en la línea por bombilla fundida o mal contacto. En faros con LED retrofit, al consumir apenas 2W en lugar de 21W, el relé interpreta bombilla fundida. Requiere reprogramar la BCM o instalar una resistencia de carga en paralelo.</p>"),
        ("Gestión Térmica en Faros LED",
         "<p>Los ledes no emiten calor por radiación frontal en el haz, sino por conducción hacia su placa trasera. Por ello, incorporan disipadores de aluminio con aletas y ventiladores eléctricos regulados por termistores NTC para evitar degradación a >85 °C.</p>"),
        ("Tercera Luz de Freno Central (S3)",
         "<p>Obligatoria en la UE desde 1998. Debe situarse sobreelevada en el eje longitudinal central del vehículo. En portones asimétricos o de doble puerta, la desviación máxima autorizada es de 15 cm.</p>")
    ], "Protocolos de Taller: Señalización y Faros LED"))

    sections.append(create_checklist_section(
        "Verificación de Maniobra y Señalización",
        [
            "Cadencia de intermitencia: 60 a 120 destellos/minuto simétrica en ambos lados.",
            "Funcionamiento de luces de emergencia sin llave de contacto (Línea 30 directa).",
            "Conmutación instantánea de luz de marcha atrás al engranar R con contacto (Línea 15).",
            "Comprobación de no desprendimiento de laca ámbar en bombillas de intermitente."
        ]
    ))

    # 4. Síntesis y Moodle XML
    sections.append(create_moodle_quiz_referral(
        2, "Señalización Óptica y Maniobra",
        "<p>Has asimilado el funcionamiento del circuito de intermitencia con aviso por sobrecadencia, el control por señales PWM, las luces de freno adaptativas de 3 fases y la tecnología de faros Matrix LED y láser.</p>"
    ))

    return create_didactic_chapter("Capítulo 2: Señalización Óptica y Maniobra", sections)


def build_chapter_3():
    """Capítulo 3: Alumbrado Especial, Antiniebla y Faros de Descarga de Xenón"""
    sections = []

    # 1. Motivación y Reto
    sections.append(create_text_section("""
    <div class="tech-hero">
      <div class="tech-badge"><i class="fa fa-bolt"></i> CAPÍTULO 3 · ALUMBRADO ESPECIAL Y XENÓN</div>
      <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Faros Antiniebla, Sistemas de Descarga de Xenón y Sensores Automáticos</h2>
      <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
        Bajo niebla densa o lluvia torrencial, un haz mal orientado crea el fenómeno de 'pared blanca' por dispersión de Rayleigh.
        Comprenderemos el diseño rasante de los antiniebla, el enclavamiento eléctrico obligatorio del piloto trasero,
        la física del arco eléctrico de xenón con picos de 25 kV y los sensores crepusculares ópticos de encendido automático.
      </p>
    </div>
    """, "Introducción Capítulo 3"))

    sections.append(create_active_challenge(
        title="Reto de Taller: El Piloto Antiniebla Trasero Inoperativo",
        scenario_html="<p>Un cliente acude al taller porque su luz antiniebla trasera no enciende al pulsar el botón del salpicadero. El técnico novato comprueba la bombilla y el fusible F12, encontrándolos en perfecto estado. ¿Qué lógica eléctrica de seguridad ha omitido comprobar antes de desmontar el cableado?</p>",
        steps=[
            ("Paso 1 (Comprobación de Enclavamiento)", "Verificar si el conmutador general de luces está en posición de 'Cruce': la normativa ECE R48 exige que el antiniebla trasero no pueda encenderse solo con luces de posición."),
            ("Paso 2 (Inspección de la Piña de Remolque)", "En vehículos con enganche, verificar el microinterruptor de la base de 13 polos: si se queda atascado con suciedad, corta la masa del antiniebla del vehículo para no reflejar en el remolque."),
            ("Paso 3 (Testigo en Cuadro)", "Comprobar el testigo amarillo auto en el cuadro de mandos para verificar si la orden es procesada por la centralita BCM.")
        ],
        badge_text="Reto de Diagnosis: Enclavamiento de Seguridad"
    ))

    # 2. Explicación Técnica e Imágenes de Referencia
    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-book"></i> FÍSICA Y ARCO ELÉCTRICO DE XENÓN</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">3.1 Lámparas de Descarga de Gas (Xenón / HID)</h3>
      <p style="color:#1e293b; line-height:1.6;">
        A diferencia de las lámparas de filamento, las lámparas de descarga de xenón no disponen de hilo conductor: la luz se produce por un <strong>arco eléctrico entre dos electrodos de wolframio</strong> inmersos en una ampolla de cuarzo a <strong>100 bares de presión</strong> rellena de gas xenón y sales de haluros metálicos.
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Fase de Encendido (Cebado):</strong> La reactancia genera un pulso de alta tensión de <strong>20 a 30 kV</strong> para ionizar el gas e iniciar el arco. Esta fase dura menos de 3 segundos.</li>
        <li><strong>Fase de Mantenimiento:</strong> Una vez estabilizado el arco, la tensión desciende a <strong>85 V</strong> con una corriente alterna de 400 Hz para evitar la migración de material entre electrodos.</li>
      </ul>
    </div>
    """, "Física del Xenón"))

    sections.append(create_image_section(
        "images/figura_composicion_lampara_xenon.png",
        "Figuras 5.18 y 5.19: Composición del arco eléctrico y estructura de la ampolla de cuarzo a 100 bar en una lámpara de xenón",
        "Composición y Arco Eléctrico de Lámpara de Xenón",
        750, 900
    ))

    sections.append(create_image_section(
        "images/figura_despiece_lamparas_xenon.png",
        "Figuras 5.15, 5.16, 5.17: Despiece y familias de lámparas de xenón para automoción (D1, D2, D3, D4)",
        "Familias y Casquillos de Lámparas de Xenón (D1S/D2S)",
        1600, 1297
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-cogs"></i> COMPONENTES Y SEGURIDAD</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">3.2 Componentes del Faro de Xenón y Bixenón</h3>
      <p style="color:#1e293b; line-height:1.6;">
        El faro de xenón integra cuatro componentes fundamentales (Figura 5.52):
      </p>
      <ol style="color:#1e293b; line-height:1.6;">
        <li><strong>Lámpara de descarga:</strong> Ampolla de cuarzo anti-UV.</li>
        <li><strong>Unidad de control y reactancia (balasto):</strong> Transforma los 12V de batería en corriente alterna estabilizada.</li>
        <li><strong>Bloque de encendido (cebador):</strong> Genera los 25.000 V de ignición.</li>
        <li><strong>Servomotor de regulación automática de alcance:</strong> Conectado a sensores de altura en los ejes delantero y trasero.</li>
      </ol>
      <p style="color:#1e293b; line-height:1.6;">
        En los faros <strong>Bixenón</strong>, una única lámpara realiza cruce y carretera mediante una <strong>trampilla móvil accionada por electroimán</strong>: en cruce la trampilla recorta el haz; en carretera se abate dejando pasar el flujo total.
      </p>
    </div>
    """, "Componentes Xenón"))

    sections.append(create_image_section(
        "images/figura_componentes_faro_xenon.png",
        "Figura 5.52: Despiece y componentes de un faro de xenón (lámpara, transformador, UCE, servomotor de regulación y lavafaros)",
        "Componentes Integrados en un Faro de Xenón",
        379, 422
    ))

    sections.append(create_image_section(
        "images/figura_esquema_electrico_xenon.png",
        "Figura 5.54: Esquema eléctrico simplificado de alimentación de una lámpara de xenón con cable apantallado",
        "Esquema Eléctrico de Alta Tensión en Faro de Xenón",
        487, 630
    ))

    sections.append(create_image_section(
        "images/figura_bixenon_trampilla_movil.png",
        "Figura 5.86: Mecanismo de conmutación bixenón mediante trampilla móvil accionada por motor eléctrico",
        "Mecanismo de Conmutación Bixenón por Trampilla Motorizada",
        860, 430
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-sun-o"></i> ENCENDIDO AUTOMÁTICO</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">3.3 Sensores Ópticos Crepusculares y de Lluvia</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Ubicado en la parte superior del parabrisas tras el retrovisor, el sensor integra fotodiodos para medir la luz ambiental y direccional. Al detectar una caída de iluminancia por debajo de un umbral programado (ej. túnel o anochecer), la centralita BCM activa las luces de posición y cruce simultáneamente.
      </p>
    </div>
    """, "Sensores Automáticos"))

    sections.append(create_image_section(
        "images/figura_sensor_lluvia_luz_optico.png",
        "Figura 5.153: Sensor óptico de lluvia y luz crepuscular en parabrisas",
        "Sensor Óptico Combinado de Lluvia y Luz Crepuscular",
        750, 500
    ))

    # 3. Protocolos de Taller
    sections.append(create_accordion([
        ("Seguridad Eléctrica ante Alta Tensión de Xenón (25 kV)",
         "<p>¡Peligro mortal de descarga eléctrica! Antes de tocar o cambiar una lámpara de xenón, desconectar obligatoriamente el encendido, sacar la llave y retirar el fusible o desconectar la batería. Esperar a que los condensadores del balasto se descarguen.</p>"),
        ("Sustitución de Lámparas de Xenón por Parejas",
         "<p>Con las horas de funcionamiento, el gas xenón altera ligeramente su composición química y el color vira hacia tonos más azulados mientras pierde flujo luminoso. Cambiar solo una lámpara genera una asimetría visual notable y rechazo en ITV.</p>"),
        ("Regla de los 10 cm en Piloto Antiniebla Trasero",
         "<p>Según ECE R48, el piloto antiniebla trasero (150-300 cd de color rojo intenso) debe estar físicamente separado al menos 10 cm de la luz de freno para que el conductor que circula detrás distinga inequívocamente cuándo se pisa el pedal de freno.</p>")
    ], "Protocolos de Seguridad y Taller: Alumbrado Especial"))

    sections.append(create_checklist_section(
        "Verificación de Alumbrado Especial y Xenón",
        [
            "Enclavamiento del antiniebla trasero: verificar que no enciende solo con posición.",
            "Testigo amarillo auto de antiniebla trasero operativo en cuadro de instrumentos.",
            "Lavafaros de alta presión operativo en vehículos xenón con flujo >2.000 lm.",
            "Regulador automático de alcance de faros xenón funcional al arrancar el motor."
        ]
    ))

    # 4. Síntesis y Moodle XML
    sections.append(create_moodle_quiz_referral(
        3, "Alumbrado Especial y Sistemas de Descarga",
        "<p>Has comprendido la física del arco de xenón, el encendido a 25 kV, la arquitectura bixenón con trampilla móvil, los sensores crepusculares y los enclavamientos legales de faros antiniebla.</p>"
    ))

    return create_didactic_chapter("Capítulo 3: Alumbrado Especial y Faros de Xenón", sections)


def build_chapter_4():
    """Capítulo 4: Cálculo Electrotécnico, Homologación y Regulación de Faros"""
    sections = []

    # 1. Motivación y Reto
    sections.append(create_text_section("""
    <div class="tech-hero">
      <div class="tech-badge"><i class="fa fa-calculator"></i> CAPÍTULO 4 · CÁLCULO Y REGULACIÓN</div>
      <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Cálculo Electrotécnico, Homologación ECE y Regulación en Regloscopio</h2>
      <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
        En alumbrado del automóvil, una caída de tensión de tan solo 0,5 V en el cableado disminuye el flujo luminoso de una lámpara un 15%, y 1,0 V de pérdida reduce su luz un 28%.
        Aprenderemos a dimensionar conductores de cobre, interpretar el marcado de homologación frontal ECE en faros, comprender las luces de curvas adaptativas y regular faros con regloscopio a 25 metros.
      </p>
    </div>
    """, "Introducción Capítulo 4"))

    sections.append(create_active_challenge(
        title="Reto de Cálculo: Instalación de Faros Supletorios de 110 W",
        scenario_html="<p>Un taller instala dos faros halógenos supletorios de 55 W cada uno (potencia total P = 110 W) en la defensa de un vehículo todoterreno. La longitud del cable desde la batería hasta los faros es de 4 metros (recorrido de ida). La caída de tensión admisible máxima se fija en ΔV = 0,3 V a 12 V de tensión nominal.</p>",
        steps=[
            ("Paso 1 (Cálculo de Intensidad Total)", "I = P / V = 110 W / 12 V = 9,17 A."),
            ("Paso 2 (Cálculo de Sección por Caída de Tensión)", "S = (2 · L · I) / (κ · ΔV) = (2 · 4 m · 9,17 A) / (56 · 0,3 V) = 73,36 / 16,8 = 4,36 mm² ➔ Sección comercial normalizada: 6 mm² (o 2,5 mm² por faro independiente)."),
            ("Paso 3 (Selección del Fusible)", "I_fusible = 1,25 · I_nom = 1,25 · 9,17 A = 11,46 A ➔ Fusible comercial normalizado: 15 A (Azul cielo tipo ATO).")
        ],
        badge_text="Reto Electrotécnico de Taller"
    ))

    # 2. Explicación Técnica e Imágenes de Referencia
    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-book"></i> FÓRMULAS ELECTROTÉCNICAS</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">4.1 Dimensionado de Cables y Fusibles de Protección</h3>
      <p style="color:#1e293b; line-height:1.6;">
        El cálculo de sección de conductor de cobre en corriente continua automotriz se rige por:
      </p>
      <div class="tech-formula-block">
        Intensidad de Corriente: <strong>I = P / V</strong> [Amperios (A)]
        <br />
        Sección por Caída de Tensión: <strong>S = (2 · L · I) / (κ · ΔV)</strong> [mm²]
        <br />
        <span style="font-size:0.9rem; color:#475569;">Donde: L = longitud cable en m, κ = 56 m/(Ω·mm²) para cobre automotriz, ΔV = caída admisible (0,3V en faros principales, 0,5V en señalización).</span>
      </div>
    </div>
    """, "Fórmulas de Cálculo"))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-file-text-o"></i> HOMOLOGACIÓN ECE FRONTAL</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">4.2 Interpretación de Marcado de Homologación en Ópticas Frontales</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Todo grupo óptico delantero homologado bajo normativa europea ECE incorpora un código estampado en el policarbonato o carcasa que define sus especificaciones técnicas y legales:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>A:</strong> Luz de posición delantera.</li>
        <li><strong>HR:</strong> Luz halógena de carretera.</li>
        <li><strong>DCR:</strong> Luz de descarga (xenón) de carretera o cruce.</li>
        <li><strong>1a:</strong> Intermitente delantero tipo 1a.</li>
        <li><strong>Flechas orientativas:</strong> Indican para qué sentido de circulación está homologado el faro (circulación por la derecha, izquierda o conmutable).</li>
        <li><strong>Cifra de referencia luminosa (ej. 17,5 / 12,5):</strong> Intensidad lumínica máxima del faro. La suma total de referencias de todos los faros de carretera no puede exceder legalmente de <strong>100</strong> (o 430.000 candelas).</li>
      </ul>
    </div>
    """, "Marcado ECE"))

    sections.append(create_image_section(
        "images/figura_homologacion_faro_delantero.png",
        "Figura 5.137: Ejemplo de inscripción y marcado de homologación grabado en el frontal de un faro delantero (Hella, E1, A, HR, DCR, 1a, flechas)",
        "Marcado Frontal de Homologación ECE en Faro Delantero",
        1190, 390
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-road"></i> ALUMBRADO EN CURVAS</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">4.3 Luces de Curvas Estáticas y Dinámicas</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Los sistemas adaptativos amplían el campo de visión nocturna en trazados virados:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Luces de curvas estáticas (Cornering light):</strong> Se enciende un foco adicional o el faro antiniebla del lado correspondiente al poner el intermitente o girar el volante a baja velocidad (<40 km/h).</li>
        <li><strong>Luces de curvas dinámicas:</strong> El proyector elipsoidal completo gira sobre un eje vertical motorizado (hasta ±15°) siguiendo el ángulo de volante y la velocidad del vehículo, iluminando hasta 200 m en la trayectoria real de la calzada.</li>
      </ul>
    </div>
    """, "Luces de Curvas"))

    sections.append(create_image_section(
        "images/figura_luces_curvas_adaptativas.png",
        "Figuras 5.138, 5.139, 5.140: Alumbrado en curva estático (antiniebla) y dinámico con giro de proyector",
        "Sistemas de Alumbrado en Curva Estático y Dinámico",
        1200, 1380
    ))

    sections.append(create_image_section(
        "images/figura_sensor_angulo_volante_hall.png",
        "Figura 5.156: Despiece del sensor Hall de ángulo de dirección en columna de volante para gestión de faros adaptativos",
        "Sensor Hall de Ángulo de Volante de Dirección",
        1160, 490
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-crosshairs"></i> METROLOGÍA DE AJUSTE</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">4.4 Regulación de Faros en Regloscopio a 25 Metros</h3>
      <p style="color:#1e293b; line-height:1.6;">
        El regloscopio reproduce la proyección del haz a una distancia normalizada de <strong>25 metros</strong> mediante una lente colimadora óptica:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Inclinación reglamentaria en turismos:</strong> Comprendida entre el <strong>-1,0% y el -1,5%</strong>.</li>
        <li><strong>Efecto del desreglaje hacia arriba (+1%):</strong> Multiplica por <strong>20</strong> el deslumbramiento cegador hacia los conductores contrarios.</li>
        <li><strong>Efecto del desreglaje hacia abajo (-2,5%):</strong> Reduce a la mitad el alcance útil sobre la calzada (apenas 30 metros de visión).</li>
      </ul>
    </div>
    """, "Regloscopio"))

    sections.append(create_image_section(
        "images/regloscopio_ajuste_faros.png",
        "Pantalla de proyección del regloscopio a 25 metros con cotas de inclinación de -1.0% a -1.5%",
        "Ajuste y Calibración de Faros en Regloscopio Óptico",
        722, 480
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-video-camera"></i> VÍDEO TÉCNICO DE REFERENCIA · CESVIMAP</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">Metrología en Taller: Proceso de Ajuste y Reglaje de Faros con Regloscopio Digital</h3>
      <p style="color:#1e293b; line-height:1.6;">
        En esta demostración técnica del canal de referencia <strong>CESVIMAP</strong> (Centro de Experimentación y Seguridad Vial, referencia nacional en Formación Profesional de Automoción), se muestra el método real de taller: alineación por visor láser con el eje del vehículo, calibración de la cámara digital y ajuste de tornillos de altura y deriva según tolerancias de homologación:
      </p>
    </div>
    """, "Vídeo CESVIMAP Regloscopio"))

    sections.append(create_video_section(
        "https://www.youtube.com/watch?v=r1aLt-3YiRE",
        "CESVIMAP: Ajuste y Reglaje de Faros con Regloscopio Digital"
    ))

    # 3. Protocolos de Taller
    sections.append(create_accordion([
        ("Condiciones Previas Obligatorias para el Reglaje de Faros",
         "<p>1. Neumáticos a presión nominal.<br />2. Vehículo sobre suelo rigurosamente plano y horizontal.<br />3. Depósito de combustible al 50% y peso de 75 kg en el asiento del conductor.<br />4. Mando manual de regulación interior en posición '0'.<br />5. Suspender el regloscopio perfectamente paralelo al eje del vehículo mediante su visor óptico o láser.</p>"),
        ("Regulación Automática Obligatoria en Faros >2.000 Lúmenes",
         "<p>Según el Reglamento ECE R48, todo proyector que emita más de 2.000 lúmenes de flujo (xenón de 35W y faros LED potentes) exige obligatoriamente regulación automática dinámica de altura por sensores de suspensión y lavafaros de alta presión.</p>")
    ], "Protocolos de Taller: Regulación y Metrología"))

    sections.append(create_checklist_section(
        "Verificación de Reglaje de Faros",
        [
            "Comprobar alineación del corte horizontal con la cota porcentual de la placa (ej. -1.2%).",
            "Verificar inclinación del codo a 15° hacia el lado derecho sin desviación lateral.",
            "Comprobar funcionamiento de los tornillos de ajuste mecánico de altura y deriva.",
            "Certificar suma de puntos de referencia lumínica inferior a 100."
        ]
    ))

    # 4. Síntesis y Moodle XML
    sections.append(create_moodle_quiz_referral(
        4, "Cálculo, Homologación y Regulación de Faros",
        "<p>Has dominado el dimensionado electrotécnico por caída de tensión y fusibles, la interpretación de códigos ECE, los sistemas de iluminación en curva y el método metrológico de alineación en regloscopio a 25 m.</p>"
    ))

    return create_didactic_chapter("Capítulo 4: Cálculo, Homologación y Regulación de Faros", sections)


def build_chapter_5():
    """Capítulo 5: Diagnosis, Metrología y Mantenimiento de Circuitos de Iluminación"""
    sections = []

    # 1. Motivación y Reto
    sections.append(create_text_section("""
    <div class="tech-hero">
      <div class="tech-badge"><i class="fa fa-stethoscope"></i> CAPÍTULO 5 · DIAGNOSIS EN TALLER</div>
      <h2 style="color:#0f172a; margin-top:0.5rem; font-size:1.6rem;">Diagnosis Avanzada, Iluminación Inteligente AFS y Caídas de Tensión</h2>
      <p style="color:#1e293b; font-size:1.05rem; line-height:1.6;">
        La evolución hacia centralitas de red de a bordo (BCM) y sistemas AFS ha transformado la diagnosis.
        Ya no basta con cambiar una bombilla: los técnicos electromecánicos deben aplicar árboles de decisiones lógicas,
        medir caídas de tensión parásitas con voltímetros digitales en carga y comprender los algoritmos del haz inteligente.
      </p>
    </div>
    """, "Introducción Capítulo 5"))

    sections.append(create_active_challenge(
        title="Reto de Taller: Faro Delantero con Iluminación Tenue y Parpadeo",
        scenario_html="<p>Un turismo moderno entra en el taller con el faro halógeno derecho alumbrando con un 30% menos de intensidad que el izquierdo. El cliente ya cambió la lámpara H7 pensando que estaba gastada, pero el problema persiste. El técnico conecta el multímetro digital para medir caídas de tensión en carga.</p>",
        steps=[
            ("Paso 1 (Medición de Caída en Línea Positiva V1)", "Punta roja en borne positivo de batería y punta negra en terminal positivo de la lámpara con luces encendidas. Lectura: 0,12 V (Correcto, <0,3 V)."),
            ("Paso 2 (Medición de Caída en Línea de Masa V2)", "Punta negra en borne negativo de batería y punta roja en casquillo de masa de la lámpara. Lectura: 0,95 V (¡Inadmisible! Límite: 0,1 V)."),
            ("Paso 3 (Reparación)", "Desmontar el tornillo del cable marrón de masa en el chasis del paso de rueda, lijar el óxido de cobre y apretar. La caída baja a 0,03 V y el faro recupera el 100% de brillo.")
        ],
        badge_text="Reto Metrológico de Taller"
    ))

    # 2. Explicación Técnica e Imágenes de Referencia
    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-sitemap"></i> SISTEMAS AFS INTELIGENTES</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">5.1 Iluminación Adaptativa Inteligente AFS (Advanced Frontlighting System)</h3>
      <p style="color:#1e293b; line-height:1.6;">
        El sistema AFS adapta automáticamente el haz luminoso a la velocidad del vehículo, la climatología y el trazado de la carretera:
      </p>
      <ul style="color:#1e293b; line-height:1.6;">
        <li><strong>Luz de Ciudad (<50 km/h):</strong> Haz muy ancho y de menor alcance para iluminar cruces, bordillos y peatones.</li>
        <li><strong>Luz de Carretera (50 a 100 km/h):</strong> Distribución estándar asimétrica a 15°.</li>
        <li><strong>Luz de Autopista (>100 km/h):</strong> El haz se eleva ligeramente y se estrecha, aumentando el alcance frontal de 70 a 140 metros.</li>
        <li><strong>Luz de Mal Tiempo:</strong> Reduce la potencia en el centro para evitar el autodeslumbramiento y amplía los márgenes laterales.</li>
      </ul>
    </div>
    """, "Sistemas AFS"))

    sections.append(create_image_section(
        "images/figura_sistema_afs_distribucion_haz.png",
        "Figuras 5.159 y 5.160: Distribuciones inteligentes del haz luminoso AFS en curvas, ciudad y autopista, y arquitectura de faro adaptativo",
        "Distribución Inteligente del Haz AFS en Diferentes Vías",
        1190, 1190
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-shield"></i> AUTODIAGNOSIS Y SEGURIDAD EN XENÓN</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">5.2 Protocolo de Autodiagnosis de Averías en Faros de Xenón</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Los faros de xenón incorporan protecciones automáticas gestionadas por la unidad de control: si se desconecta un terminal durante el funcionamiento, la tensión se reduce a menos de 35 V en medio segundo; ante fugas superiores a 30 mA, el sistema se desconecta en 0,2 segundos.
      </p>
    </div>
    """, "Diagnosis Xenón"))

    sections.append(create_image_section(
        "images/figura_protocolo_diagnosis_faro_xenon.png",
        "Tabla 5.2 y organigrama: Protocolo de diagnosis y comprobación de fallos de encendido en faros de xenón",
        "Organigrama de Diagnosis y Autoprotección en Faros de Xenón",
        1180, 500
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-wrench"></i> PRÁCTICA DE COMPROBACIÓN EN TALLER</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">5.3 Comprobación de Continuidad y Alimentación de Pilotos Traseros</h3>
      <p style="color:#1e293b; line-height:1.6;">
        En faros y pilotos traseros desmontados en banco de trabajo, se aplica tensión con una fuente regulada o batería de pruebas conectando el terminal negativo a la chapa metálica común de masa y alimentando sucesivamente cada pin positivo para verificar las funciones de posición, freno, marcha atrás e intermitencia.
      </p>
    </div>
    """, "Práctica Taller"))

    sections.append(create_image_section(
        "images/figura_comprobacion_piloto_taller.png",
        "Figuras 5.127, 5.128, 5.129: Práctica de taller de comprobación de terminales y pistas de conexión de un piloto trasero con polímetro y alimentación",
        "Comprobación de Pistas y Terminales de Piloto Trasero en Taller",
        401, 498
    ))

    sections.append(create_text_section("""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-line-chart"></i> METROLOGÍA DE VOLTAJE EN CARGA</div>
      <h3 style="color:#0f172a; margin-top:0.5rem;">5.4 Método de Medición de Caída de Tensión</h3>
      <p style="color:#1e293b; line-height:1.6;">
        Para detectar resistencias parásitas por corrosión en conectores o cables pellizcados, el voltímetro digital debe conectarse <strong>en paralelo y con el circuito encendido bajo carga</strong>. Sin corriente (I = 0 A), la caída es siempre 0 V y enmascara la avería.
      </p>
      <div class="table-responsive">
        <table class="tech-table">
          <thead>
            <tr>
              <th>Punto de Medición</th>
              <th>Conexión del Multímetro</th>
              <th>Tolerancia Máxima</th>
              <th>Acción Correctiva ante Fallo</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Línea Positiva (V1)</strong></td>
              <td>Borne (+) Bat a Terminal (+) Lámpara</td>
              <td><strong>≤ 0,3 V</strong></td>
              <td>Revisar contactos del relé, zócalo del fusible o empalmes oxidados.</td>
            </tr>
            <tr>
              <td><strong>Línea de Masa (V2)</strong></td>
              <td>Casquillo Lámpara a Borne (-) Bat</td>
              <td><strong>≤ 0,1 V</strong></td>
              <td>Limpiar óxido en tornillo de chasis (Línea 31) y aplicar grasa conductora.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    """, "Caída de Tensión"))

    sections.append(create_image_section(
        "images/diagnosis_caida_tension.png",
        "Guía metrológica de medición de caída de tensión en línea positiva y masa con voltímetro en carga",
        "Método Metrológico de Caída de Tensión en Taller",
        399, 501
    ))

    # 3. Protocolos de Taller
    sections.append(create_accordion([
        ("Degradación por Radiación Ultravioleta en Faros de Policarbonato",
         "<p>Con el paso de los años, el sol degrada el barniz protector superficial del policarbonato, volviéndolo mate y amarillento. Esto dispersa la luz y provoca rechazo en ITV. La reparación técnica exige lijado al agua en pasos sucesivos (P800, P1500, P2000, P3000), pulido con pasta y aplicación obligatoria de nuevo barniz protector 2K anti-UV.</p>"),
        ("Defecto Grave en ITV: Bombillas Ámbar Descascarilladas",
         "<p>Por la Directiva RoHS que prohíbe el cadmio en vidrios, las lámparas ámbar PY21W usan lacas superficiales que se cuartean por calor. Si la bombilla emite luz blanquecina, la ITV la califica como defecto grave por confusión de señales viales.</p>")
    ], "Protocolos de Mantenimiento y Recuperación"))

    sections.append(create_checklist_section(
        "Lista de Control Final: Entrega del Vehículo",
        [
            "1. Tensión de batería en reposo (12,6V) y con motor arrancado (14,2V).",
            "2. Caída de tensión en carga: línea positiva ≤0,3V y línea de masa ≤0,1V.",
            "3. Lectura de códigos DTC de carrocería (serie B) en la BCM sin fallos registrados.",
            "4. Comprobación de transparencia óptica y reglaje correcto en regloscopio."
        ]
    ))

    # 4. Síntesis y Moodle XML
    sections.append(create_moodle_quiz_referral(
        5, "Diagnosis y Mantenimiento de Iluminación",
        "<p>Has culminado el estudio integral de circuitos de alumbrado y señalización. Has asimilado la diagnosis metrológica de caídas de tensión en carga, las distribuciones adaptativas AFS y el mantenimiento preventivo del automóvil.</p>"
    ))

    return create_didactic_chapter("Capítulo 5: Diagnosis y Localización de Averías", sections)


# =========================================================================
# 3. EMPAQUETADOR MAESTRO H5P Y GENERADOR MOODLE XML
# =========================================================================

def build_h5p_course(destination_h5p_path):
    """Compila físicamente el paquete .h5p con sus librerías homologadas."""
    print(f"📦 Compilando curso H5P en: {destination_h5p_path}")
    print(f"📁 Copiando {len(HOMOLOGATED_DEPENDENCIES)} librerías base desde: {LIB_DIR}")

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
    print("🔨 Ensamblando los 5 capítulos con andamiaje pedagógico e ilustraciones...")
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

    content_json_path = os.path.join(temp_build_dir, "content", "content.json")
    with open(content_json_path, "w", encoding="utf-8") as f:
        json.dump(content_json, f, ensure_ascii=False, indent=2)

    # 5. Generar h5p.json con metadatos estrictos para Moodle
    h5p_manifest = {
        "title": "Circuitos de Alumbrado y Señalización del Automóvil",
        "language": "es",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["div"],
        "license": "CC BY-SA",
        "defaultLanguage": "es",
        "preloadedDependencies": HOMOLOGATED_DEPENDENCIES,
        "authors": [
            {
                "name": "Departamento de Formación Profesional - Automoción",
                "role": "Author"
            }
        ]
    }

    h5p_json_path = os.path.join(temp_build_dir, "h5p.json")
    with open(h5p_json_path, "w", encoding="utf-8") as f:
        json.dump(h5p_manifest, f, ensure_ascii=False, indent=2)

    # 6. Empaquetar ZIP sin compresión de metadatos
    if os.path.exists(destination_h5p_path):
        os.remove(destination_h5p_path)

    with zipfile.ZipFile(destination_h5p_path, "w", zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_build_dir):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, temp_build_dir)
                zip_out.write(abs_file, rel_path.replace(os.sep, '/'))

    # Limpieza
    shutil.rmtree(temp_build_dir)
    print(f"✅ Paquete H5P generado con éxito: {destination_h5p_path}")
    print(f"📊 Tamaño final: {os.path.getsize(destination_h5p_path) / (1024*1024):.2f} MB")

    # 7. Certificación técnica estricta con validador de EducaMadrid
    validate_h5p(destination_h5p_path)


def generar_evaluacion_alumbrado_xml(output_xml_path):
    """Genera el banco de preguntas sumativo oficial en formato Moodle XML (<quiz>) sin sesgo de longitud."""
    builder = MoodleXMLBuilder("Circuitos de Alumbrado y Senalizacion - Evaluacion Sumativa Oficial")

    # 1. Función de Luces Diurnas (DRL)
    builder.add_multichoice(
        "ALUM_P01_MC_Luces_Diurnas_DRL",
        "¿Cuál es la función técnica primordial de las luces de conducción diurna (DRL) y cuál es su normativa de funcionamiento al activar las luces de cruce?",
        [
            {"text": "Hacer visible el vehículo durante el día; deben atenuarse o apagarse al conectar el alumbrado de cruce.", "fraction": 100, "feedback": "¡Correcto! La normativa ECE R48 exige que las luces DRL aumenten la visibilidad frontal de día y se desactiven o reduzcan su intensidad lumínica al encender la luz de cruce para no provocar deslumbramientos."},
            {"text": "Aumentar la visibilidad lejana del conductor sobre la calzada tanto de día como de noche sin desconectarse.", "fraction": 0, "feedback": "Incorrecto. Las luces DRL son de señalización (para ser visto), no para ver el asfalto nocturno."},
            {"text": "Reemplazar a los faros antiniebla delanteros cuando el vehículo circula a velocidades inferiores a 50 km/h.", "fraction": 0, "feedback": "Incorrecto. Las luces diurnas carecen de la fotometría rasante antiniebla."},
            {"text": "Iluminar el cuadro de mandos y los pilotos de posición traseros de manera ininterrumpida.", "fraction": 0, "feedback": "Incorrecto. De día, la normativa habitual sólo exige encendido frontal; de hecho, los pilotos traseros suelen permanecer apagados."}
        ],
        general_feedback="Reglamento ECE R48: Las luces DRL (código RL) mejoran la visibilidad diurna y deben apagarse o conmutar a función de posición al activar el alumbrado nocturno."
    )

    # 2. Haz Asimétrico
    builder.add_multichoice(
        "ALUM_P02_MC_Haz_Asimetrico_15_Grados",
        "¿Por qué el haz de luz de cruce según la normativa europea ECE presenta una inclinación asimétrica ascendente de 15 grados hacia el lado derecho?",
        [
            {"text": "Para alumbrar a mayor distancia el arcén derecho y las señales sin deslumbrar a los vehículos en sentido contrario.", "fraction": 100, "feedback": "¡Correcto! En países con circulación por la derecha, los 15° amplían la visibilidad de peatones y señales hasta 75 metros por el arcén sin deslumbrar al carril opuesto."},
            {"text": "Compensar la inclinación que adopta la carrocería en curvas pronunciadas tomadas a alta velocidad en autopistas.", "fraction": 0, "feedback": "Incorrecto. La inclinación asimétrica de 15° es un diseño óptico fijo para tramos rectos y curvos."},
            {"text": "Permitir que las lámparas halógenas de cruce disipen el calor concentrado hacia la parte superior del proyector.", "fraction": 0, "feedback": "Incorrecto. El diseño del haz responde estrictamente a requerimientos fotométricos viales."},
            {"text": "Facilitar el alineado visual rápido sobre una pared de taller a 10 metros sin requerir regloscopio óptico de alineación.", "fraction": 0, "feedback": "Incorrecto. El regloscopio es estrictamente necesario para ajustar tanto la horizontal como el ángulo a 15°."}
        ],
        general_feedback="Óptica europea: El corte horizontal izquierdo evita el deslumbramiento; la elevación a 15° derecha asegura la visibilidad de señales y arcenes."
    )

    # 3. Luces de Posición Traseras
    builder.add_truefalse(
        "ALUM_P03_TF_Luces_Posicion_Obligatorias",
        "Es legalmente obligatorio que las luces de posición delanteras y traseras permanezcan encendidas simultáneamente cada vez que se activan las luces de cruce o de carretera.",
        True,
        feedback_true="¡Correcto! La normativa de seguridad vial exige que el contorno y presencia del vehículo estén permanentemente señalizados cuando el alumbrado principal está operativo.",
        feedback_false="Incorrecto. Las luces de posición deben activarse automáticamente con el alumbrado de cruce y carretera para garantizar la visibilidad del vehículo en caso de fallo de una bombilla principal."
    )

    # 4. Sensor Crepuscular
    builder.add_multichoice(
        "ALUM_P04_MC_Encendido_Automatico_Sensor_Luz",
        "En los sistemas de encendido automático de luces, ¿qué tipo de sensor y principio físico se utiliza comúnmente para detectar la caída de luminosidad exterior?",
        [
            {"text": "Un fototransistor o fotorresistencia LDR en el parabrisas que detecta la radiación óptica ambiental.", "fraction": 100, "feedback": "¡Correcto! El sensor óptico crepuscular mide la iluminancia ambiental; al descender de un umbral prefijado, la BCM activa los relés de cruce y posición."},
            {"text": "Un termistor NTC colocado junto a la rejilla del radiador que detecta el enfriamiento súbito nocturno.", "fraction": 0, "feedback": "Incorrecto. La temperatura ambiental no determina la luminosidad exterior."},
            {"text": "Un sensor piezoeléctrico de presión ubicado en la suspensión delantera que detecta la inclinación de la carrocería.", "fraction": 0, "feedback": "Incorrecto. La suspensión equipa sensores de nivel para regular faros, no para encenderlos."},
            {"text": "Un transductor capacitivo alojado en el pedal del freno que evalúa la frecuencia de pisada del conductor.", "fraction": 0, "feedback": "Incorrecto. No tiene relación con las condiciones fotométricas ambientales."}
        ],
        general_feedback="El sensor crepuscular emplea elementos optoelectrónicos (fotodiodos o fototransistores) ubicados habitualmente junto al retrovisor interior."
    )

    # 5. Faros Antiniebla Delanteros
    builder.add_truefalse(
        "ALUM_P05_TF_Antiniebla_Delantero_Uso",
        "Los faros antiniebla delanteros emiten un haz ancho y plano, situado a baja altura, diseñado para evitar el efecto de 'pared blanca' por reflexión de la luz en las gotas de niebla en suspensión.",
        True,
        feedback_true="¡Correcto! La niebla se disipa unos centímetros sobre el asfalto; un haz bajo y rasante penetra por debajo de la capa de niebla sin rebotar en los ojos del conductor.",
        feedback_false="Incorrecto. Precisamente su colocación baja y su apertura angular ancha permiten iluminar los arcenes por debajo de la capa de condensación de la niebla."
    )

    # 6. Antiniebla Trasero
    builder.add_multichoice(
        "ALUM_P06_MC_Enclavamiento_Antiniebla_Trasero",
        "¿Qué condición eléctrica y normativa de seguridad debe cumplirse para que pueda encenderse el piloto antiniebla trasero?",
        [
            {"text": "Tener previamente activadas las luces de cruce, carretera o faros antiniebla delanteros.", "fraction": 100, "feedback": "¡Correcto! La normativa europea prohíbe activar el antiniebla trasero sólo con posición, para evitar deslumbrar a los vehículos precedentes en condiciones normales."},
            {"text": "Circular obligatoriamente a una velocidad superior a 80 km/h en vías rápidas o autopistas.", "fraction": 0, "feedback": "Incorrecto. En niebla densa la velocidad debe reducirse drásticamente; la restricción es puramente eléctrica y de mando."},
            {"text": "Engranar la marcha atrás para verificar que no existen obstáculos detrás del vehículo.", "fraction": 0, "feedback": "Incorrecto. La marcha atrás y el antiniebla trasero son circuitos completamente independientes."},
            {"text": "Desconectar totalmente el sistema de climatización y el desempañador térmico de la luneta trasera.", "fraction": 0, "feedback": "Incorrecto. Los sistemas de desempañado son esenciales con niebla y operan en paralelo."}
        ],
        general_feedback="El interbloqueo legal exige luces principales encendidas antes de alimentar el antiniebla trasero, señalizado con testigo amarillo en el cuadro."
    )

    # 7. Separación Antiniebla y Freno
    builder.add_truefalse(
        "ALUM_P07_TF_Distancia_Minima_Antiniebla_Freno",
        "Según la normativa europea ECE R48, es obligatorio que exista una separación física mínima de 10 cm entre la luz de freno y el piloto antiniebla trasero.",
        True,
        feedback_true="¡Correcto! Debido a que ambas emiten luz roja de alta intensidad (150-300 cd en el antiniebla), una separación menor impediría percibir cuándo frena el vehículo.",
        feedback_false="Incorrecto. La norma exige un mínimo de 10 cm entre los bordes iluminantes para asegurar la legibilidad de la maniobra de frenado en condiciones de niebla."
    )

    # 8. Cadencia de Intermitencia
    builder.add_multichoice(
        "ALUM_P08_MC_Cadencia_Intermitencias_Averia",
        "¿Cuál es la frecuencia reglamentaria de destello de los intermitentes y qué efecto visual advierte al conductor de que una de las bombillas de 21 W se ha fundido?",
        [
            {"text": "60 a 120 destellos/minuto; al fundirse una bombilla, la cadencia del lado afectado se duplica de forma automática.", "fraction": 100, "feedback": "¡Correcto! El Reglamento ECE R48 fija entre 1 y 2 Hz (60-120 dpm). El relé o la BCM detecta la reducción de corriente y duplica la frecuencia como aviso inmediato."},
            {"text": "30 a 60 destellos/minuto; la cadencia disminuye a la mitad para evitar sobrecalentar las bombillas operativas.", "fraction": 0, "feedback": "Incorrecto. Una cadencia menor no cumple la normativa europea y retrasaría la percepción del giro."},
            {"text": "120 a 180 destellos/minuto; los indicadores se apagan por completo al fundirse cualquiera de las bombillas.", "fraction": 0, "feedback": "Incorrecto. La función de aviso legal es el parpadeo acelerado, no el apagado completo del circuito."},
            {"text": "Frecuencia fija de 240 destellos/minuto constante que nunca varía independientemente de la carga conectada.", "fraction": 0, "feedback": "Incorrecto. 240 dpm causaría confusión visual y los circuitos tradicionales aumentan su frecuencia precisamente ante la pérdida de una bombilla."}
        ],
        general_feedback="Frecuencia estándar: 1,5 Hz ± 0,5 Hz (60-120 dpm). El aumento al doble de frecuencia es el método normativo de detección de lámpara fundida."
    )

    # 9. Conmutador de Emergencia (Warning)
    builder.add_multichoice(
        "ALUM_P09_MC_Circuito_Emergencia_Warning",
        "En el circuito de intermitencia y luces de emergencia, ¿por qué el conmutador de warning se alimenta directamente de la Línea 30 (+Bat) en lugar de la Línea 15 (+Contacto)?",
        [
            {"text": "Para permitir la señalización de peligro ininterrumpida con el vehículo estacionado y el motor apagado sin llave.", "fraction": 100, "feedback": "¡Correcto! Un vehículo averiado o detenido en el arcén debe poder señalizar su emergencia con las llaves quitadas y el conductor fuera del vehículo."},
            {"text": "Evitar interferencias parásitas en la señal CAN-Bus de la unidad de control del motor durante el arranque.", "fraction": 0, "feedback": "Incorrecto. El warning es un elemento de seguridad pasiva independiente de la red motopropulsora."},
            {"text": "Garantizar que los cuatro intermitentes funcionen con mayor voltaje y brillo del que suministra el alternador.", "fraction": 0, "feedback": "Incorrecto. La tensión de batería (12,6V) es menor que la del alternador en marcha (14,2V)."},
            {"text": "Alimentar un circuito secundario de carga rápida para la batería de respaldo de la llamada de emergencia eCall.", "fraction": 0, "feedback": "Incorrecto. El pulsador de warning no gestiona la recarga de módulos telemáticos."}
        ],
        general_feedback="Seguridad vial: Las luces de emergencia deben operar en cualquier circunstancia, exigiendo conexión directa a batería permanente (borne 30)."
    )

    # 10. Modulación PWM
    builder.add_multichoice(
        "ALUM_P10_MC_Modulacion_PWM_Pilotos",
        "En vehículos modernos con electrónica de carrocería (BCM), ¿cómo se consigue que una misma tira de ledes o bombilla de un polo funcione como luz de posición y de freno?",
        [
            {"text": "Modulando el ancho de pulso (PWM): ciclo de trabajo del 15-20% para posición y 100% para luz de freno.", "fraction": 100, "feedback": "¡Correcto! La modulación PWM ajusta el valor eficaz de tensión reduciendo el ciclo de trabajo para posición y entregando el 100% continuo al pisar el freno."},
            {"text": "Conmutando la polaridad de los cables para invertir el sentido de circulación de la corriente en los diodos.", "fraction": 0, "feedback": "Incorrecto. Los diodos LED solo conducen en polarización directa; invertir la polaridad los apagaría por completo."},
            {"text": "Intercalando una resistencia calefactora cerámica en serie dentro del mazo de cables del maletero.", "fraction": 0, "feedback": "Incorrecto. Las resistencias fijas disipan calor innecesario y han sido sustituidas por transistores MOSFET con PWM."},
            {"text": "Aumentando la frecuencia de la red CAN-Bus de carrocería desde 125 kbps hasta 500 kbps durante la frenada.", "fraction": 0, "feedback": "Incorrecto. La velocidad de transmisión del bus no altera la luminosidad física de un emisor óptico."}
        ],
        general_feedback="Control PWM: Varía el tiempo de encendido relativo (Duty Cycle) para regular la iluminancia aparente sin pérdidas resistivas."
    )

    # 11. Tercera Luz de Freno
    builder.add_multichoice(
        "ALUM_P11_MC_Tercera_Luz_Freno_S3",
        "¿Qué código de homologación identifica a la tercera luz de freno central elevada y qué tolerancia de desvío permite la normativa en portones asimétricos?",
        [
            {"text": "Código S3; la normativa tolera hasta un máximo de 15 cm de desvío respecto al eje central del vehículo.", "fraction": 100, "feedback": "¡Correcto! La tercera luz de freno (CHMSL) se homologa como S3 y debe ser central, con una tolerancia de 15 cm en vehículos con puertas traseras asimétricas."},
            {"text": "Código RL; debe situarse estrictamente en el centro exacto sin tolerarse ningún milímetro de desviación.", "fraction": 0, "feedback": "Incorrecto. RL corresponde a luces de conducción diurna (Daytime Running Lights)."},
            {"text": "Código AR; permite situarla indistintamente en el lado izquierdo o derecho según el país de comercialización.", "fraction": 0, "feedback": "Incorrecto. AR identifica a las luces de marcha atrás."},
            {"text": "Código F3; puede montarse en la parte inferior del paragolpes trasero siempre que supere las 150 candelas.", "fraction": 0, "feedback": "Incorrecto. F3 corresponde a proyectores antiniebla delanteros y debe ser sobreelevada."}
        ],
        general_feedback="Tercera luz de freno: Homologación S3 (ECE R48), posición elevada sobre el plano horizontal de las luces de freno principales S1/S2."
    )

    # 12. Marcha Atrás
    builder.add_multichoice(
        "ALUM_P12_MC_Luz_Marcha_Atras_Reglamento",
        "Respecto a la luz de marcha atrás, ¿cuál es el color reglamentario, su código de homologación y el número de luces permitido en turismos?",
        [
            {"text": "Blanco, código AR; obligatorio llevar al menos una luz y opcional una segunda en la parte trasera.", "fraction": 100, "feedback": "¡Correcto! El color es blanco (código AR); los turismos deben equipar obligatoriamente una luz de marcha atrás y pueden equipar una segunda opcional."},
            {"text": "Ámbar selectivo, código F1; obligatorio llevar dos luces situadas simétricamente en los extremos del parachoques.", "fraction": 0, "feedback": "Incorrecto. El color blanco es exclusivo para indicar la dirección contraria o maniobra de retroceso."},
            {"text": "Rojo de alta intensidad, código R; sólo se autoriza una luz en el lado izquierdo del vehículo.", "fraction": 0, "feedback": "Incorrecto. La luz roja hacia atrás sólo se permite en posición, freno y antiniebla."},
            {"text": "Azul destellante, código B; obligatorio en todos los vehículos comerciales ligeros para maniobras de carga.", "fraction": 0, "feedback": "Incorrecto. La luz azul está reservada exclusivamente a vehículos prioritarios de emergencia."}
        ],
        general_feedback="Luz de marcha atrás: Color blanco (código AR). Obligatoria una, opcional dos en vehículos de categoría M1 y N1."
    )

    # 13. Iluminación Interior Temporizada
    builder.add_multichoice(
        "ALUM_P13_MC_Iluminacion_Interior_Temporizada",
        "¿Qué componente electrónico ejecuta la atenuación progresiva ('theater dimming') de los plafones interiores al cerrar las puertas del vehículo?",
        [
            {"text": "Un transistor MOSFET en la BCM controlado por modulación de ancho de pulso PWM.", "fraction": 100, "feedback": "¡Correcto! La centralita de carrocería (BCM/BSI) gestiona un transistor MOSFET variando el ciclo de trabajo para un apagado gradual y elegante."},
            {"text": "Un interruptor bimetálico térmico que se enfría paulatinamente al cortarse el paso de la corriente.", "fraction": 0, "feedback": "Incorrecto. Los bimetales antiguos no permiten un control preciso ni tiempos adaptables."},
            {"text": "Un motor paso a paso con potenciómetro reostático montado en la caja de fusibles del vano motor.", "fraction": 0, "feedback": "Incorrecto. Los reóstatos mecánicos son ineficientes y generan calor excesivo."},
            {"text": "Un condensador electrolítico de 50 Faradios conectado directamente en paralelo con cada bombilla.", "fraction": 0, "feedback": "Incorrecto. Una capacidad de tal magnitud es físicamente inviable e innecesaria en electrónica moderna."}
        ],
        general_feedback="Atenuación interior: Gestionada por software en la BCM mediante rampa PWM decreciente hacia el driver de potencia."
    )

    # 14. Cálculo de Sección
    builder.add_multichoice(
        "ALUM_P14_MC_Calculo_Seccion_Conductor",
        "Se instalan dos faros antiniebla de 55 W cada uno (potencia total P = 110 W) a 12 V. La longitud del cable es de 3 metros y la caída admisible es ΔV = 0,3 V (cobre κ = 56 m/(Ω·mm²)). ¿Qué sección teórica de cable se requiere?",
        [
            {"text": "S = 3,27 mm² (debiendo escogerse la sección comercial normalizada de 4 mm²).", "fraction": 100, "feedback": "¡Correcto! I = 110W / 12V = 9,17 A. S = (2 · 3 m · 9,17 A) / (56 · 0,3 V) = 55,02 / 16,8 = 3,27 mm². La sección normalizada inmediata superior es 4 mm²."},
            {"text": "S = 0,75 mm² (suficiente para no sobrecalentar el aislante de PVC del conductor).", "fraction": 0, "feedback": "Incorrecto. 0,75 mm² generaría una caída de tensión muy superior a 0,3 V, reduciendo drásticamente la luz emitida."},
            {"text": "S = 1,50 mm² (sección estándar válida para cualquier consumidor de potencia en automoción).", "fraction": 0, "feedback": "Incorrecto. Con 1,5 mm² la caída de tensión superaría los 0,65 V, incumpliendo el límite del 2,5% de la tensión nominal."},
            {"text": "S = 10,00 mm² (necesaria para evitar la interferencia de corrientes parásitas de alta frecuencia).", "fraction": 0, "feedback": "Incorrecto. Es una sección sobredimensionada en exceso para 9,17 A a 3 metros de recorrido."}
        ],
        general_feedback="Fórmula de cálculo: S = (2 · L · I) / (κ · ΔV). En este circuito: S = (2 · 3 · 9,17) / (56 · 0,3) = 3,27 mm² ➔ 4 mm²."
    )

    # 15. Selección de Fusible
    builder.add_multichoice(
        "ALUM_P15_MC_Seleccion_Fusible_Proteccion",
        "Para el circuito anterior con dos lámparas de 55 W (corriente nominal I = 9,17 A), ¿cuál es el calibre de fusible ATO recomendado aplicando el margen de seguridad del 25%?",
        [
            {"text": "15 A (color azul cielo, aplicando el factor de 1,25 a la corriente nominal de 9,17 A).", "fraction": 100, "feedback": "¡Correcto! I_fusible = 9,17 A · 1,25 = 11,46 A. El calibre comercial normalizado inmediatamente superior en la serie ATO/Mini es 15 A (azul cielo)."},
            {"text": "7,5 A (color marrón, para asegurar que el filamento de las lámparas nunca sufra sobretensión).", "fraction": 0, "feedback": "Incorrecto. Un fusible de 7,5 A se fundiría al instante debido a la corriente de 9,17 A y al pico inicial en frío."},
            {"text": "10 A (color rojo, operando exactamente al 92% de su capacidad nominal máxima).", "fraction": 0, "feedback": "Incorrecto. 10 A no proporciona margen de seguridad frente al pico de arranque de filamento frío (inrush current) y provocaría falsos disparos."},
            {"text": "30 A (color verde, para admitir la conexión futura de accesorios de calefacción adicionales).", "fraction": 0, "feedback": "Incorrecto. 30 A no protegería eficazmente un cable de 4 mm² ante sobrecargas moderadas prolongadas."}
        ],
        general_feedback="Calibre de fusible: I_fusible = 1,25 · I_nom = 1,25 · 9,17 = 11,46 A ➔ Fusible comercial normalizado de 15 A (Azul cielo)."
    )

    # 16. Regloscopio
    builder.add_multichoice(
        "ALUM_P16_MC_Reglaje_Faros_Regloscopio_Cota",
        "En el regloscopio óptico, ¿a qué distancia equivale la pantalla interna colimadora y cuál es la caída porcentual reglamentaria para turismos estándar?",
        [
            {"text": "Equivale a una distancia de 25 metros; la caída reglamentaria se sitúa entre el -1,0% y el -1,5%.", "fraction": 100, "feedback": "¡Correcto! La lente colimadora reproduce la pantalla a 25 metros. La inclinación estándar fijada por el fabricante oscila entre -1,0% y -1,5% (indicado en el faro con el símbolo %)."},
            {"text": "Equivale a una distancia de 5 metros; la inclinación debe ajustarse exactamente al 0,0% horizontal.", "fraction": 0, "feedback": "Incorrecto. Un ajuste al 0,0% horizontal deslumbraría gravemente en cambios de rasante y baches."},
            {"text": "Equivale a una distancia de 50 metros; la inclinación recomendada es del -3,5% hacia el suelo.", "fraction": 0, "feedback": "Incorrecto. -3,5% reduciría el alcance útil a menos de 20 metros, dejando al conductor a oscuras."},
            {"text": "Equivale a una distancia de 10 metros; los faros de xenón deben apuntar hacia arriba un +1,0%.", "fraction": 0, "feedback": "Incorrecto. Los faros de xenón jamás apuntan hacia arriba: provocarían un deslumbramiento cegador masivo."}
        ],
        general_feedback="Regloscopio: Distancia óptica de 25 m. Caída típica: 1,0% a 1,5% (10 a 15 cm de descenso a 10 metros)."
    )

    # 17. Umbral 2.000 lúmenes
    builder.add_truefalse(
        "ALUM_P17_TF_Lavafaros_Regulacion_2000_Lumenes",
        "La normativa europea exige obligatoriamente regulación automática del alcance luminoso y sistema lavafaros cuando el flujo de la fuente luminosa supera los 2.000 lúmenes (como en xenón de 35 W y faros LED de alta potencia).",
        True,
        feedback_true="¡Correcto! Fuentes con más de 2.000 lm provocan deslumbramiento crítico si los faros están sucios o desalineados por la carga del vehículo.",
        feedback_false="Incorrecto. La Directiva ECE fija en 2.000 lúmenes el límite legal estricto que exige regulador automático dinámico de altura y eyectores de lavado."
    )

    # 18. Lámparas de Xenón (25 kV)
    builder.add_truefalse(
        "ALUM_P18_TF_Tension_Cebado_Xenon_25kV",
        "Las lámparas de descarga de xenón no disponen de filamento y requieren un pulso de cebado de entre 20.000 y 30.000 V (20-30 kV) generado por el transformador/reactancia para ionizar el gas e iniciar el arco eléctrico.",
        True,
        feedback_true="¡Correcto! El arco inicial precisa de 20 a 30 kV; tras establecerse la descarga, la tensión se reduce a un valor de mantenimiento de aproximadamente 85 V.",
        feedback_false="Incorrecto. El encendido de una lámpara de descarga exige ionizar el gas xenón a alta presión (100 bar) mediante un pico de muy alta tensión (20-30 kV)."
    )

    # 19. Caída en Masa
    builder.add_multichoice(
        "ALUM_P19_MC_Diagnosis_Caida_Tension_Masa",
        "Al diagnosticar un faro halógeno derecho cuya luz es tenue y amarillenta, el voltímetro digital conectado entre el terminal de masa de la bombilla y el borne (-) de la batería marca 0,95 V en carga. ¿Cuál es el diagnóstico correcto?",
        [
            {"text": "Avería crítica en la línea de masa (borne 31): existe una resistencia parásita por óxido (máximo admisible: 0,1 V).", "fraction": 100, "feedback": "¡Correcto! En una línea de masa la caída no debe superar 0,1 V. Un valor de 0,95 V roba casi un voltio a la bombilla, reduciendo su flujo luminoso más de un 25%."},
            {"text": "El circuito de masa se encuentra en perfecto estado, ya que en masa siempre debe existir una tensión residual de 1 voltio.", "fraction": 0, "feedback": "Incorrecto. La masa del vehículo ideal debe estar a 0 V; 0,95 V es una pérdida inadmisible."},
            {"text": "El alternador está averiado y envía corriente alterna parásita a través del regulador de tensión.", "fraction": 0, "feedback": "Incorrecto. La medición se realiza entre dos puntos de masa; no evalúa el rizado del alternador."},
            {"text": "La caída de tensión en masa no puede medirse con voltímetro al no circular corriente positiva.", "fraction": 0, "feedback": "Incorrecto. La medición de caída de tensión en masa en paralelo es el método estrella de taller."}
        ],
        general_feedback="Diagnosis de masas: La caída máxima admisible en el retorno a masa (borne 31) con consumidores en carga es de 0,1 V."
    )

    # 20. Medición en Carga
    builder.add_multichoice(
        "ALUM_P20_MC_Condicion_Medicion_Caida_Tension",
        "¿Por qué la medición de caída de tensión en el cableado con el voltímetro exige obligatoriamente que las luces estén encendidas y el circuito bajo carga?",
        [
            {"text": "Porque según la Ley de Ohm (V = I · R), si la corriente es cero (circuito apagado), la caída de tensión es cero aunque exista óxido.", "fraction": 100, "feedback": "¡Correcto! Con circuito abierto (I = 0 A), no hay caída de potencial a través de la resistencia parásita (ΔV = 0 · R = 0 V), enmascarando por completo la avería."},
            {"text": "Para evitar que el multímetro digital descargue la batería del vehículo durante la toma de datos.", "fraction": 0, "feedback": "Incorrecto. Un voltímetro digital tiene una impedancia interna de 10 MΩ y no descarga la batería."},
            {"text": "Para calentar el cristal del faro y conseguir que el haz óptico se enfoque hacia el regloscopio.", "fraction": 0, "feedback": "Incorrecto. No tiene ninguna relación con la óptica del faro."},
            {"text": "Porque las unidades de control BCM bloquean la pantalla del multímetro si no detectan consumo de corriente.", "fraction": 0, "feedback": "Incorrecto. El multímetro es un instrumento autónomo e independiente de las centralitas."}
        ],
        general_feedback="Ley de Ohm: La caída de tensión sólo se manifiesta cuando circula la corriente nominal por la resistencia del conductor (ΔV = I · R)."
    )

    # 21. Bixenón
    builder.add_truefalse(
        "ALUM_P21_TF_Bixenon_Mecanismo_Trampilla",
        "En un proyector Bixenón, la conmutación entre luz de cruce y luz de carretera se produce mediante un electroimán o servomotor que abate mecánicamente el diafragma obturador interno.",
        True,
        feedback_true="¡Correcto! Utiliza una sola lámpara de xenón; el electroimán retira el obturador permitiendo proyectar el 100% del flujo luminoso en carretera.",
        feedback_false="Incorrecto. El sistema bixenón mantiene la misma lámpara encendida y mueve un obturador móvil (pantalla) para cambiar el patrón fotométrico."
    )

    # 22. Luces de Curvas Dinámicas
    builder.add_multichoice(
        "ALUM_P22_MC_Alumbrado_Curvas_Dinamico_Sensores",
        "En los sistemas de iluminación adaptativa en curva dinámica (AFS), ¿qué señales principales utiliza la unidad de control para calcular el giro motorizado de los proyectores?",
        [
            {"text": "Ángulo del volante de dirección, velocidad lineal del vehículo y aceleración transversal de guiñada.", "fraction": 100, "feedback": "¡Correcto! La centralita AFS procesa el ángulo de dirección (sensor SAS), la velocidad del vehículo y los datos del ESP para girar los proyectores hasta ±15° anticipando la curva."},
            {"text": "Nivel de combustible en el depósito y temperatura del aceite de la caja de cambios automática.", "fraction": 0, "feedback": "Incorrecto. Esos parámetros no guardan relación con la trayectoria del vehículo."},
            {"text": "Presión del pedal del acelerador y temperatura del líquido refrigerante del radiador.", "fraction": 0, "feedback": "Incorrecto. No determinan la geometría de la curva que recorre el automóvil."},
            {"text": "Intensidad del viento exterior detectada por el sensor ultrasónico del parachoques trasero.", "fraction": 0, "feedback": "Incorrecto. El viento no orienta las ópticas de los faros delanteros."}
        ],
        general_feedback="Sistemas AFS dinámicos: Combinan sensor de ángulo de volante (SAS), velocidad del vehículo y sensor de guiñada (ESP)."
    )

    # 23. Emparejamiento Bornes DIN
    builder.add_matching(
        "ALUM_P23_Matching_Bornes_DIN_Alumbrado",
        "Empareja cada número de borne según la norma DIN 72552 con su función técnica en el circuito de alumbrado:",
        [
            ("56a", "Luz de carretera o largo alcance"),
            ("56b", "Luz de cruce o corto alcance"),
            ("58", "Luces de posición y gálibo"),
            ("31", "Retorno a masa negativo de batería")
        ],
        general_feedback="Norma DIN 72552: 56a = Carretera, 56b = Cruce, 58 = Posición, 31 = Masa."
    )

    # 24. Códigos Homologación ECE
    builder.add_matching(
        "ALUM_P24_Matching_Codigos_Homologacion_ECE",
        "Empareja cada código de homologación europeo grabado en los grupos ópticos con su función reglamentaria:",
        [
            ("RL", "Luz de conducción diurna (Daytime Running Light)"),
            ("AR", "Luz de marcha atrás"),
            ("B o F3", "Faro antiniebla delantero"),
            ("S3", "Tercera luz de freno central elevada")
        ],
        general_feedback="Códigos ECE: RL = Diurna, AR = Marcha atrás, B/F3 = Antiniebla delantero, S3 = 3ª luz freno."
    )

    # 25. Requisitos de Seguridad Xenón
    builder.add_multichoice(
        "ALUM_P25_MC_Seguridad_Alta_Tension_Xenon",
        "Durante la manipulación o sustitución de una lámpara de xenón en el taller, ¿por qué es obligatorio desconectar la batería o el conector del faro antes de intervenir?",
        [
            {"text": "El cebador genera picos de 20 a 30 kV con riesgo de descarga mortal.", "fraction": 100, "feedback": "¡Correcto! El arco eléctrico inicial requiere hasta 30 kV para ionizar el gas xenón."},
            {"text": "Para evitar que el gas xenón comprimido se fugue a la atmósfera al abrir la óptica.", "fraction": 0, "feedback": "Incorrecto. La ampolla de cuarzo es hermética y no se abre."},
            {"text": "Porque el balastro electrónico contiene imanes permanentes que alteran la brújula del GPS.", "fraction": 0, "feedback": "Incorrecto. No contiene imanes."},
            {"text": "Para reiniciar el contador interno de horas de encendido registrado en el cuadro de mandos.", "fraction": 0, "feedback": "Incorrecto. No tiene relación con el odómetro."}
        ],
        general_feedback="Seguridad en faros de descarga: Pico de cebado de 20 a 30 kV. Desconectar siempre la alimentación antes de intervenir."
    )

    builder.save_xml(output_xml_path)
    validar_moodle_xml(output_xml_path)


if __name__ == '__main__':
    dest_pkg = os.path.join(SCRIPT_DIR, "Curso_Circuitos_Alumbrado_Automocion.h5p")
    build_h5p_course(dest_pkg)

    # Generar y validar banco sumativo Moodle XML
    xml_path = os.path.join(SCRIPT_DIR, "evaluacion_circuitos_alumbrado.xml")
    generar_evaluacion_alumbrado_xml(xml_path)
