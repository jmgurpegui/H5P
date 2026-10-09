#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades y Helpers Oficiales para Generación de Contenidos H5P.
Compatible al 100% con EducaMadrid y Moodle:
- mainLibrary: H5P.InteractiveBook 1.7 / H5P.QuestionSet 1.20
- Cumplimiento estricto de la Whitelist de extensiones de Moodle en content/
- Cero textos claros (garantía de alto contraste #0f172a / #14532d / #991b1b)
- Máxima compatibilidad móvil/tablet: progressType "textual", sin botones de solución
"""

import os
import re
import json
import uuid
import struct
import shutil
import zipfile

# Whitelist oficial de Moodle para la carpeta content/
MOODLE_CONTENT_WHITELIST = {
    'json', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif', 'tiff', 'eot', 'ttf', 'woff',
    'woff2', 'otf', 'webm', 'mp4', 'ogg', 'mp3', 'm4a', 'wav', 'txt', 'pdf', 'rtf',
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'csv', 'diff',
    'patch', 'swf', 'md', 'textile', 'vtt', 'webvtt', 'gltf', 'glb'
}

# Mapeo oficial de librerías instaladas
LIBS_MAP = {
    'FontAwesome': ('font-awesome', 'FontAwesome-4.5'),
    'H5P.JoubelUI': ('h5p-joubel-ui', 'H5P.JoubelUI-1.3'),
    'H5P.FontIcons': ('h5p-font-icons', 'H5P.FontIcons-1.0'),
    'H5P.Transition': ('h5p-transition', 'H5P.Transition-1.0'),
    'H5P.Question': ('h5p-question', 'H5P.Question-1.5'),
    'H5P.MultiChoice': ('h5p-multi-choice', 'H5P.MultiChoice-1.16'),
    'H5P.QuestionSet': ('H5P.QuestionSet-1.20', 'H5P.QuestionSet-1.20'),
    'H5P.Accordion': ('h5p-accordion', 'H5P.Accordion-1.0'),
    'H5P.AdvancedText': ('h5p-advanced-text', 'H5P.AdvancedText-1.1'),
    'H5P.Column': ('H5P.Column-1.16', 'H5P.Column-1.16'),
    'H5P.Image': ('h5p-image', 'H5P.Image-1.1'),
    'H5P.InteractiveBook': ('H5P.InteractiveBook-1.7', 'H5P.InteractiveBook-1.7'),
    'jQuery.ui': ('jquery-ui', 'jQuery.ui-1.10'),
    'H5P.TrueFalse': ('h5p-true-false', 'H5P.TrueFalse-1.8'),
    'H5P.Video': ('h5p-video', 'H5P.Video-1.6'),
    'H5P.Components': ('H5P.Components-1.0', 'H5P.Components-1.0')
}

def get_image_info(path):
    """Obtiene ancho, alto y mime-type para una imagen PNG, JPEG o BMP."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
            ext = os.path.splitext(path)[1].lower()
            if ext == '.png':
                mime = 'image/png'
            elif ext in ('.jpg', '.jpeg'):
                mime = 'image/jpeg'
            elif ext == '.bmp':
                mime = 'image/bmp'
            else:
                mime = 'image/png'
            return w, h, mime
    except Exception:
        pass
    return 1600, 950, 'image/png'

def copy_library_to_zip(zf, lib_source_path, target_prefix):
    """Copia archivos de librería al paquete ZIP omitiendo archivos de desarrollo."""
    ignore_names = {'.git', '.github', '.gitignore', 'package.json', 'package-lock.json',
                    'crowdin.yml', '.eslintrc.json', '.sass-lint.yml', '.h5pignore',
                    'webpack.config.js', 'README.md'}
    for root, dirs, files in os.walk(lib_source_path):
        dirs[:] = [d for d in dirs if d not in ('.git', '.github', 'node_modules', 'temp')]
        rel_root = os.path.relpath(root, lib_source_path)
        for file in files:
            if file in ignore_names or file.startswith('.'):
                continue
            src_file = os.path.join(root, file)
            if rel_root == '.':
                arcname = f"{target_prefix}/{file}"
            else:
                arcname = f"{target_prefix}/{rel_root}/{file}"
            zf.write(src_file, arcname)

def validate_moodle_whitelist(h5p_path):
    """Verifica estrictamente que ningún archivo en content/ incumpla la whitelist de extensiones de Moodle."""
    with zipfile.ZipFile(h5p_path, 'r') as zf:
        for name in zf.namelist():
            if name.startswith('content/') and not name.endswith('/'):
                ext = name.split('.')[-1].lower() if '.' in name else ''
                if ext not in MOODLE_CONTENT_WHITELIST:
                    raise ValueError(
                        f"ERROR GRAVE DE WHITELIST EN MOODLE: El archivo '{name}' en '{os.path.basename(h5p_path)}' "
                        f"tiene extensión '.{ext}' prohibida en content/!"
                    )
    print(f"✓ Whitelist de Moodle superada con éxito en {os.path.basename(h5p_path)} (0 archivos no permitidos).")

def wrap_column_item(runnable_item, default_title="Elemento interactivo"):
    """
    Envuelve un elemento ejecutable en la estructura requerida por H5P.Column 1.16:
    {"content": {...}, "useSeparator": "auto"}.
    Garantiza además subContentId y metadata.title exigidos por H5P.InteractiveBook.
    """
    if "content" in runnable_item and "useSeparator" in runnable_item:
        inner = runnable_item["content"]
    else:
        inner = runnable_item

    if "subContentId" not in inner or not inner["subContentId"]:
        inner["subContentId"] = str(uuid.uuid4())

    if "metadata" not in inner or not inner["metadata"] or not inner["metadata"].get("title"):
        inner["metadata"] = {"title": default_title}

    return {
        "content": inner,
        "useSeparator": "auto"
    }

def create_accordion(panels):
    """Genera un componente H5P.Accordion 1.0 con paneles desplegables."""
    h5p_panels = []
    for title, html_body in panels:
        h5p_panels.append({
            "title": title,
            "content": {
                "library": "H5P.AdvancedText 1.1",
                "params": {
                    "text": html_body
                },
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "title": title
                }
            }
        })
    return {
        "library": "H5P.Accordion 1.0",
        "params": {
            "panels": h5p_panels,
            "hTag": "h3"
        },
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": "Protocolos Técnicos y Procedimientos"
        }
    }

