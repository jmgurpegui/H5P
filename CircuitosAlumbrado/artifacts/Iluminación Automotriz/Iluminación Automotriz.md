# Technical Report: Automotive Lighting Systems and Electrical Circuits

---

### 1. Circuitos de alumbrado y señalización

El sistema de iluminación de un automóvil está constituido por un conjunto de dispositivos optoelectrónicos y electromecánicos distribuidos estratégica y reglamentariamente en las zonas frontal, lateral y trasera del vehículo. Su cometido principal responde de manera estricta al principio de la seguridad vial de **"ver y ser vistos"**. Este sistema proporciona al conductor la radiancia necesaria para operar el vehículo con solvencia perceptiva en condiciones de visibilidad reducida o nocturnidad y, de forma paralela, parametriza la presencia, posición, volumen geométrico, sentido de marcha, tasa de desaceleración e intenciones de maniobra ante el resto de los usuarios de la vía.

De acuerdo con las investigaciones psicofísicas y de siniestralidad vial sintetizadas en el estudio del Real Automóvil Club de España (RACE), el **90% de la información** requerida para la toma de decisiones durante la conducción se capta exclusivamente mediante la vía visual, distribuyéndose el 10% restante entre la estimulación auditiva y el sistema vestibular propioceptivo. En horario diurno, el ojo humano trabaja en un entorno de alta luminancia; sin embargo, al caer la noche, experimenta un agudo déficit de información: la capacidad visual del conductor se degrada hasta situarse en apenas un **20%** respecto a sus valores diurnos. En este régimen foto-receptivo disminuyen drásticamente el contraste lumínico, la agudeza cromática y la precisión en la estimación visual de distancias y velocidades relativas.

Fisiológicamente, el ojo adapta su respuesta dinámica a los cambios de luminancia mediante dos mecanismos concurrentes: la modificación de la sensibilidad química de la retina y el control fotométrico pupilar ejecutado por la contracción o dilatación del iris. Ante una exposición a un deslumbramiento repentino por alta intensidad luminosa incidente, el iris provoca una miosis pupilar abrupta, reduciendo de manera transitoria y crítica la capacidad perceptiva del conductor mientras el ojo no logre reacomodarse al nivel de fondo.

La estandarización cromatica internacional de los emisores lumínicos fue establecida inicialmente en la Convención de Viena sobre el Tráfico de 1949 y consolidada en la Convención sobre la Circulación Vial de las Naciones Unidas de 1968:
*   **Zona Trasera:** Emisión de luz de color rojo.
*   **Zonas Laterales e Indicadores de Dirección:** Emisión de luz de color ámbar (con la salvedad reglamentaria de Norteamérica, donde se admite el rojo en la zaga).
*   **Zona Delantera:** Emisión de luz blanca o amarillo selectivo.

A nivel de arquitectura de esquemática electrónica, existen divergencias estructurales marcadas entre la normativa de representación europea y la norteamericana (SAE/FMVSS). Los esquemas europeos jerarquizan los circuitos mediante líneas de alimentación de corriente estructuradas (líneas 30, 15 y 31 de masa centralizada), con relés dedicados e independientes para los haces de cruce y carretera. En contraste, los esquemas norteamericanos integran frecuentemente líneas interconectadas con lámparas de doble filamento que combinan la luz de posición frontal (*parking light*) y la señalización de giro sobre buses de conmutación multifunción y nodos de masa compartidos.

En el campo de las fuentes luminosas, la tecnología ha evolucionado de manera continua: desde las lámparas incandescentes convencionales con filamento de wolframio, pasando por las lámparas halógenas de tungsteno (encabezadas por la lámpara H1 introducida en Europa en 1962), los sistemas de descarga de alta intensidad (Xenón HID) y los tubos de neón, hasta la consolidación de los diodos emisores de luz (**LED**) y las matrices de estado sólido **Full LED**.

#### Estadística de Siniestralidad Vial (Datos DGT)

| Condición de Luminosidad | N.º de Accidentes | % Accidentes | N.º de Muertes | % Muertes |
| :--- | :--- | :--- | :--- | :--- |
| **Día** | 62.308 | 66% | 2.733 | 58% |
| **Noche y crepúsculo** | 31.701 | 34% | 2.008 | **42%** |
| **Total** | 94.009 | 100% | 4.741 | 100% |
| *Sólo Noche (subconjunto)* | *27.588* | *29%* | *1.755* | *37%* |

