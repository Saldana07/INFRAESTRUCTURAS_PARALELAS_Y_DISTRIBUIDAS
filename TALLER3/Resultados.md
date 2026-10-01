50 boletas, 100 compradores, pago = 0.01s, pasarela = 5 simultáneos

--- Corrida 1 ---
V1  sin lock               vendidas: 100 | disponibles: -50 | tiempo:  0.015s | ERROR (sobreventa)
V2  lock (pago dentro)     vendidas:  50 | disponibles:   0 | tiempo:  0.522s | CORRECTO
V3  lock mínimo+semáforo   vendidas:  50 | disponibles:   0 | tiempo:  0.107s | CORRECTO
V3b con 20% pagos fallidos vendidas:  40 | disponibles:  10 | tiempo:  0.107s | CORRECTO | boletas sin vender: 10

--- Corrida 2 ---
V1  sin lock               vendidas: 100 | disponibles: -50 | tiempo:  0.013s | ERROR (sobreventa)
V2  lock (pago dentro)     vendidas:  50 | disponibles:   0 | tiempo:  0.526s | CORRECTO
V3  lock mínimo+semáforo   vendidas:  50 | disponibles:   0 | tiempo:  0.106s | CORRECTO
V3b con 20% pagos fallidos vendidas:  41 | disponibles:   9 | tiempo:  0.106s | CORRECTO | boletas sin vender: 9

--- Corrida 3 ---
V1  sin lock               vendidas: 100 | disponibles: -50 | tiempo:  0.013s | ERROR (sobreventa)
V2  lock (pago dentro)     vendidas:  50 | disponibles:   0 | tiempo:  0.524s | CORRECTO
V3  lock mínimo+semáforo   vendidas:  50 | disponibles:   0 | tiempo:  0.106s | CORRECTO
V3b con 20% pagos fallidos vendidas:  38 | disponibles:  12 | tiempo:  0.106s | CORRECTO | boletas sin vender: 12