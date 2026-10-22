>>SOURCE FORMAT FREE
*> Depreciación lineal y de doble saldo decreciente.
IDENTIFICATION DIVISION.
PROGRAM-ID. demo-depreciacion.

ENVIRONMENT DIVISION.

DATA DIVISION.
WORKING-STORAGE SECTION.
COPY "fin-depreciacion.cpy".
01 ED-IMP                     PIC --,---,---,---,--9.9(6).
01 ED-IMP2                    PIC --,---,---,---,--9.9(6).
01 ED-IMP3                    PIC --,---,---,---,--9.9(6).
01 ED-TASA                    PIC -(4)9.9(12).
01 ED-ANIO                    PIC ZZZ9.
01 WS-K                       PIC 9(3) COMP-5.

PROCEDURE DIVISION.
0000-MAIN.
    DISPLAY "LINEAL"
    INITIALIZE FD-PARAMS
    MOVE "LIN" TO FD-METODO
    MOVE 15000 TO FD-COSTO
    MOVE 1500 TO FD-RESIDUAL
    MOVE 5 TO FD-VIDA
    MOVE 0 TO FD-ANIO
    CALL "fin-depreciacion" USING FD-PARAMS
    PERFORM 1000-CUADRO

    DISPLAY " "
    DISPLAY "DOBLE SALDO DECRECIENTE"
    INITIALIZE FD-PARAMS
    MOVE "DSD" TO FD-METODO
    MOVE 30000 TO FD-COSTO
    MOVE 5000 TO FD-RESIDUAL
    MOVE 5 TO FD-VIDA
    MOVE 0 TO FD-ANIO
    CALL "fin-depreciacion" USING FD-PARAMS
    PERFORM 1000-CUADRO
    STOP RUN.

1000-CUADRO.
    MOVE FD-COSTO TO ED-IMP
    DISPLAY "  Costo             " ED-IMP
    MOVE FD-RESIDUAL TO ED-IMP
    DISPLAY "  Residual          " ED-IMP
    MOVE FD-TASA-USADA TO ED-TASA
    DISPLAY "  Tasa usada        " ED-TASA
    DISPLAY "   Anio                     Cuota                 Acumulado           Valor en libros"
    DISPLAY "  ----- ------------------------- ------------------------- -------------------------"
    PERFORM VARYING WS-K FROM 1 BY 1 UNTIL WS-K > FD-FILAS
        MOVE FD-ANIO-N(WS-K) TO ED-ANIO
        MOVE FD-CUOTA-PER(WS-K) TO ED-IMP
        MOVE FD-ACUM-PER(WS-K) TO ED-IMP2
        MOVE FD-LIBROS-PER(WS-K) TO ED-IMP3
        DISPLAY "  " ED-ANIO " " ED-IMP " " ED-IMP2 " " ED-IMP3
    END-PERFORM
    DISPLAY "  Codigo            " FD-CODIGO
    .

END PROGRAM demo-depreciacion.
