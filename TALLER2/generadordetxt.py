import random
import string

total_lineas = 521356
nombre_archivo = "texto_entrada_dificil.txt"

# Bloques de texto para complicar el procesamiento
espacios_masivos = " \t \t " * 200  # Cientos de espacios y tabulaciones
texto_alternado = "aBcDeFgHiJkLmNoPqRsTuVwXyZ" * 50  # Texto largo con mayúsculas/minúsculas
caracteres_especiales = "áéíóúÑñ@#$%&*{}[]?!¿¡" * 10

print(f"Generando {nombre_archivo} con {total_lineas} líneas (Nivel de Dificultad: ALTO)...")

with open(nombre_archivo, "w", encoding="utf-8") as f:
    for i in range(total_lineas):
        # Elegir un tipo de línea difícil al azar
        tipo = random.choice([1, 2, 3, 4])
        
        if tipo == 1:
            # Línea con muchísimos espacios al inicio y al final
            linea = f"{espacios_masivos} PROCESAMIENTO PARALELO {espacios_masivos}"
        elif tipo == 2:
            # Línea extremadamente larga con letras alternadas
            linea = f"  {texto_alternado}  "
        elif tipo == 3:
            # Línea con caracteres especiales y acentos (prueba la codificación)
            linea = f"\t {caracteres_especiales} texto caótico {caracteres_especiales} \t "
        else:
            # Mezcla aleatoria y caótica
            letra_random = random.choice(string.ascii_letters) * 100
            linea = f" \t  {letra_random}  {texto_alternado[:100]} \t   "

        f.write(linea + "\n")

print(f"¡Listo! Archivo guardado como {nombre_archivo}.")
print("¡Prepárate para ver trabajar esos 12 núcleos!")