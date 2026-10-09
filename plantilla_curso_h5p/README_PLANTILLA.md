# Plantilla Oficial para Cursos H5P en EducaMadrid y Moodle
### Arquitectura Modular con Separación Estricta de Contenido (HTML) y Evaluación (Moodle XML)

Esta plantilla permite a docentes y creadores de contenido diseñar y compilar cursos interactivos **H5P** (`H5P.InteractiveBook 1.7` y `H5P.QuestionSet 1.20`) de forma ágil, desacoplando totalmente la redacción de los contenidos teóricos de la gestión del banco de preguntas evaluativo.

---

## 🏗️ 1. Arquitectura del Proyecto

```text
plantilla_curso_h5p/
├── curso_config.json            # ⚙️ Configuración central: títulos, capítulos, nota de corte y rutas
├── build_desde_plantilla.py     # 🚀 Compilador universal a paquetes .h5p
├── xml_moodle_parser.py         # 🔄 Conversor bidireccional Moodle XML <-> H5P
│
├── contenido/                   # 📖 PARTE DE CONTENIDO (100% Desacoplada)
│   ├── 00_portada.html          # Portada y guía didáctica institucional
│   ├── 01_tema_fundamentos.html # Tema teórico 1 (HTML responsive)
│   └── 02_mediateca.html        # Mediateca y recursos audiovisuales
│
├── evaluacion/                  # 📝 PARTE DE EVALUACIÓN (Moodle XML Oficial)
│   ├── preguntas_moodle.xml     # Banco de preguntas en Moodle XML (<quiz>)
│   └── validador_xml.py         # Validador de estructura, balance de opciones y feedbacks
│
└── imagenes/                    # 🖼️ Recursos multimedia rasterizados (PNG, JPG, BMP)
    └── logo2026.bmp             # Logo institucional oficial
```

---

## 🌟 2. Ventajas Clave de esta Arquitectura

1. **Separación de Responsabilidades**:
   - Los **contenidos teóricos** se redactan en archivos HTML limpios (`contenido/*.html`) con maquetación responsive sin mezclar código Python.
   - Las **preguntas** se gestionan en un único archivo XML estándar (`evaluacion/preguntas_moodle.xml`).
2. **Compatibilidad Nativa con EducaMadrid**:
   - El archivo `preguntas_moodle.xml` se puede **importar directamente en el Banco de Preguntas de EducaMadrid / Moodle** (*Ajustes del curso → Banco de preguntas → Importar → Formato XML de Moodle*).
   - No requiere duplicar el trabajo para crear exámenes nativos en Moodle y en H5P.
3. **Doble Entrega Automática**:
   - Genera el paquete de **Curso Completo** (`H5P.InteractiveBook 1.7`) con teoría, infografías, vídeos y examen final.
   - Genera el paquete de **Examen Independiente** (`H5P.QuestionSet 1.20`) para exámenes oficiales cronometrados en Moodle.
4. **Cumplimiento Estricto de Seguridad**:
   - Valida automáticamente la **Whitelist de Moodle** (cero archivos `.svg` en `content/`).
   - Genera UUIDs únicos y títulos de metadatos para evitar pantallas en blanco en el visor H5P.
5. **Regla Estricta de Legibilidad y Contraste (PROHIBIDOS TEXTOS CLAROS)**:
   - **NUNCA usar colores de texto claros** (como blanco sobre fondos susceptibles de ser sobrescritos por el aula virtual, grises claros `#94a3b8`/`#cbd5e1`, verdes pálidos `#d1fae5`/`#ecfdf5` o celestes pálidos `#e0f2fe`).
   - Moodle y los navegadores con extensiones de modo lectura o accesibilidad fuerzan con frecuencia fondos blancos o transparentes en el iframe; **cualquier texto claro se vuelve completamente invisible e ilegible**.
   - **TODOS los textos de cuerpo, tablas, listas y párrafos deben usar colores oscuros de alto contraste**: `#0f172a`, `#1e293b` o `#111827`. Los títulos destacados deben usar colores densos: verde oscuro `#047857`, azul marino `#0369a1`, rojo oscuro `#7f1d1d` o ámbar oscuro `#78350f`.

---

## 🚀 3. Guía Rápida: Cómo Crear un Nuevo Curso en 4 Pasos

### Paso 1: Redactar los Contenidos en `contenido/`
Crea o edita los archivos HTML de tus temas dentro de la carpeta `contenido/`. Puedes emplear:
- Títulos jerárquicos (`<h2>`, `<h3>`).
- Cajas de destacado (`<div style="background: #f8fafc; border-left: 4px solid #0284c7; ...">`).
- Tablas comparativas responsive.
- Listas y formatos de texto enriquecido.

