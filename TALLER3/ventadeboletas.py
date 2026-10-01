"""
TALLER 3 - CONCURRENCIA  (versión con explicación detallada)
=============================================================
PROBLEMA DEL MUNDO REAL
    Venta de boletas de un concierto. Cuando se abre la venta, cientos de
    personas intentan comprar al mismo tiempo, pero las boletas son limitadas.
    Si el sistema no está bien diseñado, se venden MÁS boletas de las que existen
    (sobreventa). Aquí lo simulamos con 100 compradores y 50 boletas.

IDEA GENERAL
    - Cada COMPRADOR es un HILO (thread).
    - Las BOLETAS DISPONIBLES son un dato COMPARTIDO que todos los hilos leen
      y modifican.  Ahí nace el problema de concurrencia.

SE COMPARAN 4 VERSIONES
    V1   Sin lock                  -> race condition: se vende de más
    V2   Lock con el pago DENTRO   -> correcta, pero lenta (todos hacen fila)
    V3   Lock mínimo + Semaphore   -> correcta y rápida
    V3b  V3 con pagos que fallan   -> muestra una debilidad real del diseño

MECANISMOS USADOS
    Lock       : exclusión mutua (un hilo a la vez en la sección crítica)
    Semaphore  : limitar cuántos hilos usan un recurso a la vez (la pasarela)
    Event      : señal de arranque para que todos compren al mismo tiempo
"""

import random      # para simular que algunos pagos son rechazados
import threading   # hilos, Lock, Semaphore y Event
import time        # sleep() para simular espera, y perf_counter() para medir

# ===================================================================
# 1. CONFIGURACIÓN (constantes que puedes cambiar para experimentar)
# ===================================================================
BOLETAS = 50            # cuántas boletas existen en total
COMPRADORES = 100       # cuántos hilos intentan comprar (el doble de boletas)
TIEMPO_PAGO = 0.01      # segundos que tarda validar un pago (simulado con sleep)
PAGOS_SIMULTANEOS = 5   # la pasarela de pago solo atiende 5 pagos a la vez

# ===================================================================
# 2. ESTADO COMPARTIDO (lo que todos los hilos pueden tocar)
# ===================================================================
disponibles = BOLETAS   # boletas que todavía se pueden vender
vendidas = 0            # boletas con pago confirmado

# LOCK: candado. Solo UN hilo a la vez puede tenerlo; los demás esperan.
# Lo usamos para proteger 'disponibles' y 'vendidas'.
lock = threading.Lock()

# SEMAPHORE(5): contador de "permisos". Hay 5 permisos; cada hilo que paga
# toma uno (acquire) y lo devuelve al terminar (release). Si no quedan
# permisos, el hilo espera. Así modelamos que la pasarela soporta 5 pagos
# simultáneos. (A diferencia del Lock, que permite solo 1.)
pasarela = threading.Semaphore(PAGOS_SIMULTANEOS)

# EVENT: una "bandera" que empieza en falso. Los hilos hacen wait() y quedan
# dormidos hasta que alguien hace set(). Es la señal de "se abrió la venta".
inicio_venta = threading.Event()


# ===================================================================
# 3. FUNCIÓN AUXILIAR: simular el pago
# ===================================================================
def procesar_pago(rng, prob_fallo):
    """
    Simula validar el pago con el banco.
      - time.sleep(): representa la espera por la red/banco. Mientras un hilo
        duerme, el sistema deja que otros hilos avancen (esto es lo que hace
        útil la concurrencia con hilos: aprovechar tiempos de espera).
      - rng.random(): número aleatorio entre 0 y 1. Si es menor que
        prob_fallo, el pago "falla" (ej: tarjeta rechazada).
    Devuelve True si el pago fue aprobado.
    """
    time.sleep(TIEMPO_PAGO)
    return rng.random() >= prob_fallo


