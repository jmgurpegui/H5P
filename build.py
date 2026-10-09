#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador Maestro de Cursos H5P para EducaMadrid y Moodle.
Ejecuta la compilación desde la plantilla modular:
- Separación de Contenidos (HTML) y Evaluación (Moodle XML)
- Formato InteractiveBook 1.7 + QuestionSet 1.20
- Compatible 100% con teléfonos móviles y tablets (progressType: textual)
- Sin opción de ver soluciones durante la realización del cuestionario

Uso:
    python3 build.py                                # Compila plantilla_curso_h5p/curso_config.json
    python3 build.py ruta/a/otro_curso_config.json  # Compila una configuración personalizada
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "plantilla_curso_h5p")

sys.path.insert(0, TEMPLATE_DIR)

from build_desde_plantilla import compilar_curso_desde_plantilla

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TEMPLATE_DIR, "curso_config.json")
    if not os.path.isfile(config_file):
        print(f"Error: No se encontró el archivo de configuración: {config_file}")
        sys.exit(1)

    compilar_curso_desde_plantilla(config_file)

if __name__ == "__main__":
    main()
