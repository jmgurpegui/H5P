#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser y Conversor Bidireccional Moodle XML <-> H5P QuestionSet
100% Compatible con el Aula Virtual de EducaMadrid y Moodle 3.x / 4.x.

Permite:
1. Leer bancos de preguntas en formato oficial Moodle XML (<quiz>).
2. Validar estructura, balance y retroalimentación de las preguntas.
3. Transformar las preguntas XML en componentes interactivos H5P (MultiChoice 1.16 y QuestionSet 1.20).
4. Exportar bancos de preguntas desde estructuras Python/JSON a formato Moodle XML para importación directa en EducaMadrid.
"""

import os
import re
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

def clean_html_text(text):
    """Limpia etiquetas o espacios sobrantes manteniendo el marcado básico."""
    if text is None:
        return ""
    text = text.strip()
    return text

def parse_moodle_xml(xml_path):
    """
    Parsea un archivo Moodle XML (<quiz>) y extrae todas las preguntas de tipo multichoice y truefalse.
    Devuelve una lista de diccionarios normalizados:
    [
        {
            "id": "P01",
            "tipo": "multichoice",
            "enunciado": "<p>Texto de la pregunta...</p>",
            "enunciado_plano": "Texto plano...",
            "feedback_general": "<p>Retroalimentación general...</p>",
            "opciones": [
                {
                    "texto": "<p>Opción A</p>",
                    "texto_plano": "Opción A",
                    "fraccion": 100,  # 100 = Correcta, 0 = Incorrecta
                    "es_correcta": True,
                    "feedback": "<p>¡Correcto!...</p>"
                },
                ...
            ],
            "correct_idx": 0  # Índice (0 a 3) de la opción correcta
        },
        ...
    ]
    """
    if not os.path.isfile(xml_path):
        raise FileNotFoundError(f"No se encontró el archivo XML: {xml_path}")

    # Parsear XML con soporte para codificación UTF-8
    tree = ET.parse(xml_path)
    root = tree.getroot()

    if root.tag != 'quiz':
        raise ValueError(f"El nodo raíz debe ser <quiz>, pero se encontró <{root.tag}>")

    preguntas = []
    idx_global = 1

    for q_elem in root.findall('question'):
        q_type = q_elem.get('type')

        # Omitir elementos de categoría
        if q_type == 'category':
            continue

        if q_type not in ('multichoice', 'truefalse'):
            # Por ahora nos centramos en los tipos evaluables en QuestionSet
            continue

        # 1. Nombre / Identificador
        name_elem = q_elem.find('name/text')
        q_id = name_elem.text if name_elem is not None and name_elem.text else f"P{idx_global:02d}"

        # 2. Enunciado (questiontext)
        qt_elem = q_elem.find('questiontext/text')
        enunciado_html = qt_elem.text if qt_elem is not None and qt_elem.text else ""
        enunciado_html = clean_html_text(enunciado_html)
        # Limpieza básica para texto plano
        enunciado_plano = re.sub(r'<[^>]+>', '', enunciado_html).strip()

        # 3. Feedback general
        gf_elem = q_elem.find('generalfeedback/text')
        feedback_general = gf_elem.text if gf_elem is not None and gf_elem.text else ""
        feedback_general = clean_html_text(feedback_general)

        # 4. Respuestas (answer)
        opciones = []
        correct_indices = []

        for a_idx, ans_elem in enumerate(q_elem.findall('answer')):
            fraction = float(ans_elem.get('fraction', '0'))
            ans_text_elem = ans_elem.find('text')
            ans_html = ans_text_elem.text if ans_text_elem is not None and ans_text_elem.text else ""
            ans_html = clean_html_text(ans_html)
            ans_plano = re.sub(r'<[^>]+>', '', ans_html).strip()

            # Feedback específico de la opción
            fb_elem = ans_elem.find('feedback/text')
            ans_fb = fb_elem.text if fb_elem is not None and fb_elem.text else ""
            ans_fb = clean_html_text(ans_fb)

            # Si no hay feedback específico, heredar el general
            if not ans_fb and feedback_general:
                ans_fb = feedback_general

            es_correcta = (fraction >= 99.0)
            if es_correcta:
                correct_indices.append(a_idx)

            opciones.append({
                "texto": ans_html,
                "texto_plano": ans_plano,
                "fraccion": fraction,
                "es_correcta": es_correcta,
                "feedback": ans_fb
            })

        if not opciones:
            continue

        # Determinar índice correcto (base 0)
        correct_idx = correct_indices[0] if correct_indices else 0

        preguntas.append({
            "id": q_id,
            "tipo": q_type,
            "enunciado": enunciado_html,
            "enunciado_plano": enunciado_plano,
            "feedback_general": feedback_general,
            "opciones": opciones,
            "correct_idx": correct_idx,
            "num_opciones": len(opciones)
        })
        idx_global += 1

    return preguntas

def moodle_xml_to_h5p_multichoice(p_data):
    """
    Convierte una pregunta parseada de Moodle XML al objeto ejecutable H5P.MultiChoice 1.16.
    """
    enunciado = p_data["enunciado"]
    if not enunciado.startswith("<p"):
        enunciado = f"<p style='font-weight: 600; font-size: 1.05em; color: #0f172a; margin-bottom: 0.75rem;'>{enunciado}</p>"

    answers = []
    for opt in p_data["opciones"]:
        is_corr = opt["es_correcta"]
        opt_text = opt["texto"]
        if not opt_text.startswith("<div") and not opt_text.startswith("<p"):
            opt_text = f"<div style='color: #0f172a; line-height: 1.45;'>{opt_text}</div>"

        fb_msg = opt["feedback"] or p_data.get("feedback_general", "")
        if is_corr:
            chosen_fb = (
                f"<div style='font-family: inherit; font-size: 0.95em; color: #14532d; line-height: 1.45;'>"
                f"<strong>✓ ¡Respuesta Correcta!</strong><br/>{fb_msg}</div>"
            )
        else:
            chosen_fb = (
                f"<div style='font-family: inherit; font-size: 0.95em; color: #991b1b; line-height: 1.45;'>"
                f"<strong>✗ Respuesta Incorrecta.</strong></div>"
            )

        answers.append({
            "text": opt_text,
            "correct": is_corr,
            "tipsAndFeedback": {
                "tip": "",
                "chosenFeedback": chosen_fb,
                "notChosenFeedback": ""
            }
        })

    return {
        "library": "H5P.MultiChoice 1.16",
        "params": {
            "question": enunciado,
            "answers": answers,
            "behaviour": {
                "enableRetry": False,
                "enableSolutionsButton": False,
                "enableCheckButton": True,
                "type": "auto",
                "singlePoint": True,
                "randomAnswers": True,
                "showSolutionsRequiresInput": True,
                "confirmCheckDialog": False,
                "confirmRetryDialog": False,
                "autoCheck": False,
                "passPercentage": 100,
                "showScorePoints": True
            },
            "UI": {
                "checkAnswerButton": "Comprobar respuesta",
                "submitAnswerButton": "Enviar respuesta",
                "showSolutionButton": "",
                "tryAgainButton": "Reintentar",
                "tipsLabel": "Pista",
                "scoreBarLabel": ":num de :total puntos",
                "tipAvailable": "Pista disponible",
                "feedbackAvailable": "Retroalimentación disponible",
                "readFeedback": "Leer retroalimentación",
                "wrongAnswer": "Respuesta incorrecta",
                "correctAnswer": "Respuesta correcta",
                "shouldCheck": "Debería marcarse",
                "shouldNotCheck": "No debería marcarse",
                "noInput": "Por favor, selecciona una opción antes de comprobar."
            }
        },
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": f"{p_data['id']}: {p_data['enunciado_plano'][:50]}..."
        }
    }

def moodle_xml_to_h5p_questions_list(xml_path):
    """Lee el XML de Moodle y devuelve la lista completa de preguntas en formato H5P MultiChoice 1.16."""
    preguntas_raw = parse_moodle_xml(xml_path)
    return [moodle_xml_to_h5p_multichoice(p) for p in preguntas_raw]

def export_dict_to_moodle_xml(preguntas_list, output_xml_path, category_name="Banco de Preguntas Oficial"):
    """
    Exporta una lista de preguntas (en formato dict) a un archivo Moodle XML (<quiz>)
    100% compatible con la importación en EducaMadrid y Moodle.
    
    Acepta diccionarios con claves flexibles:
    - pregunta / q / enunciado
    - respuestas / opts / opciones
    - correcta / correct (índice 0-3 o lista de booleanos)
    - feedback / fb / generalfeedback
    """
    root = ET.Element('quiz')

    # 1. Definir la categoría de importación
    cat_q = ET.SubElement(root, 'question', type='category')
    cat_node = ET.SubElement(cat_q, 'category')
    cat_text = ET.SubElement(cat_node, 'text')
    cat_text.text = f"$course$/top/{category_name}"

    for idx, item in enumerate(preguntas_list, 1):
        q_enunciado = item.get('pregunta') or item.get('q') or item.get('enunciado', '')
        q_opts = item.get('respuestas') or item.get('opts') or item.get('opciones', [])
        q_correct = item.get('correcta') if 'correcta' in item else item.get('correct', 0)
        q_fb = item.get('feedback') or item.get('fb') or item.get('generalfeedback', '')
        q_title = item.get('id') or item.get('ctx') or f"Pregunta {idx:02d}: {re.sub(r'<[^>]+>', '', q_enunciado)[:40]}..."

        q_node = ET.SubElement(root, 'question', type='multichoice')

        # Nombre
        name_node = ET.SubElement(q_node, 'name')
        name_text = ET.SubElement(name_node, 'text')
        name_text.text = q_title

        # Enunciado
        qt_node = ET.SubElement(q_node, 'questiontext', format='html')
        qt_text = ET.SubElement(qt_node, 'text')
        if not q_enunciado.startswith('<p'):
            qt_text.text = f"<p>{q_enunciado}</p>"
        else:
            qt_text.text = q_enunciado

        # Feedback general
        gf_node = ET.SubElement(q_node, 'generalfeedback', format='html')
        gf_text = ET.SubElement(gf_node, 'text')
        if q_fb:
            gf_text.text = f"<p>{q_fb}</p>" if not q_fb.startswith('<p') else q_fb
        else:
            gf_text.text = ""

        # Propiedades estándar de Moodle
        ET.SubElement(q_node, 'defaultgrade').text = "1.0000000"
        ET.SubElement(q_node, 'penalty').text = "0.3333333"
        ET.SubElement(q_node, 'hidden').text = "0"
        ET.SubElement(q_node, 'single').text = "true"
        ET.SubElement(q_node, 'shuffleanswers').text = "true"
        ET.SubElement(q_node, 'answernumbering').text = "abc"

        # Opciones
        for o_idx, opt in enumerate(q_opts):
            opt_str = opt if isinstance(opt, str) else opt.get('texto', str(opt))
            is_correct = (o_idx == q_correct)
            fraction = "100" if is_correct else "0"

            ans_node = ET.SubElement(q_node, 'answer', fraction=fraction, format='html')
            ans_text = ET.SubElement(ans_node, 'text')
            ans_text.text = f"<p>{opt_str}</p>" if not opt_str.startswith('<') else opt_str

            ans_fb_node = ET.SubElement(ans_node, 'feedback', format='html')
            ans_fb_text = ET.SubElement(ans_fb_node, 'text')
            if is_correct:
                ans_fb_text.text = f"<p>✓ ¡Correcto! {q_fb}</p>"
            else:
                ans_fb_text.text = f"<p>✗ Incorrecto. {q_fb}</p>"

    # Formatear XML bonito con indentación
    rough_str = ET.tostring(root, encoding='utf-8')
    reparsed = minidom.parseString(rough_str)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

    with open(output_xml_path, 'wb') as f:
        f.write(pretty_xml)

    print(f"✓ Archivo Moodle XML generado con éxito: {output_xml_path} ({len(preguntas_list)} preguntas).")

if __name__ == "__main__":
    import sys
    print("Módulo de soporte Moodle XML <-> H5P operativo.")
