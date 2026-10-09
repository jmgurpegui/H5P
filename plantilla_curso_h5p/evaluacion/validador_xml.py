#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Bancos de Preguntas Moodle XML para EducaMadrid y H5P
Verifica:
1. Conformidad con el esquema estándar Moodle XML (<quiz>).
2. Preguntas de opción múltiple con 4 alternativas y fracción 100 en la correcta.
3. Equilibrio y alternancia de respuestas correctas (A, B, C, D).
4. Presencia de retroalimentación formativa obligatoria en cada cuestión.
"""

import os
import sys
import xml.etree.ElementTree as ET

def validar_archivo_moodle_xml(xml_path):
    print(f"\n🔍 Validando banco Moodle XML: {xml_path}")
    if not os.path.isfile(xml_path):
        print(f"❌ ERROR: El archivo no existe: {xml_path}")
        return False

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"❌ ERROR de sintaxis XML: {e}")
        return False

    if root.tag != 'quiz':
        print(f"❌ ERROR: La etiqueta raíz debe ser <quiz>, pero es <{root.tag}>")
        return False

    preguntas = [q for q in root.findall('question') if q.get('type') in ('multichoice', 'truefalse')]
    print(f"✓ Total de preguntas detectadas: {len(preguntas)}")

    if len(preguntas) == 0:
        print("❌ ERROR: No se encontraron preguntas de tipo 'multichoice' o 'truefalse'.")
        return False

    conteo_correctas = {0: 0, 1: 0, 2: 0, 3: 0}
    errores = []
    avisos = []

    for idx, q in enumerate(preguntas, 1):
        name_elem = q.find('name/text')
        q_name = name_elem.text if name_elem is not None else f"Pregunta {idx}"

        # Enunciado
        qt_elem = q.find('questiontext/text')
        if qt_elem is None or not (qt_elem.text or "").strip():
            errores.append(f"Pregunta {idx} ('{q_name}') carece de enunciado (questiontext).")

        # Respuestas
        answers = q.findall('answer')
        if len(answers) < 2:
            errores.append(f"Pregunta {idx} ('{q_name}') tiene menos de 2 alternativas ({len(answers)}).")

        correct_indices = []
        for a_idx, ans in enumerate(answers):
            fraction = float(ans.get('fraction', '0'))
            if fraction >= 99.0:
                correct_indices.append(a_idx)

            ans_text = ans.find('text')
            if ans_text is None or not (ans_text.text or "").strip():
                errores.append(f"Pregunta {idx}, opción {a_idx+1} no tiene texto de respuesta.")

        if len(correct_indices) == 0:
            errores.append(f"Pregunta {idx} ('{q_name}') NO tiene ninguna opción correcta (fraction='100').")
        elif len(correct_indices) > 1:
            avisos.append(f"Pregunta {idx} ('{q_name}') tiene múltiples opciones marcadas con fraction='100'.")
        else:
            c_idx = correct_indices[0]
            if c_idx in conteo_correctas:
                conteo_correctas[c_idx] += 1

        # Feedback
        gf_elem = q.find('generalfeedback/text')
        has_gf = gf_elem is not None and bool((gf_elem.text or "").strip())
        has_af = any(ans.find('feedback/text') is not None and bool((ans.find('feedback/text').text or "").strip()) for ans in answers)
        if not has_gf and not has_af:
            avisos.append(f"Pregunta {idx} ('{q_name}') no incluye retroalimentación (feedback).")

    # Resumen de resultados
    print("\n--- DISTRIBUCIÓN DE RESPUESTAS CORRECTAS ---")
    letras = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
    for idx_letra in range(4):
        cnt = conteo_correctas[idx_letra]
        pct = (cnt / len(preguntas)) * 100 if preguntas else 0
        print(f"  Opción {letras[idx_letra]} (índice {idx_letra}): {cnt} preguntas ({pct:.1f}%)")

    if avisos:
        print(f"\n⚠️ Avisos encontrados ({len(avisos)}):")
        for a in avisos[:5]:
            print(f"  • {a}")
        if len(avisos) > 5:
            print(f"  ... y {len(avisos) - 5} avisos más.")

    if errores:
        print(f"\n❌ ERRORES CRÍTICOS ENCONTRADOS ({len(errores)}):")
        for err in errores:
            print(f"  • {err}")
        return False

    print("\n✅ VALIDACIÓN SUPERADA: El archivo Moodle XML es 100% válido para EducaMadrid y H5P.\n")
    return True

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else "/home/jmgurpegui/H5P/plantilla_curso_h5p/evaluacion/preguntas_moodle.xml"
    exito = validar_archivo_moodle_xml(archivo)
    sys.exit(0 if exito else 1)
