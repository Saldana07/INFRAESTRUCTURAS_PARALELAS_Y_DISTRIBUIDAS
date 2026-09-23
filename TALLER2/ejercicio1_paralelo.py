"""
Ejercicio 1: Descomposición por Dominio (Datos)
Procesamiento paralelo de imágenes (conversión a escala de grises).

Idea de la descomposición por dominio:
    Los DATOS (la lista de rutas de imágenes) se dividen en partes, y la
    MISMA función (convertir_a_gris) se aplica de forma independiente a
    cada parte en un proceso distinto. No hay dependencia entre los datos,
    por lo que el trabajo se reparte fácilmente entre varios núcleos de CPU.
"""

from PIL import Image
import os
import time
from multiprocessing import Pool, cpu_count


def convertir_a_gris(ruta_imagen):
    """Convierte una imagen a escala de grises. Se ejecuta en un proceso
    trabajador distinto para cada imagen que le sea asignada."""
    try:
        imagen = Image.open(ruta_imagen)
        imagen_gris = imagen.convert('L')  # 'L' representa escala de grises
        nombre_archivo, extension = os.path.splitext(ruta_imagen)
        ruta_gris = nombre_archivo + "_gris" + extension
        imagen_gris.save(ruta_gris)
        mensaje = f"Imagen convertida: {ruta_imagen} -> {ruta_gris}"
        print(mensaje)
        return mensaje
    except FileNotFoundError:
        mensaje = f"Error: No se encontró la imagen {ruta_imagen}"
        print(mensaje)
        return mensaje
    except Exception as e:
        mensaje = f"Error al procesar {ruta_imagen}: {e}"
        print(mensaje)
        return mensaje


def procesar_imagenes_paralelo(lista_imagenes, num_procesos=None):
    """Procesa la lista de imágenes en paralelo, repartiendo los datos
    (descomposición por dominio) entre varios procesos con Pool.map."""
    if num_procesos is None:
        num_procesos = cpu_count()
    print(f"Procesando en paralelo usando {num_procesos} núcleos...")
    with Pool(processes=num_procesos) as pool:
        resultados = pool.map(convertir_a_gris, lista_imagenes)

    return resultados


if __name__ == '__main__':
    directorio_imagenes = "C:/Users/sebas/Desktop/Universidad/PARALELAS/TALLER2/img"  
    lista_imagenes = [os.path.join(directorio_imagenes, f) for f in
                       os.listdir(directorio_imagenes) if
                       os.path.isfile(os.path.join(directorio_imagenes, f))
                       and "_gris" not in f]

    num_nucleos = cpu_count()
    print(f"Núcleos de CPU disponibles: {num_nucleos}")
    print(f"Imágenes a procesar: {len(lista_imagenes)}\n")

    inicio = time.time()
    procesar_imagenes_paralelo(lista_imagenes, num_procesos=num_nucleos)
    fin = time.time()

    print(f"\nTiempo total de procesamiento paralelo: {fin - inicio:.4f} segundos")
