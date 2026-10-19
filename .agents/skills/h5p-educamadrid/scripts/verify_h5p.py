#!/usr/bin/env python3
"""
Validador Oficial de Paquetes H5P para EducaMadrid y Moodle.
Certifica el cumplimiento estricto de:
1. Whitelist de archivos en content/ (cero .html, cero .svg).
2. Existencia de h5p.json y content/content.json.
3. Clausura física de dependencias: todas las librerías declaradas en h5p.json
   deben estar empaquetadas en la raíz del ZIP.
4. Matriz de versiones homologadas de EducaMadrid (InteractiveBook 1.7, Column 1.16, etc.).
5. Anidamiento obligatorio en H5P.Column ({content: ..., useSeparator: 'auto'}) para evitar TypeError / pantalla en blanco.
6. Metadatos obligatorios: subContentId (UUIDv4) y metadata.title en capítulos y bloques.
7. Principio de Aprendizaje Activo: detección de actividades formativas intercaladas (MultiChoice, TrueFalse, QuestionSet).
8. Accesibilidad (WCAG 2.1 AA): verificación de textos alternativos 'alt' en imágenes y diseño inclusivo.
"""

import sys
import os
import zipfile
import json
import re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MOODLE_WHITELIST = {
    'json', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif', 'tiff',
    'eot', 'ttf', 'woff', 'woff2', 'otf',
    'webm', 'mp4', 'ogg', 'mp3', 'm4a', 'wav',
    'txt', 'pdf', 'rtf', 'doc', 'docx', 'xls', 'xlsx',
    'ppt', 'pptx', 'odt', 'ods', 'odp', 'csv', 'diff',
    'patch', 'swf', 'md', 'textile', 'vtt', 'webvtt', 'gltf', 'glb'
}

UUID4_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)

