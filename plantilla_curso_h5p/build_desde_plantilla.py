#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor Universal de Compilación H5P desde Plantilla Modular
Separación estricta de Contenidos (HTML) y Evaluación (Moodle XML).
100% Compatible con EducaMadrid y Moodle (InteractiveBook 1.7 + QuestionSet 1.20).

Uso:
  python3 build_desde_plantilla.py [archivo_config.json]
"""

import os
import sys
import json
import uuid
import zipfile
import shutil

# Localizar directorios base
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_WORKSPACE = os.path.dirname(TEMPLATE_DIR)

# Búsqueda robusta del repositorio de librerías oficiales H5P
LIBS_BASE = None
for candidate in [
    os.path.join(TEMPLATE_DIR, "h5p_libraries"),
    os.path.join(ROOT_WORKSPACE, "h5p_libraries"),
    os.path.join(ROOT_WORKSPACE, "h5p_test_get"),
    os.path.join(TEMPLATE_DIR, "h5p_test_get")
]:
    if os.path.isdir(candidate):
        LIBS_BASE = candidate
        break

if not LIBS_BASE:
    raise FileNotFoundError("No se encontró el repositorio de librerías oficiales H5P (h5p_libraries o h5p_test_get).")

sys.path.insert(0, TEMPLATE_DIR)

from xml_moodle_parser import moodle_xml_to_h5p_questions_list, parse_moodle_xml
from h5p_utils import (
    MOODLE_CONTENT_WHITELIST, LIBS_MAP,
    get_image_info, copy_library_to_zip, validate_moodle_whitelist,
    wrap_column_item, create_accordion, create_multi_choice_check,
    create_video_component, create_question_set_params
)

def compilar_curso_desde_plantilla(config_path=None):
    if config_path is None:
        config_path = os.path.join(TEMPLATE_DIR, "curso_config.json")

    print("=" * 75)
    print("INICIANDO COMPILACIÓN DE CURSO H5P DESDE PLANTILLA MODULAR")
    print(f"Archivo de configuración: {os.path.basename(config_path)}")
    print("=" * 75)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    titulo_curso = config.get("titulo_curso", "Curso Interactivo H5P")
    desc_portada = config.get("descripcion_portada", "<p>Curso interactivo de Formación Profesional.</p>")
    img_portada_name = config.get("imagen_portada", "logo2026.bmp")
    
    output_curso_name = config.get("output_curso_h5p", "Curso_H5P.h5p")
    output_eval_name = config.get("output_evaluacion_h5p", "Evaluacion_H5P.h5p")
    
    output_curso_path = os.path.join(ROOT_WORKSPACE, output_curso_name)
    output_eval_path = os.path.join(ROOT_WORKSPACE, output_eval_name)

    # 1. PARTE DE EVALUACIÓN (Moodle XML)
    eval_cfg = config.get("evaluacion", {})
    xml_rel_path = eval_cfg.get("archivo_xml", "evaluacion/preguntas_moodle.xml")
    xml_full_path = os.path.join(TEMPLATE_DIR, xml_rel_path)
    
    print(f"\n📂 Cargando Banco de Preguntas Moodle XML: {xml_rel_path}...")
    if not os.path.isfile(xml_full_path):
        raise FileNotFoundError(f"No se encontró el archivo XML de evaluación: {xml_full_path}")

    # Convertir Moodle XML a componentes H5P MultiChoice
    questions_h5p = moodle_xml_to_h5p_questions_list(xml_full_path)
    total_preguntas = len(questions_h5p)
    pass_pct = eval_cfg.get("pass_percentage", 70)
    pool_size = eval_cfg.get("pool_size", min(20, total_preguntas))
    titulo_examen = eval_cfg.get("titulo_examen", f"Evaluación Oficial: {titulo_curso}")
    instrucciones_examen = eval_cfg.get("instrucciones_html", "<p>Responde a los supuestos prácticos para obtener tu calificación.</p>")
    print(f"✓ {total_preguntas} preguntas cargadas desde Moodle XML (Muestreo: {pool_size}, Corte: {pass_pct}%).")

    # 2. PARTE DE CONTENIDOS (HTML + Acordeones + Imágenes + Vídeos)
    chapters_spec = config.get("capitulos", [])
    chapters = []
    images_to_bundle = set()

    # Procesar imagen de portada
    img_portada_path = os.path.join(TEMPLATE_DIR, "imagenes", img_portada_name)
    if os.path.isfile(img_portada_path):
        images_to_bundle.add(img_portada_path)
        cov_w, cov_h, cov_mime = get_image_info(img_portada_path)
    else:
        cov_w, cov_h, cov_mime = 1200, 600, "image/png"

    print(f"\n📑 Procesando {len(chapters_spec)} capítulos de contenido teórico...")
    for idx, chap_cfg in enumerate(chapters_spec):
        chap_title = chap_cfg.get("titulo", f"Capítulo {idx+1}")
        html_rel = chap_cfg.get("archivo_html")
        chap_imgs = chap_cfg.get("imagenes", [])
        chap_accordions_raw = chap_cfg.get("acordeones", [])
        chap_formative_raw = chap_cfg.get("comprobacion_formativa")
        chap_video_raw = chap_cfg.get("video")

        column_content = []

        # A. Contenido HTML
        if html_rel:
            html_full = os.path.join(TEMPLATE_DIR, html_rel)
            if os.path.isfile(html_full):
                with open(html_full, "r", encoding="utf-8") as hf:
                    html_text = hf.read()
                column_content.append(wrap_column_item({
                    "library": "H5P.AdvancedText 1.1",
                    "params": {"text": html_text},
                    "subContentId": str(uuid.uuid4()),
                    "metadata": {"title": f"Teoría: {chap_title}"}
                }, default_title=f"Teoría: {chap_title}"))

        # B. Imágenes
        for img_rel in chap_imgs:
            img_full = os.path.join(TEMPLATE_DIR, "imagenes", img_rel)
            if os.path.isfile(img_full):
                images_to_bundle.add(img_full)
                w, h, mime = get_image_info(img_full)
                column_content.append(wrap_column_item({
                    "library": "H5P.Image 1.1",
                    "params": {
                        "file": {
                            "path": f"images/{img_rel}",
                            "mime": mime,
                            "width": w,
                            "height": h
                        },
                        "alt": f"Ilustración Técnica: {chap_title}",
                        "title": f"Recurso Gráfico - {chap_title}"
                    },
                    "subContentId": str(uuid.uuid4()),
                    "metadata": {"title": f"Imagen: {chap_title}"}
                }, default_title=f"Imagen: {chap_title}"))

        # C. Vídeo técnico H5P.Video 1.6
        if chap_video_raw:
            v_title = chap_video_raw.get("titulo", "Vídeo Técnico")
            v_url = chap_video_raw.get("url", "")
            if v_url:
                column_content.append(wrap_column_item({
                    "library": "H5P.AdvancedText 1.1",
                    "params": {
                        "text": (
                            "<div style='margin-top: 20px; margin-bottom: 8px;'>"
                            "<h4 style='color: #0369a1; border-left: 4px solid #0369a1; padding-left: 10px; margin: 0; font-weight: 800;'>"
                            "▶ Reproductor de Vídeo Técnico Integrado</h4></div>"
                        )
                    },
                    "subContentId": str(uuid.uuid4()),
                    "metadata": {"title": "Encabezado Vídeo"}
                }, default_title="Encabezado Vídeo"))
                column_content.append(wrap_column_item(
                    create_video_component(v_title, v_url),
                    default_title=v_title
                ))

        # D. Acordeones desplegables
        if chap_accordions_raw:
            panels = [(p.get("titulo", "Panel"), f"<div style='color: #0f172a;'>{p.get('contenido', '')}</div>") for p in chap_accordions_raw]
            column_content.append(wrap_column_item(
                create_accordion(panels),
                default_title="Protocolos y Guías Prácticas"
            ))

        # E. Comprobación formativa
        if chap_formative_raw:
            q_txt = chap_formative_raw.get("enunciado", "¿Pregunta de comprobación?")
            opts = chap_formative_raw.get("opciones", [])
            corr = chap_formative_raw.get("correcta", 0)
            fb = chap_formative_raw.get("feedback", "Retroalimentación formativa.")

            column_content.append(wrap_column_item({
                "library": "H5P.AdvancedText 1.1",
                "params": {
                    "text": (
                        "<div style='margin-top: 28px; margin-bottom: 10px; padding: 12px 16px; background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #0284c7; border-radius: 4px;'>"
                        "<strong style='color: #0f172a; font-size: 1.05em; font-weight: 800;'>⚡ Comprueba lo aprendido en este tema:</strong>"
                        "<p style='color: #0f172a; margin: 4px 0 0 0; font-size: 0.95em; font-weight: 500;'>Responde a la siguiente cuestión de autoevaluación para afianzar conceptos clave.</p></div>"
                    )
                },
                "subContentId": str(uuid.uuid4()),
                "metadata": {"title": "Comprobación Formativa"}
            }, default_title="Comprobación Formativa"))

            column_content.append(wrap_column_item(
                create_multi_choice_check(q_txt, opts, corr, fb),
                default_title="Cuestión de Autoevaluación"
            ))

        chapters.append({
            "library": "H5P.Column 1.16",
            "params": {"content": column_content},
            "subContentId": str(uuid.uuid4()),
            "metadata": {"title": chap_title}
        })

    # 3. CAPÍTULO FINAL: CUESTIONARIO OFICIAL CALIFICADO (H5P.QuestionSet 1.20)
    quiz_params = create_question_set_params(
        titulo_examen,
        instrucciones_examen,
        questions_h5p,
        pass_pct=pass_pct,
        pool_size=pool_size
    )

    eval_column = [
        wrap_column_item({
            "library": "H5P.AdvancedText 1.1",
            "params": {
                "text": (
                    "<div style='background: #f8fafc; border: 2px solid #047857; border-left: 8px solid #047857; padding: 20px 24px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);'>"
                    "<h2 style='color: #047857; margin: 0 0 10px 0; font-size: 1.5em; font-weight: 800;'>📝 Evaluación Oficial del Módulo</h2>"
                    "<p style='margin: 0; font-size: 1.05em; line-height: 1.6; color: #0f172a; font-weight: 500;'>"
                    "Este cuestionario final está conectado directamente con el Libro de Calificaciones de EducaMadrid / Moodle. "
                    "Al finalizar los supuestos y pulsar 'Guardar Calificación', tu nota se transmitirá automáticamente al calificador oficial.</p>"
                    "</div>"
                )
            },
            "subContentId": str(uuid.uuid4()),
            "metadata": {"title": "Instrucciones de Evaluación Oficial"}
        }, default_title="Instrucciones de Evaluación Oficial"),
        wrap_column_item({
            "library": "H5P.QuestionSet 1.20",
            "params": quiz_params,
            "subContentId": str(uuid.uuid4()),
            "metadata": {"title": "Cuestionario de Evaluación Oficial Moodle"}
        }, default_title="Cuestionario de Evaluación Oficial Moodle")
    ]

    chapters.append({
        "library": "H5P.Column 1.16",
        "params": {"content": eval_column},
        "subContentId": str(uuid.uuid4()),
        "metadata": {"title": "Evaluación Final (Test Oficial Moodle)"}
    })

    # 4. ESTRUCTURA H5P.InteractiveBook 1.7
    book_content = {
        "title": titulo_curso,
        "metadata": {"title": titulo_curso},
        "showCoverPage": True,
        "bookCover": {
            "coverTitle": titulo_curso,
            "coverDescription": desc_portada,
            "coverMedium": {
                "library": "H5P.Image 1.1",
                "params": {
                    "file": {
                        "path": f"images/{img_portada_name}",
                        "mime": cov_mime,
                        "width": cov_w,
                        "height": cov_h
                    },
                    "alt": "Imagen de Portada",
                    "title": titulo_curso
                },
                "subContentId": str(uuid.uuid4()),
                "metadata": {"title": "Portada"}
            }
        },
        "chapters": chapters,
        "behaviour": {
            "defaultTableOfContents": True,
            "progressIndicators": True,
            "progressAuto": True
        },
        "l10n": {
            "read": "Iniciar Lectura del Curso",
            "displayTOC": "Mostrar Menú de Contenidos",
            "hideTOC": "Ocultar Menú de Contenidos",
            "nextPage": "Siguiente Capítulo",
            "previousPage": "Capítulo Anterior",
            "navigateToTop": "Volver al Inicio",
            "fullscreen": "Pantalla Completa",
            "exitFullscreen": "Salir de Pantalla Completa"
        }
    }

    h5p_manifest_book = {
        "title": titulo_curso,
        "language": "es",
        "mainLibrary": "H5P.InteractiveBook",
        "embedTypes": ["div"],
        "preloadedDependencies": [
            {"machineName": "H5P.InteractiveBook", "majorVersion": 1, "minorVersion": 7},
            {"machineName": "H5P.Column", "majorVersion": 1, "minorVersion": 16},
            {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
            {"machineName": "H5P.Image", "majorVersion": 1, "minorVersion": 1},
            {"machineName": "H5P.Accordion", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
            {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
            {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
            {"machineName": "H5P.QuestionSet", "majorVersion": 1, "minorVersion": 20},
            {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
            {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
            {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
            {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10}
        ]
    }

    print(f"\n📘 Compilando Paquete Curso Completo: {os.path.basename(output_curso_path)}...")
    with zipfile.ZipFile(output_curso_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('h5p.json', json.dumps(h5p_manifest_book, indent=2, ensure_ascii=False))
        zf.writestr('content/content.json', json.dumps(book_content, indent=2, ensure_ascii=False))

        libs_to_bundle = [
            'H5P.InteractiveBook', 'H5P.Column', 'H5P.AdvancedText', 'H5P.Image',
            'H5P.Accordion', 'H5P.MultiChoice', 'H5P.TrueFalse', 'H5P.Question',
            'H5P.QuestionSet', 'H5P.Video', 'H5P.JoubelUI', 'FontAwesome',
            'H5P.FontIcons', 'H5P.Transition', 'H5P.Components', 'jQuery.ui'
        ]
        for lib_key in libs_to_bundle:
            folder_name, canon_name = LIBS_MAP[lib_key]
            lib_path = os.path.join(LIBS_BASE, folder_name)
            copy_library_to_zip(zf, lib_path, canon_name)

        for img_p in images_to_bundle:
            arc_name = f"content/images/{os.path.basename(img_p)}"
            zf.write(img_p, arc_name)

    validate_moodle_whitelist(output_curso_path)
    size_mb = os.path.getsize(output_curso_path) / (1024 * 1024)
    print(f"✓ Curso H5P generado con éxito: {output_curso_path} ({size_mb:.2f} MB)")

    # 5. PAQUETE DE EVALUACIÓN INDEPENDIENTE
    print(f"\n📦 Compilando Paquete de Evaluación Independiente: {os.path.basename(output_eval_path)}...")
    h5p_manifest_quiz = {
        "title": titulo_examen,
        "language": "es",
        "mainLibrary": "H5P.QuestionSet",
        "embedTypes": ["div"],
        "preloadedDependencies": [
            {"machineName": "H5P.QuestionSet", "majorVersion": 1, "minorVersion": 20},
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
            {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
            {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
            {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
            {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
            {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10}
        ]
    }

    with zipfile.ZipFile(output_eval_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('h5p.json', json.dumps(h5p_manifest_quiz, indent=2, ensure_ascii=False))
        zf.writestr('content/content.json', json.dumps(quiz_params, indent=2, ensure_ascii=False))

        libs_to_include = ['FontAwesome', 'H5P.JoubelUI', 'H5P.Question', 'H5P.MultiChoice',
                           'H5P.QuestionSet', 'H5P.FontIcons', 'H5P.Transition', 'H5P.Video',
                           'H5P.Components', 'jQuery.ui']
        for lib_name in libs_to_include:
            folder, canon = LIBS_MAP[lib_name]
            lib_source_dir = os.path.join(LIBS_BASE, folder)
            copy_library_to_zip(zf, lib_source_dir, canon)

    validate_moodle_whitelist(output_eval_path)
    size_mb = os.path.getsize(output_eval_path) / (1024 * 1024)
    print(f"✓ Paquete creado con éxito: {output_eval_path} ({size_mb:.2f} MB)")

    print("\n" + "=" * 75)
    print("PROCESO DE GENERACIÓN DESDE PLANTILLA FINALIZADO CON ÉXITO")
    print(f"✓ Curso Completo: {os.path.basename(output_curso_path)}")
    print(f"✓ Cuestionario Oficial: {os.path.basename(output_eval_path)}")
    print("✓ 100% Compatible con EducaMadrid y Moodle.")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    cfg_file = sys.argv[1] if len(sys.argv) > 1 else None
    compilar_curso_desde_plantilla(cfg_file)
