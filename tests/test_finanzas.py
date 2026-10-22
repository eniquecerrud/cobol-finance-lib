#!/usr/bin/env python3
"""Contrasta la biblioteca COBOL con fórmulas propias en decimal.Decimal.

Las referencias se calculan aquí, con precisión de 50 dígitos y redondeo
half-away-from-zero. No son valores copiados a mano.
"""

from __future__ import annotations

import csv
import os
import subprocess
import tempfile
import unittest
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
ENV = os.environ.copy()
ENV["COB_LIBRARY_PATH"] = str(BUILD)
ENV["LC_ALL"] = "C.UTF-8"

Q6 = Decimal("0.000001")
Q12 = Decimal("0.000000000001")
PREC = 50


def D(value) -> Decimal:
    return Decimal(str(value))


def q(value, quantum: Decimal) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        return D(value).quantize(quantum, rounding=ROUND_HALF_UP)


def run_calc(lines: list[str]) -> list[list[str]]:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    ) as handle:
        handle.write("\n".join(lines) + "\n")
        name = handle.name
    try:
        proc = subprocess.run(
            [str(BUILD / "fin-calc"), name],
            check=True,
            capture_output=True,
            text=True,
            env=ENV,
        )
    finally:
        os.unlink(name)
    if proc.stderr.strip():
        raise AssertionError(proc.stderr)
    return [line.split("|") for line in proc.stdout.splitlines() if line.strip()]


def run_program(name: str, args: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(BUILD / name), *(args or [])],
        check=False,
        capture_output=True,
        text=True,
        env=ENV,
    )