---

### 2. Alumbrados de posición, cruce y carretera

La iluminación delantera del vehículo se distribuye en tres funciones fotométricas principales según el alcance, la potencia y la geometría de proyección del haz luminoso:

*   **Corto alcance o luz de cruce:** Proyecta una distribución luminosa frontal y lateral optimizada para iluminar la calzada sin deslumbrar a los demás usuarios. Bajo las reglamentaciones internacionales UNECE (ECE R112/R98), se exige una **Línea de corte asimétrica (*Cut-off line*)** de trazo nítido que proyecta mayor alcance hacia el margen derecho (en sentidos de circulación por la derecha) y limita severamente el flujo luminoso dirigido al carril contrario. Por el contrario, los estándares norteamericanos SAE (FMVSS / CMVSS 108) imponen un control del gradiente de deslumbramiento menos estricto y un corte del haz de perfil más simétrico.
*   **Largo alcance o luz de carretera:** Emite un haz de alta intensidad de radiación divergente centrada en el eje longitudinal, diseñado para la conducción nocturna a alta velocidad en vías carentes de iluminación artificial. Al no incorporar control óptico de deslumbramiento, su uso exige el apagado inmediato ante la presencia de tráfico de frente o precedencia cercana. La normativa europea (CE/ECE) autoriza intensidades máximas de pico y puntos de cálculo fotométrico de candelas superiores a los umbrales máximos permitidos por la normativa estadounidense.
*   **Faros supletorios (*Auxiliary High-Beam Lamps*):** Constituyen proyectores auxiliares de largo alcance destinados a complementar la iluminación principal en áreas desprovistas de red pública. Son de uso habitual en los países nórdicos debido a la escasez de radiación solar durante el invierno, así como en vehículos de competición de rally para ensanchar el campo óptico. En vehículos todoterreno es común su instalación sobre barras transversales en el techo, elevando el plano de emisión para alargar la rasante de proyección y evitar daños por impactos. Su uso e instalación están estrictamente legislados a nivel nacional: en Rusia, el marco legal prohíbe montar más de tres pares de faros frontales en total (sumando la dotación de serie); en Paraguay, se exige que los faros supletorios permanezcan desconectados y cubiertos con una funda de material opaco al transitar por zonas urbanas.

---

### 3. Circuito de posición, cruce y carretera

Las luces de posición delanteras (denominadas en el mercado norteamericano *parking lamps* y conocidas en Rusia como *podfarniki*) definen la presencia y la anchura geométrica del vehículo tanto estacionado como en marcha. Emiten luz blanca continua (admitiéndose el color ámbar de forma exclusiva en Norteamérica) con una intensidad fotométrica estipulada internacionalmente entre **4 y 125 candelas**. Desde finales de la década de 1960, la normativa exige que el circuito mantenga conectadas las luces de posición de forma ininterrumpida mientras estén activas las luces de cruce o de carretera, asegurando una referencia visual lateral remanente en caso de que falle el filamento o módulo del faro principal.

#### Funciones Históricas y Regionales de Posición
*   **StVZO (Alemania):** El reglamento de homologación alemán StVZO (§51c) contempla la función de luz de estacionamiento unilateral (*Parkleuchten*). Con el contacto del vehículo desconectado, el conductor puede activar mediante el mando de intermitencia una luz blanca frontal de baja intensidad y una luz roja trasera en el costado del vehículo expuesto al tráfico, reduciendo el riesgo en vías estrechas sin consumo eléctrico global.
*   **Sistema Dim-Dip (Reino Unido):** Sistema introducido para los vehículos fabricados a partir de abril de 1987. El circuito activaba automáticamente un dispositivo de reducción de intensidad siempre que el encendido del motor estaba activo (posición de contacto ON) y el conductor seleccionaba únicamente las luces de posición. Mediante un potenciómetro en serie, el sistema reducía el voltaje suministrado a las lámparas halógenas de cruce hasta un **10–20%** de su rendimiento nominal (o alimentaba lámparas especiales con una salida de 200 a 800 cd), evitando que los conductores circularan exclusivamente con las luces de posición en zonas urbanas iluminadas. En 1988, el Tribunal de Justicia de las Comunidades Europeas dictaminó la ilegalidad del sistema *Dim-Dip* por constituir una barrera técnica no recogida en la directiva comunitaria de homologación de vehículos (ECE R48).

