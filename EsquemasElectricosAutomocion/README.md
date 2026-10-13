# Curso H5P: Interpretación y Diagnosis de Esquemas Eléctricos del Automóvil

Este directorio contiene el paquete interactivo H5P compilado y certificado, junto con sus recursos gráficos, scripts generadores y materiales formativos, homologado para **EducaMadrid** y entornos **Moodle**.

---

## 📦 Ficheros y Recursos del Curso

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| **`Curso_Esquemas_Electricos_Automocion.h5p`** | **Paquete H5P oficial precompilado (1.88 MB)**: Listo para subir directamente al Aula Virtual de EducaMadrid como actividad calificada. Incluye los 4 capítulos, 13 actividades interactivas, 50 bloques pedagógicos, 16 librerías base y estilos accesibles. |
| **`generar_curso_esquemas.py`** | **Script generador maestro en Python**: Compila el curso desde cero, resuelve el logotipo institucional (`logo2026.bmp`), inyecta las imágenes técnicas, ensambla el andamiaje en 4 fases y ejecuta la validación oficial. |
| **`images/`** | **Recursos gráficos técnicos de alta resolución**: Figuras oficiales extraídas del manual (mapa conceptual, tabla de colores multimarca, esquemas de climatización de Mercedes-Benz, UCH de Renault, conectores de Ford y luneta térmica de BMW). |
| **Vídeos MP4 formativos** | Archivos de vídeo de apoyo integrados con enlaces de alta velocidad a YouTube en `H5P.Video 1.6` para no sobrecargar el límite de subida del aula virtual. |

---

## 🎓 Estructura Curricular y Pedagógica (4 Unidades)

El curso está estructurado en un contenedor unificado **`H5P.InteractiveBook 1.7`** con capítulos modulares en **`H5P.Column 1.16`**, aplicando la secuencia de andamiaje en 4 fases:

### 1. Unidad 1: Utilidad de la Interpretación de Esquemas Eléctricos de Vehículos
* **1.1 Diagnosis de averías**: Metodología deductiva de los cuatro estados de un circuito (circuito abierto $R=\infty$, cortocircuito a masa $R\approx 0$, cortocircuito a positivo y caídas de tensión parásitas $V_{\text{caída}} = I \times R \le 0.2\text{ V}$).
* **1.2 Localización de componentes en el vehículo**: Identificación topográfica de cajas de fusibles/relés (BJB, CJB, UCH, SAM, FEM) y puntos críticos de masa de carrocería.
* **1.3 Localización de puntos de medición**: Conectores pasamuros, pines de centralitas (ECU/ECM) y **técnica segura de medición con agujas traseras (*back-probing*)**, prohibiendo terminantemente perforar el aislamiento.
* **Actividades Activas**: Checklist táctil de 5 reglas de oro para medir sin averiar, DragText de conceptos de diagnosis y preguntas formativas razonadas con feedback explicativo.

### 2. Unidad 2: Tipos de Esquemas Eléctricos de Vehículos
* **2.1 Esquemas de situación de componentes**: Siluetas 3D de carrocería, planos topográficos y fotografías reales de mazos de cable y puntos de masa de chasis.
* **2.2 Esquemas generales**: Arquitectura global de la red eléctrica, distribución de líneas maestras de potencia (+30 permanente y +15 bajo contacto) y redes de datos multiplexadas (CAN Bus, LIN).
* **2.3 Esquemas de detalle (unifilares desarrollados)**: Circuitos específicos tramo por tramo (inyección, climatización, alumbrado), numeración de vías de conectores, secciones de cable en $\text{mm}^2$ y códigos de color.
* **Actividades Activas**: DragText de selección de esquemas en taller, acordeón desplegable del protocolo de lectura en 4 pasos (de positivo superior a masa inferior) y autocomprobación formativa.

