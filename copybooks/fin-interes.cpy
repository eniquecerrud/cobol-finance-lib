*> CALL "fin-interes" USING FI-PARAMS.
*>
*> Tasas en forma decimal: 0.05 = 5 %. Punto decimal, no coma.
*> Importes con 6 decimales. Tasas de salida con 12 decimales.
*> Redondeo NEAREST-AWAY-FROM-ZERO.
*>
*> FI-OPERACION
*>   "SIMP"  interés simple.
*>           I  = round(capital * tasa * tiempo, 6)
*>           VF = capital + I
*>           Usa FI-TIEMPO (puede ser fraccionario, no negativo).
*>   "COMP"  interés compuesto discreto.
*>           VF = round(capital * (1 + tasa) ** periodos, 6)
*>           I  = VF - capital
*>           periodos entero >= 0. periodos 0 devuelve el capital.
*>   "VFUT"  igual que COMP; deja el resultado en FI-VALOR-FUTURO.
*>   "VPRE"  valor presente.
*>           VP = round(valor-futuro / (1 + tasa) ** periodos, 6)
*>           El valor futuro de entrada está en FI-VALOR-FUTURO.
*>   "EFEC"  tasa efectiva anual a partir de la nominal.
*>           efectiva = (1 + nominal / m) ** m - 1
*>           FI-TASA es la nominal anual, FI-CAPITALIZACIONES es m.
*>           El resultado queda en FI-TASA-SALIDA.
*>   "NOMI"  nominal anual equivalente a una efectiva.
*>           nominal = m * ((1 + efectiva) ** (1 / m) - 1)
*>           FI-TASA es la efectiva, m es FI-CAPITALIZACIONES.
*>
*> Una tasa <= -1 en operaciones compuestas, VPRE, VFUT, EFEC o NOMI
*> devuelve FIN-ERR-TASA: el factor (1 + tasa) no es positivo.
*> El interés simple sí admite tasas negativas.

01 FI-PARAMS.
   05 FI-OPERACION           PIC X(4).
   05 FI-CAPITAL             PIC S9(13)V9(6) COMP-3.
   05 FI-TASA                PIC S9(4)V9(12) COMP-3.
   05 FI-TIEMPO              PIC S9(5)V9(6) COMP-3.
   05 FI-PERIODOS            PIC 9(5) COMP-5.
   05 FI-CAPITALIZACIONES    PIC 9(5) COMP-5.
   05 FI-VALOR-FUTURO        PIC S9(13)V9(6) COMP-3.
   05 FI-VALOR-PRESENTE      PIC S9(13)V9(6) COMP-3.
   05 FI-INTERES             PIC S9(13)V9(6) COMP-3.
   05 FI-TASA-SALIDA         PIC S9(4)V9(12) COMP-3.
   05 FI-CODIGO              PIC 99.
   05 FI-MENSAJE             PIC X(80).
