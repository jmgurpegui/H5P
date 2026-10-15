# Curso Interactivo: Circuitos de Alumbrado y Señalización del Automóvil

Este directorio contiene el **paquete H5P oficial y banco de evaluación Moodle XML** para la Unidad de Trabajo sobre **Circuitos de Alumbrado y Señalización** en Formación Profesional (CFGM Electromecánica de Vehículos Automóviles - Módulo: *Circuitos Eléctricos Auxiliares del Vehículo*).

Diseñado cumpliendo estrictamente la **especificación técnica de EducaMadrid**, los **5 Pilares Pedagógicos de Aprendizaje Activo** y las pautas de **accesibilidad universal (WCAG 2.1 AA / AAA)** y diseño responsive para smartphones y tablets.

---

## 📁 Estructura del Módulo `CircuitosAlumbrado/`

```text
CircuitosAlumbrado/
├── Curso_Circuitos_Alumbrado_Automocion.h5p # Paquete interactivo certificado para EducaMadrid (6.9 MB)
├── evaluacion_circuitos_alumbrado.xml       # Banco sumativo oficial Moodle XML (25 preguntas)
├── generar_curso_alumbrado.py               # Script generador maestro con 5 capítulos y 16 actividades
├── generar_imagenes.py                      # Generador de esquemas e imágenes técnicas en alta resolución
├── images/                                  # Imágenes técnicas rasterizadas (PNG) certificadas
│   ├── proyector_elipsoidal_de.png          # Proyector DE, lámpara en F1, diafragma a 15° y haz asimétrico
│   ├── regloscopio_ajuste_faros.png         # Pantalla metrológica a 25m y tolerancias ITV (-1.0% a -1.5%)
│   ├── esquema_alumbrado_reles.png          # Esquema eléctrico normalizado DIN con relés 56a y 56b
│   ├── esquema_intermitencia_warning.png    # Circuito de intermitencia con relé 49/49a y conmutador warning
│   └── diagnosis_caida_tension.png          # Guía metrológica de medición de caídas de tensión en carga
└── artifacts/
    └── Iluminación Automotriz/
        └── Iluminación Automotriz.md        # Informe técnico y síntesis curricular extraída de NotebookLM
```

---

## 🗺️ Mapa Curricular: Los 5 Capítulos y su Correspondencia

El curso sintetiza los 15 epígrafes de la unidad curricular en **5 capítulos modulares** con andamiaje pedagógico en 4 fases:

| Capítulo H5P | Epígrafes Cubiertos | Contenidos Nucleares y Actividades Formativas |
| :--- | :--- | :--- |
| **Cap. 1: Circuitos de Alumbrado Principal** | 6.1, 6.2, 6.3, 6.4 | * Luz de posición (A, R), cruce asimétrico (15° ECE R112) y carretera (Bixenón, Matrix LED y Láser).<br>* Esquema de relés normalizado DIN (Líneas 30, 15, 31, 56, 56a, 56b, 58).<br>* Sensor crepuscular en parabrisas y encendido automático por BCM.<br>* **Interacciones**: *Hotspots proyector DE*, *Arrastre de bornes DIN*, autocomprobaciones. |
| **Cap. 2: Señalización Óptica y Maniobra** | 6.7, 6.8, 6.9, 6.10, 6.11 | * Intermitentes (60-120 ppm, 1-2 Hz) y aviso acústico de avería por caída de carga.<br>* Warning prioritario a Línea 30 permanente.<br>* Luces diurnas DRL (ECE R87) y riesgo de zaga apagada.<br>* Luces de freno (S1, S2, S3 central), frenada adaptativa y modulación PWM.<br>* Luz de marcha atrás (AR).<br>* **Interacciones**: *Checklist pre-ITV*, *Arrastre de magnitudes*, autocomprobaciones. |
| **Cap. 3: Alumbrado Especial y Confort Interior** | 6.5, 6.6, 6.12 | * Faros antiniebla delanteros (B/F3): haz rasante y prohibición en suelo mojado.<br>* Pilotos antiniebla traseros (F, 150-300 cd): **separación obligatoria de 10 cm con luz de freno** (ECE R48) y enclavamiento eléctrico con cruce.<br>* Iluminación interior: temporización (*theater dimming*) por BSI/UCH y función 'Night Panel'.<br>* **Interacciones**: *Reto de enclavamiento y piña de remolque*, *Acordeón normativo*. |
| **Cap. 4: Cálculo Electrotécnico y Regulación de Faros** | 6.13, 6.14 | * Sensibilidad luminosa: caída de 0,5V resta 15% de luz; 1,0V resta 28%.<br>* Cálculo de corriente (I = P/V), sección por caída de tensión admisible (ΔV ≤ 0,3V) y calibre de fusibles.<br>* Reglaje con regloscopio a 25 m: caída descendente -1,0% a -1,5% en turismos.<br>* Efecto del desreglaje: +1% arriba multiplica x20 el deslumbramiento; -2,5% reduce 50% de visión.<br>* Regulación automática dinámica obligatoria para flujo > 2.000 lm.<br>* **Interacciones**: *Arrastre de cálculo guiado*, *Fórmulas semánticas*. |
| **Cap. 5: Diagnosis y Localización de Averías** | 6.15 | * Redes multiplexadas (BCM, CAN, LIN): chequeo en frío y en caliente.<br>* Drivers LED, gestión térmica de juntura Tj y códigos DTC.<br>* Fallo por degradación de laca ámbar (directiva RoHS sin cadmio) emitiendo luz blanca ilegal.<br>* Medición metrológica de caídas de tensión bajo carga (masa ≤ 0,1V, positivo ≤ 0,3V).<br>* **Interacciones**: *Reto de masa sulfatada*, *Lista de cotejo sistemática de diagnosis*. |

---

## 🛠️ Compilación y Validación

Desde la raíz del repositorio, puedes gestionar el curso con el script maestro:

```bash
# Compilar y certificar este curso y su banco XML
python3 build.py alumbrado

# Compilar todos los cursos del repositorio
python3 build.py todos

# Validar el banco Moodle XML
python3 build.py validar CircuitosAlumbrado/evaluacion_circuitos_alumbrado.xml

# Validar el paquete H5P generado
python3 build.py validar CircuitosAlumbrado/Curso_Circuitos_Alumbrado_Automocion.h5p
```

---

## 📥 Despliegue en el Aula Virtual (Moodle / EducaMadrid)

### 1. Actividad Formativa H5P
1. Añade una actividad tipo **H5P** subiendo `Curso_Circuitos_Alumbrado_Automocion.h5p`.
2. En **Calificación**: No requerir nota.
3. En **Finalización de actividad**:
   - Rastreo: *Mostrar la actividad como completada cuando se cumplan las condiciones*.
   - Marcar únicamente: ☑ **El estudiante debe ver esta actividad para completarla**.
   - *(Con esta regla se garantiza el 100% de éxito en el registro de los alumnos en teléfonos y tablets, erradicando el error "No intentado")*.

### 2. Evaluación Sumativa Moodle XML
1. En la administración del curso, ve a **Banco de preguntas ➔ Importar**.
2. Formato: **Formato Moodle XML**.
3. Arrastra `evaluacion_circuitos_alumbrado.xml` e importa las 25 preguntas.
4. Crea una actividad tipo **Cuestionario (`mod_quiz`)**, selecciona las preguntas del banco y define intentos, tiempo y nota para el Libro de Calificaciones.
