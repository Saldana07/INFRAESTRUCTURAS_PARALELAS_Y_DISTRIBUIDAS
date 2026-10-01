import threading
import random
from collections import defaultdict

# Función Map: Ejecuta un bloque de simulaciones sin compartir memoria
def map_simulaciones(num_simulaciones, results, index):
    print(f"🏟️ [Hilo {index}] Iniciando {num_simulaciones} simulaciones para el partido...")
    conteo_local = defaultdict(int)
    
    for _ in range(num_simulaciones):
        # Simulación simplificada de goles (idealmente usarías Poisson)
        goles_A = random.randint(0, 4) 
        goles_B = random.randint(0, 4)
        
        if goles_A > goles_B:
            conteo_local['Victoria A'] += 1
        elif goles_A < goles_B:
            conteo_local['Victoria B'] += 1
        else:
            conteo_local['Empate'] += 1
            
    # Guarda el diccionario en el índice correspondiente del hilo
    results[index] = conteo_local
    
    # Muestra el resultado parcial calculado exclusivamente por este hilo
    print(f"✅ [Hilo {index}] Terminado. Subtotal calculado: {dict(conteo_local)}")

# Función Reduce: Combina los resultados parciales
def reduce_resultados(resultados_mapeados):
    print("\n📊 [Fase Reduce] Consolidando los datos de todos los hilos...")
    conteo_total = defaultdict(int)
    for i, conteo_parcial in enumerate(resultados_mapeados):
        print(f"   -> Extrayendo aportes del Hilo {i}...")
        for resultado, cantidad in conteo_parcial.items():
            conteo_total[resultado] += cantidad
    return conteo_total

def main():
    total_simulaciones = 100000
    num_hilos = 4
    sims_por_hilo = total_simulaciones // num_hilos
    
    threads = []
    # Lista pre-asignada para evitar problemas de concurrencia al guardar
    results = [None] * num_hilos 
    
    print(f"🚀 Iniciando motor de predicción deportiva: {total_simulaciones} simulaciones en {num_hilos} hilos concurrentes.\n")
    
    # Fase de Mapeo
    for i in range(num_hilos):
        thread = threading.Thread(target=map_simulaciones, args=(sims_por_hilo, results, i))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()
        
    # Fase de Reducción
    resultado_final = reduce_resultados(results)
    
    print("\n🏆 RESULTADOS FINALES DE LA SIMULACIÓN 🏆")
    for k, v in resultado_final.items():
        print(f"{k}: {(v / total_simulaciones) * 100:.2f}%")

if __name__ == "__main__":
    main()