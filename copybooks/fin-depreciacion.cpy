*> CALL "fin-depreciacion" USING FD-PARAMS.
*>
*> FD-METODO
*>   "LIN"  lineal. Cuota = round((costo - residual) / vida, 6).
*>          El último año absorbe el residuo para que el valor en
*>          libros termine exactamente en el residual.
*>   "DEC"  saldo decreciente a la tasa FD-TASA (decimal, > 0).
*>          Cuota = round(valor-en-libros * tasa, 6), sin bajar
*>          del residual. No fuerza el residual al último año:
*>          si la tasa es baja puede quedar valor por depreciar.
*>   "DSD"  doble saldo decreciente. Igual que DEC con tasa 2 / vida.
*>          FD-TASA-USADA devuelve esa tasa ya redondeada a 12 decimales.
*>
*> FD-ANIO
*>   0      rellena el cuadro completo. FD-CUOTA es la depreciación
*>          acumulada, FD-VALOR-LIBROS el valor final.
*>   1..vida  calcula desde el año 1 (el saldo depende de la historia)
*>          y deja en FD-CUOTA / FD-ACUMULADO / FD-VALOR-LIBROS
*>          las cifras de ese año. El cuadro incluye los años 1..N.
*> Vida entre 1 y FIN-MAX-VIDA (100). El residual no puede superar
*> al costo. OCCURS 100 debe coincidir con FIN-MAX-VIDA.

01 FD-PARAMS.
   05 FD-METODO              PIC X(3).
   05 FD-COSTO               PIC S9(13)V9(6) COMP-3.
   05 FD-RESIDUAL            PIC S9(13)V9(6) COMP-3.
   05 FD-VIDA                PIC 9(3) COMP-5.
   05 FD-TASA                PIC S9(4)V9(12) COMP-3.
   05 FD-ANIO                PIC 9(3) COMP-5.
   05 FD-TASA-USADA          PIC S9(4)V9(12) COMP-3.
   05 FD-CUOTA               PIC S9(13)V9(6) COMP-3.
   05 FD-ACUMULADO           PIC S9(13)V9(6) COMP-3.
   05 FD-VALOR-LIBROS        PIC S9(13)V9(6) COMP-3.
   05 FD-FILAS               PIC 9(3) COMP-5.
   05 FD-LINEA OCCURS 100 TIMES.
      10 FD-ANIO-N           PIC 9(3) COMP-5.
      10 FD-CUOTA-PER        PIC S9(13)V9(6) COMP-3.
      10 FD-ACUM-PER         PIC S9(13)V9(6) COMP-3.
      10 FD-LIBROS-PER       PIC S9(13)V9(6) COMP-3.
   05 FD-CODIGO              PIC 99.
   05 FD-MENSAJE             PIC X(80).
