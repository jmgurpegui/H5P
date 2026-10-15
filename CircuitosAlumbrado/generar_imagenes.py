#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Imágenes Técnicas Vectoriales Rasterizadas en Alta Resolución (PNG)
para el curso 'Circuitos de Alumbrado y Señalización del Automóvil'
Cumple con la estricta Whitelist de EducaMadrid (0 .html, 0 .svg en content/).
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/home/jmgurpegui/H5P/CircuitosAlumbrado/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_font(size):
    try:
        # Try finding standard linux fonts
        for path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def get_font_regular(size):
    try:
        for path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()

# -----------------------------------------------------------------------------
# 1. Proyector Elipsoidal DE y Haz Asimétrico a 15°
# -----------------------------------------------------------------------------
def generar_proyector_de():
    width, height = 1200, 680
    im = Image.new("RGB", (width, height), "#0f172a") # Slate 900 de fondo
    d = ImageDraw.Draw(im)
    
    font_title = get_font(28)
    font_bold = get_font(20)
    font_sub = get_font_regular(17)
    font_mono = get_font(16)
    
    # Cabecera
    d.rectangle([(0, 0), (width, 70)], fill="#1e293b")
    d.text((30, 20), "PROYECTOR ELIPSOIDAL DE (BIXENÓN / FULL LED) Y CORTE ASIMÉTRICO 15°", fill="#38bdf8", font=font_title)
    
    # 1. Esquema del Proyector
    # Reflector elipsoidal (arco)
    d.arc([(80, 160), (380, 480)], start=90, end=270, fill="#94a3b8", width=6)
    d.text((100, 120), "Reflector Elipsoidal", fill="#cbd5e1", font=font_bold)
    
    # Foco 1 (F1): Lámpara
    d.ellipse([(180, 310), (200, 330)], fill="#facc15", outline="#ca8a04", width=3)
    d.text((160, 345), "Foco F1: Lámpara\n(Xenón / LED)", fill="#fde047", font=font_mono)
    
    # Rayos desde F1 convergiendo a F2
    for y_start in [200, 260, 380, 440]:
        d.line([(190, 320), (120, y_start), (420, 320)], fill="#fef08a", width=2)
    
    # Foco 2 (F2) y Diafragma obturador
    d.line([(420, 200), (420, 440)], fill="#64748b", width=2)
    d.rectangle([(416, 320), (424, 440)], fill="#ef4444")
    d.polygon([(416, 320), (436, 305), (424, 320)], fill="#ef4444")
    d.text((360, 455), "Foco F2: Diafragma Obturador\n(Corte asimétrico a 15°)", fill="#f87171", font=font_mono)
    
    # Solenoide Bixenón
    d.rectangle([(390, 520), (450, 580)], fill="#334155", outline="#38bdf8", width=2)
    d.text((350, 595), "Solenoide Electromecánico\n(Abate pantalla para largas)", fill="#94a3b8", font=font_sub)
    d.line([(420, 440), (420, 520)], fill="#38bdf8", width=3)
    
    # Lente convergente plano-convexa (Lupa)
    d.arc([(520, 180), (620, 460)], start=270, end=90, fill="#38bdf8", width=6)
    d.line([(570, 180), (570, 460)], fill="#38bdf8", width=6)
    d.text((530, 130), "Lente Convergente (Lupa)", fill="#7dd3fc", font=font_bold)
    
    # Rayos proyectados a través de la lente
    d.polygon([(570, 240), (760, 200), (760, 440), (570, 400)], fill="#1e293b", outline="#0284c7")
    d.line([(570, 260), (760, 240)], fill="#fde047", width=3)
    d.line([(570, 320), (760, 320)], fill="#fde047", width=3)
    d.line([(570, 380), (760, 400)], fill="#fde047", width=3)
    
    # 2. Pantalla de Proyección de Haz Asimétrico ECE
    d.rectangle([(800, 130), (1150, 600)], fill="#020617", outline="#38bdf8", width=3)
    d.text((820, 150), "HUELLA PROYECTADA (NORMA ECE)", fill="#38bdf8", font=font_bold)
    
    # Eje horizontal y vertical
    d.line([(820, 380), (1130, 380)], fill="#475569", width=2) # Eje H-H
    d.line([(960, 200), (960, 560)], fill="#475569", width=2) # Eje V-V
    d.text((1100, 355), "H", fill="#94a3b8", font=font_mono)
    d.text((965, 210), "V", fill="#94a3b8", font=font_mono)
    
    # Línea de corte asimétrico: horizontal izquierda, inclinada 15° derecha
    d.line([(830, 410), (960, 410)], fill="#22c55e", width=4) # Lado izquierdo horizontal (no deslumbrar)
    d.line([(960, 410), (1120, 340)], fill="#22c55e", width=4) # Lado derecho a 15° (arcén)
    
    # Área iluminada en amarillo suave
    d.polygon([(830, 410), (960, 410), (1120, 340), (1130, 580), (830, 580)], fill="#854d0e")
    d.text((840, 520), "Zona Iluminada en Calzada", fill="#fef08a", font=font_bold)
    d.text((840, 300), "Zona Oscura (Anti-deslumbramiento)", fill="#94a3b8", font=font_sub)
    d.text((990, 320), "+15° Arcén", fill="#4ade80", font=font_bold)
    
    # Pie de gráfica
    d.rectangle([(0, 630), (width, 680)], fill="#1e293b")
    d.text((30, 645), "Normativa ECE R112/R98: El corte a 15° proporciona hasta 75 m de visibilidad en el arcén sin deslumbrar.", fill="#e2e8f0", font=font_sub)
    
    path = os.path.join(OUTPUT_DIR, "proyector_elipsoidal_de.png")
    im.save(path, "PNG", optimize=True)
    print(f"✓ Creada imagen técnica: {path}")