def pow_real(base, exponent: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        return D(base) ** exponent


def fv_compuesto(capital, tasa, periodos: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        return q(D(capital) * (1 + D(tasa)) ** periodos, Q6)


def vp_compuesto(futuro, tasa, periodos: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        return q(D(futuro) / (1 + D(tasa)) ** periodos, Q6)


def factor_anualidad(tasa, periodos: int) -> Decimal:
    """(1 - (1+r)**-n) / r. Con tasa 0 devuelve n."""
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        r = D(tasa)
        n = int(periodos)
        if r == 0:
            return Decimal(n)
        return (1 - (1 + r) ** (-n)) / r


def vp_anualidad(cuota, tasa, periodos: int, anticipada: bool) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        base = D(cuota) * factor_anualidad(tasa, periodos)
        if anticipada and D(tasa) != 0:
            base *= 1 + D(tasa)
        return q(base, Q6)


def vf_anualidad(cuota, tasa, periodos: int, anticipada: bool) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        r = D(tasa)
        n = int(periodos)
        if r == 0:
            bruto = D(cuota) * n
        else:
            bruto = D(cuota) * ((1 + r) ** n - 1) / r
            if anticipada:
                bruto *= 1 + r
        return q(bruto, Q6)


def cuota_francesa(capital, tasa, periodos: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        r = D(tasa)
        n = int(periodos)
        if r == 0:
            return q(D(capital) / n, Q6)
        factor = (1 + r) ** n
        return q(D(capital) * r * factor / (factor - 1), Q6)


def vpn(tasa, flujos) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PREC
        ctx.rounding = ROUND_HALF_UP
        total = Decimal(0)
        descuento = Decimal(1)
        r = D(tasa)
        for flujo in flujos:
            total += D(flujo) / descuento
            descuento *= 1 + r
        return total


def tir(flujos, semilla="0.1") -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 60
        ctx.rounding = ROUND_HALF_UP
        r = D(semilla)
        serie = [D(flujo) for flujo in flujos]
        for _ in range(80):
            descuento = Decimal(1)
            valor = Decimal(0)
            derivada = Decimal(0)
            for t, flujo in enumerate(serie):
                valor += flujo / descuento
                if t:
                    derivada += (-t * flujo) / (descuento * (1 + r))
                descuento *= 1 + r
            if abs(valor) < Decimal("1e-24") or derivada == 0:
                return r
            r -= valor / derivada
            if r <= -1:
                r = Decimal("-0.5")
        return r


class FinanzasDecimal(unittest.TestCase):
    def assert_cerca(self, obtenido, esperado, tolerancia, mensaje=""):
        diferencia = abs(D(obtenido) - D(esperado))
        self.assertLessEqual(
            diferencia,
            D(tolerancia),
            f"{mensaje} obtenido={obtenido} esperado={esperado} dif={diferencia}",
        )

    def test_potencia_exacta(self):
        fila = run_calc(["POT|2|10", "POT|5|0", "POT|0|5", "POT|10|3"])
        self.assertEqual(fila[0][0], "00")
        self.assertEqual(D(fila[0][1]), Decimal(1024))
        self.assertEqual(D(fila[1][1]), Decimal(1))
        self.assertEqual(D(fila[2][1]), Decimal(0))
        self.assertEqual(D(fila[3][1]), Decimal(1000))

    def test_potencia_negativa_y_cero(self):
        fila = run_calc(["POT|2|-3", "POT|4|-1", "POT|-2|3", "POT|-2|2"])
        self.assertEqual(D(fila[0][1]), Decimal("0.125"))
        self.assertEqual(D(fila[1][1]), Decimal("0.25"))
        self.assertEqual(D(fila[2][1]), Decimal(-8))
        self.assertEqual(D(fila[3][1]), Decimal(4))

    def test_potencia_error_division(self):
        fila = run_calc(["POT|0|-2"])
        self.assertEqual(fila[0][0], "02")

    def test_potencia_relativa_a_decimal(self):
        for base, exp in (("1.005", 360), ("1.01", 12), ("1.05", 600)):
            fila = run_calc([f"POT|{base}|{exp}"])[0]
            self.assertEqual(fila[0], "00")
            exacto = pow_real(base, exp)
            relativo = abs(D(fila[1]) - exacto) / abs(exacto)
            self.assertLess(relativo, Decimal("1e-12"), f"{base}^{exp}")

    def test_raiz_exacta_y_duodecima(self):
        exacta = run_calc(["RAIZ|1.21|2"])[0]
        self.assertEqual(D(exacta[1]), Decimal("1.1"))
        fila = run_calc(["RAIZ|1.12|12"])[0]
        with localcontext() as ctx:
            ctx.prec = PREC
            esperado = D("1.12") ** (Decimal(1) / Decimal(12))
        self.assert_cerca(fila[1], esperado, Decimal("1e-12"))

    def test_raiz_base_negativa(self):
        self.assertEqual(run_calc(["RAIZ|-8|3"])[0][0], "01")
        self.assertEqual(run_calc(["RAIZ|8|0"])[0][0], "01")

    def test_interes_simple_exacto(self):
        cero, caso = run_calc(["SIMP|1000|0|5", "SIMP|1000|0.08|2"])
        self.assertEqual(cero[0], "00")
        self.assertEqual(D(cero[1]), Decimal(0))
        self.assertEqual(D(cero[2]), Decimal(1000))
        self.assertEqual(D(caso[1]), Decimal(160))
        self.assertEqual(D(caso[2]), Decimal(1160))

    def test_interes_simple_fraccionario(self):
        fila = run_calc(["SIMP|1000|0.10|0.5", "SIMP|2500.5|0.04|1.25"])
        self.assertEqual(D(fila[0][1]), Decimal(50))
        self.assertEqual(D(fila[0][2]), Decimal(1050))
        interes = q(D("2500.5") * D("0.04") * D("1.25"), Q6)
        self.assertEqual(D(fila[1][1]), interes)
        self.assertEqual(D(fila[1][2]), D("2500.5") + interes)

    def test_interes_compuesto_un_periodo_y_tasa_cero(self):
        filas = run_calc(["COMP|1000|0.05|1", "COMP|1000|0|10", "VFUT|1000|0.05|1"])
        self.assertEqual(D(filas[0][1]), Decimal(1050))
        self.assertEqual(D(filas[0][2]), Decimal(50))
        self.assertEqual(D(filas[1][1]), Decimal(1000))
        self.assertEqual(D(filas[1][2]), Decimal(0))
        self.assertEqual(D(filas[2][1]), Decimal(1050))

    def test_interes_compuesto_contra_decimal(self):
        casos = [
            ("10000", "0.08", 10),
            ("250000", "0.045", 30),
            ("999.99", "0.005", 360),
            ("1", "0.1", 20),
        ]
        ordenes = [f"COMP|{c}|{r}|{n}" for c, r, n in casos]
        for fila, (capital, tasa, periodos) in zip(run_calc(ordenes), casos):
            esperado = fv_compuesto(capital, tasa, periodos)
            self.assertEqual(fila[0], "00")
            self.assert_cerca(fila[1], esperado, Q6)
            self.assert_cerca(fila[2], esperado - D(capital), Q6)

    def test_valor_presente_contra_decimal(self):
        fila = run_calc(["VPRE|20000|0.06|5", "VPRE|1050|0.05|1"])
        self.assert_cerca(fila[0][1], vp_compuesto(20000, "0.06", 5), Q6)
        self.assertEqual(D(fila[1][1]), Decimal(1000))

    def test_periodos_cero_compuesto(self):
        fila = run_calc(["COMP|1234.5|0.07|0", "VPRE|1234.5|0.07|0"])[0]
        self.assertEqual(D(fila[1]), Decimal("1234.5"))
        presente = run_calc(["VPRE|1234.5|0.07|0"])[0]
        self.assertEqual(D(presente[1]), Decimal("1234.5"))

    def test_tasa_singular(self):
        self.assertEqual(run_calc(["COMP|1000|-1|2"])[0][0], "02")
        self.assertEqual(run_calc(["VPRE|1000|-1.5|1"])[0][0], "02")
        self.assertEqual(run_calc(["EFEC|-12|12"])[0][0], "02")

    def test_efectiva_y_nominal(self):
        with localcontext() as ctx:
            ctx.prec = PREC
            ctx.rounding = ROUND_HALF_UP
            efectiva = q((1 + D("0.12") / 12) ** 12 - 1, Q12)
            nominal = q(12 * ((1 + efectiva) ** (Decimal(1) / 12) - 1), Q12)
        filas = run_calc(["EFEC|0.12|12", "EFEC|0.12|1", f"NOMI|{efectiva}|12"])
        self.assertEqual(D(filas[0][1]), efectiva)
        self.assertEqual(D(filas[1][1]), Decimal("0.12"))
        self.assert_cerca(filas[2][1], nominal, Q12)

    def test_nominal_redonda_viaje(self):
        efectiva = run_calc(["EFEC|0.07|4"])[0][1]
        nominal = run_calc([f"NOMI|{efectiva}|4"])[0][1]
        self.assert_cerca(nominal, "0.07", Decimal("0.00000000001"))

    def test_operacion_desconocida(self):
        self.assertEqual(run_calc(["NOPE|1"])[0][0], "09")

    def test_argumento_invalido(self):
        self.assertEqual(run_calc(["SIMP|abc|0.1|1"])[0][0], "01")
        self.assertEqual(run_calc(["PAGO|1000|0.01|1.5|F"])[0][0], "05")

    def test_anualidad_tasa_cero(self):
        ordinaria = run_calc(["PVAN|100|0|10|O", "FVAN|100|0|10|A", "CUOT|1000|0|10|O"])
        self.assertEqual(D(ordinaria[0][1]), Decimal(1000))
        self.assertEqual(D(ordinaria[1][1]), Decimal(1000))
        self.assertEqual(D(ordinaria[2][1]), Decimal(100))

    def test_anualidad_ordinaria_contra_decimal(self):
        fila = run_calc(["PVAN|1500|0.005|240|O", "FVAN|1500|0.005|240|O"])
        self.assert_cerca(fila[0][1], vp_anualidad(1500, "0.005", 240, False), Q6)
        self.assert_cerca(fila[1][1], vf_anualidad(1500, "0.005", 240, False), Q6)

    def test_anualidad_anticipada_relacion(self):
        filas = run_calc(
            [
                "PVAN|200|0.01|36|O",
                "PVAN|200|0.01|36|A",
                "FVAN|200|0.01|36|O",
                "FVAN|200|0.01|36|A",
            ]
        )
        self.assert_cerca(filas[0][1], vp_anualidad(200, "0.01", 36, False), Q6)
        self.assert_cerca(filas[1][1], vp_anualidad(200, "0.01", 36, True), Q6)
        self.assert_cerca(
            D(filas[1][1]),
            q(D(filas[0][1]) * Decimal("1.01"), Q6),
            Q6,
        )
        self.assert_cerca(filas[3][1], vf_anualidad(200, "0.01", 36, True), Q6)

    def test_anualidad_un_periodo(self):
        filas = run_calc(["PVAN|250|0.05|1|O", "PVAN|250|0.05|1|A"])
        self.assert_cerca(filas[0][1], q(Decimal(250) / Decimal("1.05"), Q6), Q6)
        self.assertEqual(D(filas[1][1]), Decimal(250))

    def test_cuota_recupera_valor_presente(self):
        presente = vp_anualidad(80, "0.008", 24, False)
        cuota = run_calc([f"CUOT|{presente}|0.008|24|O"])[0]
        self.assertEqual(cuota[0], "00")
        recuperado = vp_anualidad(cuota[1], "0.008", 24, False)
        self.assert_cerca(recuperado, presente, Decimal("0.0001"))

    def test_prestamo_tasa_cero_y_un_periodo(self):
        filas = run_calc(["PAGO|1200|0|12|F", "PAGO|1000|0.05|1|F"])
        self.assertEqual(D(filas[0][1]), Decimal(100))
        self.assertEqual(D(filas[0][6]), Decimal(0))
        self.assertEqual(D(filas[1][1]), Decimal(1050))
        self.assertEqual(D(filas[1][6]), Decimal(0))

    def test_prestamo_frances_cuota_y_cuadro(self):
        resumen = run_calc(["PAGO|12000|0.01|12|F"])[0]
        self.assertEqual(resumen[0], "00")
        self.assert_cerca(resumen[1], cuota_francesa(12000, "0.01", 12), Q6)
        self.assertEqual(D(resumen[6]), Decimal(0))
        filas = run_calc([f"FILA|12000|0.01|12|F|{k}" for k in range(1, 13)])
        saldo = Decimal(12000)
        cuota = D(resumen[1])
        total_cap = Decimal(0)
        for k, fila in enumerate(filas, start=1):
            self.assertEqual(fila[0], "00")
            interes = q(saldo * Decimal("0.01"), Q6)
            if k == 12 or (cuota - interes) > saldo:
                amort = saldo
                pago = amort + interes
            else:
                amort = cuota - interes
                pago = cuota
            saldo -= amort
            total_cap += amort
            self.assertEqual(D(fila[1]), pago)
            self.assertEqual(D(fila[2]), interes)
            self.assertEqual(D(fila[3]), amort)
            self.assertEqual(D(fila[4]), saldo)
        self.assertEqual(total_cap, Decimal(12000))
        self.assertEqual(saldo, Decimal(0))

    def test_prestamo_aleman_cuadro(self):
        resumen = run_calc(["PAGO|1200|0.01|12|G"])[0]
        self.assertEqual(D(resumen[1]), Decimal(100))
        primera = run_calc(["FILA|1200|0.01|12|G|1"])[0]
        self.assertEqual(D(primera[2]), Decimal(12))
        self.assertEqual(D(primera[3]), Decimal(100))
        self.assertEqual(D(primera[1]), Decimal(112))
        ultima = run_calc(["FILA|1200|0.01|12|G|12"])[0]
        self.assertEqual(D(ultima[4]), Decimal(0))
        filas = run_calc([f"FILA|1200|0.01|12|G|{k}" for k in range(1, 13)])
        self.assertEqual(sum(D(f[3]) for f in filas), Decimal(1200))

    def test_prestamo_coincide_con_anualidad(self):
        prestamo = run_calc(["PAGO|50000|0.006|180|F"])[0]
        anualidad = run_calc(["CUOT|50000|0.006|180|O"])[0]
        self.assertEqual(prestamo[0], "00")
        self.assertEqual(D(prestamo[1]), D(anualidad[1]))
        self.assert_cerca(prestamo[1], cuota_francesa(50000, "0.006", 180), Q6)

    def test_prestamo_metodo_y_plazo_invalidos(self):
        self.assertEqual(run_calc(["PAGO|1000|0.01|12|X"])[0][0], "08")
        self.assertEqual(run_calc(["PAGO|1000|0.01|0|F"])[0][0], "05")
        self.assertEqual(run_calc(["PAGO|1000|0.01|601|F"])[0][0], "05")
        self.assertEqual(run_calc(["PAGO|-5|0.01|12|F"])[0][0], "01")

    def test_hipoteca_clasica(self):
        tasa = D("0.045") / 12
        self.assertEqual(tasa, Decimal("0.00375"))
        fila = run_calc(["PAGO|250000|0.00375|360|F"])[0]
        self.assert_cerca(fila[1], cuota_francesa(250000, tasa, 360), Q6)
        self.assertEqual(D(fila[6]), Decimal(0))
        primera = run_calc(["FILA|250000|0.00375|360|F|1"])[0]
        self.assertEqual(D(primera[2]), q(Decimal(250000) * tasa, Q6))
        ultima = run_calc(["FILA|250000|0.00375|360|F|360"])[0]
        self.assertEqual(D(ultima[4]), Decimal(0))

    def test_vpn_tasa_cero_y_formula(self):
        cero = run_calc(["VPN|0|-100;40;60"])[0]
        self.assertEqual(D(cero[1]), Decimal(0))
        flujos = ["-100000", "30000", "35000", "40000", "45000"]
        fila = run_calc(["VPN|0.08|" + ";".join(flujos)])[0]
        self.assert_cerca(fila[1], q(vpn("0.08", flujos), Q6), Q6)
        uno = run_calc(["VPN|0.05|-1000;1100"])[0]
        self.assert_cerca(uno[1], q(vpn("0.05", ["-1000", "1100"]), Q6), Q6)

    def test_tir_cerrada(self):
        un_periodo = run_calc(["TIR|N|0.1|0.000000001|40|-100;110"])[0]
        self.assertEqual(un_periodo[0], "00")
        self.assertEqual(D(un_periodo[1]), Decimal("0.1"))
        dos = run_calc(["TIR|N|0.2|0.000000001|40|-100;0;121"])[0]
        self.assert_cerca(dos[1], "0.1", Decimal("1e-9"))
        self.assertEqual(dos[4], "N")

    def test_tir_negativa_y_dos_periodos(self):
        negativa = run_calc(["TIR|N|-0.05|0.000000001|40|-100;90"])[0]
        self.assertEqual(negativa[0], "00")
        self.assert_cerca(negativa[1], "-0.1", Decimal("1e-9"))
        flujos = ["-1000", "300", "400", "400", "300"]
        fila = run_calc(["TIR|N|0.1|0.000000001|80|" + ";".join(flujos)])[0]
        self.assertEqual(fila[0], "00")
        self.assert_cerca(fila[1], tir(flujos), Decimal("1e-9"))

    def test_tir_sin_cambio_de_signo(self):
        self.assertEqual(run_calc(["TIR|N|0.1|0.000000001|20|10;20;30"])[0][0], "04")
        self.assertEqual(run_calc(["TIR|N|0.1|0.000000001|20|-5;-1;0"])[0][0], "04")
        self.assertEqual(run_calc(["TIR|N|0.1|0.000000001|20|0;0;0"])[0][0], "04")
        self.assertEqual(run_calc(["TIR|N|0.1|0.000000001|20|-100"])[0][0], "04")

    def test_tir_serie_vacia(self):
        self.assertEqual(run_calc(["VPN|0.1|"])[0][0], "10")
        self.assertEqual(run_calc(["TIR|N|0.1|0.000000001|20|"])[0][0], "10")

    def test_tir_residual_de_vpn(self):
        flujos = ["-100000", "30000", "35000", "40000", "45000"]
        fila = run_calc(["TIR|N|0.1|0.000000001|80|" + ";".join(flujos)])[0]
        self.assertEqual(fila[0], "00")
        residual = vpn(fila[1], flujos)
        self.assertLess(abs(residual), Decimal("0.05"))
        self.assert_cerca(fila[2], q(residual, Q6), Decimal("0.02"))

    def test_tir_biseccion(self):
        flujos = ["-800", "200", "250", "260", "270"]
        fila = run_calc(["TIR|B|0|0.000000001|80|" + ";".join(flujos)])[0]
        self.assertEqual(fila[0], "00")
        self.assertEqual(fila[4], "B")
        self.assert_cerca(fila[1], tir(flujos), Decimal("1e-8"))

    def test_tir_newton_sin_reserva(self):
        flujos = ["-1000", "230", "240", "250", "260", "270", "280"]
        corto = run_calc(["TIR|W|0.9|0.000000000001|1|" + ";".join(flujos)])[0]
        self.assertEqual(corto[0], "03")
        completo = run_calc(["TIR|N|0.1|0.000000001|80|" + ";".join(flujos)])[0]
        self.assertEqual(completo[0], "00")
        self.assertIn(completo[4], ("N", "B"))
        self.assert_cerca(completo[1], tir(flujos), Decimal("1e-8"))

    def test_depreciacion_lineal(self):
        fila = run_calc(["LIN|1000|100|5|1", "LIN|1000|100|5|0"])
        self.assertEqual(D(fila[0][1]), Decimal(180))
        self.assertEqual(D(fila[0][2]), Decimal(180))
        self.assertEqual(D(fila[0][3]), Decimal(820))
        self.assertEqual(D(fila[1][1]), Decimal(900))
        self.assertEqual(D(fila[1][3]), Decimal(100))

    def test_depreciacion_lineal_reparto(self):
        filas = run_calc([f"LIN|1000|0|3|{anio}" for anio in (1, 2, 3)])
        self.assertEqual(D(filas[0][1]), Decimal("333.333333"))
        self.assertEqual(D(filas[1][1]), Decimal("333.333333"))
        self.assertEqual(D(filas[2][1]), Decimal("333.333334"))
        self.assertEqual(D(filas[2][3]), Decimal(0))
        self.assertEqual(sum(D(f[1]) for f in filas), Decimal(1000))

    def test_depreciacion_decreciente(self):
        filas = run_calc(
            ["DEC|1000|0|5|0.2|1", "DEC|1000|0|5|0.2|2", "DEC|1000|0|5|0.2|0"]
        )
        self.assertEqual(D(filas[0][1]), Decimal(200))
        self.assertEqual(D(filas[0][3]), Decimal(800))
        self.assertEqual(D(filas[1][1]), Decimal(160))
        self.assertEqual(D(filas[1][3]), Decimal(640))
        self.assertEqual(D(filas[2][3]), q(Decimal(1000) * (Decimal("0.8") ** 5), Q6))

    def test_depreciacion_doble_saldo(self):
        tasa = run_calc(["DSD|10000|0|5|0"])[0]
        self.assertEqual(D(tasa[4]), Decimal("0.4"))
        self.assertEqual(D(tasa[3]), Decimal("777.6"))
        self.assertEqual(D(tasa[1]), Decimal("9222.4"))
        vida3 = run_calc(["DSD|900|0|3|1"])[0]
        self.assertEqual(D(vida3[4]), Decimal("0.666666666667"))

    def test_depreciacion_piso_y_errores(self):
        piso = run_calc(["DEC|1000|900|5|0.5|1", "DEC|1000|900|5|0.5|2"])
        self.assertEqual(D(piso[0][1]), Decimal(100))
        self.assertEqual(D(piso[0][3]), Decimal(900))
        self.assertEqual(D(piso[1][1]), Decimal(0))
        self.assertEqual(run_calc(["DEC|1000|100|5|0|1"])[0][0], "01")
        self.assertEqual(run_calc(["LIN|100|200|5|1"])[0][0], "01")
        self.assertEqual(run_calc(["LIN|1000|0|0|1"])[0][0], "05")
        self.assertEqual(run_calc(["LIN|1000|0|5|9"])[0][0], "05")

    def test_lote_invariantes(self):
        with tempfile.TemporaryDirectory() as tmp:
            texto = Path(tmp) / "informe.txt"
            tabla = Path(tmp) / "informe.csv"
            proc = run_program(
                "fin-lote",
                [str(ROOT / "samples" / "lote.dat"), str(texto), str(tabla)],
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("Saldo final", texto.read_text(encoding="utf-8"))
            with tabla.open(encoding="utf-8") as handle:
                filas = list(csv.DictReader(handle))
        prestamos = [
            f for f in filas if f["tipo"] == "prestamo" and f["concepto"] == "periodo"
        ]
        for identificador, capital in (("MES-12", "12000"), ("HIP-001", "250000"), ("AUTO-002", "18000")):
            grupo = [f for f in prestamos if f["id"] == identificador]
            self.assertGreater(len(grupo), 0)
            amortizado = sum(D(f["v3"]) for f in grupo)
            self.assertEqual(amortizado, D(capital))
            self.assertEqual(D(grupo[-1]["v4"]), Decimal(0))
        resumen = next(
            f for f in filas if f["id"] == "HIP-001" and f["concepto"] == "resumen"
        )
        self.assertEqual(D(resumen["v5"]), Decimal("0.00375"))
        self.assert_cerca(resumen["v1"], cuota_francesa(250000, "0.00375", 360), Q6)

    def test_lote_contra_decimal(self):
        with tempfile.TemporaryDirectory() as tmp:
            tabla = Path(tmp) / "informe.csv"
            proc = run_program(
                "fin-lote",
                [
                    str(ROOT / "samples" / "lote.dat"),
                    str(Path(tmp) / "informe.txt"),
                    str(tabla),
                ],
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with tabla.open(encoding="utf-8") as handle:
                filas = list(csv.DictReader(handle))
        bono = next(f for f in filas if f["id"] == "BONO-1" and f["concepto"] == "tir")
        self.assert_cerca(bono["v1"], "0.1", Decimal("1e-9"))
        proyecto = ["-100000", "30000", "35000", "40000", "45000"]
        tir_proy = next(f for f in filas if f["id"] == "PROY-A" and f["concepto"] == "tir")
        self.assert_cerca(tir_proy["v1"], tir(proyecto), Decimal("1e-8"))
        vpn_proy = next(f for f in filas if f["id"] == "PROY-A" and f["concepto"] == "vpn")
        self.assert_cerca(vpn_proy["v1"], q(vpn("0.08", proyecto), Q6), Q6)
        pension = next(f for f in filas if f["id"] == "PENSION")
        self.assert_cerca(
            pension["v1"], vp_anualidad(1500, "0.005", 240, False), Q6
        )
        maquina = [
            f for f in filas if f["id"] == "MAQ-1" and f["concepto"] == "periodo"
        ]
        self.assertEqual(D(maquina[-1]["v3"]), Decimal(1500))
        self.assertEqual(sum(D(f["v1"]) for f in maquina), Decimal(13500))

    def test_lote_con_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "malo.dat"
            entrada.write_text("PRESTAMO|MALO|1000|0.05|12|12|Z\n", encoding="utf-8")
            proc = run_program(
                "fin-lote",
                [str(entrada), str(Path(tmp) / "a.txt"), str(Path(tmp) / "a.csv")],
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("08", Path(tmp, "a.csv").read_text(encoding="utf-8"))

    def test_demos_terminan(self):
        for nombre in (
            "demo-interes",
            "demo-prestamo",
            "demo-tir",
            "demo-anualidad",
            "demo-depreciacion",
        ):
            proc = run_program(nombre)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertGreater(len(proc.stdout.strip()), 40)
            self.assertNotIn("FALLO", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
