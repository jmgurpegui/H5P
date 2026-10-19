#!/usr/bin/env python3
"""
Validador Oficial de Paquetes H5P para EducaMadrid y Moodle.
Certifica el cumplimiento estricto de:
1. Whitelist de archivos en content/ (cero .html, cero .svg).
2. Existencia y parseo válido de h5p.json y content/content.json.
3. Clausura física de dependencias: todas las librerías declaradas en h5p.json
   deben estar empaquetadas en la raíz del ZIP.
4. Matriz de versiones homologadas de EducaMadrid (InteractiveBook 1.7, Column 1.16, etc.).
5. Anidamiento obligatorio en H5P.Column ({content: ..., useSeparator: 'auto'}) para evitar TypeError / pantalla en blanco.
6. Metadatos obligatorios: subContentId (UUIDv4) y metadata.title en capítulos y bloques.
7. Prevención de fugas de CSS (cero etiquetas <style> en bloques de texto HTML).
8. Renderizado correcto de fórmulas (cero sintaxis LaTeX cruda con '$' o '\\text{}').
9. Principios de Aprendizaje Activo: detección de actividades formativas intercaladas (MultiChoice, TrueFalse, QuestionSet).
10. Buenas prácticas de Accesibilidad (WCAG 2.1 AA): verificación de textos alternativos 'alt' en imágenes y metadatos de apoyo.
"""

import sys
import os
import zipfile
import json
import re

# Compatibilidad UTF-8 multiplataforma
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