# -----------------------------------------------------------------------------
# 2. Regloscopio y Ajuste Óptico de Faros (-1% a -1.5%)
# -----------------------------------------------------------------------------
def generar_regloscopio():
    width, height = 1200, 680
    im = Image.new("RGB", (width, height), "#0f172a")
    d = ImageDraw.Draw(im)
    
    font_title = get_font(28)
    font_bold = get_font(20)
    font_sub = get_font_regular(17)
    font_mono = get_font(16)
    
    # Cabecera
    d.rectangle([(0, 0), (width, 70)], fill="#1e293b")
    d.text((30, 20), "REGLAJE DE FAROS CON REGLOSCOPIO: PANTALLA Y CAÍDA DEL HAZ", fill="#38bdf8", font=font_title)
    
    # Pantalla del regloscopio a la izquierda
    d.rectangle([(80, 110), (680, 590)], fill="#020617", outline="#cbd5e1", width=4)
    d.text((100, 130), "PANTALLA DE PROYECCIÓN INTERNA DEL REGLOSCOPIO (A 25 METROS)", fill="#94a3b8", font=font_mono)
    
    # Eje H central (0%)
    d.line([(100, 260), (660, 260)], fill="#64748b", width=2)
    d.text((610, 235), "0% (H)", fill="#94a3b8", font=font_mono)
    
    # Eje V central
    d.line([(380, 150), (380, 570)], fill="#64748b", width=2)
    d.text((390, 160), "V", fill="#94a3b8", font=font_mono)
    
    # Líneas de caída reglamentarias
    d.line([(100, 310), (660, 310)], fill="#38bdf8", width=1) # -0.5%
    d.text((600, 290), "-0.5%", fill="#38bdf8", font=font_mono)
    
    d.line([(100, 360), (660, 360)], fill="#22c55e", width=3) # -1.0% (Límite superior turismo)
    d.text((580, 340), "-1.0% (ITV)", fill="#22c55e", font=font_bold)
    
    d.line([(100, 410), (660, 410)], fill="#22c55e", width=3) # -1.5% (Límite inferior turismo)
    d.text((580, 390), "-1.5% (ITV)", fill="#22c55e", font=font_bold)
    
    d.line([(100, 480), (660, 480)], fill="#f97316", width=2) # -2.5% (Exceso de caída)
    d.text((580, 460), "-2.5% (Bajo)", fill="#f97316", font=font_mono)
    
    # Haz perfectamente ajustado a -1.2%
    d.polygon([(100, 380), (380, 380), (580, 300), (660, 260), (660, 570), (100, 570)], fill="#854d0e")
    d.line([(100, 380), (380, 380)], fill="#facc15", width=4)
    d.line([(380, 380), (580, 300)], fill="#facc15", width=4)
    d.text((120, 410), "HAZ DE CRUCE CORRECTAMENTE ALINEADO (-1.2%)", fill="#fef08a", font=font_bold)
    d.text((390, 350), "Ángulo 15°", fill="#fde047", font=font_mono)
    
    # Panel de especificaciones a la derecha
    d.rectangle([(720, 110), (1140, 590)], fill="#1e293b", outline="#38bdf8", width=2)
    d.text((740, 135), "CRITERIOS METROLÓGICOS ITV", fill="#38bdf8", font=font_bold)
    
    specs = [
        ("Distancia focal simulada:", "25 metros"),
        ("Inclinación turismos:", "-1.0% a -1.5%"),
        ("Inclinación vehículos pesados:", "-2.0% a -3.5%"),
        ("Desvío hacia arriba (+1%):", "Multiplica x20 deslumbramiento"),
        ("Desvío hacia abajo (-2.5%):", "Reduce 50% distancia de visión"),
        ("Mecanismos de ajuste:", "Tornillo H (Horizontal)\nTornillo V (Vertical)"),
        ("Regulación automática:", "Obligatoria en xenón/LED\nsi flujo > 2.000 lúmenes")
    ]
    
    y_pos = 180
    for label, val in specs:
        d.text((740, y_pos), label, fill="#94a3b8", font=font_sub)
        y_pos += 24
        d.text((760, y_pos), val, fill="#f8fafc", font=font_bold)
        y_pos += 34
    
    # Pie
    d.rectangle([(0, 630), (width, 680)], fill="#1e293b")
    d.text((30, 645), "Un reglaje preciso es vital: el 42% de muertes en carretera ocurren de noche o crepúsculo (Datos DGT / RACE).", fill="#e2e8f0", font=font_sub)
    
    path = os.path.join(OUTPUT_DIR, "regloscopio_ajuste_faros.png")
    im.save(path, "PNG", optimize=True)
    print(f"✓ Creada imagen técnica: {path}")

