"""
tests/test_baraja.py
"""

import random

from games.cartas import Baraja, Carta, Palo


def test_baraja_tiene_52_cartas():
    baraja = Baraja()
    assert baraja.restantes() == 52


def test_baraja_sin_cartas_duplicadas():
    baraja = Baraja()
    assert len(set(baraja.cartas)) == 52


def test_repartir_carta_reduce_restantes_en_uno():
    baraja = Baraja()
    baraja.repartir_carta()
    assert baraja.restantes() == 51


def test_repartir_carta_devuelve_una_carta():
    baraja = Baraja()
    carta = baraja.repartir_carta()
    assert isinstance(carta, Carta)


def test_repartir_cartas_devuelve_n_cartas():
    baraja = Baraja()
    cartas = baraja.repartir_cartas(3)
    assert len(cartas) == 3
    assert all(isinstance(c, Carta) for c in cartas)


def test_repartir_cartas_reduce_restantes_en_n():
    baraja = Baraja()
    baraja.repartir_cartas(5)
    assert baraja.restantes() == 47


def test_cartas_repartidas_ya_no_estan_en_la_baraja():
    baraja = Baraja()
    repartidas = baraja.repartir_cartas(2)
    assert not any(c in baraja.cartas for c in repartidas)


def test_repartir_carta_reconstruye_baraja_si_se_queda_sin_cartas():
    baraja = Baraja()
    baraja.repartir_cartas(52)  # se queda en 0
    baraja.repartir_carta()  # debe reconstruir sola
    assert baraja.restantes() == 51


def test_repartir_cartas_reconstruye_baraja_si_no_alcanzan():
    baraja = Baraja()
    baraja.repartir_cartas(50)  # quedan 2
    baraja.repartir_cartas(5)  # pide más de las que hay -> reconstruye
    assert baraja.restantes() == 47  # 52 - 5, baraja nueva ya con el reparto aplicado


def test_shuffle_es_reproducible_con_rng_fija():
    baraja_a = Baraja(rng=random.Random(42))
    baraja_b = Baraja(rng=random.Random(42))
    assert baraja_a.cartas == baraja_b.cartas


def test_varios_mazos_multiplican_cantidad_de_cartas():
    baraja = Baraja(num_decks=2)
    assert baraja.restantes() == 104