*> CALL "fin-anualidad" USING FA-PARAMS.
*>
*> Anualidad de cuota constante. La tasa es la del periodo y los
*> periodos son enteros entre 1 y FIN-MAX-PERIODOS.
*>
*> FA-TIPO
*>   "O"  ordinaria (vencida): la cuota cae al final del periodo
*>   "A"  anticipada (due): la cuota cae al principio del periodo
*>
*> FA-OPERACION
*>   "PVAN"  valor presente de la cuota FA-CUOTA → FA-VALOR-PRESENTE
*>   "FVAN"  valor futuro de la cuota FA-CUOTA → FA-VALOR-FUTURO
*>   "CUOT"  cuota que tiene valor presente FA-VALOR-PRESENTE
*>           El resultado reemplaza FA-CUOTA.
*>
*> Con tasa 0 las dos modalidades coinciden:
*>   VP = VF = cuota * periodos
*>   cuota = valor-presente / periodos
*>
*> Con tasa distinta de cero (ordinaria):
*>   VP = cuota * (1 - (1 + tasa) ** -n) / tasa
*>   VF = cuota * ((1 + tasa) ** n - 1) / tasa
*>   cuota = VP * tasa * (1 + tasa) ** n / ((1 + tasa) ** n - 1)
*> La modalidad anticipada multiplica VP y VF por (1 + tasa)
*> y divide la cuota ordinaria por (1 + tasa).

01 FA-PARAMS.
   05 FA-OPERACION           PIC X(4).
   05 FA-TIPO                PIC X.
   05 FA-CUOTA               PIC S9(13)V9(6) COMP-3.
   05 FA-TASA                PIC S9(4)V9(12) COMP-3.
   05 FA-PERIODOS            PIC 9(5) COMP-5.
   05 FA-VALOR-PRESENTE      PIC S9(13)V9(6) COMP-3.
   05 FA-VALOR-FUTURO        PIC S9(13)V9(6) COMP-3.
   05 FA-CODIGO              PIC 99.
   05 FA-MENSAJE             PIC X(80).