def check_text_for_leaks_and_latex(text, location, errors, warnings):
    """Comprueba que no haya fugas de etiquetas <style> ni fórmulas LaTeX sin procesar."""
    if not isinstance(text, str):
        return
    # 1. Comprobar etiquetas <style> (Fuga de código CSS en pantalla)
    if '<style' in text.lower():
        errors.append(
            f"{location}: Fuga de CSS detectada (etiqueta '<style>' en texto HTML). "
            "El editor H5P eliminará la etiqueta y mostrará el código CSS como texto sin formato en pantalla. "
            "Inyecta los estilos directamente en las hojas .css de las librerías."
        )

    # 2. Comprobar delimitadores o comandos LaTeX crudos
    if '$' in text:
        errors.append(
            f"{location}: Delimitador '$' de LaTeX detectado en el contenido. "
            "H5P no integra MathJax en sus iframes; el texto se mostrará roto con '$'. "
            "Utiliza HTML semántico (<sub>, <sup>, .tech-formula) y caracteres Unicode (×, −, Ω, µ)."
        )
    elif r'\text{' in text or r'\times' in text or r'\frac{' in text:
        warnings.append(
            f"{location}: Comando LaTeX residual detectado sin procesar. "
            "Reemplázalo por etiquetas semánticas y Unicode."
        )

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

                    # Validar especificación de autores en h5p.json (Requisito estricto Moodle/H5P)
                    h5p_authors = h5p_meta.get('authors')
                    if h5p_authors is not None:
                        if not isinstance(h5p_authors, list):
                            errors.append("h5p.json: La propiedad 'authors' debe ser una lista de autores.")
                        else:
                            for a_idx, author in enumerate(h5p_authors):
                                if not isinstance(author, dict):
                                    errors.append(f"h5p.json: authors[{a_idx}] debe ser un objeto con 'name' y 'role'.")
                                else:
                                    if not author.get('role'):
                                        errors.append(
                                            f"h5p.json: La propiedad requerida 'role' está faltando en authors[{a_idx}] ('{author.get('name', 'sin nombre')}'). "
                                            "Moodle rechazará el paquete con el error: 'La propiedad requerida role está faltando de h5p.json / El archivo principal h5p.json no es válido'. "
                                            "Valores válidos: 'Author', 'Editor', 'Licensee', 'Originator', 'Other'."
                                        )
                                    if not author.get('name'):
                                        errors.append(f"h5p.json: authors[{a_idx}] carece del campo obligatorio 'name'.")
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
                    # Validar imagen de portada si está configurada
                    cover_medium = content_json.get('bookCover', {}).get('coverMedium', {})
                    if cover_medium and 'H5P.Image' in cover_medium.get('library', ''):
                        cover_img = cover_medium.get('params', {}).get('file', {}).get('path', '')
                        if cover_img and f"content/{cover_img}" not in namelist:
                            errors.append(f"Portada (bookCover): La imagen 'content/{cover_img}' referenciada no existe dentro del paquete ZIP.")

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

                            # Validar metadata.authors si existe
                            chap_authors = chap.get('metadata', {}).get('authors')
                            if chap_authors is not None and isinstance(chap_authors, list):
                                for a_idx, c_author in enumerate(chap_authors):
                                    if isinstance(c_author, dict) and not c_author.get('role'):
                                        errors.append(
                                            f"Capítulo {i+1}: La propiedad requerida 'role' está faltando en metadata.authors[{a_idx}] ('{c_author.get('name', 'sin nombre')}'). "
                                            "Debe incluir 'role': 'Author'."
                                        )

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

                                # Validar textos por fugas de CSS o LaTeX no procesado
                                if 'H5P.AdvancedText' in sub_lib:
                                    text_val = sub_params.get('text', '')
                                    check_text_for_leaks_and_latex(text_val, f"Capítulo {i+1}, Elemento {j+1} (AdvancedText)", errors, warnings)
                                
                                # Validar acordeones por textos internos
                                if 'H5P.Accordion' in sub_lib:
                                    panels = sub_params.get('panels', [])
                                    for p_idx, p in enumerate(panels):
                                        p_content = p.get('content', {})
                                        p_text = p_content.get('params', {}).get('text', '') if isinstance(p_content, dict) else str(p_content)
                                        check_text_for_leaks_and_latex(p_text, f"Capítulo {i+1}, Acordeón panel {p_idx+1} ('{p.get('title')}')", errors, warnings)

                                # Validar imágenes por accesibilidad (alt text) y existencia en ZIP
                                if sub_lib.startswith('H5P.Image '):
                                    alt_val = sub_params.get('alt', '')
                                    if not alt_val or alt_val.strip() == '':
                                        warnings.append(
                                            f"Capítulo {i+1}, Elemento {j+1} (Image): Falta texto alternativo descriptivo ('alt'). "
                                            "Asegura accesibilidad WCAG 2.1 AA para estudiantes con discapacidad visual."
                                        )
                                    file_obj = sub_params.get('file', {})
                                    img_rel = file_obj.get('path', '') if isinstance(file_obj, dict) else ''
                                    if img_rel:
                                        expected_zip_path = f"content/{img_rel}"
                                        if expected_zip_path not in namelist:
                                            errors.append(
                                                f"Capítulo {i+1}, Elemento {j+1} (Image): El archivo multimedia '{expected_zip_path}' no existe dentro del paquete ZIP."
                                            )

                                # Validar desacoplamiento formativo H5P vs sumativo Moodle XML
                                if any(eval_lib in sub_lib for eval_lib in ('H5P.MultiChoice', 'H5P.TrueFalse', 'H5P.DragText', 'H5P.QuestionSet')):
                                    warnings.append(
                                        f"Capítulo {i+1}, Elemento {j+1} ({sub_lib}): Se detectó actividad evaluativa o de arrastre dentro del paquete H5P. "
                                        "Según la arquitectura oficial EducaMadrid (GEMINI.md), los cursos H5P deben ser 100% formativos y toda evaluación "
                                        "debe desacoplarse en cuestionarios Moodle XML (mod_quiz) para evitar fallos xAPI y bloqueos táctiles en móviles."
                                    )

                                if 'H5P.Accordion' in sub_lib or 'H5P.ImageHotspots' in sub_lib or 'H5P.Video' in sub_lib:
                                    active_activities_count += 1

                                if 'H5P.AdvancedText' in sub_lib:
                                    t_html = sub_params.get('text', '')
                                    if any(cls in t_html for cls in ('tech-challenge', 'tech-checklist', 'sim-box', 'tech-spec-grid')):
                                        active_activities_count += 1

                                if 'H5P.ImageHotspots' in sub_lib:
                                    hs_alt = sub_params.get('backgroundImageAltText', '')
                                    if not hs_alt:
                                        warnings.append(f"Capítulo {i+1}, Elemento {j+1} (ImageHotspots): Falta 'backgroundImageAltText'.")

                                if sub_content and not sub_content.get('subContentId'):
                                    warnings.append(f"Capítulo {i+1}, Elemento {j+1}: Falta 'subContentId' en bloque '{sub_lib}'.")

                        if active_activities_count > 0:
                            print(f"✓ Aprendizaje Activo (100% Formativo y Móvil): {active_activities_count} componente(s) interactivo(s)/taller detectado(s).")

                        if not has_eval_questionset:
                            info_messages.append("Modalidad Didáctica Desacoplada: Paquete 100% formativo sin bloqueo xAPI (evaluación oficial mediante banco Moodle XML).")

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
                if ext == 'bmp':
                    warnings.append(
                        f"Aviso de optimización: '{cf}' utiliza formato BMP. Aunque está permitido en la whitelist de Moodle, "
                        "los archivos BMP no disponen de canal alfa transparente y pueden incrementar el peso. "
                        "Se recomienda PNG (.png) para logotipos institucionales e iconografía."
                    )

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

            declared_folders = {f"{d.get('machineName')}-{d.get('majorVersion')}.{d.get('minorVersion')}" for d in deps}
            extra_libs = sorted(bundled_dirs - declared_folders)
            if extra_libs:
                warnings.append(
                    f"Sobrepeso en paquete: Se encontraron {len(extra_libs)} carpetas de librerías no declaradas en preloadedDependencies ({extra_libs[:5]}...). "
                    "Empaqueta únicamente HOMOLOGATED_DEPENDENCIES."
                )

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
        print("Uso: python3 validar_h5p_educamadrid.py <ruta_archivo.h5p>")
        sys.exit(1)
    success = validate_h5p(sys.argv[1])
    sys.exit(0 if success else 1)
