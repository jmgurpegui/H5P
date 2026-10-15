#!/usr/bin/env python3
"""
Añade o actualiza las reglas CSS oficiales accesibles de EducaMadrid
en las hojas de estilo de las librerías base (H5P.InteractiveBook y H5P.Column).
Garantiza codificación UTF-8 y previene duplicaciones.
"""
import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PLANTILLA_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PLANTILLA_DIR)
LIB_DIR = os.path.join(BASE_DIR, 'h5p_builder', 'h5p-libraries')
CSS_FILE = os.path.join(PLANTILLA_DIR, 'estilos_educamadrid.css')

MARKER_START = "/* === EDUCAMADRID RESPONSIVE THEME START === */"
MARKER_END = "/* === EDUCAMADRID RESPONSIVE THEME END === */"

with open(CSS_FILE, 'r', encoding='utf-8') as f:
    css_rules = f.read().strip()

injected_block = f"\n\n{MARKER_START}\n{css_rules}\n{MARKER_END}\n"

target_paths = [
    os.path.join(LIB_DIR, 'H5P.InteractiveBook-1.7', 'dist', 'h5p-interactive-book.css'),
    os.path.join(LIB_DIR, 'H5P.Column-1.16', 'styles', 'h5p-column.css')
]

for p in target_paths:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Limpiar cualquier inyección previa de versiones anteriores de forma segura
        if MARKER_START in content:
            parts = content.split(MARKER_START)
            clean_content = parts[0].rstrip()
            if MARKER_END in parts[1]:
                clean_content += parts[1].split(MARKER_END)[1].rstrip()
        elif '/* === EDUCAMADRID' in content:
            clean_content = content.split('/* === EDUCAMADRID')[0].rstrip()
        else:
            clean_content = content.rstrip()

        # Guardar contenido base intacto + nuevo bloque responsive inyectado
        new_content = clean_content + injected_block
        with open(p, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✓ CSS oficial accesible inyectado limpiamente en: {p}")
    else:
        print(f"⚠️ Archivo no encontrado: {p}")
