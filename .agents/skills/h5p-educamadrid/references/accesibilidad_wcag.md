# Directrices de Accesibilidad Universal y Legibilidad (WCAG 2.1 AA / AAA)

Este documento describe los estándares de diseño inclusivo aplicados en los cursos H5P homologados para EducaMadrid y Moodle, cumpliendo la normativa europea (EN 301 549) y española (Real Decreto 1112/2018).

---

## 1. Ratios de Contraste Cromático de Textos

* **Texto general**: Mínimo 4.5:1 (WCAG AA). En nuestra plantilla superamos **7:1** (WCAG AAA) en todos los elementos principales:
  * Cuerpo de texto sobre fondo blanco: Slate 900 (`#0f172a`), con ratio **> 13:1**.
  * Encabezados de tarjetas: Azul marino (`#0c4a6e`), con ratio **> 9:1**.
  * Hero Banner: Texto blanco y subtítulo `#f0f9ff` sobre gradiente azul marino oscuro, con ratio **> 8:1**.
* **Insignias y Etiquetas (`.tech-badge`)**:
  * `.badge-blue`: fondo `#f0f9ff`, texto `#0c4a6e`, borde `#0284c7` (ratio **> 9:1**).
  * `.badge-yellow`: fondo `#fef9c3`, texto `#713f12`, borde `#ca8a04` (ratio **> 7.5:1**).
  * `.badge-green`: fondo `#dcfce7`, texto `#14532d`, borde `#16a34a` (ratio **> 7.2:1**).
  * `.badge-red`: fondo `#fee2e2`, texto `#7f1d1d`, borde `#dc2626` (ratio **> 7.8:1**).
  * `.badge-purple`: fondo `#f3e8ff`, texto `#581c87`, borde `#9333ea` (ratio **> 8:1**).
* **Cajas de Alerta Contextuales (`.alert-box`)**:
  * Textos oscuros intensos (`#450a0a`, `#451a03`, `#082f49`, `#052e16`) garantizando ratios **> 9:1** sobre sus fondos pastel.

---

## 2. Doble Señalización (Accesibilidad para Daltonismo)

* Toda advertencia, estado o resultado debe incluir un icono identificativo (`⚠️`, `📋`, `⚡`, `✓`, `[ERROR]`, `[CORRECTO]`) o texto semántico explicativo, para que usuarios con daltonismo puedan distinguir perfectamente la categoría del mensaje sin depender del color.

---

## 3. Tipografía Accesible y Alineación

* **Tamaño base**: `1rem` (16px) escalable mediante preferencias del navegador.
* **Interlineado**: `line-height: 1.65` para maximizar la legibilidad en pantallas táctiles y reducir la fatiga visual.
* **Alineación a la izquierda**: Prohibido el texto justificado (`text-align: justify`), ya que genera espaciados irregulares ("ríos") que perjudican severamente a personas con dislexia o dificultades de lectura.

---

## 4. Navegación por Teclado y Foco Visible (`:focus-visible`)

* Todo elemento interactivo (enlaces, botones, selectores de opciones, acordeones) cuenta con un anillo de foco accesible de alto contraste:
  ```css
  :focus-visible {
    outline: 3px solid #0284c7 !important;
    outline-offset: 3px !important;
  }
  ```

---

## 5. Objetivos Táctiles Accesibles (Touch Targets)

* En talleres de formación profesional, los alumnos interactúan con tablets o smartphones llevando guantes de trabajo o con manos en movimiento.
* Todos los botones (`.btn-sim`, `.btn-action`) y elementos de checklist (`.tech-checklist-item`) tienen un área mínima de **44 x 44 px**, cumpliendo el criterio WCAG 2.1 Target Size.

---

## 6. Textos Alternativos Significativos en Imágenes (`alt`)

* Cada imagen técnica (`H5P.Image 1.1`) debe incorporar un atributo `alt` que describa el valor técnico del gráfico (p. ej., *"Oscilograma de señal CAN-Bus en par trenzado mostrando tensiones recesiva de 2.5 V y dominante diferencial de 2.0 V"*), evitando textos vacíos o genéricos como *"imagen"* o *"esquema"*.
