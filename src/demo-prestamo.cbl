>>SOURCE FORMAT FREE
*> Cuadro francés de 12 meses, listo para leer como ejemplo.
IDENTIFICATION DIVISION.
PROGRAM-ID. demo-prestamo.

ENVIRONMENT DIVISION.

DATA DIVISION.
WORKING-STORAGE SECTION.
COPY "fin-prestamo.cpy".
01 ED-PER                     PIC ZZZZ9.
01 ED-IMP                     PIC --,---,---,---,--9.9(6).
01 ED-IMP2                    PIC --,---,---,---,--9.9(6).
01 ED-IMP3                    PIC --,---,---,---,--9.9(6).
01 ED-IMP4                    PIC --,---,---,---,--9.9(6).
01 ED-TASA                    PIC -(4)9.9(12).
01 WS-K                       PIC 9(5) COMP-5.
01 ED-N                       PIC Z(5)9.

PROCEDURE DIVISION.
0000-MAIN.
    INITIALIZE FL-PARAMS
    MOVE "PLAN" TO FL-OPERACION
    MOVE "F" TO FL-METODO
    MOVE 12000 TO FL-CAPITAL
    MOVE 0.01 TO FL-TASA
    MOVE 12 TO FL-PERIODOS
    CALL "fin-prestamo" USING FL-PARAMS
    DISPLAY "CUADRO DE AMORTIZACION FRANCES"
    MOVE FL-CAPITAL TO ED-IMP
    DISPLAY "  Capital           " ED-IMP
    MOVE FL-TASA TO ED-TASA
    DISPLAY "  Tasa periodica    " ED-TASA
    MOVE FL-PERIODOS TO ED-N
    DISPLAY "  Periodos          " ED-N
    MOVE FL-CUOTA TO ED-IMP
    DISPLAY "  Cuota regular     " ED-IMP
    DISPLAY " "
    DISPLAY "   Per.                     Cuota                   Interes              Amortizacion                     Saldo"
    DISPLAY "  ----- ------------------------- ------------------------- ------------------------- -------------------------"
    PERFORM VARYING WS-K FROM 1 BY 1 UNTIL WS-K > FL-FILAS
        MOVE FL-NUMERO(WS-K) TO ED-PER
        MOVE FL-CUOTA-PER(WS-K) TO ED-IMP
        MOVE FL-INTERES-PER(WS-K) TO ED-IMP2
        MOVE FL-CAPITAL-PER(WS-K) TO ED-IMP3
        MOVE FL-SALDO-PER(WS-K) TO ED-IMP4
        DISPLAY "  " ED-PER " " ED-IMP " " ED-IMP2 " " ED-IMP3 " " ED-IMP4
    END-PERFORM
    DISPLAY " "
    MOVE FL-TOTAL-INTERES TO ED-IMP
    DISPLAY "  Interes total     " ED-IMP
    MOVE FL-TOTAL-PAGADO TO ED-IMP
    DISPLAY "  Total pagado      " ED-IMP
    MOVE FL-SALDO-FINAL TO ED-IMP
    DISPLAY "  Saldo final       " ED-IMP
    DISPLAY "  Codigo            " FL-CODIGO
    STOP RUN.

END PROGRAM demo-prestamo.