### Paso 2: Configurar las Preguntas en `evaluacion/preguntas_moodle.xml`
Añade tus preguntas en formato Moodle XML estándar dentro de `evaluacion/preguntas_moodle.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<quiz>
  <question type="multichoice">
    <name>
      <text>P01: Título o resumen de la pregunta</text>
    </name>
    <questiontext format="html">
      <text><![CDATA[<p>¿Texto completo del supuesto práctico o pregunta?</p>]]></text>
    </questiontext>
    <generalfeedback format="html">
      <text><![CDATA[<p>Fundamentación técnica o normativa de la solución.</p>]]></text>
    </generalfeedback>
    <single>true</single>
    <shuffleanswers>true</shuffleanswers>
    <answer fraction="100" format="html">
      <text><![CDATA[<p>Opción correcta (fracción 100)</p>]]></text>
      <feedback format="html">
        <text><![CDATA[<p>✓ Justificación del acierto...</p>]]></text>
      </feedback>
    </answer>
    <answer fraction="0" format="html">
      <text><![CDATA[<p>Opción distractora 1 (fracción 0)</p>]]></text>
      <feedback format="html">
        <text><![CDATA[<p>✗ Justificación del error...</p>]]></text>
      </feedback>
    </answer>
    <answer fraction="0" format="html">
      <text><![CDATA[<p>Opción distractora 2 (fracción 0)</p>]]></text>
      <feedback format="html">
        <text><![CDATA[<p>✗ Justificación del error...</p>]]></text>
      </feedback>
    </answer>
    <answer fraction="0" format="html">
      <text><![CDATA[<p>Opción distractora 3 (fracción 0)</p>]]></text>
      <feedback format="html">
        <text><![CDATA[<p>✗ Justificación del error...</p>]]></text>
      </feedback>
    </answer>
  </question>
</quiz>
```

> **Comprobación de calidad:** Ejecuta el validador automático para verificar que las opciones correctas alternan de forma equitativa (25% cada una):
> ```bash
> python3 evaluacion/validador_xml.py evaluacion/preguntas_moodle.xml
> ```

### Paso 3: Ajustar `curso_config.json`
Edita `curso_config.json` con los metadatos de tu curso:
- `titulo_curso`: Nombre que aparecerá en Moodle y en la portada del libro.
- `output_curso_h5p`: Nombre del archivo `.h5p` del curso completo.
- `output_evaluacion_h5p`: Nombre del archivo `.h5p` del examen independiente.
- `evaluacion.pass_percentage`: Nota de corte (por defecto `70`%).
- `evaluacion.pool_size`: Número de preguntas aleatorias que se seleccionarán en cada intento (ej. `20`).
- `capitulos`: Lista ordenada de capítulos enlazando los archivos de `contenido/*.html`.

### Paso 4: Compilar los Paquetes H5P
Ejecuta el compilador universal:
```bash
python3 build_desde_plantilla.py
```

El script generará automáticamente los dos archivos `.h5p` en el directorio raíz listos para subir a EducaMadrid o Moodle.

---

## 📥 4. Cómo Importar las Preguntas Directamente en el Aula Virtual de EducaMadrid

Además de estar empaquetadas en los archivos H5P, puedes importar el banco de preguntas en Moodle:
1. Accede a tu curso en el **Aula Virtual de EducaMadrid**.
2. En el menú superior o bloque de administración, haz clic en **Banco de preguntas** → **Importar**.
3. Selecciona **Formato XML de Moodle**.
4. En el apartado *General*, selecciona la categoría donde deseas guardarlas.
5. Arrastra el archivo `evaluacion/preguntas_moodle.xml`.
6. Haz clic en **Importar**. Todas las preguntas quedarán disponibles para utilizarlas en cuestionarios nativos de Moodle.

---

## 🛠️ 5. Herramientas de Conversión Disponibles (`xml_moodle_parser.py`)

Si ya dispones de preguntas en estructuras Python o JSON, puedes convertirlas automáticamente a Moodle XML ejecutando:

```python
from xml_moodle_parser import export_dict_to_moodle_xml

preguntas = [
    {
        "pregunta": "¿Texto de la pregunta?",
        "respuestas": ["Opción A", "Opción B", "Opción C", "Opción D"],
        "correcta": 1,  # Base 0: Opción B
        "feedback": "Explicación técnica de la solución."
    }
]

export_dict_to_moodle_xml(preguntas, "mis_preguntas.xml", category_name="Mi Unidad Didáctica")
```