# ===================================================================
# 4. V1 - SIN LOCK  (aquí está la RACE CONDITION)
# ===================================================================
def comprar_v1(i, resultados, rng):
    """
    Parámetros:
      i          -> número del comprador (0 a 99)
      resultados -> lista donde cada hilo anota qué le pasó, en SU posición i
      rng        -> generador de números aleatorios propio de este hilo
    """
    global disponibles, vendidas   # 'global': vamos a MODIFICAR las variables compartidas

    inicio_venta.wait()            # espera dormido hasta que se abra la venta

    if disponibles > 0:            # PASO 1: VERIFICA si hay boletas
        procesar_pago(rng, 0)      # PASO 2: paga (tarda). Mientras tanto, otros
                                   #   hilos también ven "disponibles > 0"
        disponibles -= 1           # PASO 3: descuenta la boleta
        vendidas += 1
        resultados[i] = "COMPRO"
    else:
        resultados[i] = "AGOTADO"

    # PROBLEMA: entre el PASO 1 y el PASO 3 pasa tiempo. Los 100 hilos
    # verifican "hay boletas" antes de que alguno descuente, y los 100 compran.
    # Se venden 100 boletas de 50. Esto es una RACE CONDITION del tipo
    # "verificar y luego actuar" (check-then-act): verificar y descontar
    # debían ser UNA sola operación indivisible, y no lo son.


# ===================================================================
# 5. V2 - LOCK CON EL PAGO DENTRO  (correcta, pero lenta)
# ===================================================================
def comprar_v2(i, resultados, rng):
    global disponibles, vendidas
    inicio_venta.wait()

    # 'with lock:' hace dos cosas:
    #   1) toma el candado al entrar (si otro hilo lo tiene, ESPERA aquí)
    #   2) lo suelta automáticamente al salir, incluso si ocurre un error
    # Todo lo que está dentro es la SECCIÓN CRÍTICA: solo un hilo a la vez.
    with lock:
        if disponibles > 0:
            procesar_pago(rng, 0)  # <- el pago está DENTRO del lock
            disponibles -= 1
            vendidas += 1
            resultados[i] = "COMPRO"
        else:
            resultados[i] = "AGOTADO"

    # RESULTADO: nunca hay sobreventa (verificar y descontar son atómicos).
    # PERO: mientras un hilo paga (0.01 s), los demás esperan el lock.
    # 50 pagos uno tras otro = 50 x 0.01 = ~0.5 s. Se serializa todo.


# ===================================================================
# 6. V3 - LOCK MÍNIMO + SEMÁFORO  (correcta y rápida)
# ===================================================================
def crear_comprar_v3(prob_fallo):
    """
    Esta función FABRICA la función de compra con una probabilidad de fallo
    dada. Se hace así porque Thread(target=...) necesita una función con los
    mismos parámetros que las otras versiones. (Esto se llama "closure".)
    """
    def comprar_v3(i, resultados, rng):
        global disponibles, vendidas
        inicio_venta.wait()

        # --- FASE 1: RESERVAR (dentro del lock, muy corta) -----------------
        with lock:
            if disponibles == 0:           # ya no hay boletas: este hilo se va
                resultados[i] = "AGOTADO"
                return
            disponibles -= 1               # RESERVA: la boleta ya es de este
                                           # comprador y nadie más puede tomarla.
        # Aquí el lock ya se soltó. La reserva tardó microsegundos.

        # --- FASE 2: PAGAR (FUERA del lock, limitada por el semáforo) -------
        # 'with pasarela:' toma 1 permiso (espera si ya hay 5 pagando) y lo
        # devuelve al salir. Así, hasta 5 pagos ocurren EN PARALELO.
        with pasarela:
            aprobado = procesar_pago(rng, prob_fallo)

        # --- FASE 3: CONFIRMAR o DEVOLVER (dentro del lock, muy corta) ------
        with lock:
            if aprobado:
                vendidas += 1              # el pago salió bien: venta confirmada
                resultados[i] = "COMPRO"
            else:
                disponibles += 1           # el pago falló: se devuelve la boleta
                resultados[i] = "PAGO FALLIDO"

    return comprar_v3

    # POR QUÉ ES MEJOR: el lock solo protege las operaciones rápidas sobre las
    # variables compartidas. El pago (lo lento) ocurre FUERA, en paralelo.
    # 50 pagos / 5 simultáneos x 0.01 s = ~0.1 s  (5 veces más rápido que V2).
    #
    # NO HAY DEADLOCK: los dos 'with lock' no están anidados, y el semáforo se
    # toma SIN tener el lock en la mano. Ningún hilo espera algo que otro tiene
    # mientras a su vez retiene otra cosa.
    #
    # DEBILIDAD (V3b): si un pago falla y se devuelve la boleta, los compradores
    # que ya vieron "AGOTADO" se fueron. Esa boleta queda SIN VENDER.


