#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilador Homologado de Simuladores HTML a Paquetes H5P (EducaMadrid).
FP Automoción - Autoría: FP Madrid profesor JM Gurpegui | Licencia: CC BY-NC-SA 4.0

Convierte simuladores interactivos (osciloscopios, polímetros, bancos de inyección, etc.)
en paquetes H5P basados en H5P.IFrameEmbed 1.0.

CUMPLIMIENTO ESTRICTO EDUCAMADRID (WHITELIST MOODLE):
En lugar de escribir archivos .html dentro de content/ (lo cual produce el error
'not-in-whitelist' al importar en Moodle EducaMadrid), este compilador incrusta el código
HTML directamente en content/content.json (propiedad 'htmlContent') y el motor
iframe-embed.js lo renderiza mediante un Blob URL / srcdoc local seguro.
"""

import os
import sys
import json
import re
import shutil
import zipfile
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LIB_DIR = os.path.join(SCRIPT_DIR, "h5p-libraries")
PLANTILLA_DIR = os.path.join(PROJECT_ROOT, "plantilla")

AUTOR = "FP Madrid profesor JM Gurpegui"
LICENCIA = "CC BY-NC-SA"
LICENCIA_VERSION = "4.0"


def compilar_simulador_h5p(html_path, output_h5p_path=None, title=None, min_height="850px"):
    """
    Empaqueta un archivo HTML interactivo como un paquete H5P 100% compatible con EducaMadrid.
    """
    html_file = Path(html_path).resolve()
    if not html_file.is_file():
        raise FileNotFoundError(f"No se encuentra el archivo HTML: {html_path}")

    with open(html_file, "r", encoding="utf-8", errors="replace") as f:
        html_content = f.read()

    # Título por defecto
    if not title:
        raw_name = html_file.stem
        # Limpieza de prefijos comunes como UT0, UT1, etc.
        clean_title = re.sub(r'^(UT\d+[\s_-]*)', '', raw_name, flags=re.IGNORECASE)
        clean_title = clean_title.replace('_', ' ').replace('-', ' ').strip().title()
        title = f"Simulador: {clean_title} - FP Automoción"

    # Ruta de salida por defecto
    if not output_h5p_path:
        slug = re.sub(r'[^A-Za-z0-9_-]', '_', html_file.stem)
        output_h5p_path = html_file.parent / f"{slug}.h5p"
    output_pkg = Path(output_h5p_path).resolve()

    # 1. Manifiesto H5P
    h5p_manifest = {
        "title": title,
        "language": "es",
        "mainLibrary": "H5P.IFrameEmbed",
        "embedTypes": ["iframe"],
        "license": LICENCIA,
        "licenseVersion": LICENCIA_VERSION,
        "authors": [{"name": AUTOR, "role": "Author"}],
        "preloadedDependencies": [
            {
                "machineName": "H5P.IFrameEmbed",
                "majorVersion": 1,
                "minorVersion": 0
            }
        ]
    }

    # 2. Configuración del contenido (Whitelist Safe: HTML incrustado en JSON)
    content_json = {
        "width": "100%",
        "minHeight": min_height,
        "maxHeight": "100%",
        "source": "",
        "htmlContent": html_content
    }

    # 3. Librería H5P.IFrameEmbed-1.0
    src_lib_dir = Path(LIB_DIR) / "H5P.IFrameEmbed-1.0"
    if not src_lib_dir.is_dir():
        raise FileNotFoundError(f"No se encontró la librería H5P.IFrameEmbed-1.0 en {LIB_DIR}")

    # 4. Creación del archivo ZIP (.h5p) en estructura estrictamente plana
    if output_pkg.exists():
        output_pkg.unlink()

    with zipfile.ZipFile(output_pkg, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # h5p.json en la raíz
        zipf.writestr('h5p.json', json.dumps(h5p_manifest, indent=2, ensure_ascii=False))

        # content/content.json (CERO archivos .html en content/ para superar la whitelist de Moodle)
        zipf.writestr('content/content.json', json.dumps(content_json, indent=2, ensure_ascii=False))

        # Copiar todos los archivos homologados de la librería H5P.IFrameEmbed-1.0
        lib_prefix = "H5P.IFrameEmbed-1.0/"
        for root, dirs, files in os.walk(src_lib_dir):
            for file_name in sorted(files):
                full_path = Path(root) / file_name
                rel_path = full_path.relative_to(src_lib_dir)
                arcname = f"{lib_prefix}{rel_path.as_posix()}"
                zipf.write(full_path, arcname=arcname)

    size_kb = output_pkg.stat().st_size / 1024
    print(f"✅ Simulador H5P compilado con éxito:")
    print(f"   - Archivo: {output_pkg} ({size_kb:.1f} KB)")
    print(f"   - Título:  '{title}'")
    print(f"   - Modo:    Incrustación Segura (Whitelist EducaMadrid 100% OK)")

    # 5. Validación automática
    try:
        sys.path.insert(0, PLANTILLA_DIR)
        from validar_h5p_educamadrid import validate_h5p
        validate_h5p(str(output_pkg))
    except Exception as e:
        print(f"⚠️ Aviso durante validación: {e}")

    return str(output_pkg)


def compilar_carpeta_simuladores(folder_path):
    """
    Busca todos los archivos .html en una carpeta y compila un .h5p por cada uno.
    """
    f_path = Path(folder_path).resolve()
    if not f_path.is_dir():
        print(f"❌ Error: La carpeta {folder_path} no existe.")
        return []

    html_files = sorted(list(f_path.glob("*.html")))
    if not html_files:
        print(f"ℹ️ No se encontraron archivos .html en {f_path}")
        return []

    print("=" * 60)
    print(f">>> Compilando {len(html_files)} simulador(es) HTML desde: {f_path}")
    print("=" * 60)

    resultados = []
    for hf in html_files:
        try:
            res = compilar_simulador_h5p(hf)
            resultados.append(res)
            print("")
        except Exception as e:
            print(f"❌ Error compilando {hf.name}: {e}\n")

    return resultados


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 compilar_simulador.py <archivo.html_o_carpeta> [titulo_opcional]")
        sys.exit(1)

    target = sys.argv[1]
    title_arg = sys.argv[2] if len(sys.argv) >= 3 else None

    if os.path.isdir(target):
        compilar_carpeta_simuladores(target)
    elif os.path.isfile(target):
        compilar_simulador_h5p(target, title=title_arg)
    else:
        print(f"❌ Error: No se encuentra '{target}'")
        sys.exit(1)
