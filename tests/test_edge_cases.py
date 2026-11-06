"""Randfälle: leere Eingabe, ein Paket, Paket gleich Kapazität, gleich große Pakete, ungültige Eingaben, Gleichstände der Schranke."""

import pytest

import sbw_algorithm as A
import sbw_constants as C
from sbw_scenario import Instance, live_instanz, raster_instanz, raster_seed, zufallsinstanz


def test_leere_eingabe():
    assert A.ffd((), 10) == []
    assert A.l1((), 10) == 0 and A.l2((), 10) == 0 and A.optimum((), 10) == 0
    d = A.l2_detail((), 10)
    assert d["wert"] == 0 and d["l2"] == 0 and d["l2_ist_l1"] is True


def test_ein_paket_und_paket_gleich_kapazitaet():
    assert A.ffd((7,), 10) == [[0]]
    assert A.ffd((10, 10), 10) == [[0], [1]]
    assert A.ausgang(1, A.l1((7,), 10), A.l2((7,), 10), A.optimum((7,), 10)) == "l1"
    assert A.l2((10, 10, 10), 10) == 3 and A.optimum((10, 10, 10), 10) == 3


def test_gleich_grosse_pakete_fuellen_container_genau():
    assert A.ffd((5, 5, 5, 5), 10) == [[0, 1], [2, 3]]
    assert A.ausgang(2, A.l1((5, 5, 5, 5), 10), A.l2((5, 5, 5, 5), 10), 2) == "l1"


def test_gleichstand_beim_sortieren_haelt_die_nummernreihenfolge():
    assert A.ffd((4, 4, 4, 4), 10) == [[0, 1], [2, 3]]


def test_l2_bei_gleichstand_der_alpha_waehlt_das_kleinste():
    d = A.l2_detail((6, 6, 6, 2), 10)           # alpha = 0 und alpha = 2 ergeben beide 3
    assert d["alpha"] == 0 and d["wert"] == 3


def test_l2_ist_l1_wenn_kein_alpha_darueber_liegt():
    d = A.l2_detail((4, 4, 3, 3, 3, 3), 10)     # kein Paket über der halben Kapazität: L(alpha) = ceil(Summe / C) = L1
    assert d["l2_ist_l1"] is True and d["l1"] == 2 and d["l2"] == 2


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.ffd((11,), 10)                       # Paket größer als die Kapazität
    with pytest.raises(ValueError):
        A.ffd((0,), 10)                        # Größe null
    with pytest.raises(ValueError):
        Instance((3, 4), 0)                    # Kapazität null
    with pytest.raises(ValueError):
        Instance((3, 12), 10)                  # Paket größer als die Kapazität
    with pytest.raises(ValueError):
        Instance((3.5,), 10)                   # keine ganze Zahl


def test_zufallsinstanzen_sind_fest_und_liegen_im_bereich():
    a = zufallsinstanz(0.2, 0.8, 30, raster_seed(1, 2, 3), 1000)
    assert a == zufallsinstanz(0.2, 0.8, 30, raster_seed(1, 2, 3), 1000)
    assert a.n == 30 and all(200 <= s <= 800 for s in a.sizes)
    assert zufallsinstanz(0.2, 0.8, 30, raster_seed(1, 2, 4), 1000) != a
    assert raster_instanz(1, 2, 3).cap == C.MESS_CAP and raster_instanz(1, 2, 3).n == C.MESS_N[2]


def test_live_instanz_hat_mindestens_groesse_eins_und_die_kapazitaet_100():
    inst = live_instanz(2, 12, 5)               # breite Teile: untere Grenze 0,01 * 100 = 1
    assert inst.cap == 100 and inst.n == 12 and min(inst.sizes) >= 1 and max(inst.sizes) <= 90


def test_raster_seeds_sind_je_zelle_und_instanz_verschieden():
    seeds = {raster_seed(d, n, j) for d in range(3) for n in range(3) for j in range(C.INSTANZEN)}
    assert len(seeds) == 3 * 3 * C.INSTANZEN
