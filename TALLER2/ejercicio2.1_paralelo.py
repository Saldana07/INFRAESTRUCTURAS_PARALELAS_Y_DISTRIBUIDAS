import time
import multiprocessing as mp
import threading

# Tamaño del lote (puedes ajustarlo según la RAM/CPU)
TAMANO_LOTE = 10000

"""Lectura del archivo por lotes"""
def leerArchivo(ruta_entrada, salida):
    try:
        with open(ruta_entrada, 'r', encoding='utf-8') as f:
            lote = []
            for linea in f:
                lote.append(linea)
                if len(lote) >= TAMANO_LOTE:
                    salida.put(lote)
                    lote = []  # Reiniciar lote
            
            # Enviar las últimas líneas restantes si las hay
            if lote:
                salida.put(lote)
    finally:
        salida.put(None)  # Señal de fin de datos

"""Depuración de espacios por lotes"""
def eliminarEspacios(entrada, salida):
    while True:
        lote = entrada.get()
        if lote is None:
            salida.put(None)
            break
        # Procesa todo el bloque de líneas a la vez
        lote_procesado = [linea.strip() for linea in lote]
        salida.put(lote_procesado)

"""Convertir texto a mayúsculas por lotes"""
def convertirMayus(entrada, salida):
    while True:
        lote = entrada.get()
        if lote is None:
            salida.put(None)
            break
        # Procesa todo el bloque a la vez
        lote_procesado = [linea.upper() for linea in lote]
        salida.put(lote_procesado)

"""Crear archivo de salida escribiendo por lotes"""
def crearDoc(entrada, ruta_salida):
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        while True:
            lote = entrada.get()
            if lote is None:
                break
            # Escribe todo el bloque en una sola operación de disco (I/O acelerado)
            f.writelines(linea + '\n' for linea in lote)

def procesar_texto_pipeline(ruta_entrada, ruta_salida):
    """Arma el pipeline con comunicación por lotes"""
    cola_lectura_eliminacion = mp.Queue()
    cola_eliminacion_mayus = mp.Queue()
    cola_mayus_creacion = mp.Queue()

    hilos = [
        threading.Thread(target=leerArchivo, args=(ruta_entrada, cola_lectura_eliminacion)),
        threading.Thread(target=eliminarEspacios, args=(cola_lectura_eliminacion, cola_eliminacion_mayus)),
        threading.Thread(target=convertirMayus, args=(cola_eliminacion_mayus, cola_mayus_creacion)),
        threading.Thread(target=crearDoc, args=(cola_mayus_creacion, ruta_salida)),
    ]

    # 1. Iniciar TODOS los hilos en paralelo
    for h in hilos:
        h.start()

    # 2. Esperar a que TODOS los hilos terminen
    for h in hilos:
        h.join()

if __name__ == '__main__':
    ruta_entrada = "C:/Users/sebas/Desktop/Universidad/PARALELAS/TALLER2/texto_entrada.txt"
    ruta_salida = "C:/Users/sebas/Desktop/Universidad/PARALELAS/TALLER2/texto_salida_pipeline.txt"

    inicio = time.time()
    procesar_texto_pipeline(ruta_entrada, ruta_salida)
    fin = time.time()

    print(f"Tiempo total de procesamiento paralelo (por lotes): {fin - inicio:.4f} segundos")
    print(f"Archivo procesado guardado en {ruta_salida}")