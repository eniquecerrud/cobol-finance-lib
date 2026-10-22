*> Códigos de retorno compartidos por toda la biblioteca.
*> Copiar una sola vez en WORKING-STORAGE SECTION.
*>
*>  0  éxito
*>  1  argumento inválido
*>  2  tasa no admisible (menor o igual que -1, factor nulo)
*>  3  no converge (Newton-Raphson ni bisección, o fuera de rango)
*>  4  la serie no cambia de signo: la TIR no está definida
*>  5  periodos o vida útil fuera de rango, o no enteros
*>  6  desbordamiento numérico
*>  7  error de archivo o módulo no disponible
*>  8  método desconocido
*>  9  operación desconocida
*> 10  serie de flujos vacía o más larga que FIN-MAX-PERIODOS
*>
*> FIN-MAX-PERIODOS (600) debe coincidir con el OCCURS de los copybooks
*> de préstamo y de VPN/TIR. FIN-MAX-VIDA (100) con el de depreciación.
*> FIN-MAX-EXPONENTE limita la potencia entera.

78 FIN-OK                  VALUE 0.
78 FIN-ERR-ARGUMENTO       VALUE 1.
78 FIN-ERR-TASA            VALUE 2.
78 FIN-ERR-CONVERGENCIA    VALUE 3.
78 FIN-ERR-SIGNO           VALUE 4.
78 FIN-ERR-PERIODOS        VALUE 5.
78 FIN-ERR-DESBORDAMIENTO  VALUE 6.
78 FIN-ERR-ARCHIVO         VALUE 7.
78 FIN-ERR-METODO          VALUE 8.
78 FIN-ERR-OPERACION       VALUE 9.
78 FIN-ERR-SERIE           VALUE 10.
78 FIN-MAX-PERIODOS        VALUE 600.
78 FIN-MAX-VIDA            VALUE 100.
78 FIN-MAX-EXPONENTE       VALUE 9999.