# -----------------------------------------------------------------------------
# 3. Esquema Eléctrico de Alumbrado y Relés DIN
# -----------------------------------------------------------------------------
def generar_esquema_reles():
    width, height = 1200, 680
    im = Image.new("RGB", (width, height), "#0f172a")
    d = ImageDraw.Draw(im)
    
    font_title = get_font(28)
    font_bold = get_font(20)
    font_sub = get_font_regular(17)
    font_mono = get_font(16)
    
    # Cabecera
    d.rectangle([(0, 0), (width, 70)], fill="#1e293b")
    d.text((30, 20), "CIRCUITO NORMALIZADO DIN DE ALUMBRADO (POSICIÓN, CRUCE Y CARRETERA)", fill="#38bdf8", font=font_title)
    
    # Líneas de alimentación superiores
    d.line([(60, 110), (1140, 110)], fill="#ef4444", width=4) # Línea 30 (+Bat)
    d.text((70, 85), "LÍNEA 30: +12V Directo de Batería (Permanente)", fill="#ef4444", font=font_bold)
    
    d.line([(60, 160), (1140, 160)], fill="#3b82f6", width=4) # Línea 15 (+Contacto)
    d.text((70, 135), "LÍNEA 15: +12V Bajo Llave de Contacto", fill="#3b82f6", font=font_bold)
    
    # Línea 31 (Masa) inferior
    d.line([(60, 590), (1140, 590)], fill="#64748b", width=4) # Línea 31
    d.text((70, 600), "LÍNEA 31: Masa de Chasis (0V)", fill="#94a3b8", font=font_bold)
    
    # 1. Interruptor General de Luces
    d.rectangle([(100, 220), (220, 360)], fill="#1e293b", outline="#facc15", width=3)
    d.text((110, 230), "Conmutador\nPrincipal", fill="#fde047", font=font_bold)
    d.text((110, 280), "0: Apagado\n1: Posición (58)\n2: Alumbrado (56)", fill="#e2e8f0", font=font_mono)
    d.line([(160, 160), (160, 220)], fill="#3b82f6", width=3) # Conexión a Línea 15
    
    # 2. Conmutador de Cruce / Carretera (Palanca de luces)
    d.rectangle([(300, 220), (440, 360)], fill="#1e293b", outline="#38bdf8", width=3)
    d.text((310, 230), "Palanca Mando\nCruce/Carretera", fill="#38bdf8", font=font_bold)
    d.text((310, 280), "Borne 56 Entr.\nBorne 56b: Cruce\nBorne 56a: Larga", fill="#e2e8f0", font=font_mono)
    d.line([(220, 330), (300, 330)], fill="#facc15", width=3) # Línea 56
    
    # 3. Relé de Luz de Cruce (56b)
    d.rectangle([(520, 200), (680, 340)], fill="#1e293b", outline="#22c55e", width=3)
    d.text((535, 215), "RELÉ CRUCE (56b)", fill="#4ade80", font=font_bold)
    d.text((535, 245), "Bobina: 85 - 86\nContacto: 30 - 87", fill="#94a3b8", font=font_mono)
    d.line([(440, 260), (520, 260)], fill="#38bdf8", width=3) # Señal 56b a borne 86
    d.line([(600, 110), (600, 200)], fill="#ef4444", width=3) # Borne 30 relé a bat
    d.line([(640, 340), (640, 590)], fill="#64748b", width=2) # Borne 85 a masa
    
    # 4. Relé de Luz de Carretera (56a)
    d.rectangle([(520, 390), (680, 530)], fill="#1e293b", outline="#3b82f6", width=3)
    d.text((535, 405), "RELÉ CARRETERA (56a)", fill="#60a5fa", font=font_bold)
    d.text((535, 435), "Bobina: 85 - 86\nContacto: 30 - 87", fill="#94a3b8", font=font_mono)
    d.line([(440, 330), (480, 330), (480, 450), (520, 450)], fill="#38bdf8", width=3) # Señal 56a a borne 86
    d.line([(600, 110), (600, 390)], fill="#ef4444", width=3) # Borne 30 a bat
    d.line([(640, 530), (640, 590)], fill="#64748b", width=2) # Borne 85 a masa
    
    # 5. Cajas de Fusibles y Faros
    # Cruce: Faros Izq y Dch
    d.rectangle([(750, 240), (830, 280)], fill="#dc2626", outline="#ffffff", width=2)
    d.text((760, 250), "F1 10A", fill="#ffffff", font=font_bold)
    d.rectangle([(750, 300), (830, 340)], fill="#dc2626", outline="#ffffff", width=2)
    d.text((760, 310), "F2 10A", fill="#ffffff", font=font_bold)
    d.line([(680, 290), (710, 290), (710, 260), (750, 260)], fill="#22c55e", width=3)
    d.line([(710, 290), (710, 320), (750, 320)], fill="#22c55e", width=3)
    
    d.rectangle([(910, 230), (1110, 290)], fill="#334155", outline="#22c55e", width=2)
    d.text((925, 245), "Faro Cruce Izquierdo (55W)", fill="#4ade80", font=font_bold)
    d.rectangle([(910, 310), (1110, 370)], fill="#334155", outline="#22c55e", width=2)
    d.text((925, 325), "Faro Cruce Derecho (55W)", fill="#4ade80", font=font_bold)
    d.line([(830, 260), (910, 260)], fill="#22c55e", width=3)
    d.line([(830, 320), (910, 320)], fill="#22c55e", width=3)
    d.line([(1010, 290), (1010, 590)], fill="#64748b", width=2)
    d.line([(1010, 370), (1010, 590)], fill="#64748b", width=2)
    
    # Carretera: Faros Izq y Dch
    d.rectangle([(750, 420), (830, 460)], fill="#dc2626", outline="#ffffff", width=2)
    d.text((760, 430), "F3 10A", fill="#ffffff", font=font_bold)
    d.rectangle([(750, 480), (830, 520)], fill="#dc2626", outline="#ffffff", width=2)
    d.text((760, 490), "F4 10A", fill="#ffffff", font=font_bold)
    d.line([(680, 470), (710, 470), (710, 440), (750, 440)], fill="#3b82f6", width=3)
    d.line([(710, 470), (710, 500), (750, 500)], fill="#3b82f6", width=3)
    
    d.rectangle([(910, 420), (1110, 470)], fill="#334155", outline="#3b82f6", width=2)
    d.text((925, 435), "Faro Carretera Izq (60W)", fill="#60a5fa", font=font_bold)
    d.rectangle([(910, 490), (1110, 540)], fill="#334155", outline="#3b82f6", width=2)
    d.text((925, 505), "Faro Carretera Dch (60W)", fill="#60a5fa", font=font_bold)
    d.line([(830, 440), (910, 440)], fill="#3b82f6", width=3)
    d.line([(830, 500), (910, 500)], fill="#3b82f6", width=3)
    d.line([(1050, 470), (1050, 590)], fill="#64748b", width=2)
    d.line([(1050, 540), (1050, 590)], fill="#64748b", width=2)
    
    path = os.path.join(OUTPUT_DIR, "esquema_alumbrado_reles.png")
    im.save(path, "PNG", optimize=True)
    print(f"✓ Creada imagen técnica: {path}")

