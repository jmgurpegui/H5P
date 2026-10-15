import os
import subprocess
from PIL import Image

FFMPEG = "/mnt/c/Users/jmgur/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
VIDEO = "/home/jmgurpegui/H5P/CircuitosAlumbrado/alumbrado.mp4"
FRAMES_DIR = "/home/jmgurpegui/H5P/CircuitosAlumbrado/master_4k_frames"
IMG_DIR = "/home/jmgurpegui/H5P/CircuitosAlumbrado/images"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# 1. Extract 4K key frames at exact seconds
seconds_needed = [6, 12, 18, 32, 35, 38, 40, 54, 62, 66, 68, 70, 71, 74, 78, 82, 84]

for s in seconds_needed:
    frame_path = os.path.join(FRAMES_DIR, f"sec_{s:02d}.png")
    if not os.path.exists(frame_path):
        print(f"Extracting frame at {s}s...")
        cmd = [FFMPEG, "-y", "-ss", f"{s}.0", "-i", VIDEO, "-vframes", "1", "-q:v", "1", frame_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def crop_and_save(sec, box, filename):
    frame_path = os.path.join(FRAMES_DIR, f"sec_{sec:02d}.png")
    im = Image.open(frame_path)
    cropped = im.crop(box)
    out_path = os.path.join(IMG_DIR, filename)
    cropped.save(out_path, "PNG", optimize=True)
    print(f"✓ Saved {filename} from sec_{sec:02d}.png: size={cropped.size}")

# CROP DEFINITIONS (Frame 3840 x 2088)
# Left page content:  X ~880 to ~2080, Y ~300 to ~1850
# Right page content: X ~2180 to ~3380, Y ~300 to ~1850

# Cap 1: Posicion, Cruce, Carretera
crop_and_save(6, (2170, 410, 3380, 1850), "figura_distribucion_lamparas_vehiculo.png")
crop_and_save(18, (1200, 850, 2070, 1280), "figura_marcado_lampara_h7.png")
crop_and_save(32, (880, 1480, 2060, 1830), "figura_optica_paraboloides_haz.png")
crop_and_save(32, (2260, 1370, 3140, 1830), "figura_optica_pantalla_cruce.png")
crop_and_save(35, (880, 920, 2060, 1400), "figura_faro_elipsoidal_de.png")

# Cap 2: Encendido Automatico y Antiniebla
crop_and_save(12, (2350, 520, 3100, 1420), "figura_composicion_lampara_xenon.png")
crop_and_save(12, (900, 1370, 2060, 1820), "figura_despiece_lamparas_xenon.png")
crop_and_save(38, (2220, 920, 3060, 1475), "figura_componentes_faro_xenon.png")
crop_and_save(40, (1150, 550, 2060, 880), "figura_esquema_electrico_xenon.png")
crop_and_save(54, (1200, 420, 2060, 850), "figura_bixenon_trampilla_movil.png")
crop_and_save(78, (2600, 980, 3350, 1480), "figura_sensor_lluvia_luz_optico.png")

# Cap 3: Intermitencia, Emergencia, DRL, Freno, Luces Especiales
crop_and_save(54, (2200, 1300, 3380, 1840), "figura_despiece_faro_matrix_led.png")
crop_and_save(62, (900, 1550, 2060, 1840), "figura_faro_laser_alcance_comparativa.png")
crop_and_save(70, (2200, 380, 3380, 920), "figura_senales_pwm_senalizacion.png")
crop_and_save(71, (880, 980, 2060, 1400), "figura_luces_freno_adaptativo.png")

# Cap 4: Dimensionado y Regulacion
crop_and_save(74, (880, 570, 2070, 960), "figura_homologacion_faro_delantero.png")
crop_and_save(74, (2200, 400, 3400, 1780), "figura_luces_curvas_adaptativas.png")
crop_and_save(82, (900, 650, 2060, 1140), "figura_sensor_angulo_volante_hall.png")

# Cap 5: Diagnosis y Metrologia
crop_and_save(40, (2200, 1100, 3380, 1600), "figura_protocolo_diagnosis_faro_xenon.png")
crop_and_save(68, (2200, 680, 3380, 1820), "figura_comprobacion_piloto_taller.png")
crop_and_save(84, (880, 290, 2070, 1480), "figura_sistema_afs_distribucion_haz.png")

print("All master figures cropped and certified!")
