*> CALL "fin-vpn-tir" USING FT-PARAMS.
*>
*> VPN (valor presente neto, NPV) y TIR (tasa interna de retorno, IRR).
*> El flujo de índice 1 es el periodo 0 y no se descuenta.
*> El flujo t+1 se descuenta con (1 + tasa) ** t.
*>
*> FT-OPERACION
*>   "VPN "  evalúa FT-VPN a la tasa FT-TASA.
*>   "TIR "  resuelve VPN(r) = 0.
*>           FT-TASA es la semilla de Newton-Raphson.
*>           FT-TOLERANCIA 0 selecciona 0.000000001 (1e-9) sobre la tasa.
*>           FT-MAX-ITER 0 selecciona 80 iteraciones.
*>           FT-ESTRATEGIA
*>             "N" o espacio  Newton-Raphson y, si no basta, bisección
*>             "W"            solo Newton-Raphson
*>             "B"            solo bisección
*>           FT-METODO queda en "N" o "B" según el camino que convergió.
*>           FT-ITERACIONES cuenta los pasos de ese camino.
*>           FT-VPN queda con el valor actual residual en la TIR hallada.
*>
*> La bisección busca un cambio de signo de la VPN en la rejilla
*> -0.99 .. 5000. Fuera de ese intervalo el código es 3.
*> Si todos los flujos son >= 0 o todos son <= 0, el código es 4.
*> Hace falta al menos un flujo estrictamente positivo y uno negativo.
*> Máximo: OCCURS 600 flujos, incluido el periodo 0.

01 FT-PARAMS.
   05 FT-OPERACION           PIC X(4).
   05 FT-ESTRATEGIA          PIC X.
   05 FT-TASA                PIC S9(4)V9(12) COMP-3.
   05 FT-TOLERANCIA          PIC S9(4)V9(12) COMP-3.
   05 FT-MAX-ITER            PIC 9(5) COMP-5.
   05 FT-NUM-FLUJOS          PIC 9(5) COMP-5.
   05 FT-FLUJO OCCURS 600 TIMES
                             PIC S9(13)V9(6) COMP-3.
   05 FT-VPN                 PIC S9(13)V9(6) COMP-3.
   05 FT-TIR                 PIC S9(4)V9(12) COMP-3.
   05 FT-ITERACIONES         PIC 9(5) COMP-5.
   05 FT-METODO              PIC X.
   05 FT-CODIGO              PIC 99.
   05 FT-MENSAJE             PIC X(80).
