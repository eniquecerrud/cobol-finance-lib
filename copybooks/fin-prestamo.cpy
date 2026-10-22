*> CALL "fin-prestamo" USING FL-PARAMS.
*>
*> Amortización de un capital a tasa periódica fija.
*> FL-TASA es la tasa del periodo (en una hipoteca mensual,
*> nominal anual / 12), no la tasa anual.
*>
*> FL-OPERACION
*>   "PAGO"  calcula la cuota y también rellena el cuadro
*>   "PLAN"  igual que PAGO; el nombre deja explícito el cuadro
*> Las dos operaciones comparten el mismo cálculo para que la cuota
*> y el cuadro no puedan divergir.
*>
*> FL-METODO
*>   "F"  francés (cuota total fija). FL-CUOTA es esa cuota.
*>        El último periodo absorbe el residuo de redondeo:
*>        su cuota puede diferir en el último dígito para que el
*>        saldo final sea exactamente cero.
*>   "G"  alemán (capital constante). FL-CUOTA es la cuota de
*>        capital, no el pago total. El pago total de cada periodo
*>        es capital + interés y está en FL-CUOTA-PER.
*>
*> Importes del cuadro redondeados a 6 decimales.
*> Interés del periodo = round(saldo_anterior * tasa, 6).
*> FL-CUOTA-INICIAL y FL-CUOTA-FINAL son el pago total del primer
*> y del último periodo.
*> Máximo: OCCURS 600, el mismo tope que FIN-MAX-PERIODOS.

01 FL-PARAMS.
   05 FL-OPERACION           PIC X(4).
   05 FL-METODO              PIC X.
   05 FL-CAPITAL             PIC S9(13)V9(6) COMP-3.
   05 FL-TASA                PIC S9(4)V9(12) COMP-3.
   05 FL-PERIODOS            PIC 9(5) COMP-5.
   05 FL-CUOTA               PIC S9(13)V9(6) COMP-3.
   05 FL-CUOTA-INICIAL       PIC S9(13)V9(6) COMP-3.
   05 FL-CUOTA-FINAL         PIC S9(13)V9(6) COMP-3.
   05 FL-TOTAL-INTERES       PIC S9(13)V9(6) COMP-3.
   05 FL-TOTAL-PAGADO        PIC S9(13)V9(6) COMP-3.
   05 FL-SALDO-FINAL         PIC S9(13)V9(6) COMP-3.
   05 FL-FILAS               PIC 9(5) COMP-5.
   05 FL-LINEA OCCURS 600 TIMES.
      10 FL-NUMERO           PIC 9(5) COMP-5.
      10 FL-CUOTA-PER        PIC S9(13)V9(6) COMP-3.
      10 FL-INTERES-PER      PIC S9(13)V9(6) COMP-3.
      10 FL-CAPITAL-PER      PIC S9(13)V9(6) COMP-3.
      10 FL-SALDO-PER        PIC S9(13)V9(6) COMP-3.
   05 FL-CODIGO              PIC 99.
   05 FL-MENSAJE             PIC X(80).
