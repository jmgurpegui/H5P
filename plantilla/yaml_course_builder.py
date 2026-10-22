#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador Automático de Cursos H5P y Cuestionarios Moodle XML desde YAML.
FP Automoción - EducaMadrid (Profesor JM Gurpegui)

Permite desacoplar totalmente el contenido pedagógico (redactado limpiamente en YAML)
de la lógica de empaquetado, dependencias H5P, optimización metrológica y generación XML.
"""

import os
import re
import sys
import uuid
import yaml
import shutil
from pathlib import Path

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from generar_curso_plantilla import (
    AUTOR,
    LICENCIA,
    LICENCIA_VERSION,
    preparar_imagenes,
    create_text_section,
    create_image_section,
    create_image_hotspots,
    create_accordion,
    create_active_challenge,
    create_checklist_section,
    create_checkpoint_section,
    create_simulation_box,
    create_video_section,
    create_diagnostic_table,
    create_component_spec_card,
    create_moodle_quiz_referral,
    create_didactic_sequence_chapter,
    create_chapter,
    build_h5p_package,
)
from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
from validar_h5p_educamadrid import validate_h5p


def _build_hero_html(item):
    titulo = item.get("titulo", "Unidad Didáctica")
    subtitulo = item.get("subtitulo", "")
    badges = item.get("badges", ["FP Automoción", "EducaMadrid H5P", "WCAG 2.1 AAA"])
    badge_colors = ["badge-blue", "badge-green", "badge-yellow", "badge-red", "badge-purple"]
    badges_html = " ".join(
        f'<span class="tech-badge {badge_colors[i % len(badge_colors)]}">{b}</span>'
        for i, b in enumerate(badges)
    )
    return f"""
    <div class="tech-hero">
      <h2>{titulo}</h2>
      <p>{subtitulo}</p>
      <div class="tech-badge-container">
        {badges_html}
      </div>
    </div>
    """


def _construir_seccion(item):
    """Convierte un bloque del diccionario YAML en una sección H5P oficial."""
    tipo = (item.get("tipo") or "").lower()

    if tipo in ("hero", "cabecera"):
        html = _build_hero_html(item)
        titulo = item.get("titulo_seccion") or item.get("titulo") or "Cabecera de Unidad"
        return create_text_section(html, titulo)

    elif tipo in ("texto", "html"):
        html = item.get("html") or item.get("texto") or "<p></p>"
        titulo = item.get("titulo", "Contenido Técnico")
        return create_text_section(html, titulo)

    elif tipo in ("ficha_tecnica", "spec_card", "componente"):
        specs = item.get("especificaciones") or []
        if isinstance(specs, dict):
            specs = list(specs.items())
        elif isinstance(specs, list) and specs and isinstance(specs[0], dict):
            specs = [(s.get("parametro", ""), s.get("valor", "")) for s in specs]

        pinout = item.get("bornes") or item.get("pinout") or []
        if isinstance(pinout, dict):
            pinout = list(pinout.items())
        elif isinstance(pinout, list) and pinout and isinstance(pinout[0], dict):
            pinout = [(p.get("borne", ""), p.get("descripcion", "")) for p in pinout]

        return create_component_spec_card(
            component_name=item.get("nombre_componente", "Componente"),
            category_badge=item.get("categoria", "FICHA TÉCNICA DE TALLER"),
            specs_dict=specs,
            pinout_list=pinout,
            oscilloscope_note=item.get("nota_osciloscopio", "")
        )

    elif tipo in ("tabla_diagnosis", "diagnosis", "cuadro_averias"):
        filas = []
        raw_filas = item.get("filas") or []
        for r in raw_filas:
            if isinstance(r, (list, tuple)):
                filas.append(r)
            elif isinstance(r, dict):
                filas.append((
                    r.get("sintoma", ""),
                    r.get("metodo_medicion", r.get("metodo", "")),
                    r.get("valores_referencia", r.get("valores", "")),
                    r.get("accion_correctiva", r.get("accion", ""))
                ))
        return create_diagnostic_table(
            title=item.get("titulo", "Cuadro de Diagnosis Metrológica en Taller"),
            rows=filas
        )

    elif tipo in ("checklist", "verificacion"):
        return create_checklist_section(
            title=item.get("titulo", "Lista de Verificación de Taller"),
            items=item.get("items", [])
        )

    elif tipo in ("checkpoint", "comprobacion"):
        intro = item.get("texto") or item.get("pregunta") or item.get("intro_text") or ""
        badge = item.get("badge", "Pausa Activa de Comprensión")
        return create_checkpoint_section(
            item.get("titulo", "Punto de Comprobación Técnica"),
            intro,
            badge
        )

    elif tipo in ("reto", "desafio", "challenge"):
        scenario = item.get("problema") or item.get("escenario") or item.get("descripcion") or ""
        if item.get("consejo"):
            scenario += f"<p style='margin-top:0.5rem;'><strong>Consejo de taller:</strong> {item['consejo']}</p>"
        steps = item.get("pasos", item.get("steps", []))
        badge = item.get("badge", "Reto Práctico de Taller")
        return create_active_challenge(
            item.get("titulo", "Reto de Taller"),
            scenario,
            steps,
            badge
        )

    elif tipo in ("acordeon", "desplegable"):
        paneles = []
        raw_paneles = item.get("paneles", [])
        for p in raw_paneles:
            if isinstance(p, dict):
                paneles.append((p.get("titulo", ""), p.get("html", p.get("contenido", ""))))
            elif isinstance(p, (list, tuple)) and len(p) >= 2:
                paneles.append((p[0], p[1]))
        return create_accordion(
            panels_data=paneles,
            title=item.get("titulo", "Protocolo Técnico Desplegable")
        )

    elif tipo in ("video", "videotutorial"):
        return create_video_section(
            video_url=item.get("url", item.get("video_url", "")),
            title=item.get("titulo", "Vídeo Técnico Demostrativo de Taller")
        )

    elif tipo in ("simulador_caja", "simulacion"):
        return create_simulation_box(
            item.get("titulo", "Entorno de Simulación Metrológica"),
            item.get("descripcion", ""),
            item.get("boton", "Abrir Simulador Interactivo"),
            item.get("url", item.get("enlace", "#"))
        )

    elif tipo in ("imagen", "figura"):
        return create_image_section(
            rel_path=item.get("archivo", item.get("path", "")),
            alt_text=item.get("alt", "Imagen técnica de automoción"),
            title=item.get("titulo", "Figura Técnica"),
            width=item.get("ancho"),
            height=item.get("alto")
        )

    elif tipo in ("derivacion_moodle", "quiz_referral", "evaluacion_referral"):
        return create_moodle_quiz_referral(
            item.get("numero_tema", 1),
            item.get("titulo_tema", "Unidad"),
            item.get("descripcion", item.get("instrucciones", ""))
        )

    else:
        # Fallback genérico a bloque de texto
        contenido = item.get("html") or item.get("texto") or str(item)
        titulo = item.get("titulo", "Sección Técnica")
        return create_text_section(contenido, titulo)


def _construir_capitulo(raw_cap):
    """Construye un capítulo H5P respetando la secuencia didáctica de 4 fases o lista plana."""
    titulo = raw_cap.get("titulo", "Capítulo")

    # Si declara fases didácticas explícitas (secuencia oficial de 4 fases)
    fases_keys = ("fase1_intro", "fase2_explicacion", "fase3_practica", "fase4_evaluacion")
    if any(k in raw_cap for k in fases_keys):
        f1 = [_construir_seccion(item) for item in raw_cap.get("fase1_intro", [])]
        f2 = [_construir_seccion(item) for item in raw_cap.get("fase2_explicacion", [])]
        f3 = [_construir_seccion(item) for item in raw_cap.get("fase3_practica", [])]
        f4 = [_construir_seccion(item) for item in raw_cap.get("fase4_evaluacion", [])]
        return create_didactic_sequence_chapter(titulo, f1, f2, f3, f4)

    # Si declara secciones directas
    secciones = [_construir_seccion(item) for item in raw_cap.get("secciones", [])]
    return create_chapter(titulo, secciones)


def _construir_evaluacion_moodle(eval_config, xml_output_path):
    """Construye y valida el banco de preguntas Moodle XML desde el bloque YAML."""
    categoria = eval_config.get("categoria", "FP Automoción - Evaluacion Oficial")
    builder = MoodleXMLBuilder(categoria)

    for p in eval_config.get("preguntas", []):
        tipo = (p.get("tipo") or "multichoice").lower()
        nombre = p.get("nombre", f"P_{uuid.uuid4().hex[:6]}")
        enunciado = p.get("enunciado", "")
        fb_general = p.get("feedback_general", "")

        if tipo in ("multichoice", "opcion_multiple", "test"):
            raw_opts = p.get("opciones", [])
            opts = []
            for o in raw_opts:
                if isinstance(o, dict):
                    # Manejo de boolean 'correcta' o valor numérico 'fraccion'
                    if "correcta" in o:
                        frac = 100 if o["correcta"] else 0
                    else:
                        frac = o.get("fraccion", 0)
                    opts.append({
                        "text": str(o.get("texto", "")),
                        "fraction": frac,
                        "feedback": o.get("feedback", "")
                    })
                elif isinstance(o, (list, tuple)) and len(o) >= 2:
                    opts.append({
                        "text": str(o[0]),
                        "fraction": 100 if o[1] is True else (0 if o[1] is False else int(o[1])),
                        "feedback": o[2] if len(o) > 2 else ""
                    })

            single = p.get("single", True)
            shuffle = p.get("shuffle", True)
            builder.add_multichoice(nombre, enunciado, opts, fb_general, single=single, shuffle=shuffle)

        elif tipo in ("numerical", "calculo", "numerica"):
            valor = float(p.get("valor", p.get("respuesta", 0.0)))
            tol = float(p.get("tolerancia", 0.05))
            fb = p.get("feedback", "")
            unidades = p.get("unidades", None)
            builder.add_numerical(nombre, enunciado, valor, tol, fb, fb_general, units=unidades)

        elif tipo in ("shortanswer", "respuesta_corta"):
            raw_resps = p.get("respuestas", [])
            resps = []
            for r in raw_resps:
                if isinstance(r, dict):
                    resps.append({
                        "text": str(r.get("texto", "")),
                        "fraction": r.get("fraccion", 100),
                        "feedback": r.get("feedback", "")
                    })
                elif isinstance(r, (list, tuple)):
                    resps.append({
                        "text": str(r[0]),
                        "fraction": r[1] if len(r) > 1 else 100,
                        "feedback": r[2] if len(r) > 2 else ""
                    })
                elif isinstance(r, str):
                    resps.append({"text": r, "fraction": 100, "feedback": ""})

            builder.add_shortanswer(nombre, enunciado, resps, fb_general, usecase=1 if p.get("case_sensitive") else 0)

        elif tipo in ("truefalse", "verdadero_falso"):
            correcta = bool(p.get("correcta", True))
            builder.add_truefalse(
                nombre,
                enunciado,
                is_correct=correcta,
                feedback_true=p.get("feedback_true", ""),
                feedback_false=p.get("feedback_false", ""),
                general_feedback=fb_general
            )

        elif tipo in ("matching", "emparejamiento"):
            raw_subqs = p.get("parejas", p.get("subquestions", []))
            pairs = []
            for item in raw_subqs:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    pairs.append((item[0], item[1]))
                elif isinstance(item, dict):
                    pairs.append((item.get("concepto", item.get("pregunta", "")), item.get("definicion", item.get("respuesta", ""))))
            builder.add_matching(nombre, enunciado, pairs, fb_general, shuffle=p.get("shuffle", True))

        elif tipo in ("ddimageortext", "arrastrar_imagen", "drag_drop_image", "drag_image"):
            raw_img = p.get("imagen", p.get("image_path", ""))
            img_path = raw_img
            if img_path and not os.path.isabs(img_path) and not os.path.exists(img_path):
                cand = os.path.join(os.path.dirname(xml_output_path), img_path)
                if os.path.exists(cand):
                    img_path = cand
            raw_items = p.get("items", p.get("elementos", []))
            items = []
            for it in raw_items:
                if isinstance(it, dict):
                    items.append({
                        "text": str(it.get("texto", it.get("text", ""))),
                        "x": it.get("x", it.get("xleft")),
                        "y": it.get("y", it.get("ytop")),
                        "group": it.get("grupo", it.get("group", 1)),
                        "infinite": bool(it.get("infinite", False)),
                        "choice": it.get("choice")
                    })
            builder.add_ddimageortext(
                nombre,
                enunciado,
                image_path=img_path,
                items=items,
                general_feedback=fb_general,
                shuffle=p.get("shuffle", True),
                penalty=float(p.get("penalty", 0.3333333)),
                defaultgrade=str(p.get("defaultgrade", "1.0000000"))
            )

    builder.save_xml(xml_output_path)
    validar_moodle_xml(xml_output_path)
    print(f"✅ Archivo Moodle XML generado: {xml_output_path}")


def compilar_curso_desde_yaml(yaml_path, output_dir=None, images_dir=None):
    """
    Lee un archivo YAML estructurado y compila:
    1. Paquete H5P InteractiveBook (.h5p) formativo.
    2. Banco de evaluación Moodle XML (.xml) sumativo.
    3. Validación y certificación automática según estándares EducaMadrid.
    """
    yaml_file = Path(yaml_path).resolve()
    if not yaml_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo YAML: {yaml_path}")

    base_dir = yaml_file.parent
    target_dir = Path(output_dir).resolve() if output_dir else base_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"El archivo YAML {yaml_path} no tiene un formato de diccionario válido en la raíz.")

    # Metadatos del curso
    meta = data.get("meta", {})
    titulo = meta.get("titulo", "Curso FP Automoción")
    subtitulo = meta.get("subtitulo", titulo)
    desc = meta.get("descripcion", "Curso interactivo formativo y banco Moodle XML para Formación Profesional.")
    autor = meta.get("autor", AUTOR)
    licencia = meta.get("licencia", LICENCIA)

    slug = re.sub(r'[^a-z0-9]+', '_', titulo.lower()).strip('_')
    if not slug:
        slug = "curso_automocion"

    h5p_pkg_path = str(target_dir / f"{slug}.h5p")
    xml_path = str(target_dir / f"evaluacion_{slug}.xml")

    # Optimización previa de imágenes si existe carpeta de imágenes
    img_dir_candidates = [
        images_dir,
        base_dir / "images",
        base_dir / "img",
        target_dir / "images"
    ]
    img_source = None
    for cand in img_dir_candidates:
        if cand and os.path.isdir(str(cand)):
            img_source = str(cand)
            break

    if img_source:
        preparar_imagenes(img_source)

    # Construcción de capítulos H5P
    capitulos = []
    for raw_cap in data.get("capitulos", []):
        capitulos.append(_construir_capitulo(raw_cap))

    if capitulos:
        build_h5p_package(
            output_path=h5p_pkg_path,
            title=titulo,
            book_cover_title=subtitulo,
            book_cover_desc=desc,
            chapters=capitulos,
            images_source_dir=img_source
        )
        validate_h5p(h5p_pkg_path)
    else:
        print("⚠️ Aviso: No se definieron capítulos en el archivo YAML. Omitiendo generación de paquete H5P.")

    # Construcción de banco Moodle XML si está definido
    eval_moodle = data.get("evaluacion_moodle")
    if eval_moodle and eval_moodle.get("preguntas"):
        _construir_evaluacion_moodle(eval_moodle, xml_path)
    else:
        print("ℹ️ No se especificaron preguntas en 'evaluacion_moodle'. Omitiendo generación de XML.")

    return {
        "h5p": h5p_pkg_path if capitulos else None,
        "xml": xml_path if eval_moodle else None
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 yaml_course_builder.py <ruta_archivo.yaml> [directorio_salida]")
        sys.exit(1)

    in_yaml = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) >= 3 else None
    res = compilar_curso_desde_yaml(in_yaml, out_dir)
    print("\n✓ Proceso completado con éxito:")
    if res["h5p"]:
        print(f"  - H5P: {res['h5p']}")
    if res["xml"]:
        print(f"  - XML: {res['xml']}")