def create_true_false_check(question_text, is_true, feedback):
    """Crea una comprobación formativa True/False."""
    return {
        "library": "H5P.TrueFalse 1.8",
        "params": {
            "question": f"<p style='font-weight: 600; font-size: 1.05em; color: #0f172a; line-height: 1.5;'>{question_text}</p>",
            "correct": "true" if is_true else "false",
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": False,
                "enableCheckButton": True,
                "confirmCheckDialog": False,
                "confirmRetryDialog": False,
                "autoCheck": False
            },
            "l10n": {
                "trueText": "Verdadero",
                "falseText": "Falso",
                "score": "Puntuación: @score de @total puntos",
                "checkAnswer": "Comprobar respuesta",
                "showSolutionButton": "",
                "tryAgain": "Reintentar",
                "wrongAnswerMessage": f"<span style='color: #991b1b; font-weight: bold;'>✗ Incorrecto.</span> {feedback}",
                "correctAnswerMessage": f"<span style='color: #14532d; font-weight: bold;'>✓ ¡Correcto!</span> {feedback}",
                "scoreBarLabel": "Has obtenido :num de :total puntos"
            }
        },
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": f"Autocomprobación: {question_text[:40]}"
        }
    }

def create_multi_choice_check(question_text, options, correct_idx, feedback):
    """Crea una comprobación formativa MultiChoice."""
    answers = []
    for i, opt in enumerate(options):
        is_corr = (i == correct_idx)
        answers.append({
            "text": f"<div style='color: #0f172a; line-height: 1.45;'>{opt}</div>",
            "correct": is_corr,
            "tipsAndFeedback": {
                "tip": "",
                "chosenFeedback": (
                    f"<div style='font-family: inherit; font-size: 0.95em; color: {'#14532d' if is_corr else '#991b1b'};'>"
                    f"<strong>{'✓ ¡Respuesta Correcta!' if is_corr else '✗ Respuesta Incorrecta.'}</strong><br/>{feedback}</div>"
                ),
                "notChosenFeedback": ""
            }
        })
    return {
        "library": "H5P.MultiChoice 1.16",
        "params": {
            "question": f"<p style='font-weight: 600; font-size: 1.05em; color: #0f172a; margin-bottom: 0.75rem; line-height: 1.5;'>{question_text}</p>",
            "answers": answers,
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": False,
                "enableCheckButton": True,
                "type": "auto",
                "singlePoint": True,
                "randomAnswers": True,
                "showSolutionsRequiresInput": True
            },
            "UI": {
                "checkAnswerButton": "Comprobar respuesta",
                "submitAnswerButton": "Enviar respuesta",
                "showSolutionButton": "",
                "tryAgainButton": "Reintentar",
                "tipsLabel": "Pista",
                "scoreBarLabel": ":num de :total puntos"
            }
        },
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": f"Autoevaluación: {question_text[:40]}"
        }
    }

