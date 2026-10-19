#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador, Generador y Validador Maestro de la Plantilla H5P y Evaluación Moodle XML para EducaMadrid (FP Automoción).

Uso:
    python3 build.py                                  # Inyecta CSS, compila/valida la plantilla y sincroniza el skill
    python3 build.py nuevo <Carpeta> ["Título"]       # Crea la estructura base (YAML + Python) para un nuevo curso
    python3 build.py <CarpetaCurso>                   # Compila y valida un curso local específico (YAML o Python)
    python3 build.py todos                            # Compila la plantilla y todos los cursos locales existentes
    python3 build.py simuladores [carpeta_o_archivo]  # Compila simuladores HTML a H5P compatible con EducaMadrid
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
YAML_BUILDER = os.path.join(PLANTILLA_DIR, "yaml_course_builder.py")
SIMULADOR_BUILDER = os.path.join(ROOT_DIR, "h5p_builder", "compilar_simulador.py")


def sincronizar_skill():
    """Mantiene sincronizados los scripts, recursos y ejemplos del skill con la plantilla maestra."""
    if not os.path.isdir(SKILL_DIR):
        return
    sync_pairs = [
        (os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py"), os.path.join(SKILL_DIR, "scripts", "generar_curso.py")),
        (os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py"), os.path.join(SKILL_DIR, "examples", "curso_modelo_ejemplo.py")),
        (os.path.join(PLANTILLA_DIR, "yaml_course_builder.py"), os.path.join(SKILL_DIR, "scripts", "yaml_course_builder.py")),
        (os.path.join(PLANTILLA_DIR, "contenido_modelo.yaml"), os.path.join(SKILL_DIR, "examples", "contenido_modelo.yaml")),
        (SIMULADOR_BUILDER, os.path.join(SKILL_DIR, "scripts", "compilar_simulador.py")),
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
    """Localiza carpetas de cursos en el directorio raíz que contengan un script o archivo YAML."""
    cursos = []
    for entry in sorted(os.listdir(ROOT_DIR)):
        full_dir = os.path.join(ROOT_DIR, entry)
        if not os.path.isdir(full_dir) or entry in ("plantilla", "h5p_builder", ".git", ".agents", "__pycache__"):
            continue
        scripts = sorted(glob.glob(os.path.join(full_dir, "generar_curso*.py")))
        yamls = sorted(glob.glob(os.path.join(full_dir, "contenido_curso*.yaml")) + glob.glob(os.path.join(full_dir, "*.yaml")))
        if scripts:
            cursos.append((entry, full_dir, "script", scripts[0]))
        elif yamls:
            cursos.append((entry, full_dir, "yaml", yamls[0]))
    return cursos


def compilar_curso_local(nombre_o_ruta):
    for item in descubrir_cursos_locales():
        entry, full_dir, tipo, fuente = item
        if nombre_o_ruta.lower() in (entry.lower(), os.path.basename(fuente).lower()):
            print("=" * 60)
            print(f">>> Compilando Curso Local: {entry} ({os.path.basename(fuente)})...")
            print("=" * 60)
            if tipo == "script":
                ret = subprocess.call([sys.executable, fuente])
                if ret != 0:
                    sys.exit(ret)
            else:
                ret = subprocess.call([sys.executable, YAML_BUILDER, fuente, full_dir])
                if ret != 0:
                    sys.exit(ret)
            return True
    return False


def crear_nuevo_curso(folder_name, course_title=None):
    """Genera el esqueleto desacoplado (YAML + Python) para un nuevo curso H5P + Moodle XML."""
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

    yaml_path = os.path.join(target_dir, "contenido_curso.yaml")
    script_path = os.path.join(target_dir, f"generar_curso_{slug}.py")

    # 1. Archivo YAML con el contenido desacoplado
    yaml_content = f"""# =============================================================================
# CURSO FP AUTOMOCIÓN - COMUNIDAD DE MADRID (EDUCAMADRID)
# Módulo: {title}
# Autoría: FP Madrid profesor JM Gurpegui | Licencia: CC BY-NC-SA 4.0
# =============================================================================

meta:
  titulo: "{title}"
  subtitulo: "Fundamentos Técnicos y Protocolos de Diagnosis en Taller"
  descripcion: "Curso interactivo formativo y banco Moodle XML para Formación Profesional de Automoción."
  autor: "FP Madrid profesor JM Gurpegui"
  licencia: "CC BY-NC-SA"
  version_licencia: "4.0"
  idioma: "es"

# Secuencia didáctica de 4 fases para aprendizaje activo:
#   fase1_intro: Motivación, contexto y activación de conocimientos previos
#   fase2_explicacion: Fichas técnicas de componentes, esquemas y conceptos clave
#   fase3_practica: Tablas de diagnosis, listas de comprobación y retos en vehículo
#   fase4_evaluacion: Derivación formativa al cuestionario oficial en Moodle
capitulos:
  - titulo: "Unidad 1: Fundamentos y Diagnosis"
    fase1_intro:
      - tipo: "hero"
        titulo: "Unidad 1: {title}"
        subtitulo: "Fundamentos técnicos, arquitectura de componentes y protocolos de comprobación en taller."
        badges:
          - "FP Automoción"
          - "EducaMadrid H5P"
          - "WCAG 2.1 AAA"

    fase2_explicacion:
      - tipo: "ficha_tecnica"
        nombre_componente: "Componente o Sensor Principal de la Unidad"
        categoria: "FICHA TÉCNICA DE TALLER"
        especificaciones:
          - parametro: "Tensión nominal"
            valor: "12.0 V – 14.4 V"
          - parametro: "Resistencia interna"
            valor: "Valor nominal en Ω a 20 °C"
          - parametro: "Caída máxima admisible"
            valor: "≤ 0.2 V en línea positiva / ≤ 0.1 V en masa"
        bornes:
          - borne: "Borne 30"
            descripcion: "Alimentación positiva permanente directa desde batería."
          - borne: "Borne 15"
            descripcion: "Positivo bajo llave de contacto."
          - borne: "Borne 31"
            descripcion: "Retorno a masa en chasis o borne negativo."
        nota_osciloscopio: "Verifica la señal con el circuito bajo carga nominal utilizando agujas de back-probing."

    fase3_practica:
      - tipo: "tabla_diagnosis"
        titulo: "Cuadro de Diagnosis Metrológica en Taller"
        filas:
          - sintoma: "Fallo de activación del componente"
            metodo_medicion: "Polímetro en V DC entre pin de alimentación y masa bajo carga"
            valores_referencia: "Nominal: 12.5 V | Avería: 0 V"
            accion_correctiva: "Verificar fusible de protección y continuidad de línea positiva."

      - tipo: "checklist"
        titulo: "Protocolo de Verificación en Vehículo"
        items:
          - "Comprobar tensión de batería en reposo (> 12.4 V)."
          - "Medir caída de tensión en línea positiva y masa bajo carga real."
          - "Verificar ausencia de códigos DTC en centralita con equipo de diagnosis."

    fase4_evaluacion:
      - tipo: "derivacion_moodle"
        numero_tema: 1
        titulo_tema: "{title}"
        descripcion: "Has completado el estudio técnico y los protocolos de diagnosis de la unidad. Realiza el cuestionario oficial en Moodle para registrar tu calificación."

# Evaluación oficial desacoplada en formato Moodle XML (mod_quiz)
evaluacion_moodle:
  categoria: "FP Automoción - Evaluacion Oficial {title}"
  preguntas:
    - tipo: "multichoice"
      nombre: "P01_Caida_Tension_Maxima_Masa"
      enunciado: "¿Cuál es la caída de tensión máxima admisible en una línea de retorno a masa (Borne 31) de potencia medida bajo carga nominal?"
      opciones:
        - texto: "Menor o igual a 0.1 V entre el casquillo del consumidor y el borne negativo de la batería."
          correcta: true
          feedback: "¡Correcto! Una caída superior a 0.1 V en masa indica sulfatación o fijación floja en carrocería."
        - texto: "Entre 1.2 V y 2.5 V siempre que el fusible de protección de la línea no se haya fundido."
          correcta: false
          feedback: "Incorrecto. Esa caída de tensión restaría potencia crítica al actuador."
        - texto: "Exactamente 5.0 V estabilizados por el regulador interno de la unidad electrónica de control."
          correcta: false
          feedback: "Incorrecto. 5 V es la tensión de referencia de sensores, no la caída en masa."
        - texto: "Hasta un 25% de la tensión nominal de la batería con el motor térmico girando a ralentí."
          correcta: false
          feedback: "Incorrecto. Un 25% (3 V) inutilizaría el funcionamiento del consumidor."
      feedback_general: "En líneas de retorno a masa (Borne 31), la caída máxima admisible bajo carga es de 0.1 V."

    - tipo: "numerical"
      nombre: "P02_Calculo_Ley_Ohm"
      enunciado: "Por un conector con resistencia parásita de <strong>R = 0.2 Ω</strong> circula una corriente de <strong>I = 8 A</strong>. Calcula la caída de tensión (ΔV = I × R) en voltios:"
      valor: 1.6
      tolerancia: 0.05
      unidades: ["V", "voltios"]
      feedback: "¡Correcto! ΔV = 8 A × 0.2 Ω = 1.6 V."
      feedback_general: "Aplicando la Ley de Ohm: ΔV = I × R = 8 A × 0.2 Ω = 1.6 V."

    - tipo: "shortanswer"
      nombre: "P03_Borne_DIN_Masa"
      enunciado: "Según la norma DIN 72552, ¿cuál es el código numérico correspondiente al borne de retorno a masa del vehículo?"
      respuestas:
        - texto: "31"
          fraccion: 100
          feedback: "¡Correcto! El borne 31 designa la masa."
        - texto: "borne 31"
          fraccion: 100
          feedback: "¡Correcto!"
      feedback_general: "La norma DIN 72552 asigna el borne 31 a la masa del chasis."
"""

    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    # 2. Script Python ligero para compilar
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador del Curso: {title}
Lee automáticamente contenido_curso.yaml y compila tanto el paquete H5P como el banco Moodle XML.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PLANTILLA_DIR = os.path.join(PROJECT_ROOT, "plantilla")
sys.path.insert(0, PLANTILLA_DIR)

from yaml_course_builder import compilar_curso_desde_yaml

if __name__ == "__main__":
    yaml_file = os.path.join(SCRIPT_DIR, "contenido_curso.yaml")
    compilar_curso_desde_yaml(yaml_file, output_dir=SCRIPT_DIR)
'''

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"✅ Nuevo curso inicializado en: {target_dir}")
    print(f"   - Contenido pedagógico (YAML): {yaml_path}")
    print(f"   - Script compilador:           {script_path}")
    print(f"   - Carpeta de imágenes:         {images_dir}")
    print(f"   Ejecuta 'python3 build.py {clean_folder}' para compilarlo y certificarlo.")


def compilar_simuladores(target=None):
    """Compila simuladores HTML a paquetes H5P con incrustación segura para EducaMadrid."""
    if not os.path.exists(SIMULADOR_BUILDER):
        print(f"❌ Error: No se encontró el compilador de simuladores en {SIMULADOR_BUILDER}")
        sys.exit(1)

    if target:
        cmd = [sys.executable, SIMULADOR_BUILDER, target]
        ret = subprocess.call(cmd)
        if ret != 0:
            sys.exit(ret)
        return

    # Si no se especifica ruta, busca carpetas candidatas típicas
    candidatos = [
        os.path.join(ROOT_DIR, "simuladores"),
        os.path.join(ROOT_DIR, "Simuladores"),
        os.path.expanduser("~/simuladores"),
        os.path.expanduser("~/Simuladores"),
        "/mnt/chromeos/MyFiles/simuladores",
        "/mnt/chromeos/MyFiles/Simuladores",
    ]
    encontrada = None
    for cand in candidatos:
        if os.path.isdir(cand):
            encontrada = cand
            break

    if encontrada:
        print(f">>> Carpeta de simuladores localizada: {encontrada}")
        cmd = [sys.executable, SIMULADOR_BUILDER, encontrada]
        ret = subprocess.call(cmd)
        if ret != 0:
            sys.exit(ret)
    else:
        print("ℹ️ No se detectó ninguna carpeta 'simuladores/' local por defecto.")
        print("   Uso:")
        print("     python3 build.py simuladores <carpeta_con_htmls>")
        print("     python3 build.py simuladores <archivo_simulador.html>")
        print("")
        print("   Ejemplo:")
        print('     python3 build.py simuladores "UT0 simulador_osciloscopio_rigol.html"')


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
    for entry in descubrir_cursos_locales():
        full_dir = entry[1]
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
    elif sys.argv[1].lower() in ["simuladores", "simulador"]:
        target = sys.argv[2] if len(sys.argv) >= 3 else None
        compilar_simuladores(target)
    elif sys.argv[1].lower() in ["todos", "all"]:
        compilar_plantilla()
        for entry, _, _, _ in descubrir_cursos_locales():
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