# -----------------------------------------------------------------------------
# 4. Esquema de Intermitencia y Luces de Emergencia (Warning)
# -----------------------------------------------------------------------------
def generar_intermitencia_warning():
    width, height = 1200, 680
    im = Image.new("RGB", (width, height), "#0f172a")
    d = ImageDraw.Draw(im)
    
    font_title = get_font(28)
    font_bold = get_font(20)
    font_sub = get_font_regular(17)
    font_mono = get_font(16)
    
    # Cabecera
    d.rectangle([(0, 0), (width, 70)], fill="#1e293b")
    d.text((30, 20), "CIRCUITO DE INTERMITENCIA Y LUCES DE EMERGENCIA (WARNING)", fill="#38bdf8", font=font_title)
    
    # Líneas de alimentación
    d.line([(60, 110), (1140, 110)], fill="#ef4444", width=4) # Línea 30
    d.text((70, 85), "LÍNEA 30: +12V Permanente Batería (Alimentación Emergencia)", fill="#ef4444", font=font_bold)
    
    d.line([(60, 160), (1140, 160)], fill="#3b82f6", width=4) # Línea 15
    d.text((70, 135), "LÍNEA 15: +12V Contacto (Alimentación Intermitencia Ordinaria)", fill="#3b82f6", font=font_bold)
    
    d.line([(60, 590), (1140, 590)], fill="#64748b", width=4) # Línea 31
    d.text((70, 600), "LÍNEA 31: Masa (0V)", fill="#94a3b8", font=font_bold)
    
    # 1. Interruptor de Warning (Prioritario)
    d.rectangle([(100, 220), (320, 390)], fill="#1e293b", outline="#ef4444", width=3)
    d.text((115, 235), "CONMUTADOR WARNING", fill="#f87171", font=font_bold)
    d.text((115, 270), "Entrada: Línea 30 y 15\nSalida: Borne 49 Relé\nPuentea ramal L + R\nPrioridad sobre palanca", fill="#f1f5f9", font=font_mono)
    d.line([(160, 110), (160, 220)], fill="#ef4444", width=3)
    d.line([(240, 160), (240, 220)], fill="#3b82f6", width=3)
    
    # 2. Relé Electrónico de Intermitencia
    d.rectangle([(400, 220), (600, 390)], fill="#1e293b", outline="#facc15", width=3)
    d.text((415, 235), "CENTRALITA INTERMITENCIA", fill="#fde047", font=font_bold)
    d.text((415, 270), "Borne 49: +12V Alimentación\nBorne 49a: Salida Pulsante\nBorne 31: Masa\nCadencia: 60-120 ppm\nSupervisión de carga", fill="#e2e8f0", font=font_mono)
    d.line([(320, 300), (400, 300)], fill="#fde047", width=3) # Señal a borne 49
    d.line([(500, 390), (500, 590)], fill="#64748b", width=2) # Borne 31 a masa
    
    # 3. Palanca de Dirección
    d.rectangle([(680, 220), (840, 390)], fill="#1e293b", outline="#38bdf8", width=3)
    d.text((695, 235), "MANDO DIRECCIÓN", fill="#38bdf8", font=font_bold)
    d.text((695, 270), "Entrada: Borne 49a\nPos. L: Izquierda\nPos. 0: Neutro\nPos. R: Derecha", fill="#f1f5f9", font=font_mono)
    d.line([(600, 300), (680, 300)], fill="#fde047", width=3) # Salida 49a a mando
    
    # 4. Ramales de Lámparas Ámbar
    # Izquierda
    d.rectangle([(910, 210), (1130, 330)], fill="#334155", outline="#f59e0b", width=2)
    d.text((925, 225), "RAMAL IZQUIERDO (L)", fill="#fbbf24", font=font_bold)
    d.text((925, 255), "Delantero (21W)\nLateral Retrovisor (5W)\nTrasero (21W) + Testigo", fill="#e2e8f0", font=font_mono)
    d.line([(840, 260), (910, 260)], fill="#f59e0b", width=3)
    d.line([(1020, 330), (1020, 590)], fill="#64748b", width=2)
    
    # Derecha
    d.rectangle([(910, 370), (1130, 490)], fill="#334155", outline="#f59e0b", width=2)
    d.text((925, 385), "RAMAL DERECHO (R)", fill="#fbbf24", font=font_bold)
    d.text((925, 415), "Delantero (21W)\nLateral Retrovisor (5W)\nTrasero (21W) + Testigo", fill="#e2e8f0", font=font_mono)
    d.line([(840, 350), (870, 350), (870, 430), (910, 430)], fill="#f59e0b", width=3)
    d.line([(1020, 490), (1020, 590)], fill="#64748b", width=2)
    
    # Retorno warning
    d.line([(210, 390), (210, 540), (890, 540), (890, 290), (910, 290)], fill="#f87171", width=2)
    d.line([(890, 540), (890, 460), (910, 460)], fill="#f87171", width=2)
    
    # Pie
    d.rectangle([(0, 630), (width, 680)], fill="#1e293b")
    d.text((30, 645), "Si se funde una lámpara de 21W, la caída de consumo duplica la frecuencia del destello (aviso acústico/óptico).", fill="#e2e8f0", font=font_sub)
    
    path = os.path.join(OUTPUT_DIR, "esquema_intermitencia_warning.png")
    im.save(path, "PNG", optimize=True)
    print(f"✓ Creada imagen técnica: {path}")

