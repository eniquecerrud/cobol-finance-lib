*> CALL "fin-potencia" USING FP-PARAMS.
*>
*> Potencia entera y raíz n-ésima en punto fijo COMP-3.
*> Cada multiplicación se redondea a 16 decimales con
*> ROUNDED MODE IS NEAREST-AWAY-FROM-ZERO (half away from zero).
*> La potencia de exponente positivo se calcula por multiplicaciones
*> sucesivas, no con el operador ** (que en GnuCOBOL pasa por coma
*> flotante). La raíz usa Newton-Raphson sobre esa potencia.
*>
*> FP-OPERACION
*>   "POWI"  resultado = base ** exponente entero
*>           exponente 0 devuelve 1 (incluido 0 ** 0)
*>           exponente negativo devuelve el recíproco
*>   "RAIZ"  resultado = base ** (1 / exponente)
*>           base negativa o exponente <= 0 es un error
*> FP-EXPONENTE  entero con valor absoluto <= FIN-MAX-EXPONENTE
*> FP-CODIGO     ver fin-estado.cpy

01 FP-PARAMS.
   05 FP-OPERACION           PIC X(4).
   05 FP-BASE                PIC S9(20)V9(16) COMP-3.
   05 FP-EXPONENTE           PIC S9(5) COMP-5.
   05 FP-RESULTADO           PIC S9(20)V9(16) COMP-3.
   05 FP-CODIGO              PIC 99.
   05 FP-MENSAJE             PIC X(80).