### 3. Unidad 3: Simbología Empleada en los Esquemas Eléctricos de Vehículos
* **3.1 Normalización DIN (DIN 72552 / DIN 40719)**:
  * **Borne 30**: Positivo directo de batería (alimentación permanente).
  * **Borne 15**: Positivo conmutado tras llave de contacto (ignición/encendido).
  * **Borne 31**: Masa / retorno a negativo de batería (chasis).
  * **Borne 50**: Mando del motor de arranque (posición START).
  * **Borne X / 75**: Positivo de accesorios con desconexión automática durante el arranque para preservar la batería.
  * **Bornes 85 y 86**: Bobina de excitación de relé (con diodo supresor de transitorios).
  * **Bornes 30 y 87**: Contacto de potencia de relé (normalmente abierto).
* **3.2 Simbología propia de cada fabricante**: Tablas comparativas de colores de conductores en inglés, alemán y francés; fórmulas semánticas de cálculo de sección de cable.
* **Actividades Activas**: DragText de emparejamiento de bornes DIN 72552, reto crítico sobre inversión de polaridad en relés con diodo y autocomprobación de colorimetría alemana.

### 4. Unidad 4: Estudio de Esquemas Eléctricos de Fabricantes
* **4.1 Mercedes-Benz**: Arquitectura de módulos SAM (`N10/1`), designación de componentes (`W` masas, `N` calculadores, `X` conectores, `K` relés, `F` fusibles) y regla de color alemana (marrón `BN` masa, rojo `RD` positivo).
* **4.2 Ford**: Sistema de cuadrículas y coordenadas, designación alfanumérica de circuitos (ej. `91-PG30A.75BK/WH`), cajas BJB/CJB, empalmes soldados (`S`) y masas (`G`).
* **4.3 Renault**: Sistema numérico universal (`120` inyección, `645` UCH, `597` UPC, `103` alternador, `104` clausor, `107` batería, `163` arranque), conectores modulares coloreados (`BA`, `GR`, `NO`) y prefijos de alimentación (`BP`, `AP`).
* **4.4 BMW**: Sistema ISTA y WDS, nomenclatura de conectores `X` (`X11004`, `X18284`), colores en idioma alemán (`BR` marrón masa, `RT` rojo positivo, `SW` negro contacto, `WS/GE` bus CAN) y señales Kl. 30<46.
* **Actividades Activas**: DragText de descodificación de cables multimarca, acordeón de consulta rápida y evaluación formativa multimarca.

---

## 🛠️ Cómo Regenerar y Validar el Paquete

Para volver a compilar el paquete tras realizar modificaciones en los textos o añadir nuevas actividades:

```bash
# Desde la raíz del repositorio
python3 EsquemasElectricosAutomocion/generar_curso_esquemas.py

# O validar manualmente cualquier archivo H5P
python3 plantilla/validar_h5p_educamadrid.py EsquemasElectricosAutomocion/Curso_Esquemas_Electricos_Automocion.h5p
```

---

## ✅ Certificación Técnica Oficial EducaMadrid

* **Whitelist Moodle**: 100% CUMPLIDO (0 `.html` locales, 0 `.svg`).
* **Clausura de librerías**: 16 librerías homologadas incluidas físicamente en la raíz del ZIP.
* **Anidamiento en Column**: 100% verificado (`{"content": ..., "useSeparator": "auto"}` con UUIDv4 únicos).
* **Fórmulas matemáticas**: HTML semántico (`<sub>`, `<sup>`, `.tech-formula`) sin LaTeX crudo.
* **Fugas de CSS**: Cero etiquetas `<style>` en bloques HTML; estilos inyectados directamente en librerías base.
* **Accesibilidad WCAG 2.1 AA / AAA**: Contraste alto con texto Slate 900 (`#0f172a`), cajas con bordes accesibles, botones y checkboxes $\ge 44 \times 44\text{ px}$ y textos alternativos `alt` descriptivos en todas las imágenes.
