# Matemáticas financieras en COBOL

Biblioteca de subprogramas reutilizables para interés, préstamos, anualidades,
VPN/TIR y depreciación. El cálculo vive en decimal empaquetado (`COMP-3`), con
redondeo explícito, y se enlaza con `CALL` y un área de parámetros documentada
en copybooks.

## Por qué COBOL y aritmética decimal

Los importes y las tasas de un préstamo son decimales exactos: 0,045 anual o
una cuota de 1.266,713275. El punto flotante binario (`COMP-1`, `COMP-2`, y
también el operador `**` de GnuCOBOL, que pasa por coma flotante) no puede
representar 0,10 ni 0,01, y el error se acumula a lo largo de 360 cuotas.

`PACKED-DECIMAL` / `COMP-3` guarda cada dígito en decimal. Esta biblioteca:

- no usa `FUNCTION ANNUITY` ni `FUNCTION PRESENT-VALUE` (intrínsecos de punto flotante);
- calcula `(1 + tasa) ** n` con multiplicaciones sucesivas redondeadas;
- resuelve la raíz n-ésima (tasa nominal equivalente) por Newton-Raphson sobre esa potencia;
- declara el redondeo en cada resultado: `ROUNDED MODE IS NEAREST-AWAY-FROM-ZERO`
  (half away from zero, el redondeo comercial clásico).

La escala pública es de **6 decimales en importes** y **12 decimales en tasas**.
El trabajo interno de potencias usa 16 decimales. Las tasas van en forma
decimal (`0.045` = 4,5 %). Los ficheros usan **punto** decimal para poder
cruzarlos con CSV y con las pruebas; el texto de los informes está en español.

## Requisitos

