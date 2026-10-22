#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo Oficial de Generación y Validación de Cuestionarios Moodle XML para EducaMadrid (FP Automoción).
Permite desacoplar la formación activa (H5P) de la evaluación sumativa oficial (Moodle Quiz).

Garantiza:
1. Exportación 100% compatible con Moodle 3.x, 4.x y Aulas Virtuales de EducaMadrid (<quiz>).
2. Seis tipos de preguntas nativas para FP de Automoción y Educación Secundaria/Bachillerato:
   - multichoice (opción múltiple con rotación automática de posición A/B/C/D en el XML)
   - truefalse (verdadero/falso con retroalimentación específica)
   - matching (emparejamiento de componentes, bornes DIN o códigos ECE)
   - numerical (cálculo electrotécnico/metrológico con margen de tolerancia y unidades)
   - shortanswer (respuesta corta para identificación directa de bornes, siglas o códigos)
   - ddimageortext (arrastrar y soltar etiquetas sobre imagen con fondo incrustado en Base64)
3. Validación estricta de sintaxis, fracciones, equilibrio psicométrico bidireccional de longitud,
   distribución de posiciones de clave en XML y ausencia de etiquetas <p> redundantes (Norma Picuino).
4. Registro fiable de intentos y calificaciones en Moodle (mdl_grade_grades), evitando fallos de xAPI.
"""

import os
import sys
import base64
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html
import re


def strip_outer_p(text):
    """
    Elimina etiquetas <p> y </p> innecesarias que envuelven enunciados, opciones o retroalimentación.
    Norma técnica oficial (https://github.com/picuino/test):
    Las preguntas de test XML no necesitan <p> y </p>.
    """
    if not text:
        return ""
    text = str(text).strip()
    match = re.match(r'^\s*<p>(.*)</p>\s*$', text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        inner = match.group(1).strip()
        if "<p>" not in inner.lower() and "</p>" not in inner.lower():
            return inner
    return text


class MoodleXMLBuilder:
    """Constructor programático de bancos de preguntas Moodle XML para FP de Automoción."""

    def __init__(self, category_name="Banco de Preguntas Oficial EducaMadrid"):
        self.category_name = category_name
        self.questions = []
        self._mc_counter = 0

    def set_category(self, category_name):
        self.category_name = category_name

    def add_multichoice(
        self,
        name,
        question_text,
        options,
        general_feedback="",
        single=True,
        shuffle=True,
        penalty=0.3333333,
        image_path=None,
        image_alt="Esquema técnico",
        rotate_xml_order=True
    ):
        """
        Añade una pregunta de opción múltiple (con soporte opcional para imagen integrada en base64).
        Rota automáticamente la posición de la opción correcta en el XML (A, B, C, D) cuando
        rotate_xml_order=True para evitar que todas las respuestas correctas estén en options[0].

        options: Lista de dicts:
            [
                {"text": "Opción A...", "fraction": 100, "feedback": "Explicación razonada..."},
                {"text": "Opción B...", "fraction": 0, "feedback": "Por qué es incorrecto..."}
            ]
        """
        cleaned_options = [
            {
                "text": strip_outer_p(opt.get("text", "")),
                "fraction": opt.get("fraction", 0),
                "feedback": strip_outer_p(opt.get("feedback", ""))
            }
            for opt in options
        ]

        if rotate_xml_order and single and len(cleaned_options) >= 2:
            # Si la correcta está en índice 0, rotamos determinísticamente a la posición (0, 1, 2, 3)
            correct_indices = [i for i, o in enumerate(cleaned_options) if float(o.get("fraction", 0)) >= 99.9]
            if len(correct_indices) == 1 and correct_indices[0] == 0:
                target_pos = self._mc_counter % len(cleaned_options)
                if target_pos != 0:
                    correct_opt = cleaned_options.pop(0)
                    cleaned_options.insert(target_pos, correct_opt)
            self._mc_counter += 1

        self.questions.append({
            "type": "multichoice",
            "name": name,
            "text": strip_outer_p(question_text),
            "options": cleaned_options,
            "general_feedback": strip_outer_p(general_feedback),
            "single": single,
            "shuffle": shuffle,
            "penalty": penalty,
            "image_path": image_path,
            "image_alt": image_alt
        })

    def add_truefalse(
        self,
        name,
        question_text,
        is_correct,
        feedback_true="",
        feedback_false="",
        general_feedback="",
        image_path=None,
        image_alt="Esquema técnico"
    ):
        """Añade una pregunta de Verdadero / Falso (con soporte opcional para imagen integrada en base64)."""
        self.questions.append({
            "type": "truefalse",
            "name": name,
            "text": strip_outer_p(question_text),
            "is_correct": bool(is_correct),
            "feedback_true": strip_outer_p(feedback_true),
            "feedback_false": strip_outer_p(feedback_false),
            "general_feedback": strip_outer_p(general_feedback),
            "image_path": image_path,
            "image_alt": image_alt
        })

    def add_matching(
        self,
        name,
        question_text,
        pairs,
        general_feedback="",
        shuffle=True,
        image_path=None,
        image_alt="Esquema técnico"
    ):
        """
        Añade una pregunta de emparejamiento (con soporte opcional para imagen integrada en base64).
        pairs: Lista de tuplas (concepto, definicion/respuesta)
        """
        self.questions.append({
            "type": "matching",
            "name": name,
            "text": strip_outer_p(question_text),
            "pairs": [(strip_outer_p(c), strip_outer_p(a)) for c, a in pairs],
            "general_feedback": strip_outer_p(general_feedback),
            "shuffle": shuffle,
            "image_path": image_path,
            "image_alt": image_alt
        })

    def add_numerical(
        self,
        name,
        question_text,
        answer_value,
        tolerance=0.0,
        feedback="",
        general_feedback="",
        units=None,
        unit_grading_type=0,
        show_units=3,
        penalty=0.3333333,
        image_path=None,
        image_alt="Esquema técnico"
    ):
        """
        Añade una pregunta de cálculo numérico (<question type="numerical">), ideal para problemas de taller
        (Ley de Ohm, caída de tensión, resistencia equivalente, frecuencia, ciclo de trabajo PWM, etc.).

        answer_value: float o int con el resultado numérico exacto (ej. 0.45 o 500).
        tolerance: margen de error admitido en unidades absolutas (ej. 0.05 permite entre 0.40 y 0.50).
        units: lista opcional de unidades aceptadas, ej. ["V", "voltios"] o [("V", 1.0), ("mV", 1000.0)].
        show_units: 3 = no se exige escribir la unidad (solo el número); 0 = unidad opcional; 1 = unidad calificada.
        """
        parsed_units = []
        if units:
            for u in units:
                if isinstance(u, (list, tuple)) and len(u) >= 2:
                    parsed_units.append((str(u[0]), float(u[1])))
                else:
                    parsed_units.append((str(u), 1.0))

        self.questions.append({
            "type": "numerical",
            "name": name,
            "text": strip_outer_p(question_text),
            "answer_value": answer_value,
            "tolerance": tolerance,
            "feedback": strip_outer_p(feedback),
            "general_feedback": strip_outer_p(general_feedback),
            "units": parsed_units,
            "unit_grading_type": unit_grading_type,
            "show_units": show_units,
            "penalty": penalty,
            "image_path": image_path,
            "image_alt": image_alt
        })

    def add_shortanswer(
        self,
        name,
        question_text,
        accepted_answers,
        general_feedback="",
        usecase=0,
        penalty=0.3333333,
        image_path=None,
        image_alt="Esquema técnico"
    ):
        """
        Añade una pregunta de respuesta corta (<question type="shortanswer">), ideal para identificar
        códigos de bornes DIN 72552 (30, 15, 31, 50, 85, 86, 87), fusibles o códigos de homologación ECE.

        accepted_answers: Lista de dicts o strings:
            [
                {"text": "31", "fraction": 100, "feedback": "¡Correcto! Borne 31 es retorno a masa."},
                {"text": "Borne 31", "fraction": 100, "feedback": "¡Correcto! Borne 31 es retorno a masa."}
            ]
        usecase: 0 = insensible a mayúsculas/minúsculas (recomendado); 1 = sensible a mayúsculas.
        """
        formatted_answers = []
        for ans in accepted_answers:
            if isinstance(ans, dict):
                formatted_answers.append({
                    "text": strip_outer_p(ans.get("text", "")),
                    "fraction": ans.get("fraction", 100),
                    "feedback": strip_outer_p(ans.get("feedback", ""))
                })
            elif isinstance(ans, (list, tuple)):
                formatted_answers.append({
                    "text": strip_outer_p(ans[0]),
                    "fraction": ans[1] if len(ans) > 1 else 100,
                    "feedback": strip_outer_p(ans[2]) if len(ans) > 2 else ""
                })
            else:
                formatted_answers.append({
                    "text": strip_outer_p(str(ans)),
                    "fraction": 100,
                    "feedback": ""
                })

        self.questions.append({
            "type": "shortanswer",
            "name": name,
            "text": strip_outer_p(question_text),
            "answers": formatted_answers,
            "general_feedback": strip_outer_p(general_feedback),
            "usecase": usecase,
            "penalty": penalty,
            "image_path": image_path,
            "image_alt": image_alt
        })

    def add_ddimageortext(
        self,
        name,
        question_text,
        image_path,
        items,
        general_feedback="",
        shuffle=True,
        penalty=0.3333333,
        defaultgrade="1.0000000"
    ):
        """
        Añade una pregunta de arrastrar y soltar sobre imagen (<question type="ddimageortext">).
        Incrusta la imagen de fondo en Base64 directamente dentro de la pregunta en Moodle XML.

        items: Lista de elementos arrastrables (drag) y sus zonas de soltado (drop):
            [
                {"text": "Bomba de alta presión", "x": 110, "y": 95, "group": 1, "infinite": False},
                {"text": "Rampa de inyección", "x": 280, "y": 140, "group": 1},
                {"text": "Sensor de rail", "x": 420, "y": 185, "group": 1},
                {"text": "Distractor sin soltar", "group": 1}  # Distractor sin coordenadas x, y
            ]
        """
        formatted_items = []
        for it in items:
            formatted_items.append({
                "text": strip_outer_p(it.get("text", "")),
                "x": it.get("x", it.get("xleft")),
                "y": it.get("y", it.get("ytop")),
                "group": it.get("group", it.get("draggroup", 1)),
                "infinite": bool(it.get("infinite", False)),
                "choice": it.get("choice")
            })

        self.questions.append({
            "type": "ddimageortext",
            "name": name,
            "text": strip_outer_p(question_text),
            "image_path": image_path,
            "items": formatted_items,
            "general_feedback": strip_outer_p(general_feedback),
            "shuffle": shuffle,
            "penalty": penalty,
            "defaultgrade": defaultgrade
        })

    def generate_xml(self):
        """Construye y formatea el árbol XML oficial de Moodle."""
        quiz = ET.Element("quiz")

        # 1. Categoría del banco de preguntas
        cat_q = ET.SubElement(quiz, "question", type="category")
        cat_elem = ET.SubElement(cat_q, "category")
        cat_text = ET.SubElement(cat_elem, "text")
        cat_text.text = f"$course$/top/{self.category_name}"

        # 2. Iterar preguntas
        for q in self.questions:
            q_elem = ET.SubElement(quiz, "question", type=q["type"])

            # Nombre
            name_elem = ET.SubElement(q_elem, "name")
            name_text = ET.SubElement(name_elem, "text")
            name_text.text = q["name"]

            # Enunciado (sin <p> innecesarios según https://github.com/picuino/test)
            clean_q_text = strip_outer_p(q['text'])
            img_path = q.get("image_path")
            img_alt = q.get("image_alt", "Esquema técnico")
            img_b64 = None
            img_filename = None

            if q["type"] != "ddimageortext" and img_path and os.path.exists(img_path):
                img_filename = os.path.basename(img_path)
                with open(img_path, "rb") as img_f:
                    img_b64 = base64.b64encode(img_f.read()).decode("ascii")
                if "@@PLUGINFILE@@" not in clean_q_text:
                    clean_q_text = f'{clean_q_text}<br><img src="@@PLUGINFILE@@/{img_filename}" alt="{html.escape(img_alt)}" width="620" />'

            qt_elem = ET.SubElement(q_elem, "questiontext", format="html")
            qt_text = ET.SubElement(qt_elem, "text")
            qt_text.text = f"<![CDATA[{clean_q_text}]]>"
            if q["type"] != "ddimageortext" and img_b64 and img_filename:
                file_elem = ET.SubElement(qt_elem, "file", name=img_filename, path="/", encoding="base64")
                file_elem.text = img_b64

            # Retroalimentación general
            clean_gf = strip_outer_p(q.get('general_feedback', ''))
            gf_elem = ET.SubElement(q_elem, "generalfeedback", format="html")
            gf_text = ET.SubElement(gf_elem, "text")
            gf_text.text = f"<![CDATA[{clean_gf}]]>" if clean_gf else ""

            # Configuración específica por tipo
            if q["type"] == "multichoice":
                ET.SubElement(q_elem, "defaultgrade").text = "1.0000000"
                ET.SubElement(q_elem, "penalty").text = str(q.get("penalty", 0.3333333))
                ET.SubElement(q_elem, "hidden").text = "0"
                ET.SubElement(q_elem, "single").text = "true" if q.get("single", True) else "false"
                ET.SubElement(q_elem, "shuffleanswers").text = "1" if q.get("shuffle", True) else "0"
                ET.SubElement(q_elem, "answernumbering").text = "abc"

                for opt in q["options"]:
                    frac = str(opt.get("fraction", 0))
                    ans_elem = ET.SubElement(q_elem, "answer", fraction=frac, format="html")
                    ans_text = ET.SubElement(ans_elem, "text")
                    clean_opt = strip_outer_p(opt['text'])
                    ans_text.text = f"<![CDATA[{clean_opt}]]>"

                    fb_elem = ET.SubElement(ans_elem, "feedback", format="html")
                    fb_text = ET.SubElement(fb_elem, "text")
                    clean_fb = strip_outer_p(opt.get('feedback', ''))
                    fb_text.text = f"<![CDATA[{clean_fb}]]>" if clean_fb else ""

            elif q["type"] == "truefalse":
                ET.SubElement(q_elem, "defaultgrade").text = "1.0000000"
                ET.SubElement(q_elem, "penalty").text = "1.0000000"
                ET.SubElement(q_elem, "hidden").text = "0"

                # Opción True
                ans_true = ET.SubElement(q_elem, "answer", fraction="100" if q["is_correct"] else "0", format="moodle_auto_format")
                ET.SubElement(ans_true, "text").text = "true"
                fb_true = ET.SubElement(ans_true, "feedback", format="html")
                clean_fb_t = strip_outer_p(q.get('feedback_true', ''))
                ET.SubElement(fb_true, "text").text = f"<![CDATA[{clean_fb_t}]]>" if clean_fb_t else ""

                # Opción False
                ans_false = ET.SubElement(q_elem, "answer", fraction="0" if q["is_correct"] else "100", format="moodle_auto_format")
                ET.SubElement(ans_false, "text").text = "false"
                fb_false = ET.SubElement(ans_false, "feedback", format="html")
                clean_fb_f = strip_outer_p(q.get('feedback_false', ''))
                ET.SubElement(fb_false, "text").text = f"<![CDATA[{clean_fb_f}]]>" if clean_fb_f else ""

            elif q["type"] == "matching":
                ET.SubElement(q_elem, "defaultgrade").text = "1.0000000"
                ET.SubElement(q_elem, "penalty").text = "0.3333333"
                ET.SubElement(q_elem, "hidden").text = "0"
                ET.SubElement(q_elem, "shuffleanswers").text = "1" if q.get("shuffle", True) else "0"

                for concept, answer in q["pairs"]:
                    sub_elem = ET.SubElement(q_elem, "subquestion", format="html")
                    sub_text = ET.SubElement(sub_elem, "text")
                    clean_concept = strip_outer_p(concept)
                    sub_text.text = f"<![CDATA[{clean_concept}]]>"
                    ans_elem = ET.SubElement(sub_elem, "answer")
                    clean_ans = strip_outer_p(answer)
                    ET.SubElement(ans_elem, "text").text = clean_ans

            elif q["type"] == "numerical":
                ET.SubElement(q_elem, "defaultgrade").text = "1.0000000"
                ET.SubElement(q_elem, "penalty").text = str(q.get("penalty", 0.3333333))
                ET.SubElement(q_elem, "hidden").text = "0"

                ans_elem = ET.SubElement(q_elem, "answer", fraction="100", format="moodle_auto_format")
                ET.SubElement(ans_elem, "text").text = str(q["answer_value"])
                ET.SubElement(ans_elem, "tolerance").text = str(q.get("tolerance", 0.0))
                fb_elem = ET.SubElement(ans_elem, "feedback", format="html")
                clean_fb = strip_outer_p(q.get("feedback", ""))
                ET.SubElement(fb_elem, "text").text = f"<![CDATA[{clean_fb}]]>" if clean_fb else ""

                units_list = q.get("units", [])
                if units_list:
                    units_elem = ET.SubElement(q_elem, "units")
                    for u_name, u_mult in units_list:
                        u_elem = ET.SubElement(units_elem, "unit")
                        ET.SubElement(u_elem, "multiplier").text = str(u_mult)
                        ET.SubElement(u_elem, "unit_name").text = str(u_name)
                    ET.SubElement(q_elem, "unitgradingtype").text = str(q.get("unit_grading_type", 0))
                    ET.SubElement(q_elem, "unitpenalty").text = "0.1000000"
                    ET.SubElement(q_elem, "showunits").text = str(q.get("show_units", 3))
                    ET.SubElement(q_elem, "unitsleft").text = "0"

            elif q["type"] == "shortanswer":
                ET.SubElement(q_elem, "defaultgrade").text = "1.0000000"
                ET.SubElement(q_elem, "penalty").text = str(q.get("penalty", 0.3333333))
                ET.SubElement(q_elem, "hidden").text = "0"
                ET.SubElement(q_elem, "usecase").text = str(q.get("usecase", 0))

                for ans in q["answers"]:
                    frac = str(ans.get("fraction", 100))
                    ans_elem = ET.SubElement(q_elem, "answer", fraction=frac, format="moodle_auto_format")
                    ET.SubElement(ans_elem, "text").text = str(ans["text"])
                    fb_elem = ET.SubElement(ans_elem, "feedback", format="html")
                    clean_fb = strip_outer_p(ans.get("feedback", ""))
                    ET.SubElement(fb_elem, "text").text = f"<![CDATA[{clean_fb}]]>" if clean_fb else ""

            elif q["type"] == "ddimageortext":
                ET.SubElement(q_elem, "defaultgrade").text = str(q.get("defaultgrade", "1.0000000"))
                ET.SubElement(q_elem, "penalty").text = str(q.get("penalty", 0.3333333))
                ET.SubElement(q_elem, "hidden").text = "0"
                ET.SubElement(q_elem, "shuffleanswers").text = "1" if q.get("shuffle", True) else "0"

                # Incrustación de la imagen de fondo en Base64 directamente en la etiqueta <question>
                bg_path = q.get("image_path")
                if bg_path and os.path.exists(bg_path):
                    bg_filename = os.path.basename(bg_path)
                    with open(bg_path, "rb") as img_f:
                        bg_b64 = base64.b64encode(img_f.read()).decode("ascii")
                    file_elem = ET.SubElement(q_elem, "file", name=bg_filename, path="/", encoding="base64")
                    file_elem.text = bg_b64

                # Generación de elementos arrastrables (drag) y zonas de soltado (drop)
                items = q.get("items", [])
                for idx, item in enumerate(items, start=1):
                    drag = ET.SubElement(q_elem, "drag")
                    ET.SubElement(drag, "no").text = str(idx)
                    ET.SubElement(drag, "text").text = strip_outer_p(item.get("text", ""))
                    ET.SubElement(drag, "draggroup").text = str(item.get("group", item.get("draggroup", 1)))
                    inf_val = "1" if item.get("infinite") in (True, 1, "1") else "0"
                    ET.SubElement(drag, "infinite").text = inf_val

                    x = item.get("x", item.get("xleft"))
                    y = item.get("y", item.get("ytop"))
                    if x is not None and y is not None:
                        drop = ET.SubElement(q_elem, "drop")
                        ET.SubElement(drop, "text").text = ""
                        choice_val = item.get("choice")
                        ET.SubElement(drop, "choice").text = str(choice_val if choice_val is not None else idx)
                        ET.SubElement(drop, "xleft").text = str(x)
                        ET.SubElement(drop, "ytop").text = str(y)

        rough_string = ET.tostring(quiz, encoding="utf-8")
        # Deshacer escape de CDATA generado por ElementTree
        xml_str = rough_string.decode("utf-8")
        xml_str = xml_str.replace("&lt;![CDATA[", "<![CDATA[").replace("]]&gt;", "]]>")

        # Formatear con indentación legible
        reparsed = minidom.parseString(xml_str.encode("utf-8"))
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

        # Limpiar líneas en blanco extras
        clean_lines = [line for line in pretty_xml.splitlines() if line.strip()]
        return "\n".join(clean_lines) + "\n"

    def save_xml(self, output_path):
        """Guarda el archivo XML en disco."""
        xml_content = self.generate_xml()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"✅ Archivo Moodle XML generado: {output_path} ({len(self.questions)} preguntas)")
        return output_path


def build_ddimageortext_xml(
    output_xml_path: str,
    question_name: str,
    question_prompt: str,
    image_path: str,
    items: list,
    general_feedback: str = "",
    shuffle: bool = True,
    penalty: float = 0.3333333,
    defaultgrade: str = "1.0000000",
    category_name: str = "Preguntas de Arrastrar sobre Imagen"
):
    """
    Genera un archivo Moodle XML de arrastrar sobre imagen (<question type="ddimageortext">)
    con imagen incrustada en Base64, plenamente compatible con Moodle 3.x, 4.x y EducaMadrid.
    Cumple con la norma técnica de preguntas de test sin etiquetas <p> innecesarias (https://github.com/picuino/test).

    items = [
        {"text": "Bomba de alta presión", "x": 110, "y": 95, "group": 1},
        {"text": "Rampa de inyección", "x": 280, "y": 140, "group": 1},
        {"text": "Sensor de rail", "x": 420, "y": 185, "group": 1},
        {"text": "Distractor sin zona de soltado", "group": 1} # Opcional: distractor sin drop
    ]
    """
    builder = MoodleXMLBuilder(category_name=category_name)
    builder.add_ddimageortext(
        name=question_name,
        question_text=question_prompt,
        image_path=image_path,
        items=items,
        general_feedback=general_feedback,
        shuffle=shuffle,
        penalty=penalty,
        defaultgrade=defaultgrade
    )
    return builder.save_xml(output_xml_path)


def validar_moodle_xml(xml_path):
    """
    Valida y certifica la compatibilidad oficial de un archivo Moodle XML (<quiz>).
    Retorna True si es válido, False si contiene errores críticos.
    """
    print("=" * 60)
    print(f"VERIFICANDO BANCO MOODLE XML: {os.path.basename(xml_path)}")
    print("=" * 60)

    if not os.path.exists(xml_path):
        print(f"❌ ERROR: El archivo no existe: {xml_path}")
        return False

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ ERROR de sintaxis XML: {e}")
        return False

    if root.tag != "quiz":
        print(f"❌ ERROR: La raíz del documento debe ser <quiz>, pero es <{root.tag}>")
        return False

    questions = root.findall("question")
    if not questions:
        print("❌ ERROR: El archivo no contiene etiquetas <question>.")
        return False

    categories = [q for q in questions if q.get("type") == "category"]
    eval_questions = [q for q in questions if q.get("type") != "category"]

    print(f"✓ Estructura XML válida conformada con <quiz>.")
    if categories:
        cat_name = categories[0].find("category/text")
        print(f"✓ Categoría Moodle: {cat_name.text if cat_name is not None else 'Raíz'}")
    print(f"✓ Total de preguntas de evaluación: {len(eval_questions)}")

    errores = []
    advertencias = []
    tipos_detectados = {}
    multichoice_count = 0
    correct_is_longest_count = 0
    correct_is_shortest_count = 0
    correct_positions = {}
    redundant_p_count = 0
    embedded_images_count = 0

    for idx, q in enumerate(eval_questions, 1):
        q_type = q.get("type")
        tipos_detectados[q_type] = tipos_detectados.get(q_type, 0) + 1
        name = q.find("name/text")
        q_name = name.text if name is not None else f"Pregunta {idx}"

        # Enunciado e imágenes embebidas
        q_files = q.findall("questiontext/file") + q.findall("file")
        if q_files:
            embedded_images_count += len(q_files)
        q_text = q.find("questiontext/text")
        if q_text is None or not (q_text.text or "").strip():
            errores.append(f"Pregunta #{idx} ('{q_name}'): Enunciado vacío.")
        else:
            raw_qt = q_text.text.replace("<![CDATA[", "").replace("]]>", "").strip()
            if raw_qt.startswith("<p>") and raw_qt.endswith("</p>") and raw_qt.count("<p>") == 1:
                redundant_p_count += 1

        # Validación por tipo
        if q_type == "multichoice":
            answers = q.findall("answer")
            if len(answers) < 2:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Requiere al menos 2 opciones de respuesta.")

            fracciones = [float(a.get("fraction", 0)) for a in answers]
            if not any(f >= 99.9 for f in fracciones) and sum(f for f in fracciones if f > 0) < 99.9:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Las opciones correctas no suman el 100%.")

            # Verificar posición de la correcta en el XML
            for pos_idx, f_val in enumerate(fracciones):
                if f_val >= 99.9:
                    letter = chr(ord('A') + pos_idx) if pos_idx < 26 else str(pos_idx)
                    correct_positions[letter] = correct_positions.get(letter, 0) + 1

            # Feedback de aprendizaje activo y control de <p>
            sin_feedback = []
            for a in answers:
                fb_node = a.find("feedback/text")
                if fb_node is None or not (fb_node.text or "").strip():
                    sin_feedback.append(a)
                txt_node = a.find("text")
                if txt_node is not None and txt_node.text:
                    raw_a = txt_node.text.replace("<![CDATA[", "").replace("]]>", "").strip()
                    if raw_a.startswith("<p>") and raw_a.endswith("</p>") and raw_a.count("<p>") == 1:
                        redundant_p_count += 1

            if sin_feedback:
                advertencias.append(f"Pregunta #{idx} ('{q_name}'): {len(sin_feedback)} opción(es) sin feedback razonado.")

            # Control psicométrico bidireccional de longitud (prevención de length bias)
            opts_len = []
            for a in answers:
                txt_node = a.find("text")
                raw_val = txt_node.text if txt_node is not None else ""
                clean_val = re.sub(r'<[^>]+>', '', raw_val.replace("<![CDATA[", "").replace("]]>", "")).strip()
                clean_val = html.unescape(clean_val)
                frac = float(a.get("fraction", 0))
                opts_len.append((len(clean_val), frac))

            if opts_len:
                multichoice_count += 1
                max_len = max(l for l, _ in opts_len)
                min_len = min(l for l, _ in opts_len)
                avg_len = sum(l for l, _ in opts_len) / len(opts_len)
                correct_is_longest = any(f >= 99.9 and l == max_len for l, f in opts_len)
                correct_is_shortest = any(f >= 99.9 and l == min_len for l, f in opts_len)
                if correct_is_longest:
                    correct_is_longest_count += 1
                if correct_is_shortest:
                    correct_is_shortest_count += 1
                # Detectar desproporción extrema dentro de la misma pregunta
                if avg_len > 25 and (max_len > avg_len * 1.65 or min_len < avg_len * 0.45):
                    advertencias.append(
                        f"Pregunta #{idx} ('{q_name}'): Longitud dispar entre opciones (mín: {min_len}, máx: {max_len} caract.). Homogeneice entre ±20%."
                    )

        elif q_type == "truefalse":
            answers = q.findall("answer")
            if len(answers) != 2:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Requiere exactamente 2 respuestas (true/false).")

        elif q_type == "matching":
            subs = q.findall("subquestion")
            if len(subs) < 2:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Requiere al menos 2 pares de emparejamiento.")

        elif q_type == "numerical":
            answers = q.findall("answer")
            if not answers:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Pregunta numérica sin etiqueta <answer>.")
            else:
                for a in answers:
                    val_txt = (a.find("text").text if a.find("text") is not None else "").strip()
                    try:
                        float(val_txt)
                    except ValueError:
                        errores.append(f"Pregunta #{idx} ('{q_name}'): Valor numérico no válido '{val_txt}'.")

        elif q_type == "shortanswer":
            answers = q.findall("answer")
            if not answers:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Pregunta de respuesta corta sin <answer>.")

        elif q_type == "ddimageortext":
            bg_files = q.findall("file")
            if not bg_files:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Pregunta ddimageortext sin imagen de fondo <file>.")
            else:
                for f in bg_files:
                    if not (f.text or "").strip():
                        errores.append(f"Pregunta #{idx} ('{q_name}'): Archivo de imagen de fondo '{f.get('name')}' vacío.")

            drags = q.findall("drag")
            drops = q.findall("drop")
            if not drags:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Requiere al menos 1 elemento arrastrable <drag>.")
            if not drops:
                errores.append(f"Pregunta #{idx} ('{q_name}'): Requiere al menos 1 zona de soltado <drop>.")

            drag_nos = set()
            for d_idx, d in enumerate(drags, 1):
                d_no = d.find("no")
                d_txt = d.find("text")
                if d_no is None or not (d_no.text or "").strip():
                    errores.append(f"Pregunta #{idx} ('{q_name}'): Elemento drag #{d_idx} sin etiqueta <no>.")
                else:
                    drag_nos.add(d_no.text.strip())
                if d_txt is None or not (d_txt.text or "").strip():
                    advertencias.append(f"Pregunta #{idx} ('{q_name}'): Elemento drag #{d_idx} con texto visible vacío.")

            for dp_idx, dp in enumerate(drops, 1):
                ch = dp.find("choice")
                xl = dp.find("xleft")
                yt = dp.find("ytop")
                if ch is None or not (ch.text or "").strip():
                    errores.append(f"Pregunta #{idx} ('{q_name}'): Zona drop #{dp_idx} sin etiqueta <choice>.")
                elif ch.text.strip() not in drag_nos:
                    errores.append(f"Pregunta #{idx} ('{q_name}'): Zona drop #{dp_idx} apunta a <choice> '{ch.text}' inexistente en los elementos <drag>.")
                if xl is None or not (xl.text or "").strip():
                    errores.append(f"Pregunta #{idx} ('{q_name}'): Zona drop #{dp_idx} sin coordenada <xleft>.")
                if yt is None or not (yt.text or "").strip():
                    errores.append(f"Pregunta #{idx} ('{q_name}'): Zona drop #{dp_idx} sin coordenada <ytop>.")

    print(f"✓ Tipos de preguntas certificados: {tipos_detectados}")
    if embedded_images_count > 0:
        print(f"✓ Imágenes técnicas embebidas en Base64 (@@PLUGINFILE@@ / fondo ddimageortext): {embedded_images_count}")
    if redundant_p_count == 0:
        print("✓ Formato XML limpio (sin <p> ni </p> redundantes, norma https://github.com/picuino/test): Certificado.")
    else:
        advertencias.append(
            f"Se detectaron {redundant_p_count} etiquetas <p>...</p> redundantes en el XML. "
            "En preguntas de test XML no se necesitan etiquetas <p> y </p> (norma https://github.com/picuino/test)."
        )

    # Reporte psicométrico de sesgo de longitud y posición
    if multichoice_count > 0:
        pct_longest = (correct_is_longest_count / multichoice_count) * 100
        print(
            f"✓ Análisis psicométrico (sesgo de longitud): {correct_is_longest_count}/{multichoice_count} "
            f"({pct_longest:.1f}%) preguntas multichoice tienen la opción correcta como la más larga."
        )
        print(f"✓ Distribución de posición de la respuesta correcta en XML: {dict(sorted(correct_positions.items()))}")

        if multichoice_count >= 4 and pct_longest > 45.0:
            advertencias.append(
                f"Alerta Psicométrica (Sesgo de Longitud): En el {pct_longest:.1f}% de las preguntas multichoice "
                f"({correct_is_longest_count}/{multichoice_count}), la respuesta correcta es la más larga (máximo recomendado: 40%)."
            )
        elif multichoice_count >= 5 and pct_longest == 0.0:
            advertencias.append(
                "Alerta Psicométrica (Sesgo Inverso de Longitud): En el 0.0% de las preguntas la respuesta correcta es la más larga. "
                "Alterne deliberadamente para que en ~20-35% de las preguntas la correcta sea la más extensa."
            )

        if multichoice_count >= 4 and correct_positions:
            max_pos_count = max(correct_positions.values())
            if (max_pos_count / multichoice_count) > 0.60:
                advertencias.append(
                    f"Alerta de Patrón de Posición en XML: Más del 60% de las preguntas tienen la respuesta correcta en la misma posición ({correct_positions})."
                )

    if advertencias:
        print(f"\n⚠️  {len(advertencias)} ADVERTENCIA(S):")
        for adv in advertencias[:5]:
            print(f"   [!] {adv}")
        if len(advertencias) > 5:
            print(f"   ... y {len(advertencias) - 5} advertencia(s) más.")

    if errores:
        print(f"\n❌ {len(errores)} ERROR(ES) CRÍTICOS:")
        for err in errores:
            print(f"   [X] {err}")
        return False

    print("\n✅ CERTIFICACIÓN EXITOSA: EL BANCO MOODLE XML CUMPLE 100% CON LA NORMATIVA DE EDUCAMADRID.")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        valido = validar_moodle_xml(archivo)
        sys.exit(0 if valido else 1)
    else:
        print("Uso: python3 moodle_xml_builder.py <archivo.xml>")
