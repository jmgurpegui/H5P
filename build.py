#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador y Validador Maestro de Cursos H5P para EducaMadrid y Moodle.
Proporciona acceso unificado a los generadores certificados y al validador oficial.

Uso:
    python3 build.py                     # Compila y valida el curso modelo de la plantilla oficial
    python3 build.py esquemas            # Compila y valida el curso de Interpretación de Esquemas Eléctricos
    python3 build.py validar <pkg.h5p>   # Valida cualquier paquete H5P según normativa EducaMadrid
"""

import os
import sys
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PLANTILLA_DIR = os.path.join(ROOT_DIR, "plantilla")
ESQUEMAS_DIR = os.path.join(ROOT_DIR, "EsquemasElectricosAutomocion")
VALIDADOR = os.path.join(PLANTILLA_DIR, "validar_h5p_educamadrid.py")

def compilar_plantilla():
    print("=" * 60)
    print(">>> Compilando Curso Modelo desde plantilla...")
    print("=" * 60)
    script = os.path.join(PLANTILLA_DIR, "generar_curso_plantilla.py")
    ret = subprocess.call([sys.executable, script])
    if ret != 0:
        sys.exit(ret)

def compilar_esquemas():
    print("=" * 60)
    print(">>> Compilando Curso: Esquemas Eléctricos de Automoción...")
    print("=" * 60)
    script = os.path.join(ESQUEMAS_DIR, "generar_curso_esquemas.py")
    ret = subprocess.call([sys.executable, script])
    if ret != 0:
        sys.exit(ret)

def validar_paquete(paquete_path):
    print("=" * 60)
    print(f">>> Validando paquete H5P: {paquete_path}")
    print("=" * 60)
    ret = subprocess.call([sys.executable, VALIDADOR, paquete_path])
    if ret != 0:
        sys.exit(ret)

def main():
    if len(sys.argv) == 1:
        compilar_plantilla()
    elif sys.argv[1].lower() in ["plantilla", "modelo"]:
        compilar_plantilla()
    elif sys.argv[1].lower() in ["esquemas", "automocion"]:
        compilar_esquemas()
    elif sys.argv[1].lower() in ["todos", "all"]:
        compilar_plantilla()
        print("\n")
        compilar_esquemas()
    elif sys.argv[1].lower() in ["validar", "valida", "check"]:
        if len(sys.argv) < 3:
            print("Uso: python3 build.py validar <ruta_al_paquete.h5p>")
            sys.exit(1)
        validar_paquete(sys.argv[2])
    elif sys.argv[1].endswith(".h5p"):
        validar_paquete(sys.argv[1])
    else:
        print(f"Opción no reconocida: {sys.argv[1]}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
