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
import re
import unicodedata

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
    {"machineName": "H5P.Table", "majorVersion": 1, "minorVersion": 2},
    {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
    {"machineName": "H5P.ImageHotspots", "majorVersion": 1, "minorVersion": 10},
    {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
    {"machineName": "H5P.Accordion", "majorVersion": 1, "minorVersion": 0},
    {"machineName": "H5P.Image", "majorVersion": 1, "minorVersion": 1},
    {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
    {"machineName": "H5P.Column", "majorVersion": 1, "minorVersion": 16},
    {"machineName": "H5P.InteractiveBook", "majorVersion": 1, "minorVersion": 7}
]

# =========================================================================
# 0. CONFIGURACIÓN GLOBAL: AUTORÍA, LICENCIA E IMÁGENES
# =========================================================================

AUTOR = "FP Madrid profesor JM Gurpegui"
LICENCIA = "CC BY-NC-SA"
LICENCIA_VERSION = "4.0"

MAX_IMAGE_WIDTH = 1280            # Ancho máximo en píxeles de las imágenes empaquetadas
JPEG_QUALITY = 85                 # Calidad JPG (85 = equilibrio nitidez/peso)
PNG_A_JPG_UMBRAL = 300 * 1024     # PNG opacos más pesados que esto se convierten a JPG
FORMATOS_IMAGEN = ('.png', '.jpg', '.jpeg', '.gif')  # WebP NO está en la whitelist de Moodle

# Registro de imágenes optimizadas: clave = nombre original o seguro -> metadatos reales
IMAGE_REGISTRY = {}


def nombre_seguro(filename):
    """Convierte un nombre de archivo en ASCII seguro: sin espacios, tildes ni caracteres especiales."""
    base, ext = os.path.splitext(os.path.basename(filename))
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode('ascii')
    base = re.sub(r'[^A-Za-z0-9_-]+', '_', base).strip('_').lower() or 'imagen'
    return base + ext.lower()


def preparar_imagenes(src_dir, cache_dir=None):
    """
    Optimiza todas las imágenes de src_dir con Pillow antes de empaquetar:
    - Redimensiona a un ancho máximo de MAX_IMAGE_WIDTH px (sin deformar).
    - JPG: recomprime a calidad JPEG_QUALITY.
    - PNG con transparencia: se mantiene PNG optimizado.
    - PNG opaco pesado (> PNG_A_JPG_UMBRAL): se convierte a JPG.
    - Renombra a nombres seguros (sin espacios ni tildes).
    Registra en IMAGE_REGISTRY la ruta, dimensiones reales y tipo MIME de cada imagen.
    """
    from PIL import Image

    src_dir = os.path.abspath(src_dir)
    if not os.path.isdir(src_dir):
        return IMAGE_REGISTRY
    if cache_dir is None:
        cache_dir = os.path.join(os.path.dirname(src_dir), '_imagenes_optimizadas')
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

    usados = set()
    total_antes = total_despues = 0
    for name in sorted(os.listdir(src_dir)):
        src = os.path.join(src_dir, name)
        ext = os.path.splitext(name)[1].lower()
        if not os.path.isfile(src):
            continue
        if ext not in FORMATOS_IMAGEN:
            print(f"⚠️ Imagen ignorada (formato no admitido en Moodle): {name}")
            continue

        seguro = nombre_seguro(name)
        base = os.path.splitext(seguro)[0]
        candidato, n = base, 2
        while candidato in usados:
            candidato, n = f"{base}_{n}", n + 1
        usados.add(candidato)
        bytes_antes = os.path.getsize(src)

        if ext == '.gif':
            final = candidato + '.gif'
            shutil.copy2(src, os.path.join(cache_dir, final))
            with Image.open(src) as im:
                w, h = im.size
            mime = 'image/gif'
        else:
            with Image.open(src) as im:
                im.load()
                tiene_alfa = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
                im = im.convert('RGBA' if tiene_alfa else 'RGB')
                if im.width > MAX_IMAGE_WIDTH:
                    nuevo_alto = round(im.height * MAX_IMAGE_WIDTH / im.width)
                    im = im.resize((MAX_IMAGE_WIDTH, nuevo_alto), Image.LANCZOS)
                w, h = im.size

                if ext in ('.jpg', '.jpeg'):
                    final, mime = candidato + '.jpg', 'image/jpeg'
                    im.save(os.path.join(cache_dir, final), 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
                else:
                    final, mime = candidato + '.png', 'image/png'
                    destino_png = os.path.join(cache_dir, final)
                    im.save(destino_png, 'PNG', optimize=True)
                    if not tiene_alfa and os.path.getsize(destino_png) > PNG_A_JPG_UMBRAL:
                        os.remove(destino_png)
                        final, mime = candidato + '.jpg', 'image/jpeg'
                        im.save(os.path.join(cache_dir, final), 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)

        ruta_final = os.path.join(cache_dir, final)
        bytes_despues = os.path.getsize(ruta_final)
        total_antes += bytes_antes
        total_despues += bytes_despues
        info = {
            "path": ruta_final,
            "rel_path": f"images/{final}",
            "width": w,
            "height": h,
            "mime": mime,
            "original": name
        }
        for clave in (name, seguro, final, f"images/{name}", f"images/{final}"):
            IMAGE_REGISTRY[clave] = info
        print(f"✓ Imagen optimizada: {name} → images/{final} ({w}x{h} px, {bytes_antes // 1024} KB → {bytes_despues // 1024} KB)")

    if total_antes:
        print(f"✓ Optimización de imágenes: {total_antes / 1048576:.2f} MB → {total_despues / 1048576:.2f} MB")
    return IMAGE_REGISTRY


def resolver_imagen(ref, width=None, height=None):
    """Devuelve (rel_path, mime, width, height) usando el registro de imágenes optimizadas si existe."""
    info = IMAGE_REGISTRY.get(ref) or IMAGE_REGISTRY.get(os.path.basename(ref))
    if info:
        return info["rel_path"], info["mime"], info["width"], info["height"]
    mime = "image/png" if ref.lower().endswith('.png') else "image/jpeg"
    return ref, mime, width or 1600, height or 900

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
                "license": LICENCIA
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

def create_image_section(rel_path, alt_text, title="Imagen Técnica", width=None, height=None):
    """
    Crea un bloque nativo H5P.Image 1.1 homologado con alt text descriptivo obligatorio.
    Si la imagen fue procesada con preparar_imagenes(), usa su ruta segura y dimensiones reales.
    """
    path, mime, width, height = resolver_imagen(rel_path, width, height)
    return create_column_wrapper("H5P.Image 1.1", {
        "contentName": "Image",
        "file": {
            "path": path,
            "mime": mime,
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
                    "license": LICENCIA
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

    img_path, img_mime, img_w, img_h = resolver_imagen(image_rel_path)
    params = {
        "image": {
            "path": img_path,
            "mime": img_mime,
            "copyright": {"license": "U"},
            "width": img_w,
            "height": img_h
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
            "license": LICENCIA,
            "authors": [{"name": AUTOR, "role": "Author"}]
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

def create_video_section(video_url, title="Vídeo Técnico Demostrativo de Taller"):
    """
    Genera un bloque nativo H5P.Video 1.6 para enlazar vídeos demostrativos de taller
    (YouTube o Mediateca EducaMadrid) sin incrementar el peso del archivo .h5p.
    """
    mime_type = "video/YouTube" if ("youtube.com" in video_url or "youtu.be" in video_url) else "video/mp4"
    params = {
        "visuals": {
            "fit": True,
            "controls": True
        },
        "playback": {
            "autoplay": False,
            "loop": False
        },
        "l10n": {
            "name": "Vídeo",
            "loading": "Cargando reproductor de vídeo...",
            "noPlayers": "No se encontraron reproductores compatibles con este formato de vídeo.",
            "noSources": "Falta la fuente de vídeo.",
            "aborted": "La reproducción de vídeo ha sido interrumpida.",
            "networkFailure": "Fallo de red al cargar el vídeo.",
            "cannotDecode": "No se puede decodificar el medio.",
            "formatNotSupported": "Formato de vídeo no soportado.",
            "mediaEncrypted": "Medio cifrado.",
            "unknownError": "Error desconocido.",
            "invalidYtId": "ID de YouTube no válido.",
            "unknownYtId": "No se ha podido localizar el vídeo con ese ID de YouTube.",
            "restrictedYt": "El propietario de este vídeo no permite su reproducción incrustada."
        },
        "sources": [
            {
                "path": video_url,
                "mime": mime_type,
                "copyright": {"license": "U"}
            }
        ]
    }
    return create_column_wrapper("H5P.Video 1.6", params, title)

def create_diagnostic_table(title, rows, intro_text=None):
    """
    Genera una tabla técnica normalizada de Diagnosis en Taller de Automoción:
    Columnas: Síntoma en Vehículo | Punto de Medida / Instrumento | Valor Nominal vs. Avería | Causa Raíz y Acción Correctiva.
    rows: Lista de tuplas/listas de 4 elementos: (sintoma, instrumento_punto, valores, accion)
    """
    intro_part = f"<p>{intro_text}</p>" if intro_text else ""
    rows_html = ""
    for r in rows:
        if len(r) >= 4:
            rows_html += f"""
            <tr>
              <td><strong>{r[0]}</strong></td>
              <td>{r[1]}</td>
              <td><span class="tech-formula">{r[2]}</span></td>
              <td>{r[3]}</td>
            </tr>
            """
    html = f"""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-stethoscope"></i> CUADRO METROLÓGICO DE DIAGNOSIS EN TALLER</div>
      <h3>{title}</h3>
      {intro_part}
      <div class="table-responsive">
        <table class="tech-table">
          <thead>
            <tr>
              <th>Síntoma en el Vehículo</th>
              <th>Punto de Medida / Instrumento</th>
              <th>Valor Nominal vs. Avería</th>
              <th>Causa Raíz y Acción Correctiva</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """
    return create_text_section(html, f"Diagnosis: {title}")

def create_component_spec_card(component_name, category_badge, specs_dict, pinout_list=None, oscilloscope_note=None):
    """
    Genera una Ficha Técnica Estandarizada de Sensor / Actuador de Automoción.
    specs_dict: Diccionario o lista de tuplas (etiqueta, valor), ej. [("Resistencia a 20 °C", "800 - 1000 Ω"), ("Tensión alimentación", "5.0 V ± 0.1 V")]
    pinout_list: Lista opcional de tuplas (pin_o_borne, funcion), ej. [("Pin 1 (Borne 15)", "+12 V tras contacto"), ("Pin 2 (Borne 31)", "Masa electrónica ECU")]
    oscilloscope_note: Nota opcional sobre forma de onda característica en osciloscopio.
    """
    items = specs_dict.items() if isinstance(specs_dict, dict) else specs_dict
    specs_html = ""
    for label, val in items:
        specs_html += f"""
        <div class="tech-spec-item">
          <span class="tech-spec-label">{label}</span>
          <span class="tech-spec-value">{val}</span>
        </div>
        """

    pinout_html = ""
    if pinout_list:
        pins = "".join(
            f'<li class="tech-pinout-badge"><strong>{p[0]}:</strong> {p[1]}</li>'
            for p in pinout_list
        )
        pinout_html = f"""
        <h4 style="color:#0c4a6e; margin:12px 0 6px 0; font-size:1rem;">Asignación de Bornes / Pinout (DIN 72552):</h4>
        <ul class="tech-pinout-list">{pins}</ul>
        """

    osc_html = ""
    if oscilloscope_note:
        osc_html = f"""
        <div class="alert-box alert-info" style="margin:12px 0 0 0; padding:12px 16px;">
          <strong>📈 Patrón en Osciloscopio / Polímetro:</strong> {oscilloscope_note}
        </div>
        """

    html = f"""
    <div class="tech-card">
      <div class="tech-card-badge"><i class="fa fa-microchip"></i> {category_badge}</div>
      <h3>{component_name}</h3>
      <div class="tech-spec-grid">
        {specs_html}
      </div>
      {pinout_html}
      {osc_html}
    </div>
    """
    return create_text_section(html, f"Ficha Técnica: {component_name}")

# =========================================================================
# 6. EMPAQUETADOR MAESTRO Y COMPILACIÓN DEL ARCHIVO .H5P
# =========================================================================

def build_h5p_package(output_path, title, book_cover_title, book_cover_desc, chapters, extra_images=None, images_source_dir=None, show_cover_page=True):
    """Compila físicamente el archivo ZIP final con estructura, accesibilidad y dependencias certificadas."""
    build_dir = os.path.join(PLANTILLA_DIR, "_build_tmp")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    content_dir = os.path.join(build_dir, 'content')
    images_dir = os.path.join(content_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)

    # 1. Copiar librerías homologadas exclusivamente
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

    # 3. Copiar imágenes optimizadas (Pillow: ≤1280 px, nombres seguros, dimensiones reales)
    if images_source_dir and os.path.isdir(images_source_dir) and not IMAGE_REGISTRY:
        hay_imgs = any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) for f in os.listdir(images_source_dir))
        if hay_imgs:
            print("⚠️ Aviso: llama a preparar_imagenes() ANTES de crear los capítulos para registrar dimensiones reales.")
            preparar_imagenes(images_source_dir)
    copiadas = set()
    for info in IMAGE_REGISTRY.values():
        if info["path"] in copiadas or not os.path.exists(info["path"]):
            continue
        shutil.copy2(info["path"], os.path.join(content_dir, info["rel_path"]))
        copiadas.add(info["path"])
    if copiadas:
        print(f"✓ {len(copiadas)} imagen(es) optimizada(s) empaquetada(s) en content/images/")

    # 4. Copiar imágenes adicionales individuales si existen
    if extra_images:
        for src, rel in extra_images:
            if os.path.exists(src):
                dst = os.path.join(content_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

    # 5. Construir content.json
    content_data = {
        "showCoverPage": show_cover_page,
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
                    "license": LICENCIA,
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

    # 6. Construir h5p.json
    h5p_manifest = {
        "title": title,
        "language": "es",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["div"],
        "license": LICENCIA,
        "authors": [{"name": AUTOR, "role": "Author"}],
        "licenseVersion": LICENCIA_VERSION,
        "preloadedDependencies": HOMOLOGATED_DEPENDENCIES
    }

    with open(os.path.join(build_dir, 'h5p.json'), 'w', encoding='utf-8') as f:
        json.dump(h5p_manifest, f, ensure_ascii=False, indent=2)

    # 7. Empaquetar ZIP (filtrando estrictamente según whitelist de H5P / Lumi / Moodle)
    if os.path.exists(output_path):
        os.remove(output_path)

    allowed_h5p_ext = {
        'json', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif', 'tiff', 'svg',
        'eot', 'ttf', 'woff', 'woff2', 'otf', 'webm', 'mp4', 'ogg', 'mp3',
        'm4a', 'wav', 'txt', 'pdf', 'rtf', 'doc', 'docx', 'xls', 'xlsx',
        'ppt', 'pptx', 'odt', 'ods', 'odp', 'xml', 'csv', 'diff', 'patch',
        'swf', 'md', 'textile', 'vtt', 'webvtt', 'gltf', 'glb', 'js', 'css'
    }
    excluded_dev_files = {
        'LICENSE', 'crowdin.yml', 'package.json', 'package-lock.json',
        'webpack.config.js', 'webpack.dev.config.js', 'karma.conf.js'
    }

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_dir):
            for file in sorted(files):
                if file.startswith('.') or file in excluded_dev_files:
                    continue
                ext = file.rsplit('.', 1)[-1].lower() if '.' in file else ''
                if ext not in allowed_h5p_ext:
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, build_dir).replace('\\', '/')
                if rel_path.startswith('H5P.InteractiveBook-1.7/src/'):
                    continue
                zipf.write(abs_path, rel_path)

    shutil.rmtree(build_dir)
    print(f"\n✅ Paquete H5P generado: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")


# =========================================================================
# EJEMPLO MAESTRO: CURSO MODELO QUE INTEGRA LOS 5 PILARES PEDAGÓGICOS
# =========================================================================
def generar_evaluacion_modelo_xml(output_xml_path):
    """Genera y valida el banco de preguntas Moodle XML oficial desacoplado de la plantilla (13 preguntas, 6 tipos)."""
    try:
        from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
    except ImportError:
        sys.path.insert(0, PLANTILLA_DIR)
        from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml

    builder = MoodleXMLBuilder("Plantilla Oficial EducaMadrid - Evaluacion Sumativa Automocion")

    # P1: Desacoplamiento de H5P y XML (Correcta es la más larga #1 de 6 -> 33.3% equilibrado)
    builder.add_multichoice(
        "P01_Desacoplamiento_Evaluacion",
        "¿Por qué la normativa oficial de EducaMadrid recomienda separar los contenidos interactivos H5P del cuestionario sumativo oficial en Moodle XML?",
        [
            {
                "text": "Garantizar el registro infalible de notas en Moodle evitando pérdidas de eventos xAPI y bloqueos táctiles en móviles.",
                "fraction": 100,
                "feedback": "¡Correcto! El criterio de visualización en Moodle es 100% infalible, mientras que la nota sumativa se gestiona con fiabilidad absoluta mediante los cuestionarios nativos Moodle Quiz (mod_quiz)."
            },
            {
                "text": "Cumplir la restricción que prohíbe evaluar contenidos interactivos en ciclos de Formación Profesional.",
                "fraction": 0,
                "feedback": "Incorrecto. H5P dispone de actividades propias, pero las sentencias xAPI dependen de conexión estable y cookies que fallan con frecuencia en smartphones."
            },
            {
                "text": "Reducir el tamaño de descarga del paquete H5P y minimizar el consumo de datos en el Aula Virtual.",
                "fraction": 0,
                "feedback": "Incorrecto. Aunque reduce el peso, el motivo crítico es la fiabilidad del registro de calificaciones en mdl_grade_grades."
            },
            {
                "text": "Impedir que el alumnado repita las actividades formativas durante el estudio autónomo de la unidad.",
                "fraction": 0,
                "feedback": "Incorrecto. Precisamente la parte formativa permite consulta libre e ilimitada."
            }
        ],
        general_feedback="El desacoplamiento garantiza que el estudio en H5P sea 100% fluido y la evaluación sumativa se registre de forma nativa e infalible en Moodle."
    )

    # P2: Contraste WCAG 2.1 AAA (Correcta es la más larga #2 de 6 -> 33.3% equilibrado)
    builder.add_multichoice(
        "P02_Contraste_WCAG_AAA",
        "Según las directrices de accesibilidad universal WCAG 2.1 nivel AAA para entornos educativos, ¿cuál es el ratio de contraste mínimo exigido para el texto principal?",
        [
            {
                "text": "Al menos 7:1 para garantizar lectura nítida sin fatiga visual en cualquier pantalla o luz de taller.",
                "fraction": 100,
                "feedback": "¡Correcto! El nivel AAA exige un ratio mínimo de 7:1 para texto estándar, prohibiendo textos de color claro o pálido."
            },
            {
                "text": "Al menos 4.5:1 exigido únicamente para textos secundarios en el nivel de conformidad básico AA.",
                "fraction": 0,
                "feedback": "Incorrecto. 4.5:1 es el umbral mínimo del nivel AA, pero la plantilla adopta el estándar superior AAA (>= 7:1)."
            },
            {
                "text": "Al menos 3:1 válido para cualquier tipo de texto técnico y tablas de medición en dispositivos móviles.",
                "fraction": 0,
                "feedback": "Incorrecto. 3:1 resulta insuficiente para texto de lectura técnica."
            },
            {
                "text": "Cualquier valor libre siempre que se utilicen colores corporativos suaves sobre fondos claros.",
                "fraction": 0,
                "feedback": "Incorrecto. Los textos claros sobre fondos claros son ilegibles en proyectores y móviles."
            }
        ],
        general_feedback="El estándar AAA (contraste > 7:1 y texto principal #0f172a > 13:1) asegura legibilidad total en proyectores de aula, móviles y talleres."
    )

    # P3: Whitelist de Moodle (Distractor más largo que la correcta)
    builder.add_multichoice(
        "P03_Whitelist_Moodle_Seguridad",
        "¿Qué formatos de archivo están estrictamente prohibidos dentro del directorio content/ de un paquete H5P para prevenir el error 'not-in-whitelist'?",
        [
            {
                "text": "Archivos vectoriales .svg y documentos locales .html.",
                "fraction": 100,
                "feedback": "¡Correcto! Moodle bloquea archivos SVG y HTML locales en content/ para neutralizar ataques de inyección de código malicioso (Stored XSS). Todos los esquemas deben rasterizarse a PNG o JPEG."
            },
            {
                "text": "Archivos de mapa de bits comprimidos en formato .png y .jpg de alta resolución.",
                "fraction": 0,
                "feedback": "Incorrecto. PNG y JPEG son formatos plenamente admitidos y recomendados por la whitelist oficial."
            },
            {
                "text": "Grabaciones de audio en .mp3 y tipografías web .woff2 incluidas en las librerías.",
                "fraction": 0,
                "feedback": "Incorrecto. El audio y las fuentes web forman parte de la lista blanca admitida."
            },
            {
                "text": "Estructuras de configuración y metadatos del paquete en formato .json estándar.",
                "fraction": 0,
                "feedback": "Incorrecto. content.json es el núcleo semántico indispensable del paquete H5P."
            }
        ],
        general_feedback="H5PValidator.php rechaza cualquier paquete con extensiones fuera de la whitelist oficial tanto en content/ como en las librerías."
    )

    # P4: Andamiaje pedagógico (Distractor más largo que la correcta)
    builder.add_multichoice(
        "P04_Andamiaje_Cuatro_Fases",
        "¿Cuál es la secuencia didáctica progresiva en 4 fases que estructura cada unidad interactiva según el modelo de Aprendizaje Activo?",
        [
            {
                "text": "1. Motivación activa ➔ 2. Explicación ➔ 3. Práctica guiada ➔ 4. Síntesis y evaluación.",
                "fraction": 100,
                "feedback": "¡Correcto! Esta progresión pedagógica activa conocimientos previos, expone teoría concisa con fichas técnicas, ejercita protocolos de taller y deriva a la evaluación oficial."
            },
            {
                "text": "1. Examen inicial sin base previa ➔ 2. Lectura lineal teórica ➔ 3. Descanso pautado ➔ 4. Entrega de informe.",
                "fraction": 0,
                "feedback": "Incorrecto. El andamiaje pedagógico exige preparación y práctica antes de la evaluación."
            },
            {
                "text": "1. Práctica directa en banco ➔ 2. Dudas en el foro ➔ 3. Examen sumativo ➔ 4. Repetición de la evaluación.",
                "fraction": 0,
                "feedback": "Incorrecto. La práctica sin andamiaje ni explicación previa de seguridad genera riesgos y errores en taller."
            },
            {
                "text": "1. Visionado de vídeo externo ➔ 2. Descarga de manual en PDF ➔ 3. Cuestionario ➔ 4. Calificación final.",
                "fraction": 0,
                "feedback": "Incorrecto. Este enfoque fragmentado dispersa la atención del estudiante; el modelo oficial unifica la secuencia."
            }
        ],
        general_feedback="El andamiaje en 4 fases sustituye los muros de texto pasivo por interacción cognitiva estructurada."
    )

    # P5: Touch targets en dispositivos móviles (Correcta más corta que los distractores)
    builder.add_multichoice(
        "P05_Touch_Targets_Moviles",
        "Para garantizar que los contenidos sean perfectamente accesibles y utilizables en smartphones y tablets (incluso con guantes en taller), ¿qué dimensión mínima deben tener los objetivos táctiles?",
        [
            {
                "text": "44 x 44 píxeles como dimensión ergonómica mínima (WCAG 2.5.5).",
                "fraction": 100,
                "feedback": "¡Correcto! 44 x 44 px es el tamaño mínimo ergonómico para interacción táctil con el pulgar o dedos enguantados."
            },
            {
                "text": "Al menos 60 x 60 píxeles obligatorios exclusivamente en monitores de escritorio.",
                "fraction": 0,
                "feedback": "Incorrecto. El requisito ergonómico táctil aplica de forma prioritaria a pantallas móviles y tablets."
            },
            {
                "text": "Un máximo de 24 x 24 píxeles para condensar más botones en pantallas pequeñas.",
                "fraction": 0,
                "feedback": "Incorrecto. Botones tan pequeños provocan pulsaciones accidentales constantes en teléfonos móviles."
            },
            {
                "text": "El ancho estricto del texto visible sin añadir relleno ni márgenes de pulsación.",
                "fraction": 0,
                "feedback": "Incorrecto. Los elementos táctiles exigen áreas de pulsación mínimas independientes de la longitud del texto."
            }
        ],
        general_feedback="Los botones, listas de cotejo y cabeceras de acordeón deben respetar siempre touch targets >= 44x44 px."
    )

    # P6: Fórmulas matemáticas (Distractores ligeramente más largos)
    builder.add_multichoice(
        "P06_Formulas_HTML_Semantico",
        "¿Por qué está prohibido utilizar delimitadores LaTeX crudos ($ ... $) en los textos de H5P?",
        [
            {
                "text": "Porque H5P.AdvancedText no incorpora MathJax por defecto y mostraría el código fuente sin formatear.",
                "fraction": 100,
                "feedback": "¡Correcto! Se debe utilizar siempre HTML semántico y Unicode (<sub>, <sup>, .tech-formula), asegurando renderizado inmediato y accesible."
            },
            {
                "text": "Porque el compilador de LaTeX genera incompatibilidades críticas con los navegadores móviles actuales.",
                "fraction": 0,
                "feedback": "Incorrecto. LaTeX es multiplataforma, pero requiere motores de renderizado que no residen en el iframe de H5P."
            },
            {
                "text": "Porque la sintaxis matemática LaTeX vulnera los protocolos de seguridad cortafuegos del servidor Moodle.",
                "fraction": 0,
                "feedback": "Incorrecto. No supone un problema de seguridad, sino de ausencia de motor MathJax dentro del iframe H5P."
            },
            {
                "text": "Porque su procesamiento incrementa exponencialmente el peso del archivo comprimido superando la cuota.",
                "fraction": 0,
                "feedback": "Incorrecto. El texto plano no añade peso; el fallo es visual al mostrarse los signos de dólar crudos."
            }
        ],
        general_feedback="El estándar HTML semántico + Unicode garantiza compatibilidad universal en tablets, móviles y lectores de pantalla."
    )

    # P7: Verdadero / Falso - Inyección de estilos
    builder.add_truefalse(
        "P07_TF_Inyeccion_Estilos_CSS",
        "¿Es una práctica correcta insertar etiquetas &lt;style&gt; dentro de los bloques de contenido de H5P para aplicar estilos personalizados?",
        False,
        feedback_true="Incorrecto. El sanitizador de H5P elimina las etiquetas &lt;style&gt; pero expone el código CSS como texto plano residual visible en pantalla (CSS leakage).",
        feedback_false="¡Correcto! Es falso. Los estilos accesibles deben inyectarse limpiamente en las hojas de estilo de las librerías base (h5p-interactive-book.css y h5p-column.css).",
        general_feedback="La inyección en librerías base previene fugas de código y unifica el tema visual."
    )

    # P8: Verdadero / Falso - Menú en móviles
    builder.add_truefalse(
        "P08_TF_Menu_Table_Of_Contents_Movil",
        "Para optimizar la visualización en dispositivos móviles, se recomienda configurar 'defaultTableOfContents: false' en InteractiveBook para evitar que el índice lateral cubra el contenido al abrir el curso.",
        True,
        feedback_true="¡Correcto! Al configurar defaultTableOfContents: false, el estudiante ve directamente la portada y el tema en su teléfono, pudiendo desplegar el menú táctilmente cuando lo desee.",
        feedback_false="Incorrecto. Si defaultTableOfContents es true, el menú ocupa toda la pantalla en smartphones y bloquea la visualización del contenido.",
        general_feedback="El diseño responsive exige que el menú no obstruya la lectura inicial en pantallas reducidas."
    )

    # P9: Emparejamiento - Bornes DIN 72552 e Instrumentación
    builder.add_matching(
        "P09_Emparejamiento_Bornes_DIN_72552",
        "Relaciona cada código de borne normalizado según DIN 72552 con su función eléctrica en el automóvil:",
        [
            ("Borne 30", "Alimentación positiva permanente directa desde el borne positivo de la batería"),
            ("Borne 15", "Positivo conmutado tras llave de contacto o encendido activado"),
            ("Borne 31", "Línea de retorno a masa conectada al chasis o polo negativo de batería"),
            ("Borne 50", "Señal positiva temporal de excitación del solenoide del motor de arranque")
        ],
        general_feedback="El dominio de los bornes DIN 72552 (30, 15, 31, 50, 85, 86, 87) es indispensable para la lectura de esquemas eléctricos."
    )

    # P10: Cálculo Numérico de Taller (type="numerical")
    builder.add_numerical(
        "P10_Calculo_Caida_Tension_Contacto",
        "Durante la comprobación bajo carga de una línea de alimentación por la que circulan <strong>I = 10 A</strong>, un borne sulfatado presenta una resistencia parásita de <strong>R = 0.25 Ω</strong>. Calcula la caída de tensión (ΔV = I × R) en voltios que medirá el polímetro entre los extremos del borne:",
        answer_value=2.5,
        tolerance=0.05,
        feedback="¡Correcto! Aplicando la Ley de Ohm: ΔV = 10 A × 0.25 Ω = 2.5 V (valor muy superior al máximo admisible de 0.2 V, confirmando avería en el contacto).",
        general_feedback="Por la Ley de Ohm (ΔV = I × R), 10 A × 0.25 Ω = 2.5 V. Cualquier caída superior a 0.2 V en una línea de potencia exige limpiar y reapretar el terminal.",
        units=["V", "voltios"]
    )

    # P11: Cálculo Numérico de Frecuencia de Sensor (type="numerical")
    builder.add_numerical(
        "P11_Calculo_Frecuencia_Sensor_Hall",
        "Al diagnosticar con el osciloscopio la señal cuadrada de un sensor Hall de régimen (CKP), mides un período completo de <strong>T = 0.002 s</strong> (2 ms). Calcula la frecuencia <strong>f = 1 / T</strong> de la señal en hercios (Hz):",
        answer_value=500,
        tolerance=1.0,
        feedback="¡Correcto! f = 1 / 0.002 s = 500 Hz.",
        general_feedback="La frecuencia es la inversa del período expresado en segundos: f = 1 / 0.002 s = 500 Hz.",
        units=["Hz", "hercios"]
    )

    # P12: Respuesta Corta - Identificación directa de borne DIN (type="shortanswer")
    builder.add_shortanswer(
        "P12_Identificacion_Borne_Masa_DIN",
        "Escribe únicamente el <strong>número de dos dígitos</strong> que identifica la línea de retorno a masa directa al chasis o negativo de batería según la norma alemana DIN 72552:",
        accepted_answers=[
            {"text": "31", "fraction": 100, "feedback": "¡Correcto! El número 31 designa universalmente la masa según DIN 72552."},
            {"text": "Borne 31", "fraction": 100, "feedback": "¡Correcto! El Borne 31 designa universalmente la masa según DIN 72552."}
        ],
        general_feedback="Según la norma DIN 72552, el número 31 identifica siempre el retorno a masa (habitualmente cable marrón BR en vehículos alemanes)."
    )

    # P13: Arrastrar sobre Imagen (type="ddimageortext") - Identificación de elementos de taller
    builder.add_ddimageortext(
        "P13_Arrastrar_Imagen_Esquema_Rele_Bornes",
        "Arrastra los rótulos a su posición correspondiente sobre el esquema técnico del relé de automoción:",
        image_path=os.path.join(PLANTILLA_DIR, "logo2026.png"),
        items=[
            {"text": "Borne 30 (Entrada Batería)", "x": 60, "y": 40, "group": 1},
            {"text": "Borne 87 (Salida a Consumidor)", "x": 240, "y": 40, "group": 1},
            {"text": "Bobina de Mando (85 - 86)", "x": 150, "y": 120, "group": 1},
            {"text": "Diodo de Supresión de Picos", "x": 150, "y": 180, "group": 1},
        ],
        general_feedback="La correcta identificación de los terminales de un relé es esencial para realizar diagnósticos y mediciones de caída de tensión en el taller."
    )

    builder.save_xml(output_xml_path)
    validar_moodle_xml(output_xml_path)


def cargar_curso_yaml(yaml_path, output_dir=None, images_dir=None):
    """
    Compila un curso completo (H5P InteractiveBook + Moodle XML) a partir de un archivo YAML.
    Desacopla el contenido pedagógico de la lógica de programación y empaquetado.
    """
    try:
        from yaml_course_builder import compilar_curso_desde_yaml
    except ImportError:
        from plantilla.yaml_course_builder import compilar_curso_desde_yaml
    return compilar_curso_desde_yaml(yaml_path, output_dir=output_dir, images_dir=images_dir)


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
            <span class="tech-badge badge-blue">Formación Profesional Automoción</span>
            <span class="tech-badge badge-green">EducaMadrid Moodle Ready</span>
            <span class="tech-badge badge-yellow">WCAG 2.1 AAA Accesible</span>
            <span class="tech-badge badge-purple">100% Formativo + Moodle XML</span>
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
    # CAPÍTULO 1: MEDIDAS ELÉCTRICAS, FICHAS TÉCNICAS Y DIAGNOSIS EN TALLER
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

    # Fase 2: Explicación técnica interactiva con fórmulas semánticas y ficha de componente
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
              Con una corriente de 10 A y 0.25 Ω de resistencia parásita en un borne: 10 A × 0.25 Ω = <strong>2.5 V de caída</strong>
            </div>
          </div>
        </div>
        """, "Fundamentos de Medición y Ley de Ohm"),
        create_component_spec_card(
            component_name="Relé Electromagnético de Potencia (4/5 Patillas DIN 72552)",
            category_badge="FICHA TÉCNICA DE ACTUADOR / CONMUTACIÓN",
            specs_dict=[
                ("Resistencia Bobina (85-86)", "75 Ω – 100 Ω (a 20 °C)"),
                ("Consumo de Excitación", "120 mA – 160 mA (a 12 V)"),
                ("Caída Máxima Contacto (30-87)", "≤ 0.15 V bajo carga nominal"),
                ("Corriente Nominal Potencia", "20 A – 40 A según calibre")
            ],
            pinout_list=[
                ("Borne 85", "Negativo de bobina (masa 31 o mando ECU)"),
                ("Borne 86", "Positivo de excitación de bobina (+15)"),
                ("Borne 30", "Entrada de potencia directa (+Bat protegida)"),
                ("Borne 87", "Salida normalmente abierta (NO) al consumidor")
            ],
            oscilloscope_note="Al desactivar la bobina (85-86), un relé con diodo o resistencia antiparasitaria limita el pico inductivo a < 35 V."
        )
    ]

    # Fase 3: Práctica guiada activa con tabla de diagnosis, checklist táctil, acordeón y simulador
    c1_fase3_practica = [
        create_diagnostic_table(
            title="Protocolo de Diagnosis por Caída de Tensión en Circuito de Potencia",
            rows=[
                (
                    "Consumidor no actúa o funciona con debilidad",
                    "Voltímetro en paralelo entre Borne (+) Batería y entrada positiva del consumidor (bajo carga)",
                    "Nominal: ≤ 0.2 V | Avería: 2.5 V",
                    "Sulfatación o contacto fogueado en relé (30-87) o portafusibles. Limpiar y reapretar."
                ),
                (
                    "Calentamiento anómalo en conector de chasis",
                    "Voltímetro en paralelo entre carcasa masa del consumidor y Borne (-) Batería (bajo carga)",
                    "Nominal: ≤ 0.1 V | Avería: 1.4 V",
                    "Óxido en tornillo de masa (Borne 31). Lijar terminal, aplicar grasa conductora y apretar a par."
                )
            ],
            intro_text="Recuerda realizar todas las mediciones de caída de tensión con el circuito cerrado y el consumidor activado:"
        ),
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
            "<p>Has completado el análisis de la Ley de Ohm aplicada a caídas de tensión parásitas, fichas técnicas de relés DIN 72552, tablas de diagnosis bajo consumo real con multímetro y protocolos de comprobación. Para registrar tu evaluación oficial en el Libro de Calificaciones, realiza el cuestionario Moodle XML correspondiente.</p>"
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
        book_cover_desc="Plantilla técnica maestra para Formación Profesional de Automoción en EducaMadrid y Moodle. Integración de los 5 pilares pedagógicos de aprendizaje activo, andamiaje, fichas técnicas, tablas de diagnosis y accesibilidad WCAG 2.1 AAA.",
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


