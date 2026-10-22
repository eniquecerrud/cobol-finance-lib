>>SOURCE FORMAT FREE
*> Anualidad ordinaria y anticipada, valor presente y futuro.
IDENTIFICATION DIVISION.
PROGRAM-ID. demo-anualidad.

ENVIRONMENT DIVISION.

DATA DIVISION.
WORKING-STORAGE SECTION.
COPY "fin-anualidad.cpy".
01 ED-IMP                     PIC --,---,---,---,--9.9(6).
01 ED-TASA                    PIC -(4)9.9(12).
01 ED-N                       PIC Z(5)9.

PROCEDURE DIVISION.
0000-MAIN.
    DISPLAY "ANUALIDAD ORDINARIA — VALOR PRESENTE"
    INITIALIZE FA-PARAMS
    MOVE "PVAN" TO FA-OPERACION
    MOVE "O" TO FA-TIPO
    MOVE 1500 TO FA-CUOTA
    MOVE 0.005 TO FA-TASA
    MOVE 240 TO FA-PERIODOS
    CALL "fin-anualidad" USING FA-PARAMS
    PERFORM 1000-MOSTRAR-PV

    DISPLAY " "
    DISPLAY "ANUALIDAD ANTICIPADA — VALOR FUTURO"
    INITIALIZE FA-PARAMS
    MOVE "FVAN" TO FA-OPERACION
    MOVE "A" TO FA-TIPO
    MOVE 2000 TO FA-CUOTA
    MOVE 0.004 TO FA-TASA
    MOVE 36 TO FA-PERIODOS
    CALL "fin-anualidad" USING FA-PARAMS
    MOVE FA-CUOTA TO ED-IMP
    DISPLAY "  Cuota             " ED-IMP
    MOVE FA-TASA TO ED-TASA
    DISPLAY "  Tasa periodica    " ED-TASA
    MOVE FA-PERIODOS TO ED-N
    DISPLAY "  Periodos          " ED-N
    MOVE FA-VALOR-FUTURO TO ED-IMP
    DISPLAY "  Valor futuro      " ED-IMP
    DISPLAY "  Codigo            " FA-CODIGO
    STOP RUN.

1000-MOSTRAR-PV.
    MOVE FA-CUOTA TO ED-IMP
    DISPLAY "  Cuota             " ED-IMP
    MOVE FA-TASA TO ED-TASA
    DISPLAY "  Tasa periodica    " ED-TASA
    MOVE FA-PERIODOS TO ED-N
    DISPLAY "  Periodos          " ED-N
    MOVE FA-VALOR-PRESENTE TO ED-IMP
    DISPLAY "  Valor presente    " ED-IMP
    DISPLAY "  Codigo            " FA-CODIGO
    .

END PROGRAM demo-anualidad.
