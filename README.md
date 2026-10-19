# Plantilla Oficial de Cursos H5P y Cuestionarios Moodle XML para EducaMadrid (FP Automoción)

Este repositorio contiene el **entorno maestro y plantilla homologada** para la creación, maquetación y validación de cursos interactivos **H5P** (100 % formativos) y bancos de evaluación sumativa en **Moodle XML** destinados a las Aulas Virtuales de **EducaMadrid** (Formación Profesional de Automoción).

> **Política del Repositorio**: En GitHub se mantiene **exclusivamente la plantilla maestra y el toolkit de compilación/validación**, sin subir paquetes `.h5p` ni carpetas de cursos concretos.

---

## 📁 Estructura del Repositorio

```text
H5P/
├── GEMINI.md                                 # Reglas operativas y psicométricas del entorno
├── REQUISITOS_CURSOS_H5P_EDUCAMADRID.md      # Especificación oficial EducaMadrid (Técnica, Pedagógica y Accesibilidad)
├── build.py                                  # Script maestro de inicialización, compilación, inyección CSS y validación
├── plantilla/                                # Toolkit y plantilla técnica maestra
│   ├── generar_curso_plantilla.py            # Generador maestro con helpers didácticos y de taller de Automoción
│   ├── validar_h5p_educamadrid.py            # Validador de certificación EducaMadrid / Lumi / Moodle
│   ├── moodle_xml_builder.py                 # Constructor y validador psicométrico de bancos Moodle XML (5 tipos)
│   ├── evaluacion_modelo_moodle.xml          # Banco de preguntas modelo sumativo para Moodle (12 preguntas)
│   ├── estilos_educamadrid.css               # Hoja de estilos accesible y responsive (WCAG AAA, cero texto claro)
│   ├── append_css_to_libraries.py            # Inyector limpio de CSS en librerías base
│   ├── logo2026.png / logo2026.bmp           # Logotipo institucional oficial (Comunidad de Madrid)
│   ├── CC.png                                # Logotipo oficial Creative Commons
│   ├── Plantilla_Curso_Modelo_EducaMadrid.h5p# Paquete H5P modelo certificado y listo para Moodle
│   └── README.md                             # Documentación detallada de la plantilla
│
├── h5p_builder/
│   └── h5p-libraries/                        # Repositorio maestro de librerías oficiales H5P depuradas (whitelist)
│
└── .agents/
    ├── rules/
    │   └── cuestionarios_xml.md              # Reglas psicométricas para bancos Moodle XML
    └── skills/
        └── h5p-educamadrid/                  # Skill oficial para Agentes de IA (Gemini / Antigravity)
```

---

## 🚀 Comandos Rápidos con `build.py`

El script maestro [`build.py`](build.py) centraliza todas las operaciones:

```bash
# 1. Compilar CSS, certificar la plantilla maestra y sincronizar el skill
python3 build.py

# 2. Inicializar la carpeta y el código base para un NUEVO curso de Automoción
python3 build.py nuevo SistemasInyeccion "Sistemas de Inyección Electrónica"

# 3. Compilar y validar un curso creado localmente
python3 build.py SistemasInyeccion

# 4. Validar todos los bancos de preguntas Moodle XML
python3 build.py xml

# 5. Inyectar estilos CSS accesibles y responsive en las librerías base
python3 build.py css

# 6. Validar cualquier paquete .h5p o banco .xml individual
python3 build.py validar <ruta_al_archivo.h5p_o_xml>
```

---

## 🛠️ Helpers para FP de Automoción en `generar_curso_plantilla.py`

| Función Helper | Propósito Didáctico en Automoción |
| :--- | :--- |
| `create_header_logo()` | Cabecera institucional oficial con resolución dinámica de logotipo. |
| `create_text_section(html, titulo)` | Bloques teóricos de alto contraste (`#0f172a`) y fórmulas semánticas (`.tech-formula`). |
| `create_component_spec_card(...)` | **Ficha técnica de sensor/actuador**: valores nominales ($\Omega$, V, A, Hz), pinout DIN 72552 y patrón de osciloscopio. |
| `create_diagnostic_table(titulo, filas)` | **Tabla metrológica de diagnosis en taller**: Síntoma ➔ Punto de medida / Instrumento ➔ Valor nominal vs. Avería ➔ Causa raíz y acción correctiva. |
| `create_video_section(url, titulo)` | Bloque nativo `H5P.Video 1.6` para vídeos técnicos demostrativos (YouTube / Mediateca EducaMadrid). |
| `create_image_section(...)` | Esquema técnico rasterizado (`.png` / `.jpg`) con texto alternativo accesible (`alt`). |
| `create_image_hotspots(...)` | Esquema interactivo con puntos de inspección táctiles (`H5P.ImageHotspots 1.10`). |
| `create_active_challenge(...)` | Reto práctico de taller paso a paso ante casos reales de avería (`.tech-challenge`). |
| `create_checklist_section(...)` | Lista de cotejo de verificación en vehículo con área táctil $\ge 44 \times 44\text{ px}$. |
| `create_accordion(...)` | Protocolos de taller desplegables (`H5P.Accordion 1.0`). |
| `create_simulation_box(...)` | Enlace a simuladores de circuitos o laboratorios externos seguros. |
| `create_moodle_quiz_referral(...)` | Cierre de capítulo (Fase 4) con síntesis y derivación al cuestionario oficial en Moodle (`mod_quiz`). |

---

## 📝 Cuestionarios Moodle XML (`moodle_xml_builder.py`)

El constructor `MoodleXMLBuilder` soporta **5 tipos de preguntas nativas de Moodle** ideales para FP de Automoción y aplica controles psicométricos automáticos:

1. **`add_multichoice(...)`**: Opción múltiple con retroalimentación razonada en cada opción, `<shuffleanswers>1</shuffleanswers>` y **rotación automática de la posición de la opción correcta (A, B, C, D) en el código XML**.
2. **`add_numerical(...)`**: Problemas de cálculo numérico de taller (Ley de Ohm, caída de tensión $\Delta V = I \cdot R$, frecuencia $f = 1/T$, ciclo de trabajo PWM) con margen de tolerancia (`<tolerance>`) y unidades (`V`, `A`, `Ω`, `Hz`).
3. **`add_shortanswer(...)`**: Respuesta corta para identificación directa de códigos de bornes DIN 72552 (`30`, `15`, `31`, `50`, `85`, `86`, `87`) o códigos de homologación ECE.
4. **`add_matching(...)`**: Emparejamiento de componentes, siglas multimarca o bornes con su función.
5. **`add_truefalse(...)`**: Preguntas de Verdadero/Falso para axiomas técnicos y normas de seguridad en taller.

### Reglas Psicométricas Certificadas Automáticamente
- **Control bidireccional contra sesgo de longitud (*Length Bias*)**: Verifica que la respuesta correcta sea la más larga en una proporción equilibrada (**entre el 15 % y el 40 %** de las preguntas `multichoice`), evitando tanto que la más larga sea siempre la correcta como el patrón inverso (`0 %`).
- **Distribución equitativa en el XML**: Verifica que la opción correcta (`fraction="100"`) se reparta entre las posiciones A, B, C y D del archivo XML.
- **Formato limpio sin `<p>` redundantes (Norma Picuino)**: Elimina envoltorios `<p>...</p>` innecesarios en enunciados, respuestas y feedbacks.
