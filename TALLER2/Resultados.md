# Resultados de Procesamiento: Secuencial vs Paralelo

## Ejercicio 1: Procesamiento de Imágenes

### Metodología y Condiciones de las Pruebas

Para garantizar que las pruebas fueran completamente justas y evitar conflictos de lectura/escritura o caché cruzado, **cada ejecución (secuencial y paralela) tuvo su carpeta independiente de imágenes**. Ambas carpetas en cada caso de prueba contenían exactamente los mismos archivos y el mismo número de imágenes.

Adicionalmente, todas las ejecuciones de procesamiento paralelo fueron configuradas para utilizar un total de **12 núcleos**.

### Prueba 1: Conjunto de 190 Imágenes
* **Tiempo total de procesamiento secuencial:** 2.8000 segundos
* **Tiempo total de procesamiento paralelo:** 0.9504 segundos

### Prueba 2: Conjunto de 50 Imágenes
* **Tiempo total de procesamiento secuencial:** 0.8927 segundos
* **Tiempo total de procesamiento paralelo:** 0.7916 segundos

### Prueba 3: Conjunto de 20 Imágenes
* **Tiempo total de procesamiento secuencial:** 0.4020 segundos
* **Tiempo total de procesamiento paralelo:** 0.5986 segundos

### Análisis de Rendimiento (Imágenes)
Al observar las tres pruebas, se evidencia claramente el impacto del *overhead* (el tiempo y recursos que consume el sistema para gestionar múltiples hilos o procesos) al distribuir el trabajo en 12 núcleos, el cual varía drásticamente según la carga de trabajo:

* **Con carga alta (190 imágenes):** El enfoque paralelo es significativamente superior (casi 3 veces más rápido). Aquí hay suficientes datos para que el trabajo simultáneo de los 12 núcleos justifique con creces el costo de coordinarlos.
* **Con carga media (50 imágenes):** El enfoque paralelo sigue ganando, pero la diferencia es mínima (aproximadamente 0.1 segundos). El beneficio de la paralelización apenas logra superar el tiempo extra que toma dividir las tareas.
* **Con carga baja (20 imágenes):** El procesamiento secuencial resulta ser **más rápido**. En este caso, el tiempo que el sistema invierte en levantar la concurrencia, distribuir apenas 20 imágenes entre 12 núcleos distintos y recolectar los resultados, es mayor que el tiempo necesario para que un solo núcleo las procese una tras otra.

---

## Ejercicio 2: Procesamiento de Texto de Gran Escala

Este ejercicio evalúa el rendimiento al procesar un archivo de texto masivo.

### Características del Archivo de Entrada
* **Líneas totales:** 521.356
* **Caracteres totales:** 111.760.632 (aprox. 111 MB de texto puro)

### Resultados de Ejecución

**Procesamiento Secuencial**
* **Tiempo total:** 1.9037 segundos
* **Archivo de salida:** `...\TALLER2\texto_salida_secuencial.txt`

**Procesamiento Paralelo (Pipeline)**
* **Tiempo total:** 1.1468 segundos
* **Archivo de salida:** `...\TALLER2\texto_salida_pipeline.txt`

### Análisis de Rendimiento (Texto)
Para el procesamiento de este volumen de texto (más de 111 millones de caracteres), el enfoque paralelo o de *pipeline* demuestra ser aproximadamente un **40% más rápido** que el enfoque secuencial. La reducción del tiempo de ejecución indica que, ante cargas de datos masivas como un archivo de 521 mil líneas, el costo computacional de dividir y gestionar la carga de trabajo paralela está más que justificado por el ahorro en el tiempo total de procesamiento.