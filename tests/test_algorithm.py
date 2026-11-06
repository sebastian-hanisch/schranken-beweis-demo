"""Kern an den vier Mini-Instanzen von Hand (Rechnung in tests/conftest.py) und an den vier Handbeispielen der App."""

import pytest

import sbw_algorithm as A
import sbw_constants as C
import sbw_evaluation as ev
from sbw_scenario import beispiel


def _zahlen(inst):
    bins = A.ffd(inst.sizes, inst.cap)
    d = A.l2_detail(inst.sizes, inst.cap)
    return len(bins), d["l1"], d["l2"], A.optimum(inst.sizes, inst.cap), A.ausgang(len(bins), d["l1"], d["l2"], A.optimum(inst.sizes, inst.cap))


def test_mini_l1(mini_l1):
    assert A.ffd(mini_l1.sizes, 10) == [[0, 1], [2, 3, 4]]
    assert _zahlen(mini_l1) == (2, 2, 2, 2, "l1")


def test_mini_l2(mini_l2):
    assert A.ffd(mini_l2.sizes, 10) == [[0, 3], [1], [2]]
    assert _zahlen(mini_l2) == (3, 2, 3, 3, "l2")


def test_mini_l2_aufteilung_von_hand(mini_l2):
    d = A.l2_detail(mini_l2.sizes, 10)
    assert d["alpha"] == 0 and d["j1"] == [] and d["j2"] == [6, 6, 6] and d["j3"] == [2]
    assert (d["frei"], d["summe_j3"], d["extra"], d["wert"], d["l1"], d["l2"], d["l2_ist_l1"]) == (12, 2, 0, 3, 2, 3, False)


def test_mini_offen_optimal(mini_offen_optimal):
    assert A.ffd(mini_offen_optimal.sizes, 10) == [[0, 1], [2, 3], [4]]
    assert _zahlen(mini_offen_optimal) == (3, 2, 2, 3, "offen_optimal")


def test_mini_offen_nicht_optimal(mini_offen_nicht_optimal):
    assert A.ffd(mini_offen_nicht_optimal.sizes, 10) == [[0, 1], [2, 3, 4], [5]]
    assert _zahlen(mini_offen_nicht_optimal) == (3, 2, 2, 2, "offen_nicht_optimal")


# --- die vier Handbeispiele der App (Phase 0, mit der Teilmengen-DP geprüft) ---------------------------------------------------------------------


@pytest.mark.parametrize("index,summe,ffd,l1,l2,opt,aus", [
    (0, 613, 7, 7, 7, 7, "l1"),
    (1, 834, 11, 9, 11, 11, "l2"),
    (2, 498, 6, 5, 5, 6, "offen_optimal"),
    (3, 496, 6, 5, 5, 5, "offen_nicht_optimal"),
])
def test_handbeispiele(index, summe, ffd, l1, l2, opt, aus):
    inst = beispiel(index)
    assert inst.n == 12 and inst.cap == 100 and sum(inst.sizes) == summe
    assert _zahlen(inst) == (ffd, l1, l2, opt, aus)
    a = ev.analyse(ev.Settings(index))
    assert (a.ffd, a.schranke_l1, a.detail["l2"], a.opt, a.ausgang) == (ffd, l1, l2, opt, aus)


def test_handbeispiel_2_l2_rechnung():
    """Beispiel 2: beim besten alpha = 33 sind J1 acht Pakete über 67, J2 zwei Pakete (67, 67) mit 66 freiem Platz, J3 = {34, 33} mit Summe 67: 8 + 2 + ceil((67 - 66)/100) = 11."""
    d = A.l2_detail(beispiel(1).sizes, 100)
    assert d["alpha"] == 33 and len(d["j1"]) == 8 and d["j2"] == [67, 67] and d["j3"] == [34, 33]
    assert (d["frei"], d["summe_j3"], d["extra"], d["wert"]) == (66, 67, 1, 11)


def test_alle_ffd_packungen_sind_zulaessig():
    for i in C.BEISPIELE:
        inst = beispiel(i)
        assert A.container_pruefen(inst.sizes, A.ffd(inst.sizes, inst.cap), inst.cap)


def test_ausgang_ordnung_der_zweige():
    assert A.ausgang(5, 5, 5, 5) == "l1"           # FFD = L1 = L2: zuerst L1
    assert A.ausgang(5, 4, 5, 5) == "l2"
    assert A.ausgang(6, 5, 5, 6) == "offen_optimal"
    assert A.ausgang(6, 5, 5, 5) == "offen_nicht_optimal"
    assert A.ausgang(6, 5, 5, None) == "offen_unentschieden"
    assert A.ausgang(5, 5, 6, None) == "l1"        # bewiesen, obwohl das Optimum unbekannt ist