- [GnuCOBOL](https://gnucobol.sourceforge.io/) 3.1 o superior (`cobc`). En Ubuntu: `sudo apt-get install gnucobol`.
- Python 3, solo para la suite que recalcula las referencias con `decimal.Decimal`.
- GNU Make y bash.

Formato de todos los fuentes: libre (`>>SOURCE FORMAT FREE` y `cobc -free`).

## Compilación y pruebas

```bash
make          # módulos .so en build/ y programas
make test     # arnés COBOL + unittest de Python + demos
make demo     # vuelve a escribir ejemplos/
make clean
```

`make` compila con `-Wall` y falla si `cobc` emite algún aviso.

Los subprogramas son módulos dinámicos. Para ejecutar un programa hace falta
el directorio `build/` en `COB_LIBRARY_PATH` (el `Makefile` ya lo exporta):

```bash
export COB_LIBRARY_PATH="$PWD/build"
./build/fin-lote samples/lote.dat ejemplos/informe.txt ejemplos/informe.csv
./build/fin-calc samples/ordenes.txt
./build/demo-prestamo
```

La integración continua (`.github/workflows/ci.yml`) instala GnuCOBOL en
`ubuntu-latest` y ejecuta `make test`.

## Programas

| Programa | Papel |
| --- | --- |
| `fin-potencia` | Potencia entera y raíz n-ésima en `COMP-3` |
| `fin-interes` | Interés simple y compuesto, VP, VF, efectiva y nominal |
| `fin-anualidad` | Anualidad ordinaria y anticipada |
| `fin-prestamo` | Cuota y cuadro francés o alemán |
| `fin-vpn-tir` | VPN y TIR |
| `fin-depreciacion` | Lineal, saldo decreciente y doble saldo |
| `fin-calc` | Interfaz de texto, una orden por línea (la usan las pruebas) |
| `fin-lote` | Lee un fichero de casos y escribe informe + CSV |
| `demo-*` | Ejemplos con datos fijos |
| `fin-humo` | Arnés COBOL de identidades exactas |

## Precisión, topes y códigos

`FIN-MAX-PERIODOS` es 600 (también el `OCCURS` de los cuadros de préstamo y de
los flujos). `FIN-MAX-VIDA` es 100. `FIN-MAX-EXPONENTE` es 9999. Esos topes
están en `copybooks/fin-estado.cpy` y deben coincidir con los `OCCURS`.

| Código | Significado |
| ---: | --- |
| 00 | Éxito |
| 01 | Argumento inválido |
| 02 | Tasa no admisible (`<= -1`) o división por cero |
| 03 | La TIR no converge en el intervalo buscado (−0,99 … 5000) |
| 04 | La serie no cambia de signo: la TIR no está definida |
| 05 | Periodos o vida fuera de rango, o no enteros |
| 06 | Desbordamiento numérico |
| 07 | Fichero o módulo no disponible |
| 08 | Método desconocido |
| 09 | Operación desconocida |
| 10 | Serie de flujos vacía o demasiado larga |

Una tasa cero no es un error: las fórmulas tienen forma cerrada
(`VP = cuota × n`, `cuota = capital / n`).

## API

Cada copybook es el área de `LINKAGE` del subprograma y el área que el llamador
declara (en `WORKING-STORAGE` o donde corresponda). Se pasa por referencia:

```cobol
COPY "fin-interes.cpy".
MOVE "COMP" TO FI-OPERACION
MOVE 10000 TO FI-CAPITAL
MOVE 0.08 TO FI-TASA
MOVE 10 TO FI-PERIODOS
CALL "fin-interes" USING FI-PARAMS
```

El nombre del `CALL` es el `PROGRAM-ID`. Los módulos se recompilan con
`cobc -m -free -I copybooks`.

### `fin-potencia` — `copybooks/fin-potencia.cpy`

```cobol
01 FP-PARAMS.
   05 FP-OPERACION           PIC X(4).
   05 FP-BASE                PIC S9(20)V9(16) COMP-3.
   05 FP-EXPONENTE           PIC S9(5) COMP-5.
   05 FP-RESULTADO           PIC S9(20)V9(16) COMP-3.
   05 FP-CODIGO              PIC 99.
   05 FP-MENSAJE             PIC X(80).
```

| Operación | Resultado |
| --- | --- |
| `POWI` | `base ** exponente` entero. El exponente 0 devuelve 1. El negativo devuelve el recíproco. |
| `RAIZ` | `base ** (1 / exponente)`, base ≥ 0 e índice > 0. |

### `fin-interes` — `copybooks/fin-interes.cpy`

```cobol
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
```

| Operación | Fórmula |
| --- | --- |
| `SIMP` | `I = round(capital × tasa × tiempo, 6)`, `VF = capital + I`. El tiempo puede ser fraccionario. |
| `COMP`, `VFUT` | `VF = round(capital × (1 + tasa) ** periodos, 6)`, `I = VF − capital`. Periodos entero ≥ 0. |
| `VPRE` | `VP = round(valor-futuro / (1 + tasa) ** periodos, 6)`. El futuro entra en `FI-VALOR-FUTURO`. |
| `EFEC` | `efectiva = (1 + nominal / m) ** m − 1`. Nominal en `FI-TASA`, `m` en `FI-CAPITALIZACIONES`, salida en `FI-TASA-SALIDA`. |
| `NOMI` | `nominal = m × ((1 + efectiva) ** (1 / m) − 1)`. |

### `fin-anualidad` — `copybooks/fin-anualidad.cpy`

```cobol
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
```

`FA-TIPO`: `O` ordinaria (vencida, fin de periodo) o `A` anticipada (comienzo).
La tasa es la del periodo. Con tasa distinta de cero, la ordinaria es

```text
VP = cuota × (1 − (1 + tasa) ** −n) / tasa
VF = cuota × ((1 + tasa) ** n − 1) / tasa
```

y la anticipada multiplica esos valores por `(1 + tasa)`. `CUOT` despeja la
cuota a partir de `FA-VALOR-PRESENTE` (es la misma cuota del préstamo francés
cuando el tipo es `O`).

| Operación | Entrada | Salida |
| --- | --- | --- |
| `PVAN` | `FA-CUOTA` | `FA-VALOR-PRESENTE` |
| `FVAN` | `FA-CUOTA` | `FA-VALOR-FUTURO` |
| `CUOT` | `FA-VALOR-PRESENTE` | `FA-CUOTA` |

### `fin-prestamo` — `copybooks/fin-prestamo.cpy`

```cobol
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
```

`FL-TASA` es la tasa **del periodo**. En el lote, una hipoteca mensual usa
`nominal anual / 12` (0,045 / 12 = 0,00375), no la tasa efectiva.

| Método | Significado |
| --- | --- |
| `F` | Francés, cuota total fija. `FL-CUOTA` es esa cuota. |
| `G` | Alemán, capital constante. `FL-CUOTA` es la cuota de capital, no el pago total. |

`PAGO` y `PLAN` hacen el mismo cálculo y rellenan el cuadro, para que la cuota
y el saldo no puedan divergir. El interés de cada periodo es
`round(saldo anterior × tasa, 6)`. El último periodo absorbe el residuo de
redondeo y deja el saldo en cero; por eso `FL-CUOTA-FINAL` puede diferir de
`FL-CUOTA` en el último dígito.

### `fin-vpn-tir` — `copybooks/fin-vpn-tir.cpy`

```cobol
01 FT-PARAMS.
   05 FT-OPERACION           PIC X(4).
   05 FT-ESTRATEGIA          PIC X.
   05 FT-TASA                PIC S9(4)V9(12) COMP-3.
   05 FT-TOLERANCIA          PIC S9(4)V9(12) COMP-3.
   05 FT-MAX-ITER            PIC 9(5) COMP-5.
   05 FT-NUM-FLUJOS          PIC 9(5) COMP-5.
   05 FT-FLUJO OCCURS 600 TIMES PIC S9(13)V9(6) COMP-3.
   05 FT-VPN                 PIC S9(13)V9(6) COMP-3.
   05 FT-TIR                 PIC S9(4)V9(12) COMP-3.
   05 FT-ITERACIONES         PIC 9(5) COMP-5.
   05 FT-METODO              PIC X.
   05 FT-CODIGO              PIC 99.
   05 FT-MENSAJE             PIC X(80).
```

El flujo 1 es el periodo 0 y no se descuenta. El flujo `t + 1` se divide por
`(1 + tasa) ** t`.

| Operación | Detalle |
| --- | --- |
| `VPN` | Evalúa `FT-VPN` a `FT-TASA`. |
| `TIR` | Resuelve `VPN(r) = 0`. `FT-TASA` es la semilla de Newton-Raphson. Tolerancia 0 selecciona `1e-9`. Iteraciones 0 seleccionan 80. |

`FT-ESTRATEGIA`: `N` (o espacio) Newton y, si no basta, bisección; `W` solo
Newton; `B` solo bisección. `FT-METODO` queda en `N` o `B`. La bisección busca
un cambio de signo de la VPN en la rejilla de −0,99 a 5000. Hace falta al menos
un flujo estrictamente positivo y uno negativo; si no, el código es 04.

### `fin-depreciacion` — `copybooks/fin-depreciacion.cpy`

```cobol
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
```

| Método | Regla |
| --- | --- |
| `LIN` | `round((costo − residual) / vida, 6)`. El último año ajusta para terminar exactamente en el residual. |
| `DEC` | `round(valor en libros × tasa, 6)`, sin bajar del residual. La tasa tiene que ser positiva. No fuerza el residual al cierre de la vida: con una tasa baja puede quedar importe por depreciar. |
| `DSD` | Igual que `DEC` con tasa `2 / vida`, devuelta en `FD-TASA-USADA`. |

`FD-ANIO` 0 rellena el cuadro completo y deja en `FD-CUOTA` la depreciación
acumulada. Un año concreto se calcula desde el año 1, porque el saldo depende
de la historia.

## `fin-calc`

Una orden por línea, campos separados por `|`. Las líneas en blanco y las que
empiezan por `#` se ignoran. Cada orden escribe una línea
`codigo|campo|campo`. Con código distinto de 00 el resto es el mensaje.

```text
SIMP|capital|tasa|tiempo
COMP|capital|tasa|periodos          → valor futuro|interés
VPRE|valor futuro|tasa|periodos
VFUT|capital|tasa|periodos
EFEC|nominal|m
NOMI|efectiva|m
PVAN|cuota|tasa|periodos|O
FVAN|cuota|tasa|periodos|A
CUOT|valor presente|tasa|periodos|O
PAGO|capital|tasa periodica|periodos|F
FILA|capital|tasa|periodos|F|periodo
VPN|tasa|cf0;cf1;cf2
TIR|estrategia|semilla|tolerancia|max iter|cf0;cf1
POT|base|exponente
RAIZ|base|indice
LIN|costo|residual|vida|anio
DEC|costo|residual|vida|tasa|anio
DSD|costo|residual|vida|anio
```

`samples/ordenes.txt` produce `ejemplos/fin-calc.txt`. Por ejemplo, 10.000 al
8 % durante 10 periodos:

```text
00|21589.249973|11589.249973
```

## Lote

`samples/lote.dat` mezcla préstamos, flujos, anualidades y depreciaciones.
Los comentarios empiezan por `#`.

```text
PRESTAMO|id|capital|tasa anual nominal|periodos por año|plazo|F o G
FLUJO|id|tasa de descuento|tolerancia|max iter|cf0;cf1;cf2
ANUALIDAD|id|cuota|tasa periodica|periodos|O o A|PV o FV
DEPRECIACION|id|costo|residual|vida|tasa|LIN, DEC o DSD
```

```bash
./build/fin-lote samples/lote.dat ejemplos/informe.txt ejemplos/informe.csv
```

El CSV tiene la cabecera `tipo,id,concepto,n,v1,v2,v3,v4,v5,codigo`.

| tipo | concepto | columnas |
| --- | --- | --- |
| `prestamo` | `periodo` | n = periodo; v1 cuota; v2 interés; v3 amortización; v4 saldo |
| `prestamo` | `resumen` | v1 cuota regular o capital constante; v2 interés total; v3 total pagado; v4 saldo; v5 tasa periódica |
| `flujo` | `flujo` | n = periodo (0 = inicial); v1 importe |
| `flujo` | `vpn` / `tir` | v1 resultado; en la TIR, v2 iteraciones y v3 método (`N` o `B`) |
| `anualidad` | `valor_presente` o `valor_futuro` | v1 valor; v2 cuota; v3 tasa; v4 tipo; v5 modo |
| `depreciacion` | `periodo` | v1 cuota; v2 acumulado; v3 valor en libros |
| `error` | mensaje | `codigo` distinto de 00. El proceso termina con estado 1 si hubo algún error |

## Ejemplos

`make demo` regenera `ejemplos/`. El cuadro francés de 12.000 a 1 % mensual en
12 meses (`demo-prestamo`):

```text
CUADRO DE AMORTIZACION FRANCES
  Capital                       12,000.000000
  Tasa periodica        0.010000000000
  Periodos              12
  Cuota regular                  1,066.185464

   Per.                     Cuota                   Interes              Amortizacion                     Saldo
  ----- ------------------------- ------------------------- ------------------------- -------------------------
      1              1,066.185464                120.000000                946.185464             11,053.814536
      2              1,066.185464                110.538145                955.647319             10,098.167217
      3              1,066.185464                100.981672                965.203792              9,132.963425
      4              1,066.185464                 91.329634                974.855830              8,158.107595
      5              1,066.185464                 81.581076                984.604388              7,173.503207
      6              1,066.185464                 71.735032                994.450432              6,179.052775
      7              1,066.185464                 61.790528              1,004.394936              5,174.657839
      8              1,066.185464                 51.746578              1,014.438886              4,160.218953
      9              1,066.185464                 41.602190              1,024.583274              3,135.635679
     10              1,066.185464                 31.356357              1,034.829107              2,100.806572
     11              1,066.185464                 21.008066              1,045.177398              1,055.629174
     12              1,066.185466                 10.556292              1,055.629174                  0.000000

  Interes total                    794.225570
  Total pagado                  12,794.225570
  Saldo final                        0.000000
```

La cuota del periodo 12 sube 0,000002 para cerrar el saldo. La suma de las
amortizaciones es el capital.

Hipoteca de `samples/lote.dat` (`HIP-001`): 250.000, nominal 4,5 % en 360 meses.
Cuota regular 1.266,713275; interés del primer mes 937,50; último pago
1.266,712944; interés total 206.016,778669; saldo final 0. El cuadro completo
está en `ejemplos/informe.txt`.

Otras salidas de los demos:

| Caso | Resultado |
| --- | --- |
| Simple: 10.000 al 8 % durante 2,5 años | Interés 2.000, valor futuro 12.000 |
| Compuesto: 10.000 al 8 % durante 10 periodos | Valor futuro 21.589,249973 |
| Valor presente de 20.000 dentro de 5 periodos al 6 % | 14.945,163457 |
| Nominal 12 % con 12 capitalizaciones | Efectiva 0,126825030132; al volver a nominal se recupera 0,12 |
| Anualidad ordinaria de 1.500 al 0,5 % durante 240 periodos | Valor presente 209.371,157524 |
| Proyecto −100.000; 30.000; 35.000; 40.000; 45.000 | VPN al 8 % = 22.614,269505; TIR = 0,170936863395 (Newton, 5 iteraciones) |
| Bono −1.000; 1.100 | TIR = 0,10 |
| Lineal 15.000 con residual 1.500 en 5 años | Cuota 2.700; valor final 1.500 |
| Doble saldo de 30.000 con residual 5.000 en 5 años | Tasa 0,40; el año 4 llega al residual y el 5 queda en cero |

El sistema alemán del mismo préstamo de 12.000 cobra 1.000 de capital cada mes.
El primer pago es 1.120 (1.000 + 120 de interés) y el último, 1.010.

## Pruebas

Hay dos arneses y no comparten una tabla de resultados escritos a mano.

1. `tests/fin-humo.cbl` llama a los subprogramas y comprueba identidades
   exactas en `COMP-3`: 2^10 = 1024, interés simple 1.000 × 0,08 × 2 = 160,
   compuesto de un periodo, tasa −1, anualidad a tasa cero, francés de un
   periodo, alemán con capital 100, TIR de un periodo igual a 0,10, serie sin
   cambio de signo, depreciación lineal de 180. Termina con estado distinto de
   cero si alguna falla.
2. `tests/test_finanzas.py` vuelve a calcular cada caso con `decimal.Decimal`
   (precisión 50, redondeo half-away-from-zero) y compara. Cubre tasa cero,
   un solo periodo, tiempo fraccionario, hipoteca de 360 meses, cierre del
   cuadro, TIR negativa, serie sin cambio de signo, bisección forzada (`B`),
   Newton sin reserva que no converge (`W` con una iteración), piso del
   residual y el CSV del lote.

## Cómo añadir una función

1. Crear `copybooks/fin-nueva.cpy` con un único `01` de parámetros: operación,
   entradas, salidas, `PIC 99` de código y `PIC X(80)` de mensaje. Documentar
   la fórmula y la escala en comentarios al principio del copybook. Reutilizar
   los códigos de `fin-estado.cpy`. Si hace falta una tabla, el `OCCURS` tiene
   que ser el mismo número que la constante de tope.
2. Crear `src/fin-nueva.cbl` con `PROGRAM-ID` en minúsculas, cláusula
   `IS INITIAL` y `GOBACK` (un `STOP RUN` dentro del subprograma cortaría
   también al llamador). Copiar `fin-estado.cpy` en `WORKING-STORAGE` y el
   copybook nuevo en `LINKAGE`. Validar antes de calcular. Cada resultado sale
   de un `COMPUTE ... ROUNDED MODE IS NEAREST-AWAY-FROM-ZERO`, con
   `ON SIZE ERROR` donde el producto pueda desbordar. Las potencias enteras se
   piden con `CALL "fin-potencia"`, no con `**`.
3. Añadir el módulo a `MODULES` en el `Makefile`.
4. Añadir una orden en `src/fin-calc.cbl` para poder probarla desde texto.
   Si el lote debe imprimirla, añadir el tipo de registro en `src/fin-lote.cbl`
   y una fila de `samples/lote.dat`.
5. Añadir un caso exacto en `tests/fin-humo.cbl` cuando la identidad sea
   cerrada, y un método en `tests/test_finanzas.py` cuya referencia salga de
   `Decimal`, no de un número anotado.
6. Documentar la operación en esta página, en la misma forma que el resto de
   la API.

## Licencia

MIT. Véase [LICENSE](LICENSE).