# -----------------------------------------------------------------------------
# 5. Guía Metrológica de Diagnosis por Caída de Tensión (Voltmeter Drop)
# -----------------------------------------------------------------------------
def generar_diagnosis_caida_tension():
    width, height = 1200, 680
    im = Image.new("RGB", (width, height), "#0f172a")
    d = ImageDraw.Draw(im)
    
    font_title = get_font(28)
    font_bold = get_font(20)
    font_sub = get_font_regular(17)
    font_mono = get_font(16)
    
    # Cabecera
    d.rectangle([(0, 0), (width, 70)], fill="#1e293b")
    d.text((30, 20), "DIAGNOSIS EN TALLER: MÉTODO DE CAÍDA DE TENSIÓN EN CARGA (VOLTÍMETRO)", fill="#38bdf8", font=font_title)
    
    # Batería
    d.rectangle([(80, 240), (220, 420)], fill="#1e293b", outline="#e2e8f0", width=3)
    d.text((105, 260), "BATERÍA", fill="#f8fafc", font=font_bold)
    d.text((105, 300), "Tensión nominal:\n12.6V (Parado)\n14.2V (Alternador)", fill="#94a3b8", font=font_mono)
    d.text((100, 390), "(+) ROJO", fill="#ef4444", font=font_bold)
    d.text((160, 390), "(-) AZUL", fill="#3b82f6", font=font_bold)
    
    # Carga: Faro bajo prueba
    d.rectangle([(900, 240), (1120, 420)], fill="#334155", outline="#facc15", width=3)
    d.text((920, 260), "FARO EN SERVICIO", fill="#fde047", font=font_bold)
    d.text((920, 300), "Lámpara H7 (55W)\nCorriente I = 4.58A\nCircuito cerrado\ny encendido", fill="#e2e8f0", font=font_mono)
    
    # Línea positiva con interruptor/relé
    d.line([(120, 240), (120, 160), (940, 160), (940, 240)], fill="#ef4444", width=4)
    d.rectangle([(480, 140), (580, 180)], fill="#0f172a", outline="#ef4444", width=2)
    d.text((490, 150), "Relé / Mando", fill="#f87171", font=font_mono)
    
    # Línea negativa / masa
    d.line([(180, 420), (180, 500), (1060, 500), (1060, 420)], fill="#3b82f6", width=4)
    d.rectangle([(480, 480), (600, 520)], fill="#0f172a", outline="#3b82f6", width=2)
    d.text((490, 490), "Punto Masa Chasis", fill="#60a5fa", font=font_mono)
    
    # Voltímetro 1: Caída de tensión en positivo (V1)
    d.rectangle([(440, 220), (620, 320)], fill="#020617", outline="#22c55e", width=3)
    d.text((460, 230), "VOLTÍMETRO V1", fill="#4ade80", font=font_bold)
    d.text((460, 260), "Caída línea (+):\nMax admisible: 0.3V\n(Lectura OK: 0.15V)", fill="#f8fafc", font=font_mono)
    d.line([(440, 270), (130, 270), (130, 160)], fill="#22c55e", width=2) # Conexión a borne bat +
    d.line([(620, 270), (930, 270), (930, 240)], fill="#22c55e", width=2) # Conexión a terminal lámpara +
    
    # Voltímetro 2: Caída de tensión en masa (V2)
    d.rectangle([(440, 350), (620, 450)], fill="#020617", outline="#38bdf8", width=3)
    d.text((460, 360), "VOLTÍMETRO V2", fill="#38bdf8", font=font_bold)
    d.text((460, 390), "Caída línea (-):\nMax admisible: 0.1V\n(Lectura OK: 0.04V)", fill="#f8fafc", font=font_mono)
    d.line([(440, 400), (190, 400), (190, 420)], fill="#38bdf8", width=2) # Conexión a borne bat -
    d.line([(620, 400), (1050, 400), (1050, 420)], fill="#38bdf8", width=2) # Conexión a casquillo masa
    
    # Tabla de diagnóstico
    d.rectangle([(80, 540), (1120, 620)], fill="#1e293b", outline="#e2e8f0", width=1)
    d.text((100, 550), "REGLAS DE ORO EN TALLER:", fill="#facc15", font=font_bold)
    d.text((100, 575), "1. Medir SIEMPRE con el circuito encendido y consumiendo corriente (en carga). Con circuito abierto la caída es 0V.", fill="#e2e8f0", font=font_sub)
    d.text((100, 595), "2. Pérdida de 0.5V = -15% de luz. Pérdida de 1.0V = -28% de luz. Una masa oxidada es la causa del 70% de faros tenues.", fill="#e2e8f0", font=font_sub)
    
    path = os.path.join(OUTPUT_DIR, "diagnosis_caida_tension.png")
    im.save(path, "PNG", optimize=True)
    print(f"✓ Creada imagen técnica: {path}")

if __name__ == "__main__":
    print("Iniciando generación de imágenes técnicas para CircuitosAlumbrado...")
    generar_proyector_de()
    generar_regloscopio()
    generar_esquema_reles()
    generar_intermitencia_warning()
    generar_diagnosis_caida_tension()
    print("✅ Todas las imágenes técnicas han sido generadas con éxito.")
