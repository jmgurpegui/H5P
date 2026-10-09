# Entorno de Creación de Cursos H5P para EducaMadrid y Moodle

Este entorno está preparado como **plantilla modular de producción** para compilar cursos interactivos en formato H5P (`H5P.InteractiveBook 1.7` y `H5P.QuestionSet 1.20`) compatibles al 100% con EducaMadrid y plataformas Moodle.

---

## 📁 Estructura del Espacio de Trabajo

```text
/home/jmgurpegui/H5P/
├── build.py                       # 🚀 Script ejecutable para compilar cualquier curso (python3 build.py)
├── REQUISITOS_CURSOS_H5P_EDUCAMADRID.md # 📋 Normativa oficial, compatibilidad y whitelist Moodle
├── h5p_libraries/                 # 📚 Caché oficial de librerías máquina H5P (FontAwesome, JoubelUI, QuestionSet, etc.)
│
├── plantilla_curso_h5p/           # 🧩 PLANTILLA MODULAR PARA NUEVOS CURSOS
│   ├── curso_config.json          # ⚙️ Configuración central: títulos, capítulos, vídeos y rutas
│   ├── build_desde_plantilla.py   # 🔄 Motor de compilación a paquetes .h5p
│   ├── xml_moodle_parser.py       # 📑 Parser de preguntas en formato Moodle XML
│   ├── h5p_utils.py               # 🛠️ Helpers H5P, validación whitelist y formateo responsive
│   │
│   ├── contenido/                 # 📖 Contenidos teóricos en HTML limpio (100% desacoplados)
│   │   ├── 00_portada.html        # Portada y guía didáctica
│   │   ├── 01_tema_fundamentos.html # Tema teórico modular
│   │   └── 02_mediateca.html      # Mediateca audiovisual y enlaces
│   │
│   ├── evaluacion/                # 📝 Banco de evaluación oficial
│   │   ├── preguntas_moodle.xml   # Preguntas en formato Moodle XML (<quiz>)
│   │   ├── validador_xml.py       # Validador de estructura y balance de opciones
│   │   ├── preguntas_economia_circular.xml # Banco de referencia (48 preguntas)
│   │   └── preguntas_retos_agenda2030.xml  # Banco de referencia (48 preguntas)
│   │
│   └── imagenes/                  # 🖼️ Recursos gráficos (PNG, JPG, BMP)
│       └── logo2026.bmp           # Logotipo institucional
│
└── _archivo_cursos_anteriores/    # 🗄️ Histórico de cursos previos compilados y scripts auxiliares
```

---

## 🚀 Cómo Crear un Nuevo Curso en 3 Pasos

### 1. Redactar el Contenido Teórico
Edita o añade tus temas HTML en `plantilla_curso_h5p/contenido/`:
- Usa texto estándar en HTML con etiquetas semánticas (`<h2>`, `<p>`, `<ul>`, `<table>`).
- **Regla estricta:** Todos los textos deben usar **colores oscuros de alto contraste** (`#0f172a`, `#14532d`, `#0369a1`). Prohibidos textos de colores claros.

### 2. Definir las Preguntas en Moodle XML
Edita `plantilla_curso_h5p/evaluacion/preguntas_moodle.xml`:
- Formato XML de Moodle nativo (`<quiz> ... <question type="multichoice">`).
- Este mismo archivo XML se puede importar directamente en el **Banco de Preguntas de EducaMadrid** sin modificar código.

### 3. Configurar y Compilar
Ajusta `plantilla_curso_h5p/curso_config.json` con los títulos y capítulos de tu curso y ejecuta:

```bash
python3 build.py
```

El compilador generará automáticamente dos paquetes listos para subir al aula virtual:
1. **`Curso_Modelo_Plantilla.h5p`** (Libro Interactivo con teoría, infografías, vídeos y test final).
2. **`Evaluacion_Modelo_Plantilla.h5p`** (Cuestionario independiente para exámenes oficiales en Moodle).

---

## 📱 Características Técnicas Garantizadas

- **Máxima compatibilidad móvil/tablet:** Indicador de progreso textual (`progressType: "textual"`), evitando el desbordamiento horizontal de puntos en teléfonos.
- **Sin opción de ver la solución:** El botón de ver la respuesta correcta está deshabilitado durante la realización de la prueba y en la pantalla de resultados.
- **Botones claros en español:** Botones concisos adaptados a pantallas táctiles (*«Siguiente»*, *«Anterior»*, *«Comprobar respuesta»*, *«Finalizar prueba»*, *«Guardar calificación»*).
- **Moodle Whitelist 100% superada:** Todos los recursos gráficos se empaquetan en formatos permitidos (`png`, `jpg`, `bmp`), evitando bloqueos en EducaMadrid.
