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

Este ejercicio evalúa el rendimiento al procesar archivos de texto masivos con diferentes niveles de complejidad computacional. Ambos archivos constan de **521.356 líneas**.

### Prueba 1: Texto de Complejidad Estándar
Archivo con una distribución normal de caracteres y espacios.

**Resultados:**
* **Tiempo total de procesamiento secuencial:** 1.9037 segundos
* **Tiempo total de procesamiento paralelo (Pipeline):** 1.1468 segundos

### Prueba 2: Texto de Alta Dificultad Computacional
Archivo diseñado específicamente para estresar el procesador y las funciones de limpieza. 
**Dificultades introducidas:**
1. **Exceso de espacios y tabulaciones:** Líneas con cientos de espacios en blanco al inicio y al final, obligando a la función `.strip()` a iterar mucho más para limpiar cada extremo.
2. **Líneas excesivamente largas en minúsculas:** Cadenas de texto repetitivas de gran longitud para forzar a la función `.upper()` a transformar una cantidad masiva de caracteres por ciclo.
3. **Mayor peso en memoria:** Al multiplicar el tamaño de cada línea, se eleva considerablemente la carga de lectura y escritura en disco.

**Resultados:**
* **Tiempo total de procesamiento secuencial:** 3.5355 segundos
* **Tiempo total de procesamiento paralelo (Pipeline):** 3.4346 segundos

### Análisis de Rendimiento (Texto)
Los resultados del Ejercicio 2 muestran un comportamiento muy interesante del procesamiento en paralelo frente a diferentes tipos de carga:

* **Con carga computacional normal (Prueba 1):** El modelo paralelo es aproximadamente un **40% más rápido**. La distribución de las tareas compensa ampliamente el costo de la paralelización.
* **Con carga computacional extrema (Prueba 2):** Los tiempos generales casi se duplican para ambos enfoques (pasando de ~1.9s a ~3.5s) debido a la pesada carga de limpieza (`strip`) y conversión (`upper`). Aunque el enfoque paralelo sigue siendo más rápido (3.43s vs 3.53s), **la brecha de rendimiento se cierra drásticamente**. 
Esto ocurre porque, ante líneas tan largas y pesadas, el "cuello de botella" deja de ser exclusivamente el procesamiento en la CPU y pasa a ser la **velocidad de lectura/escritura del disco (I/O)** y el movimiento de grandes bloques de memoria entre los procesos. Los 12 núcleos están listos para trabajar, pero tienen que esperar a que el sistema operativo mueva estos datos masivos, limitando la ventaja de la paralelización.