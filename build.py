#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador y Validador Maestro de Cursos H5P y Evaluación Moodle XML para EducaMadrid.
Proporciona acceso unificado a los generadores certificados, temas responsive y validadores.

Uso:
    python3 build.py                     # Compila y valida el curso modelo H5P y su banco Moodle XML
    python3 build.py esquemas            # Compila y valida el curso de Esquemas Eléctricos y su XML
    python3 build.py todos               # Compila y valida todos los cursos del repositorio
    python3 build.py xml                 # Valida todos los bancos de preguntas Moodle XML
    python3 build.py css                 # Inyecta limpiamente los estilos responsive en librerías base
    python3 build.py validar <pkg.h5p>   # Valida un paquete H5P según normativa EducaMadrid
    python3 build.py validar <banco.xml> # Valida un banco Moodle XML oficial
"""

import os
import sys
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTILLA_DIR = os.path.join(ROOT_DIR, "plantilla")
ESQUEMAS_DIR = os.path.join(ROOT_DIR, "EsquemasElectricosAutomocion")
ALUMBRADO_DIR = os.path.join(ROOT_DIR, "CircuitosAlumbrado")
VALIDADOR_H5P = os.path.join(PLANTILLA_DIR, "validar_h5p_educamadrid.py")
VALIDADOR_XML = os.path.join(PLANTILLA_DIR, "moodle_xml_builder.py")
INJECT_CSS = os.path.join(PLANTILLA_DIR, "append_css_to_libraries.py")

def compilar_plantilla():
    print("=" * 60)
    print(">>> Compilando Curso Modelo y Banco Moodle XML (Plantilla)...")
    print("=" * 60)
    script = os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py")
    ret = subprocess.call([sys.executable, script])
    if ret != 0:
        sys.exit(ret)

def compilar_esquemas():
    print("=" * 60)
    print(">>> Compilando Curso y Banco Moodle XML: Esquemas Eléctricos...")
    print("=" * 60)
    script = os.path.join(ESQUEMAS_DIR, "generar_curso_esquemas.py")
    ret = subprocess.call([sys.executable, script])
    if ret != 0:
        sys.exit(ret)

def compilar_alumbrado():
    print("=" * 60)
    print(">>> Compilando Curso y Banco Moodle XML: Circuitos de Alumbrado...")
    print("=" * 60)
    script = os.path.join(ALUMBRADO_DIR, "generar_curso_alumbrado.py")
    ret = subprocess.call([sys.executable, script])
    if ret != 0:
        sys.exit(ret)

def inyectar_css():
    print("=" * 60)
    print(">>> Inyectando estilos responsive oficiales en librerías base...")
    print("=" * 60)
    ret = subprocess.call([sys.executable, INJECT_CSS])
    if ret != 0:
        sys.exit(ret)

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
    xml_files = [
        os.path.join(PLANTILLA_DIR, "evaluacion_modelo_moodle.xml"),
        os.path.join(ESQUEMAS_DIR, "evaluacion_esquemas_electricos.xml"),
        os.path.join(ALUMBRADO_DIR, "evaluacion_circuitos_alumbrado.xml")
    ]
    for xf in xml_files:
        if os.path.exists(xf):
            validar_banco_xml(xf)
            print("")

def main():
    if len(sys.argv) == 1:
        compilar_plantilla()
    elif sys.argv[1].lower() in ["plantilla", "modelo"]:
        compilar_plantilla()
    elif sys.argv[1].lower() in ["esquemas", "automocion"]:
        compilar_esquemas()
    elif sys.argv[1].lower() in ["alumbrado", "luces", "iluminacion"]:
        compilar_alumbrado()
    elif sys.argv[1].lower() in ["todos", "all"]:
        compilar_plantilla()
        print("\n")
        compilar_esquemas()
        print("\n")
        compilar_alumbrado()
    elif sys.argv[1].lower() in ["xml", "evaluacion"]:
        validar_todos_xml()
    elif sys.argv[1].lower() in ["css", "estilos"]:
        inyectar_css()
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
        print(f"Opción no reconocida: {sys.argv[1]}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