En términos de consumo energético, las luces de posición operan en un rango de **4 a 10 W** por punto de luz, generando un flujo luminoso de **40 a 130 lúmenes**, frente a la mayor demanda eléctrica y disipación térmica de las ópticas de cruce y carretera.

#### Comparativa de Parámetros de Alumbrado: ECE vs. Norteamérica (SAE/FMVSS)

| Parámetro / Función | Normativa ECE (Europa / Internacional) | Normativa Norteamericana (SAE / FMVSS 108) |
| :--- | :--- | :--- |
| **Color de posición delantera** | Blanco exclusivo | Blanco o Ámbar |
| **Corte de haz de cruce** | Línea de corte asimétrica (*Cut-off line*) afilada (ECE R112/R98) | Simétrico / Menos restrictivo en deslumbramiento |
| **Intensidad de largo alcance** | Mayor límite de intensidad máxima (candelas) | Menor límite de intensidad máxima permitida |
| **Luz de posición delantera** | 4 a 125 candelas | 4 a 125 candelas |

---

### 4. Encendido automático de luces

La integración de unidades de control electrónico (ECU) de carrocería en los sistemas Full LED permite el control direccionado de cada diodo luminoso de forma individual o mediante la agrupación de matriz de puntos (*Matrix LED*). Estos módulos procesan la información suministrada por cámaras de visión artificial y sensores de luminancia ambiental para conmutar, dimar o apagar segmentos diódicos específicos en milisegundos. Esta arquitectura permite mantener activa la iluminación de largo alcance de forma permanente, proyectando una zona de sombra o "corte dinámico" únicamente sobre el área donde se detecta la presencia de otros vehículos, optimizando el campo visual periférico sin deslumbrar.

#### Riesgos Asociados a la Automatización y DRL
Existe un peligro operativo severo derivado de la confusión por parte del conductor entre el encendido automático de las Luces de Conducción Diurna (DRL) y la activación de los faros de cruce. Puesto que las DRL son proyectores frontales de intensidad media/alta pensados únicamente para señalización diurna, al circular en condiciones de penumbra o túneles con las DRL encendidas, la calzada no recibe la iluminación requerida y, de forma crítica, **los pilotos de posición traseros permanecen apagados**, dejando la zaga del vehículo desprotegida y propiciando colisiones por alcance.

---

### 5. Alumbrado antiniebla

Las ópticas antiniebla están calculadas para contrarrestar la dispersión de la luz provocada por la refracción en las gotas de agua en suspensión, bruma, polvo o copos de nieve.

#### Faros Antiniebla Delanteros
Emiten un haz de luz plano y ancho, provisto de una línea de corte superior de altísimo gradiente para evitar que la luz penetre en la masa de niebla y vuelva reflejada hacia los ojos del conductor (efecto estroboscópico o "pared blanca"). Se instalan en el faldón inferior del paragolpes. Pueden emular luz blanca o amarillo selectivo. Su función radica en iluminar los bordes de la calzada a baja velocidad. En la legislación europea, está prohibido su uso sobre pavimentos mojados si no concurre una degradación meteorológica severa, dado que el reflejo de la luz sobre la lámina de agua del suelo deslumbra al tráfico saliente.

#### Pilotos Antiniebla Traseros
Son dispositivos de señalización pasiva que emiten una luz roja de alta intensidad (comprendida entre **150 y 300 candelas** bajo reglamentación UNECE). Su función es penetrar las capas densas de niebla para advertir la presencia de la zaga a larga distancia.

Se autoriza su montaje en disposición única o simétrica doble. Cuando se instala un único piloto, la normativa exige que se sitúe en la línea media del vehículo o en el costado del conductor. La norma ECE R48 impone una separación geométrica mínima de **10 cm** entre el borde de la superficie iluminada del piloto antiniebla trasero y la luz de freno para impedir el enmascaramiento visual de la señal de parada.