# ===================================================================
# 7. EJECUTOR: lanza los 100 hilos, espera y verifica el resultado
# ===================================================================
def ejecutar(nombre, funcion, semilla):
    global disponibles, vendidas

    # Reinicia el estado para que cada versión parta desde cero
    disponibles, vendidas = BOLETAS, 0
    inicio_venta.clear()               # vuelve a bajar la bandera del Event

    # Lista de resultados con un espacio por comprador. CADA HILO ESCRIBE SOLO
    # EN SU POSICIÓN i, así que no hay conflicto y no se necesita lock aquí.
    # (Diseñar para NO compartir es mejor que sincronizar lo compartido.)
    resultados = [None] * COMPRADORES

    # Crea los 100 hilos (todavía NO están corriendo).
    # Cada hilo recibe su número i, la lista de resultados, y su propio
    # generador aleatorio con semilla distinta -> el experimento es reproducible.
    hilos = [
        threading.Thread(
            target=funcion,
            args=(i, resultados, random.Random(semilla + i)),
        )
        for i in range(COMPRADORES)
    ]

    for h in hilos:
        h.start()                      # arranca cada hilo; todos se bloquean en
                                       # inicio_venta.wait() (esperando la señal)

    t0 = time.perf_counter()           # empieza el cronómetro
    inicio_venta.set()                 # ¡SE ABRE LA VENTA! Despierta a los 100 hilos
    for h in hilos:
        h.join()                       # espera a que TODOS terminen antes de seguir
    t = time.perf_counter() - t0       # detiene el cronómetro

    # VERIFICACIÓN de correctitud:
    #   - no se vendió más de lo que había
    #   - las disponibles no son negativas
    #   - lo vendido + lo que queda = lo que había al inicio (nada se perdió)
    correcto = (vendidas <= BOLETAS and disponibles >= 0
                and vendidas + disponibles == BOLETAS)
    estado = "CORRECTO" if correcto else "ERROR (sobreventa)"

    # Boletas que sobraron aunque había demanda (solo tiene sentido si es correcto)
    sin_vender = disponibles if correcto else 0

    print(f"{nombre:<26} vendidas: {vendidas:3d} | disponibles: {disponibles:3d} "
          f"| tiempo: {t:6.3f}s | {estado}"
          + (f" | boletas sin vender: {sin_vender}" if sin_vender else ""))
    return correcto, t


# ===================================================================
# 8. PROGRAMA PRINCIPAL
# ===================================================================
if __name__ == "__main__":
    print(f"{BOLETAS} boletas, {COMPRADORES} compradores, "
          f"pago = {TIEMPO_PAGO}s, pasarela = {PAGOS_SIMULTANEOS} simultáneos\n")

    # Repite 3 veces para ver que el comportamiento es consistente
    for corrida in range(1, 6):
        print(f"--- Corrida {corrida} ---")
        s = corrida * 1000                     # semilla distinta por corrida
        ejecutar("V1  sin lock", comprar_v1, s)
        ejecutar("V2  lock (pago dentro)", comprar_v2, s)
        ejecutar("V3  lock mínimo+semáforo", crear_comprar_v3(0.0), s)       # 0% fallos
        ejecutar("V3b con 20% pagos fallidos", crear_comprar_v3(0.20), s)    # 20% fallos
        print()