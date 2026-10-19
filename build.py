#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador, Generador y Validador Maestro de la Plantilla H5P y Evaluación Moodle XML para EducaMadrid (FP Automoción).

Uso:
    python3 build.py                                  # Inyecta CSS, compila/valida la plantilla y sincroniza el skill
    python3 build.py nuevo <Carpeta> ["Título"]       # Crea la estructura base para un nuevo curso de Automoción
    python3 build.py <CarpetaCurso>                   # Compila y valida un curso local específico
    python3 build.py todos                            # Compila la plantilla y todos los cursos locales existentes
    python3 build.py xml                              # Valida todos los bancos de preguntas Moodle XML
    python3 build.py css                              # Inyecta limpiamente los estilos responsive en librerías base
    python3 build.py validar <archivo.h5p_o_xml>      # Valida un paquete H5P o un banco Moodle XML
"""

import os
import re
import sys
import glob
import shutil
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTILLA_DIR = os.path.join(ROOT_DIR, "plantilla")
SKILL_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "h5p-educamadrid")
VALIDADOR_H5P = os.path.join(PLANTILLA_DIR, "validar_h5p_educamadrid.py")
VALIDADOR_XML = os.path.join(PLANTILLA_DIR, "moodle_xml_builder.py")
INJECT_CSS = os.path.join(PLANTILLA_DIR, "append_css_to_libraries.py")


def sincronizar_skill():
    """Mantiene sincronizados los scripts, recursos y ejemplos del skill con la plantilla maestra."""
    if not os.path.isdir(SKILL_DIR):
        return
    sync_pairs = [
        (os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py"), os.path.join(SKILL_DIR, "scripts", "generar_curso.py")),
        (os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py"), os.path.join(SKILL_DIR, "examples", "curso_modelo_ejemplo.py")),
        (os.path.join(PLANTILLA_DIR, "validar_h5p_educamadrid.py"), os.path.join(SKILL_DIR, "scripts", "validar_h5p.py")),
        (os.path.join(PLANTILLA_DIR, "moodle_xml_builder.py"), os.path.join(SKILL_DIR, "scripts", "moodle_xml_builder.py")),
        (os.path.join(PLANTILLA_DIR, "append_css_to_libraries.py"), os.path.join(SKILL_DIR, "scripts", "inyectar_css.py")),
        (os.path.join(PLANTILLA_DIR, "estilos_educamadrid.css"), os.path.join(SKILL_DIR, "resources", "estilos_educamadrid.css")),
        (os.path.join(PLANTILLA_DIR, "Plantilla_Curso_Modelo_EducaMadrid.h5p"), os.path.join(SKILL_DIR, "examples", "Plantilla_Curso_Modelo_EducaMadrid.h5p")),
        (os.path.join(PLANTILLA_DIR, "evaluacion_modelo_moodle.xml"), os.path.join(SKILL_DIR, "examples", "evaluacion_modelo_moodle.xml")),
        (os.path.join(ROOT_DIR, "REQUISITOS_CURSOS_H5P_EDUCAMADRID.md"), os.path.join(PLANTILLA_DIR, "REQUISITOS_CURSOS_H5P_EDUCAMADRID.md")),
    ]
    for src, dst in sync_pairs:
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    print("✓ Skill (.agents/skills/h5p-educamadrid/) sincronizado con la plantilla maestra.")


def inyectar_css():
    print("=" * 60)
    print(">>> Inyectando estilos responsive oficiales en librerías base...")
    print("=" * 60)
    ret = subprocess.call([sys.executable, INJECT_CSS])
    if ret != 0:
        sys.exit(ret)


def compilar_plantilla():
    inyectar_css()
    print("=" * 60)
    print(">>> Compilando Curso Modelo y Banco Moodle XML (Plantilla)...")
    print("=" * 60)
    script = os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py")
    ret = subprocess.call([sys.executable, script])
    if ret != 0:
        sys.exit(ret)
    sincronizar_skill()


def descubrir_cursos_locales():
    """Localiza carpetas de cursos en el directorio raíz que contengan un script generar_curso_*.py."""
    cursos = []
    for entry in sorted(os.listdir(ROOT_DIR)):
        full_dir = os.path.join(ROOT_DIR, entry)
        if not os.path.isdir(full_dir) or entry in ("plantilla", "h5p_builder", ".git", ".agents", "__pycache__"):
            continue
        scripts = sorted(glob.glob(os.path.join(full_dir, "generar_curso*.py")))
        if scripts:
            cursos.append((entry, full_dir, scripts[0]))
    return cursos


def compilar_curso_local(nombre_o_ruta):
    for entry, full_dir, script in descubrir_cursos_locales():
        if nombre_o_ruta.lower() in (entry.lower(), os.path.basename(script).lower()):
            print("=" * 60)
            print(f">>> Compilando Curso Local: {entry} ({os.path.basename(script)})...")
            print("=" * 60)
            ret = subprocess.call([sys.executable, script])
            if ret != 0:
                sys.exit(ret)
            return True
    return False


def crear_nuevo_curso(folder_name, course_title=None):
    """Genera el esqueleto completo para un nuevo curso H5P + Moodle XML de FP de Automoción."""
    clean_folder = re.sub(r'[^A-Za-z0-9_-]', '', folder_name)
    if not clean_folder:
        print("❌ Error: Nombre de carpeta no válido.")
        sys.exit(1)

    target_dir = os.path.join(ROOT_DIR, clean_folder)
    if os.path.exists(target_dir):
        print(f"⚠️ La carpeta '{target_dir}' ya existe.")
        sys.exit(1)

    slug = re.sub(r'[^a-z0-9]+', '_', clean_folder.lower()).strip('_')
    title = course_title or f"Curso de Automoción: {clean_folder}"
    images_dir = os.path.join(target_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    script_path = os.path.join(target_dir, f"generar_curso_{slug}.py")
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del Curso H5P (100% Formativo) y Banco de Preguntas Moodle XML (Sumativo):
{title}
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PLANTILLA_DIR = os.path.join(PROJECT_ROOT, "plantilla")
sys.path.insert(0, PLANTILLA_DIR)

from generar_curso_plantilla import (
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
    build_h5p_package,
)
from moodle_xml_builder import MoodleXMLBuilder, validar_moodle_xml
from validar_h5p_educamadrid import validate_h5p


def build_chapter_1():
    fase1_intro = [
        create_text_section("""
        <div class="tech-hero">
          <h2>Unidad 1: {title}</h2>
          <p>Fundamentos técnicos, arquitectura de componentes y protocolos de comprobación en taller.</p>
          <div class="tech-badge-container">
            <span class="tech-badge badge-blue">FP Automoción</span>
            <span class="tech-badge badge-green">EducaMadrid H5P</span>
            <span class="tech-badge badge-yellow">WCAG 2.1 AAA</span>
          </div>
        </div>
        """, "Introducción Unidad 1")
    ]

    fase2_explicacion = [
        create_component_spec_card(
            component_name="Componente o Sensor Principal de la Unidad",
            category_badge="FICHA TÉCNICA DE TALLER",
            specs_dict=[
                ("Tensión nominal", "12.0 V – 14.4 V"),
                ("Resistencia interna", "Valor en Ω a 20 °C"),
                ("Caída máxima admisible", "≤ 0.2 V en línea positiva / ≤ 0.1 V en masa")
            ],
            pinout_list=[
                ("Borne 30", "Positivo directo de batería"),
                ("Borne 15", "Positivo bajo llave de contacto"),
                ("Borne 31", "Retorno a masa en chasis")
            ],
            oscilloscope_note="Verifica la señal con el circuito bajo carga nominal utilizando agujas de back-probing."
        )
    ]

    fase3_practica = [
        create_diagnostic_table(
            title="Cuadro de Diagnosis Metrológica en Taller",
            rows=[
                (
                    "Fallo de activación del sistema",
                    "Polímetro en V DC entre alimentación y masa bajo carga",
                    "Nominal: 12.5 V | Avería: 0 V",
                    "Verificar fusible de protección y continuidad de línea positiva."
                )
            ]
        ),
        create_checklist_section(
            title="Protocolo de Verificación en Vehículo",
            items=[
                "Comprobar tensión de batería en reposo (> 12.4 V).",
                "Medir caída de tensión en línea positiva y masa bajo carga real.",
                "Verificar ausencia de códigos DTC en centralita con equipo de diagnosis."
            ]
        )
    ]

    fase4_sintesis = [
        create_moodle_quiz_referral(
            1,
            "{title}",
            "<p>Has completado el estudio técnico y los protocolos de diagnosis de la unidad. Realiza el cuestionario oficial en Moodle para registrar tu calificación.</p>"
        )
    ]

    return create_didactic_sequence_chapter(
        "1. Fundamentos y Diagnosis",
        fase1_intro,
        fase2_explicacion,
        fase3_practica,
        fase4_sintesis
    )


def generar_banco_xml(xml_path):
    builder = MoodleXMLBuilder("{title} - Evaluacion Oficial")

    builder.add_multichoice(
        "P01_Caida_Tension_Maxima",
        "¿Cuál es la caída de tensión máxima admisible en una línea de masa de potencia medida bajo carga nominal en el vehículo?",
        [
            {{"text": "Menor o igual a 0.1 V entre el casquillo del consumidor y el borne negativo.", "fraction": 100, "feedback": "¡Correcto! Una caída superior a 0.1 V en masa indica sulfatación o tornillo oxidado en chasis."}},
            {{"text": "Entre 1.2 V y 2.5 V siempre que el fusible de protección no se haya fundido.", "fraction": 0, "feedback": "Incorrecto. Esa caída de tensión restaría potencia crítica al actuador."}},
            {{"text": "Exactamente 5.0 V estabilizados por la unidad de control electrónico del motor.", "fraction": 0, "feedback": "Incorrecto. 5 V es la tensión de referencia de sensores, no la caída en masa."}},
            {{"text": "Hasta un 25% de la tensión nominal de la batería con el motor a ralentí.", "fraction": 0, "feedback": "Incorrecto. Un 25% (3 V) inutilizaría el circuito."}}
        ],
        general_feedback="En líneas de masa (Borne 31), la caída máxima admisible bajo carga es de 0.1 V (y hasta 0.2-0.3 V en línea positiva)."
    )

    builder.add_numerical(
        "P02_Calculo_Ley_Ohm",
        "Por un conector con resistencia parásita de <strong>R = 0.2 Ω</strong> circula una intensidad de <strong>I = 8 A</strong>. Calcula la caída de tensión (ΔV = I × R) en voltios:",
        answer_value=1.6,
        tolerance=0.05,
        feedback="¡Correcto! ΔV = 8 A × 0.2 Ω = 1.6 V.",
        general_feedback="Aplicando la Ley de Ohm: ΔV = I × R = 8 A × 0.2 Ω = 1.6 V.",
        units=["V", "voltios"]
    )

    builder.save_xml(xml_path)
    validar_moodle_xml(xml_path)


if __name__ == "__main__":
    output_h5p = os.path.join(SCRIPT_DIR, "Curso_{clean_folder}.h5p")
    output_xml = os.path.join(SCRIPT_DIR, "evaluacion_{slug}.xml")

    chapters = [build_chapter_1()]
    build_h5p_package(
        output_path=output_h5p,
        title="{title}",
        book_cover_title="{title}",
        book_cover_desc="Curso técnico interactivo para Formación Profesional de Automoción en EducaMadrid.",
        chapters=chapters,
        images_source_dir=os.path.join(SCRIPT_DIR, "images")
    )
    validate_h5p(output_h5p)
    generar_banco_xml(output_xml)
'''
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"✅ Nuevo curso inicializado en: {target_dir}")
    print(f"   - Script generador: {script_path}")
    print(f"   - Carpeta de imágenes: {images_dir}")
    print(f"   Ejecuta 'python3 build.py {clean_folder}' para compilarlo y validarlo.")


def validar_paquete_h5p(paquete_path):
    print("=" * 60)
    print(f">>> Validando paquete H5P: {paquete_path}")
    print("=" * 60)
    ret = subprocess.call([sys.executable, VALIDADOR_H5P, paquete_path])
    if ret != 0:
        sys.exit(ret)


def validar_banco_xml(xml_path):
    print("=" * 60)
    print(f">>> Validando Banco Moodle XML: {xml_path}")
    print("=" * 60)
    ret = subprocess.call([sys.executable, VALIDADOR_XML, xml_path])
    if ret != 0:
        sys.exit(ret)


def validar_todos_xml():
    xml_files = [os.path.join(PLANTILLA_DIR, "evaluacion_modelo_moodle.xml")]
    for _, full_dir, _ in descubrir_cursos_locales():
        xml_files.extend(sorted(glob.glob(os.path.join(full_dir, "*.xml"))))
    for xf in xml_files:
        if os.path.exists(xf):
            validar_banco_xml(xf)
            print("")


def main():
    if len(sys.argv) == 1:
        compilar_plantilla()
    elif sys.argv[1].lower() in ["plantilla", "modelo"]:
        compilar_plantilla()
    elif sys.argv[1].lower() in ["nuevo", "new", "init"]:
        if len(sys.argv) < 3:
            print('Uso: python3 build.py nuevo <NombreCarpeta> ["Título del Curso"]')
            sys.exit(1)
        titulo = sys.argv[3] if len(sys.argv) >= 4 else None
        crear_nuevo_curso(sys.argv[2], titulo)
    elif sys.argv[1].lower() in ["todos", "all"]:
        compilar_plantilla()
        for entry, _, _ in descubrir_cursos_locales():
            print("\n")
            compilar_curso_local(entry)
    elif sys.argv[1].lower() in ["xml", "evaluacion"]:
        validar_todos_xml()
    elif sys.argv[1].lower() in ["css", "estilos"]:
        inyectar_css()
        sincronizar_skill()
    elif sys.argv[1].lower() in ["validar", "valida", "check"]:
        if len(sys.argv) < 3:
            print("Uso: python3 build.py validar <ruta_a_archivo.h5p_o_xml>")
            sys.exit(1)
        target = sys.argv[2]
        if target.endswith(".xml"):
            validar_banco_xml(target)
        else:
            validar_paquete_h5p(target)
    elif sys.argv[1].endswith(".h5p"):
        validar_paquete_h5p(sys.argv[1])
    elif sys.argv[1].endswith(".xml"):
        validar_banco_xml(sys.argv[1])
    else:
        if not compilar_curso_local(sys.argv[1]):
            print(f"Opción o curso no reconocido: {sys.argv[1]}")
            print(__doc__)
            sys.exit(1)


if __name__ == "__main__":
    main()