def create_video_component(title, youtube_url, poster_img_path=None):
    """Crea un componente oficial H5P.Video 1.6 con reproductor YouTube."""
    return {
        "library": "H5P.Video 1.6",
        "params": {
            "sources": [
                {
                    "path": youtube_url,
                    "mime": "video/YouTube"
                }
            ],
            "visuals": {
                "fit": True,
                "controls": True
            },
            "playback": {
                "autoplay": False,
                "loop": False
            },
            "l10n": {
                "name": "Vídeo Pedagógico",
                "loading": "Cargando reproductor de vídeo...",
                "noPlayers": "No se encontró ningún reproductor de vídeo compatible.",
                "noSources": "No hay fuentes de vídeo disponibles.",
                "aborted": "Reproducción abortada.",
                "networkFailure": "Fallo de red en la carga del vídeo.",
                "cannotDecode": "No se puede descodificar el medio.",
                "formatNotSupported": "Formato de vídeo no admitido.",
                "unknownError": "Error desconocido en el reproductor."
            }
        },
        "subContentId": str(uuid.uuid4()),
        "metadata": {
            "title": title
        }
    }

def create_question_set_params(title, intro_text, questions, pass_pct=70, pool_size=20):
    """
    Crea los parámetros de QuestionSet oficial sincronizado con EducaMadrid y Moodle:
    - progressType: "textual" (máxima compatibilidad móvil/tablet)
    - showSolutionButton: False (sin revelación de soluciones)
    - retryButton: "off" por pregunta (evita adivinación por ensayo y error)
    - Textos de botones concisos y 100% en español
    """
    return {
        "introPage": {
            "showIntroPage": True,
            "title": title,
            "introduction": (
                f"<div style='font-family: inherit; font-size: 1em; line-height: 1.6; color: #0f172a;'>"
                f"{intro_text}"
                f"<div style='background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #059669; padding: 12px 16px; margin: 14px 0; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>"
                f"<strong style='color: #064e3b; font-size: 1.05em;'>📋 Condiciones de la Evaluación:</strong>"
                f"<ul style='margin: 8px 0 0 20px; padding: 0; line-height: 1.6; color: #0f172a;'>"
                f"<li>El cuestionario selecciona automáticamente <strong>{pool_size} preguntas aleatorias</strong> de un banco total de {len(questions)} cuestiones.</li>"
                f"<li>Nota mínima para superar la prueba: <strong>{pass_pct}%</strong> (equivalente a 7/10 en el calificador).</li>"
                f"<li>Las alternativas de respuesta se barajan aleatoriamente en cada intento.</li>"
                f"<li>Al pulsar <strong>'Finalizar y Enviar'</strong>, tu puntuación quedará automáticamente registrada en el aula virtual.</li>"
                f"</ul>"
                f"</div>"
                f"</div>"
            ),
            "startButtonText": "Comenzar evaluación"
        },
        "progressType": "textual",
        "passPercentage": pass_pct,
        "randomQuestions": True,
        "poolSize": pool_size,
        "questions": questions,
        "disableBackwardsNavigation": False,
        "override": {
            "checkButton": True,
            "showSolutionButton": "off",
            "retryButton": "off"
        },
        "endGame": {
            "showResultPage": True,
            "showSolutionButton": False,
            "showRetryButton": True,
            "noResultMessage": "Evaluación completada con éxito",
            "message": "Informe de Calificación de la Evaluación Oficial",
            "overallFeedback": [
                {
                    "from": 0,
                    "to": pass_pct - 1,
                    "feedback": (
                        f"<div style='background: #fef2f2; border: 1px solid #fecaca; padding: 14px 18px; border-radius: 6px; margin: 12px 0;'>"
                        f"<strong style='color: #991b1b; font-size: 1.1em;'>✗ Calificación insuficiente (&lt; {pass_pct}%)</strong>"
                        f"<p style='color: #450a0a; margin: 6px 0 0 0;'>No has alcanzado la nota de corte requerida. Revisa los contenidos teóricos y normativos antes de realizar un nuevo intento en el aula virtual.</p>"
                        f"</div>"
                    )
                },
                {
                    "from": pass_pct,
                    "to": 89,
                    "feedback": (
                        f"<div style='background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px 18px; border-radius: 6px; margin: 12px 0;'>"
                        f"<strong style='color: #14532d; font-size: 1.1em;'>✓ ¡Aprobado con Calificación NOTABLE!</strong>"
                        f"<p style='color: #14532d; margin: 6px 0 0 0;'>Has demostrado un dominio sólido de los conceptos y competencias de la unidad didáctica.</p>"
                        f"</div>"
                    )
                },
                {
                    "from": 90,
                    "to": 100,
                    "feedback": (
                        f"<div style='background: #f0fdf4; border: 1px solid #86efac; padding: 14px 18px; border-radius: 6px; margin: 12px 0;'>"
                        f"<strong style='color: #166534; font-size: 1.15em;'>★ ¡Excelente! Calificación SOBRESALIENTE</strong>"
                        f"<p style='color: #14532d; margin: 6px 0 0 0;'>Dominio impecable en todos los resultados de aprendizaje y criterios de evaluación.</p>"
                        f"</div>"
                    )
                }
            ],
            "solutionButtonText": "",
            "retryButtonText": "Reintentar cuestionario",
            "finishButtonText": "Guardar calificación",
            "submitButtonText": "Enviar calificación a Moodle"
        },
        "texts": {
            "prevButton": "Anterior",
            "previous": "Pregunta anterior",
            "nextButton": "Siguiente",
            "next": "Siguiente pregunta",
            "finishButton": "Finalizar prueba",
            "submitButton": "Enviar calificación",
            "textualProgress": "Pregunta @current de @total",
            "jumpToQuestion": "Ir a la pregunta %d",
            "questionLabel": "Pregunta",
            "readSpeakerProgress": "Pregunta @current de @total",
            "unansweredText": "Sin responder",
            "answeredText": "Respondida",
            "currentQuestionText": "Pregunta actual",
            "navigationLabel": "Navegación de preguntas",
            "questionSetInstruction": "Selecciona la opción deseada y navega con los botones inferiores.",
            "noQuestionAdded": "No se han añadido preguntas a esta prueba."
        }
    }
