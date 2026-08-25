from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import random

class Palo(str, Enum):
    CORAZON = "corazon"
    DIAMANTE = "diamante"
    TREBOL = "trebol"
    ESPADA = "espada"

RANGOS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

@dataclass(frozen=True)
class Carta:
    palo: Palo
    rango: str

    def __str__(self) -> str:
        return f"{self.rango} de {self.palo.value}"

class Baraja:
    def __init__(self, num_decks: int = 1, rng: random.Random | None = None):
        self.num_decks = num_decks
        self.rng = rng or random.Random()
        self.cartas: list[Carta] = []
        self.reset()

    def reset(self) -> None:
        self.cartas = [Carta(palo, rango) for palo in Palo for rango in RANGOS] * self.num_decks
        self.rng.shuffle(self.cartas)
        
    def repartir_carta(self) -> Carta:
                if len(self.cartas) < 1:
            self.reset()
        dealt = self.cartas[:n]
        self.cartas = self.cartas[n:]
        return dealt
    