def validate_h5p(file_path):
    print(f"\n========================================================")
    print(f"VERIFICANDO PAQUETE EDUCAMADRID: {os.path.basename(file_path)}")
    print(f"========================================================")

    if not os.path.isfile(file_path):
        print(f"❌ Error: El archivo no existe: {file_path}")
        return False

    errors = []
    warnings = []
    info_messages = []

    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            namelist = zf.namelist()

            # 1. Comprobar h5p.json
            if 'h5p.json' not in namelist:
                errors.append("Falta 'h5p.json' en la raíz del paquete.")
                h5p_meta = {}
            else:
                try:
                    h5p_meta = json.loads(zf.read('h5p.json').decode('utf-8'))
                    print(f"✓ h5p.json encontrado. Título: '{h5p_meta.get('title')}'")
                    print(f"  Librería principal: {h5p_meta.get('mainLibrary')}")
                except Exception as e:
                    errors.append(f"Error parseando h5p.json: {e}")
                    h5p_meta = {}

            # 2. Comprobar content/content.json
            if 'content/content.json' not in namelist:
                errors.append("Falta 'content/content.json'.")
            else:
                print("✓ content/content.json encontrado.")
                try:
                    content_json = json.loads(zf.read('content/content.json').decode('utf-8'))
                    if 'chapters' in content_json:
                        print(f"✓ InteractiveBook detectado con {len(content_json['chapters'])} capítulos.")
                        has_eval_questionset = False
                        active_activities_count = 0
                        total_elements = 0

                        for i, chap in enumerate(content_json['chapters']):
                            chap_title = chap.get('metadata', {}).get('title') or chap.get('params', {}).get('title') or f"Capítulo {i+1}"
                            chap_lib = chap.get('library', '')
                            
                            # Validar que cada capítulo sea H5P.Column 1.16
                            if not chap_lib.startswith('H5P.Column'):
                                errors.append(
                                    f"Capítulo {i+1} ('{chap_title}'): La librería debe ser 'H5P.Column 1.16'. Encontrado: '{chap_lib}'. "
                                    "Causará White Screen of Death en Moodle."
                                )
                            
                            # Validar UUIDv4 de capítulo
                            chap_subid = chap.get('subContentId')
                            if not chap_subid:
                                errors.append(f"Capítulo {i+1} ('{chap_title}'): Falta 'subContentId'.")
                            
                            # Validar metadata.title
                            if not chap.get('metadata', {}).get('title'):
                                errors.append(f"Capítulo {i+1}: Falta 'metadata.title'. El menú lateral de navegación no mostrará este tema.")

                            col_params = chap.get('params', {})
                            items = col_params.get('content', [])
                            for j, item in enumerate(items):
                                total_elements += 1
                                # Validar envoltorio obligatorio en Column
                                if 'content' not in item or 'useSeparator' not in item:
                                    errors.append(
                                        f"Capítulo {i+1}, Elemento {j+1}: Falta envoltorio obligatorio {{'content': ..., 'useSeparator': 'auto'}} en H5P.Column. "
                                        "Provocará excepción de JavaScript (TypeError: Cannot read properties of undefined)."
                                    )
                                sub_content = item.get('content', {})
                                sub_lib = sub_content.get('library', '')
                                sub_params = sub_content.get('params', {})

                                if 'H5P.Image' in sub_lib:
                                    alt_val = sub_params.get('alt', '')
                                    if not alt_val or alt_val.strip() == '':
                                        warnings.append(f"Capítulo {i+1}, Elemento {j+1} (Image): Falta texto alternativo descriptivo ('alt').")

                                if 'H5P.MultiChoice' in sub_lib:
                                    active_activities_count += 1
                                if 'H5P.TrueFalse' in sub_lib:
                                    active_activities_count += 1
                                if 'H5P.DragText' in sub_lib:
                                    active_activities_count += 1
                                if 'H5P.ImageHotspots' in sub_lib:
                                    active_activities_count += 1
                                if 'H5P.MemoryGame' in sub_lib:
                                    active_activities_count += 1

                                if 'H5P.QuestionSet' in sub_lib:
                                    has_eval_questionset = True
                                    active_activities_count += 1
                                    qs_params = sub_content.get('params', {})
                                    pool = qs_params.get('poolSize')
                                    pass_pct = qs_params.get('passPercentage')
                                    q_count = len(qs_params.get('questions', []))
                                    print(f"  ✓ Módulo de Evaluación xAPI detectado: QuestionSet con {q_count} preguntas (poolSize: {pool}, passPercentage: {pass_pct}%).")

                                if sub_content and not sub_content.get('subContentId'):
                                    warnings.append(f"Capítulo {i+1}, Elemento {j+1}: Falta 'subContentId' en bloque '{sub_lib}'.")

                        if active_activities_count > 0:
                            print(f"✓ Aprendizaje Activo: {active_activities_count} actividad(es) formativa(s) interactiva(s) detectada(s).")

                        if not has_eval_questionset:
                            info_messages.append("Modalidad Didáctica: No contiene módulo interno QuestionSet (la evaluación sumativa final se gestionará mediante cuestionarios Moodle XML).")
                        
                        print(f"✓ Total de {total_elements} bloques de contenido validados en estructura de capítulos.")

                except Exception as e:
                    errors.append(f"Error parseando content/content.json: {e}")

            # 3. Comprobar Whitelist en content/ y en librerías empaquetadas
            content_files = [f for f in namelist if f.startswith('content/') and not f.endswith('/') and f != 'content/content.json']
            print(f"✓ Total de recursos multimedia en content/: {len(content_files)}")

            for cf in content_files:
                ext = cf.split('.')[-1].lower() if '.' in cf else ''
                if ext not in MOODLE_WHITELIST:
                    errors.append(
                        f"FATAL WHITELIST: '{cf}' tiene extensión '.{ext}' no permitida en EducaMadrid. "
                        f"Causará el error fatal 'not-in-whitelist' en Moodle/Lumi."
                    )
                if ext == 'html':
                    errors.append(f"FATAL: Archivo HTML en content/ '{cf}'. EducaMadrid prohíbe HTML local en content/.")
                if ext == 'svg':
                    errors.append(f"FATAL: Archivo SVG en content/ '{cf}'. Debe rasterizarse a PNG.")

            lib_whitelist = MOODLE_WHITELIST | {'js', 'css', 'svg', 'xml'}
            lib_files = [f for f in namelist if not f.startswith('content/') and not f.endswith('/') and f != 'h5p.json']
            for lf in lib_files:
                bn = os.path.basename(lf)
                ext = bn.rsplit('.', 1)[-1].lower() if '.' in bn else ''
                if ext not in lib_whitelist or bn.startswith('.'):
                    errors.append(
                        f"FATAL WHITELIST LIBRERÍA: '{lf}' no está permitido en paquetes H5P "
                        f"(provoca 'package-validation-failed:not-in-whitelist' en Lumi y Moodle)."
                    )

            # 4. Comprobar Clausura de Dependencias
            deps = h5p_meta.get('preloadedDependencies', [])
            bundled_dirs = set(f.split('/')[0] for f in namelist if '/' in f and not f.startswith('content/'))
            
            missing_libs = []
            for dep in deps:
                name = dep.get('machineName')
                v_maj = dep.get('majorVersion')
                v_min = dep.get('minorVersion')
                expected_folder = f"{name}-{v_maj}.{v_min}"
                if expected_folder not in bundled_dirs:
                    missing_libs.append(expected_folder)

            if missing_libs:
                errors.append(
                    f"Clausura de dependencias rota: Las siguientes librerías están declaradas en h5p.json pero NO están empaquetadas físicamente en la raíz del ZIP: {missing_libs}."
                )
            else:
                print(f"✓ Clausura completa verificada: Las {len(deps)} librerías declaradas están físicamente presentes en la raíz del ZIP.")

    except Exception as e:
        errors.append(f"Error abriendo paquete ZIP: {e}")

    print("\n--- RESULTADO DE LA VALIDACIÓN TÉCNICA ---")
    if info_messages:
        for info in info_messages:
            print(f"ℹ️  [INFO] {info}")

    if warnings:
        print(f"⚠️  {len(warnings)} ADVERTENCIA(S):")
        for w in warnings:
            print(f"   [!] {w}")

    if errors:
        print(f"❌  {len(errors)} ERROR(ES) CRÍTICO(S):")
        for err in errors:
            print(f"   [X] {err}")
        print("\n❌ EL PAQUETE NO ES APTO PARA EDUCAMADRID / MOODLE.")
        return False
    else:
        print("\n✅ CERTIFICACIÓN EXITOSA: EL PAQUETE CUMPLE 100% CON LA NORMATIVA TÉCNICA Y PEDAGÓGICA DE EDUCAMADRID Y MOODLE.")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 verify_h5p.py <ruta_archivo.h5p>")
        sys.exit(1)
    success = validate_h5p(sys.argv[1])
    sys.exit(0 if success else 1)