#### Comparativa: Alumbrado Antiniebla Delantero vs. Trasero

| Faro Antiniebla Delantero | Piloto Antiniebla Trasero |
| :--- | :--- |
| **Patrón del haz:** Ancho, plano y con corte superior de alto gradiente (*Cut-off*) | **Patrón del haz:** Difuso de alta penetración e intensidad focalizada |
| **Color de emisión:** Blanco o Amarillo Selectivo | **Color de emisión:** Rojo intenso |
| **Ubicación e intensidad:** Montaje bajo en el paragolpes frontal | **Ubicación e intensidad:** 150 a 300 cd; montaje único (centro/lado conductor) o doble simétrico |
| **Restricciones reglamentarias:** Prohibida su activación en suelo mojado sin niebla | **Restricciones reglamentarias:** Separación mínima obligatoria de 10 cm con la luz de freno (ECE R48) |

---

### 6. Circuitos de iluminación antiniebla

El circuito de control del piloto antiniebla trasero funciona mediante una lógica de interbloqueo comandada por un conmutador de mando manual que exige, como condición previa para su activación, el encendido de los faros de cruce o antiniebla delanteros.

Las divergencias reglamentarias internacionales marcan el comportamiento del mercado:
*   **Mercado Europeo (UNECE):** El montaje del piloto antiniebla trasero es obligatorio. El circuito debe incorporar un testigo de control independiente en el cuadro de instrumentos de color amarillo auto (*Amber*) para informar al conductor de su funcionamiento.
*   **Mercado Norteamericano:** La luz antiniebla trasera no es mandatoria bajo el estándar FMVSS 108. Por este motivo, al importar vehículos europeos a EE. UU., los talleres de conversión reconfiguran habitualmente la línea del piloto antiniebla posterior para alimentarla en paralelo con las luces de freno primarias.

---

### 7. Intermitencia y emergencia

El sistema de señalización direccional e indicación de peligro advierte a los demás usuarios sobre los cambios de trayectoria, desplazamientos laterales o la presencia de situaciones de riesgo en la vía.

*   **Cadencia de destello:** La reglamentación internacional establece una frecuencia de intermitencia estable y continua comprendida estrictamente entre **60 y 120 pulsaciones por minuto** (1 a 2 Hz).
*   **Estandarización del color:** Las normas ECE imponen la luz **ámbar** para todos los indicadores de dirección (delanteros, laterales y traseros). En Norteamérica se autoriza el color rojo o ámbar en la zaga. Los estudios de campo ejecutados por la agencia NHTSA (publicados en 2008 y 2009) demostraron que los intermitentes traseros de color ámbar reducen la probabilidad de sufrir colisiones por alcance hasta en un **28%** frente a las señales de color rojo, debido a la nula ambigüedad con el circuito de freno.
*   **Intermitentes secuenciales:** Esta arquitectura se implementó en vehículos emblemáticos como el Ford Thunderbird (1965–1971), Shelby Mustang (1968–1970), Chrysler Imperial (1969) y Nissan Cedric JDM (1971). Los primeros sistemas basaban su lógica en un motor eléctrico que hacía girar, mediante un juego de engranajes reducidos, un eje de tres levas electromecánicas que actuaban sobre los contactos de cada bombilla. Posteriormente, la electromecánica fue sustituida por unidades de control de estado sólido transistorizadas sin componentes móviles. Pese a que la norma FMVSS 108 exigía originalmente que toda la superficie reflectante se iluminase de forma simultánea, las reinterpretaciones normativas permitieron la reintroducción moderna de los sistemas secuenciales dinámicos (iniciada comercialmente en el Ford Mustang 2010 y generalizada por el Grupo Volkswagen).
*   **Repetidores laterales en retrovisores:** El montaje de intermitentes laterales en las carcasas de los espejos retrovisores (introducido por Mercedes-Benz en el Clase SLK R170) ha desplazado a las ópticas de la aleta, demostrando mediante estudios fotométricos una superior visibilidad dentro de los ángulos ciegos laterales.

---

### 8. Circuitos de intermitencia y emergencia

El circuito eléctrico de intermitencia combina la gestión de la palanca de conmutación de dirección con la anulación por prioridad del sistema de emergencia:

