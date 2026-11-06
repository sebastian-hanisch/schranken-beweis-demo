"""Instanzen: Handbeispiele, zufällige Live-Instanzen und Rasterinstanzen mit festen Seeds."""

import random
from dataclasses import dataclass

import sbw_constants as C


@dataclass(frozen=True)
class Instance:
    sizes: tuple          # Paketgrößen, ganzzahlig und positiv
    cap: int = C.CAP      # Kapazität eines Containers

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for s in self.sizes:
            if not isinstance(s, int) or s <= 0 or s > self.cap:
                raise ValueError(f"Paketgröße {s!r} ungültig (ganz, 1 bis {self.cap})")

    @property
    def n(self) -> int:
        return len(self.sizes)


def beispiel(index: int) -> Instance:
    return Instance(tuple(C.BEISPIELE[index]), C.CAP)


def zufallsinstanz(lo: float, hi: float, n: int, seed: int, cap: int) -> Instance:
    """n Pakete, Größen ganzzahlig und gleichverteilt zwischen lo*cap und hi*cap (mindestens 1)."""
    rng = random.Random(seed)
    a, b = max(1, int(lo * cap)), int(hi * cap)
    return Instance(tuple(rng.randint(a, b) for _ in range(n)), cap)


def live_instanz(verteilung: int, n: int, seed: int) -> Instance:
    _, _, lo, hi = C.VERTEILUNGEN[verteilung]
    return zufallsinstanz(lo, hi, n, seed, C.CAP)


def raster_seed(verteilung: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Rasterzelle (Größenbereich, Paketzahl); stabil über Läufe und Rechner."""
    return 1_000_000 * (verteilung + 1) + 1_000 * (n_index + 1) + j


def raster_instanz(verteilung: int, n_index: int, j: int) -> Instance:
    _, _, lo, hi = C.VERTEILUNGEN[verteilung]
    return zufallsinstanz(lo, hi, C.MESS_N[n_index], raster_seed(verteilung, n_index, j), C.MESS_CAP)
