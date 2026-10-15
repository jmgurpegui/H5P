# Requisitos Técnicos y Seguridad H5P para EducaMadrid y Moodle

Este documento detalla las normas de seguridad informática, empaquetado, arquitectura semántica y compatibilidad de librerías para la plataforma EducaMadrid (Moodle).

---

## 1. La Whitelist Estricta de Archivos en `content/`

El validador institucional de Moodle (`H5PValidator.php`) bloquea la subida de paquetes si detecta cualquier archivo cuya extensión no esté en su lista blanca:

```
json, png, jpg, jpeg, gif, bmp, tif, tiff, eot, ttf, woff, woff2, otf,
webm, mp4, ogg, mp3, m4a, wav, txt, pdf, rtf, doc, docx, xls, xlsx,
ppt, pptx, odt, ods, odp, csv, diff, patch, swf, md, textile, vtt, webvtt, gltf, glb
```

### Prohibiciones Críticas
1. **PROHIBIDO archivos `.svg`**: Moodle los bloquea por riesgo de inyección de código (*Stored XSS*). Deben rasterizarse a **PNG o JPEG** en alta resolución (1200 a 1600 px).
2. **PROHIBIDO archivos `.html` locales en `content/`**: Causan error inmediato `not-in-whitelist`.
3. **Multimedia pesado**: Los vídeos (`.mp4`, `.webm`) y audios pesados deben alojarse en la **Mediateca de EducaMadrid** e incrustarse mediante URL externa en `H5P.Video 1.6` o `H5P.InteractiveVideo 1.27`.

---

## 2. Clausura Física de Dependencias en el ZIP

EducaMadrid no descarga librerías dinámicamente si el usuario carece de privilegios de administrador.
* **Norma**: Todas las librerías declaradas en `h5p.json` (`preloadedDependencies`) deben incluir físicamente su carpeta completa en la raíz del ZIP resultante.
* **Matriz Homologada de Versiones**:
  * `H5P.InteractiveBook`: 1.7 (v1.7.5)
  * `H5P.Column`: 1.16 (v1.16.7)
  * `H5P.MultiChoice`: 1.16
  * `H5P.TrueFalse`: 1.8
  * `H5P.DragText`: 1.10
  * `H5P.ImageHotspots`: 1.10
  * `H5P.Text`: 1.1
  * `H5P.Question`: 1.5
  * `H5P.QuestionSet`: 1.20 (v1.20.31)
  * `H5P.AdvancedText`: 1.1
  * `H5P.Accordion`: 1.0
  * `H5P.Image`: 1.1
  * `H5P.Video`: 1.6
  * `FontAwesome`: 4.5
  * `H5P.JoubelUI`: 1.3
  * `H5P.FontIcons`: 1.0
  * `H5P.Transition`: 1.0
  * `jQuery.ui`: 1.10

### Metadatos de Autoría en `h5p.json` (`authors` y `role`)
Si se declara `authors`, cada elemento de la lista debe incluir obligatoriamente las claves `name` y `role`:
```json
"authors": [
  {
    "name": "Profesorado de Automoción",
    "role": "Author"
  }
]
```
> [!CAUTION]
> Omitir `"role"` en `authors` provoca el rechazo inmediato en Moodle: *"La propiedad requerida role está faltando de h5p.json. El archivo principal h5p.json no es válido"*.

---

## 3. Prevención de Pantalla en Blanco (*White Screen of Death*)

En `H5P.Column 1.16`, cada elemento en `params.content` debe estar envuelto obligatoriamente dentro de un objeto grupo con `content` y `useSeparator: "auto"`:

```json
{
  "content": [
    {
      "content": {
        "library": "H5P.AdvancedText 1.1",
        "params": { "text": "<p>Contenido técnico...</p>" },
        "subContentId": "6b2a0c64-2db3-4318-9717-386d34bcf1b3",
        "metadata": { "title": "Título de la Sección" }
      },
      "useSeparator": "auto"
    }
  ]
}
```

* Si se omite el envoltorio exterior, el motor arroja `TypeError: Cannot read properties of undefined (reading 'library')` y deja la pantalla en blanco.
* Todo componente instanciable debe incluir un UUIDv4 único en `subContentId` y una cadena descriptiva en `metadata.title`.

---

## 4. Fórmulas Matemáticas y Magnitudes Eléctricas (Sin LaTeX)

1. **Prohibido LaTeX (`$ ... $`, `$$ ... $$`, `\text{}`)**:
   - `H5P.AdvancedText 1.1` no ejecuta MathJax ni KaTeX; el código fuente queda visible y roto en pantalla.
2. **Estándar Oficial: HTML Semántico + Unicode**:
   - Subíndices: `<sub>` (ej. `V<sub>diff</sub>`, `V<sub>ADC</sub>`, `I<sub>carga</sub>`).
   - Superíndices: `<sup>` (ej. `10<sup>−9</sup> S`, `mm<sup>2</sup>`).
   - Símbolos Unicode: `×` (`&times;`), `−` (`&minus;`), `Ω` (`&Omega;`), `µ` (`&micro;`), `Δ` (`&Delta;`), `≥` (`&ge;`), `≤` (`&le;`).
3. **Clases CSS Normalizadas**:
   - En línea: `<span class="tech-formula">V = I × R</span>`.
   - En bloque:
     ```html
     <div class="tech-formula-block">
       <span class="tech-formula">V<sub>diff</sub> = V<sub>CAN-H</sub> − V<sub>CAN-L</sub> = 3.5 V − 1.5 V = <strong>2.0 V</strong></span>
       <div class="tech-formula-desc">Tensión diferencial calculada entre líneas del bus CAN.</div>
     </div>
     ```

---

## 5. Prevención de Fugas de Código CSS (*CSS Leakage*)

* **Cero etiquetas `<style>` en `H5P.AdvancedText`**: El sanitizador de H5P elimina las etiquetas `<style>` pero deja el texto CSS interno visible en pantalla como texto plano.
* **Solución**: Los estilos globales se inyectan en las hojas `.css` de las librerías base (`H5P.InteractiveBook-1.7/dist/h5p-interactive-book.css` y `H5P.Column-1.16/styles/h5p-column.css`) mediante `plantilla/append_css_to_libraries.py`.

---

## 6. Cabecera Institucional y Formatos de Imagen (`logo2026`)

* Ubicación obligatoria en el ZIP: `content/images/<nombre_del_logo>`.
* Inserción como primer elemento de cada capítulo mediante el componente nativo **`H5P.Image 1.1`** con texto alternativo accesible (`alt="Comunidad de Madrid - Unión Europea - Formación Profesional Pública"`).
* **Evaluación técnica de formatos para logotipos**:
  * **PNG (`.png`) — Recomendado al 100%**: Canal alfa completo para transparencia real (evita recuadros blancos sobre fondos `#f8fafc` o temas oscuros), compresión sin pérdidas con tipografía y bordes nítidos, y peso óptimo (~100-200 KB).
  * **BMP (`.bmp`) — Soportado pero no recomendado**: Permitido en la whitelist de Moodle, pero carece de canal alfa transparente (forzando fondos rectangulares opacos) y genera un peso excesivo sin comprimir (~1.1 MB a 2 MB).
  * **SVG (`.svg`) — Prohibido**: Bloqueado por seguridad anti-XSS en Moodle.
  * Los generadores resuelven dinámicamente si existe `logo2026.bmp`, `logo2026.png` o `logo2026.jpg`, calculando automáticamente sus dimensiones reales y tipo MIME.