*   **Interruptor de Luces de Emergencia (*Hazard Warning Switch*):** Este mando de control independiente puentea la palanca de la columna de dirección. Al ser accionado, conmuta la alimentación de todas las lámparas del circuito de intermitencia de forma simultánea y en fase. La normativa exige la presencia de un testigo óptico de color rojo en el salpicadero con parpadeo sincronizado y la emisión de una señal acústica.
*   **Mecanismos de supervisión de carga y avería:** El sistema dispone de un circuito de detección de corriente. Si el filamento de una bombilla se rompe o existe una interrupción en el consumo eléctrico de un diodo, la caída de carga hace que el relé o módulo electrónico aumente (o reduzca) de forma drástica la frecuencia de parpadeo, proporcionando un chivato audiovisual automático que alerta inmediatamente al conductor del fallo.
*   **Sistemas de pulsador alternativo:** En aplicaciones de transporte urbano de pasajeros (como los autobuses de la Transit Authority de Nueva York desde los años 1950), el conmutador del intermitente se integra en un pedal de suelo accionado por el pie izquierdo del conductor. Esta configuración elimina el mecanismo de retorno mecánico de la columna y permite mantener ambas manos fijas sobre el volante durante la maniobra.

---

### 9. Luces de conducción diurna

Las Luces de Conducción Diurna (DRL, *Daytime Running Lights*) están calculadas para acentuar la visibilidad pasiva del vehículo en movimiento durante la circulación diurna.

#### Variaciones Normativas Regionales
*   **Reglamento ECE (ECE R87):** Exige proyectores diurnos dedicados de color blanco que emitan una intensidad fotométrica comprendida entre **400 y 1200 candelas** proyectadas hacia adelante.
*   **Reglamento Norteamericano:** Permite límites de emisión superiores de hasta **7000 candelas**, autorizando el uso de los faros de largo alcance funcionando a voltaje reducido mediante modulación por ancho de pulsos (PWM), configuración que provoca frecuentes quejas por deslumbramiento.

#### Lógica del Circuito de Control
Cuando un emisor DRL se encuentra posicionado a corta distancia del intermitente delantero dentro de la misma tulipa óptica, la unidad de control atenuará de forma automática la intensidad de la luz diurna (función *dimming*) o la apagará por completo en el lado correspondiente mientras el intermitente adyacente se encuentre parpadeando, impidiendo el enmascaramiento óptico de la señal de giro.

---

### 10. Luces de freno

Las luces de freno se conmutan instantáneamente al detectar la presión sobre la bomba hidráulica o mediante el sensor del pedal, emitiendo una luz de color rojo continuo de intensidad superior a la de las luces de posición traseras.

*   **Valores de intensidad fotométrica:** La reglamentación ECE estipula un rango de **60 a 185 candelas** por emisor individual. En el estándar SAE de Norteamérica, el rango exigido se eleva a un intervalo de entre **80 y 300 candelas**.
*   **Tercera luz de freno (CHMSL):** La central de freno elevada (*Center High-Mounted Stop Lamp*) es de instalación obligatoria en Norteamérica desde 1986, Australia (1990), Chile (1994) y Europa (1998). Exige una luz de emisión fija continua (sin destello en condiciones normales). La norma ECE R48 obliga a instalarla en el centro del eje de simetría horizontal, admitiéndose una desviación máxima de **15 cm** solo en portones traseros de apertura asimétrica (como en el furgón Fiat Scudo). Las pruebas de campo iniciales con flotas de taxis reflejaron reducciones en accidentes del 50%, estabilizándose la eficacia real a largo plazo en un 5%.

#### Sistemas de Indicación de Frenado de Emergencia
Ante una deceleración extrema, los fabricantes han desarrollado estrategias de señalización activa:
*   **Mercedes-Benz:** Parpadeo acelerado a alta frecuencia de las luces de freno primarias.
*   **Volvo:** Incremento en la intensidad del flujo luminoso proyectado por las ópticas traseras.
*   **BMW (*Adaptive Brake Lights*):** El módulo de control activa filamentos o diodos secundarios ubicados en las ópticas de posición traseras alimentándolos a alta potencia cuando el módulo ABS detecta una frenada de alta intensidad.
*   **Grupo Volkswagen (VW, Audi, Seat, Škoda):** El sistema **Frenado de emergencia asistido (Emergency Brake Assist / EBA)**, en coordinación con la ECU del ABS, activa de forma automática las luces de emergencia (*hazard lights*), las cuales continúan parpadeando hasta que el vehículo reanuda la marcha o se desactivan manualmente.

