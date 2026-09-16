from decimal import Decimal
from unittest.mock import patch

import pytest

from app.games.base import BaseGame
from app.games.coinflip.game import CoinflipGame


def test_coinflip_implementa_basegame():
    assert isinstance(CoinflipGame(), BaseGame)


def test_gana_cuando_eleccion_coincide():
    with patch("app.games.coinflip.game.random.choice", return_value="cara"):
        r = CoinflipGame().play("u1", Decimal("20"), eleccion="cara")
    assert r["resultado"] == "win"
    assert r["moneda"] == "cara"
    assert r["payout"] == Decimal("40")  # apuesta x2


def test_pierde_cuando_eleccion_no_coincide():
    with patch("app.games.coinflip.game.random.choice", return_value="cruz"):
        r = CoinflipGame().play("u1", Decimal("20"), eleccion="cara")
    assert r["resultado"] == "loss"
    assert r["moneda"] == "cruz"
    assert r["payout"] == Decimal("0")


def test_eleccion_invalida_lanza_error():
    with pytest.raises(ValueError):
        CoinflipGame().play("u1", Decimal("20"), eleccion="otro")


def test_rules_y_house_edge():
    juego = CoinflipGame()
    rules = juego.get_rules()
    assert juego.name == "coinflip"
    assert rules["opciones"] == ["cara", "cruz"]
    assert juego.get_house_edge() == 0.0
