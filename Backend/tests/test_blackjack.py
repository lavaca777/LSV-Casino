"""
tests/test_blackjack.py
"""

import random

from games.cartas import Carta, Palo
from games.blackjack import (
    desicion_bot,
    es_blackjack_natural,
    es_busted,
    es_mano_blanda,
    resolver_ganador,
    turno_bot,
    valor_mano,
)


def C(rango: str, palo: Palo = Palo.CORAZON) -> Carta:
    """Atajo para crear cartas en los tests."""
    return Carta(palo, rango)


# --- valor_mano ------------------------------------------------------

def test_valor_mano_cartas_numericas():
    assert valor_mano([C("4"), C("5")]) == 9


def test_valor_mano_figuras_valen_diez():
    assert valor_mano([C("K"), C("Q")]) == 20


def test_valor_mano_as_cuenta_once_si_cabe():
    assert valor_mano([C("A"), C("6")]) == 17


def test_valor_mano_as_baja_a_uno_para_evitar_pasarse():
    assert valor_mano([C("A"), C("9"), C("5")]) == 15  # 11+9+5=25 -> As baja a 1


def test_valor_mano_dos_ases():
    assert valor_mano([C("A"), C("A")]) == 12  # un As en 11, otro en 1


# --- es_blackjack_natural / es_busted --------------------------------

def test_es_blackjack_natural_true_con_21_de_dos_cartas():
    assert es_blackjack_natural([C("A"), C("K")]) is True


def test_es_blackjack_natural_false_con_21_de_tres_cartas():
    assert es_blackjack_natural([C("7"), C("7"), C("7")]) is False


def test_es_busted_true_sobre_21():
    assert es_busted([C("K"), C("Q"), C("5")]) is True


def test_es_busted_false_en_21():
    assert es_busted([C("K"), C("Q"), C("A")]) is False


# --- es_mano_blanda ----------------------------------------------------

def test_mano_blanda_true_con_as_en_once():
    assert es_mano_blanda([C("A"), C("6")]) is True


def test_mano_blanda_false_con_as_forzado_a_uno():
    assert es_mano_blanda([C("A"), C("9"), C("5")]) is False  # As ya vale 1, no 11


def test_mano_blanda_false_sin_as():
    assert es_mano_blanda([C("10"), C("7")]) is False


def test_mano_blanda_true_en_soft_alto():
    # soft 20 (A+9): sigue siendo "blanda" en definición, pero
    # desicion_bot NO debe tratarla como el caso 50/50 (eso es solo soft 17)
    assert es_mano_blanda([C("A"), C("9")]) is True


# --- desicion_bot ----------------------------------------------------

def test_bot_pide_carta_bajo_17():
    assert desicion_bot([C("9"), C("6")]) == "hit"  # 15 duro


def test_bot_se_planta_en_17_duro_o_mas():
    assert desicion_bot([C("10"), C("7")]) == "stand"  # 17 duro


def test_bot_se_planta_sobre_17():
    assert desicion_bot([C("10"), C("9")]) == "stand"  # 19


def test_bot_se_planta_en_soft_20_sin_azar():
    # clave: la regla 50/50 es SOLO para soft 17, no para cualquier soft >=17
    assert desicion_bot([C("A"), C("9")]) == "stand"  # soft 20


def test_bot_soft_17_cincuenta_cincuenta_semilla_stand():
    mano = [C("A"), C("6")]  # soft 17
    assert desicion_bot(mano, random.Random(0)) == "stand"


def test_bot_soft_17_cincuenta_cincuenta_semilla_hit():
    mano = [C("A"), C("6")]  # soft 17
    assert desicion_bot(mano, random.Random(1)) == "hit"


def test_bot_funciona_sin_rng_explicito():
    # rng=None no debe tronar (usa random global como fallback)
    resultado = desicion_bot([C("A"), C("6")])
    assert resultado in ("hit", "stand")


# --- turno_bot (con baraja falsa controlada) ------------------------

class BarajaFija:
    """Baraja falsa que reparte cartas predefinidas, para tests deterministas."""

    def __init__(self, cartas: list[Carta]):
        self._cartas = cartas

    def repartir_carta(self) -> Carta:
        carta, self._cartas = self._cartas[0], self._cartas[1:]
        return carta

    def repartir_cartas(self, n: int) -> list[Carta]:
        cartas, self._cartas = self._cartas[:n], self._cartas[n:]
        return cartas


def test_turno_bot_se_detiene_en_17_duro():
    baraja = BarajaFija([])  # no debería necesitar pedir nada
    mano = turno_bot([C("10"), C("7")], baraja)
    assert valor_mano(mano) == 17
    assert len(mano) == 2


def test_turno_bot_pide_hasta_plantarse():
    baraja = BarajaFija([C("5")])  # una carta para completar 12 -> 17
    mano = turno_bot([C("6"), C("6")], baraja)
    assert valor_mano(mano) == 17
    assert len(mano) == 3


def test_turno_bot_se_detiene_si_se_pasa():
    baraja = BarajaFija([C("K")])  # 6+6+10 = pasa
    mano = turno_bot([C("6"), C("6")], baraja)
    assert es_busted(mano) is True


# --- resolver_ganador -----------------------------------------------

def test_resolver_ganador_jugador_gana_por_mayor_total():
    jugador = [C("10"), C("9")]  # 19
    bots = [[C("10"), C("7")]]  # 17
    assert resolver_ganador(jugador, bots) == "win"


def test_resolver_ganador_jugador_pierde_por_menor_total():
    jugador = [C("10"), C("7")]  # 17
    bots = [[C("10"), C("9")]]  # 19
    assert resolver_ganador(jugador, bots) == "loss"


def test_resolver_ganador_empate():
    jugador = [C("10"), C("7")]  # 17
    bots = [[C("9"), C("8")]]  # 17
    assert resolver_ganador(jugador, bots) == "draw"


def test_resolver_ganador_jugador_pasado_siempre_pierde():
    jugador = [C("10"), C("9"), C("5")]  # se pasa
    bots = [[C("2"), C("2")]]  # bot con mano muy baja
    assert resolver_ganador(jugador, bots) == "loss"


def test_resolver_ganador_todos_los_bots_se_pasan_jugador_gana():
    jugador = [C("9"), C("5")]  # 14, no gran mano
    bots = [[C("10"), C("9"), C("5")], [C("10"), C("8"), C("6")]]  # ambos se pasan
    assert resolver_ganador(jugador, bots) == "win"


def test_resolver_ganador_ignora_bots_pasados_al_comparar():
    jugador = [C("10"), C("6")]  # 16
    bots = [
        [C("10"), C("9"), C("5")],  # se pasa, no cuenta
        [C("10"), C("8")],  # 18, sí cuenta
    ]
    assert resolver_ganador(jugador, bots) == "loss"  # 16 < 18