---

### 11. Luces de marcha atrás

La función de marcha atrás proporciona la visibilidad trasera necesaria durante las maniobras de retroceso y advierte de forma pasiva a los peatones y demás vehículos sobre la dirección de movimiento del vehículo.

*   **Estándar cromatico:** Emisión de luz **blanca** continua en todo el marco internacional.
*   **Excepciones históricas:** En Australia, Nueva Zelanda y el estado de Washington se autorizó temporalmente la luz de marcha atrás de color ámbar, aprovechando el circuito del intermitente trasero como luz fija. En la actualidad, las reglamentaciones han convergido hacia la obligatoriedad del color blanco.

---

### 12. Iluminación interior del vehículo

La iluminación interior o de cortesía proporciona el flujo luminoso preciso en el habitáculo para el acceso, la lectura de planos y la identificación de mandos sin afectar la visión periférica nocturna.

*   **Componentes del sistema:** Plafones centrales de techo, proyectores en los pozo de pies, guías de luz LED en manillas de puertas, iluminadores de escalones, lámparas para guantera, consolas centrales y proyectores direccionales de lectura.
*   **Atenuación temporizada (*Theater Dimming*):** Circuito electrónico integrado que mantiene la iluminación encendida tras cerrar las puertas, aplicando una rampa de apagado progresivo durante un intervalo de aproximadamente **2 minutos**, o provocando un apagado instantáneo al girar la llave a la posición de encendido del motor.
*   **Instrumentación y ergonomía visual:** El cuadro de instrumentos incorpora iluminación de fondo regulable. Destaca el sistema **"Night Panel"** desarrollado por Saab a partir de tecnología aeronáutica: mediante un interruptor, desactiva la iluminación de todos los instrumentos y pantallas del salpicadero durante la conducción nocturna, manteniendo activo únicamente el velocímetro para evitar el cansancio ocular y preservar la visión nocturna del conductor (reactivando los relojes auxiliares solo ante emergencias del motor).
*   **Redes optoelectrónicas distribuidas:** Iluminación mediante proyectores centrales de descarga Xenón HID o módulos LED que transmiten el flujo luminoso a través de redes de fibra óptica plástica hacia múltiples puntos del habitáculo.

---

### 13. Cálculo y dimensionado de circuitos de iluminación

El cálculo electromecánico para el dimensionado del cableado, los fusibles de protección y las etapas de disipación se basa en la potencia consumida y el flujo luminoso requerido.

#### Parámetros Eléctricos y Fotométricos por Categoría de Lámpara

| Categoría de Señalización | Potencia Eléctrica (Watts) | Flujo Luminoso (Lúmenes) | Intensidad Lumínica (Candelas) |
| :--- | :--- | :--- | :--- |
| **Alta Potencia** (Freno, Intermitentes, Marcha Atrás, Antiniebla Trasero) | 21 W a 27 W | 280 a 570 lm | 22 a 45 cd |
| **Baja Potencia** (Posición, Marcadores Laterales, Iluminación Interior) | 4 W a 10 W | 40 a 130 lm | Variable según función |

#### Dimensionado Térmico y Gestión de Juntura en Sistemas LED
A pesar del bajo consumo de potencia eléctrica de los diodos emisores de luz en relación con su flujo luminoso (alta eficacia luminosa en lm/W), el proceso de recombinación de portadores en la juntura semiconductora del LED no emite radiación infrarroja en el haz de luz (como ocurre con las lámparas halógenas), sino que concentra una elevada carga térmica localizada en el propio encapsulado diódico. 

Esta temperatura de juntura ($T_j$) exige el diseño e integración de **sistemas de gestión térmica específicos** (disipadores pasivos de aluminio extruido o trenzas de cobre, e incluso microventiladores de flujo forzado) dentro del faro. Si la temperatura de juntura excede los límites del fabricante, el rendimiento diódico sufre una severa degradación de flujo luminotécnico y un fallo prematuro. La necesidad de incorporar estas etapas de disipación eleva sensiblemente los costes de fabricación de las ópticas Full LED.

#### Medición e Inspección Fotométrica
La verificación de la intensidad luminosa se efectúa utilizando **luxómetros** integrados en los equipos alineadores de faros (*headlamp testers*), midiendo la iluminancia en lux para determinar el rendimiento fotométrico tanto en el patrón de cruce como en el de carretera.

---

### 14. Regulación de faros

El alineador de faros (o verificador de haz lumínico) es el instrumento metrológico empleado en los centros de Inspección Técnica de Vehículos (ITV) y talleres para ajustar con exactitud la inclinación y la intensidad del haz de proyección.

#### Construcción y Elementos del Alineador de Faros
1.  **Caja Óptica:** Conjunto con apantallamiento fotométrico equipado con una sola lente de luz colimada diseñada para enfocar el patrón del haz sin distorsiones ópticas.
2.  **Columna Vertical de Ajuste:** Estructura graduada montada sobre un riel inferior que permite deslizar la caja óptica lateralmente. Permite regular la altura de medición de la lente en un rango continuo de **500 mm a 1500 mm**, admitiendo la inspección desde turismos hasta vehículos de transporte pesado.
3.  **Sistema de Alineación Longitudinal:** La parte superior de la columna incorpora un espejo visor de alineación o un puntero láser de nivelación para garantizar el paralelo entre la caja óptica y el eje longitudinal del vehículo bajo ensayo.

#### Procedimiento de Inspección e Inclinación del Haz
Durante el proceso de verificación, el haz proyectado por el faro se encauza a través de la lente colimadora y se dibuja sobre una pantalla interna graduada. Esta pantalla dispone de líneas de referencia de color rojo o azul que marcan los porcentajes de inclinación descendente respecto al centro óptico:

*   **0,5%** (Inclinación mínima habitual en turismos)
*   **1,25%**
*   **2%**
*   **2,75%**
*   **3,25% y 4%:** Porcentajes de inclinación aplicados específicamente en la inspección y reglaje de vehículos pesados de carga y autobuses.

El técnico evaluador analiza manualmente la posición de la línea de corte (*cut-off*) proyectada sobre la pantalla graduada, verificando el cumplimiento de los límites de desviación horizontal y vertical marcados por la Directiva de Homologación.

---

### 15. Diagnosis de circuitos de iluminación del vehículo

La diagnosis técnica y el mantenimiento predictivo de los sistemas de iluminación involucran comprobaciones eléctricas, fotométricas y de degradación química de los componentes:

1.  **Detección de averías por consumo de carga:** Verificación mediante el cambio de la frecuencia de destello del relé de intermitencia cuando se rompe un filamento o se interrumpe la carga en un ramal LED, modificando la cadencia de parpadeo como chivato automático para el conductor.
2.  **Degradación del color en lámparas ámbar y directiva RoHS:** Debido a la prohibición del uso de vidrio tintado con cadmio por la directiva europea **RoHS (Restriction of Hazardous Substances)** debido a la toxicidad del metal pesado, las bombillas ámbar modernas sustituyeron el cristal dopado por recubrimientos superficiales de laca sobre vidrio transparente. Los constantes ciclos térmicos de calentamiento y enfriamiento provocan que la laca exterior se agriete, se cuartee y se desprenda del cristal. En consecuencia, la bombilla desgastada emite luz blanca ilegal en la señalización de giro, requiriendo su sustitución inmediata.
3.  **Comprobación de la eficacia lumínica y opacidad:** Diagnóstico del deterioro del haz luminoso mediante luxómetros para cuantificar la pérdida de candelas/lux debida a la opacificación de las tulipas de policarbonato por degradación UV, el envejecimiento de la bombilla halógena o la pérdida de reflectividad en las parábolas reflectoras.
4.  **Inspección de elementos retrorreflectantes (Catadióptricos):** Verificación técnica de los retrorreflectores pasivos obligatorios (rojo en la zaga, ámbar en los laterales y blanco en el frente). Estos elementos garantizan que el vehículo refleje la luz de proyectores externos de vuelta hacia su fuente, manteniendo la visibilidad del automóvil aun cuando exista un fallo total en la red eléctrica del vehículo.