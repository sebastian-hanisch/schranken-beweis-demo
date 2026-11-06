"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (sbw_precomputed.json) wird je Zelle nachgerechnet: die Aufteilung L1 / L2 / offen für alle neun Zellen (schnell, ohne Optimum), die vollständigen
  Codes für die Zellen mit 12 Paketen (Teilmengen-DP) und eine Stichprobe entschiedener offener Instanzen mit 20 Paketen (ganzzahliges Programm, übersprungen ohne scipy).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet, über das GANZE Raster gezählt und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README."""

import itertools
from pathlib import Path

import pytest

import sbw_algorithm as A
import sbw_constants as C
import sbw_evaluation as ev
from sbw_scenario import raster_instanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
NAME = {0: "mittel", 1: "groß", 2: "breit"}


def codes(d, ni):
    return ev.vorberechnet()["zellen"][ev.zelle_schluessel(d, ni)]


def test_raster_hat_alle_zellen_und_die_zahl_der_instanzen():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.MESS_CAP == 1000 and daten["ilp_zeitlimit"] == C.ILP_ZEITLIMIT == 10.0
    assert set(daten["zellen"]) == {ev.zelle_schluessel(d, ni) for d, ni in ZELLEN} and len(ZELLEN) == 9
    assert all(len(c) == 100 and set(c) <= set(C.AUSGANG_CODES) for c in daten["zellen"].values())


@pytest.mark.parametrize("d,ni", ZELLEN)
def test_aufteilung_l1_l2_offen_stimmt_mit_frischer_rechnung(d, ni):
    z = ev.zaehlen(codes(d, ni))
    frisch = ev.aufteilung_frisch(d, ni)
    assert (z["l1"], z["l2"], z["offen_optimal"] + z["offen_nicht_optimal"] + z["offen_unentschieden"]) == (frisch["l1"], frisch["l2"], frisch["offen"])


@pytest.mark.parametrize("d", range(3))
def test_codes_der_zellen_mit_12_paketen_stimmen_mit_der_dp_ueberein(d):
    ni = C.MESS_N.index(12)
    erwartet = []
    for j in range(C.INSTANZEN):
        inst = raster_instanz(d, ni, j)
        f, s1, s2 = len(A.ffd(inst.sizes, inst.cap)), A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
        opt = A.optimum(inst.sizes, inst.cap)
        erwartet.append("1" if f == s1 else "2" if f == s2 else "o" if opt == f else "n")
        if f in (s1, s2):
            assert opt == f, (d, j)               # bewiesen heißt: FFD ist wirklich optimal
    assert "".join(erwartet) == codes(d, ni)


@pytest.mark.parametrize("d", range(3))
def test_stichprobe_der_zellen_mit_20_paketen_stimmt_mit_dem_ganzzahligen_programm_ueberein(d):
    pytest.importorskip("scipy")
    from dev.ilp import optimum_ilp

    ni = C.MESS_N.index(20)
    entschieden = [j for j, c in enumerate(codes(d, ni)) if c in "on"][:3]
    assert entschieden, "keine entschiedene offene Instanz in der Zelle"
    for j in entschieden:
        inst = raster_instanz(d, ni, j)
        f, s2 = len(A.ffd(inst.sizes, inst.cap)), A.l2(inst.sizes, inst.cap)
        opt = optimum_ilp(inst.sizes, inst.cap, s2, f, 120.0)
        assert opt is not None and ("o" if opt == f else "n") == codes(d, ni)[j], (d, j)


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def test_readme_tabelle_gibt_jede_zelle_wieder():
    for d, ni in ZELLEN:
        z = ev.zeile(d, ni)
        zeile = f"| {NAME[d]} | {z['n']} | {z['l1']} | {z['l2']} | {z['offen']} | {z['offen_optimal']} | {z['offen_nicht_optimal']} | {z['offen_unentschieden']} |"
        assert zeile in README, zeile
        assert z["l1"] + z["l2"] + z["offen"] == z["instanzen"] == 100


def test_mittlere_teile_l2_beweist_nie_mehr_als_l1():
    assert sum(ev.zeile(0, ni)["l2"] for ni in range(3)) == 0
    assert "in **0 von 300** Instanzen mehr als L₁" in README


def test_offene_faelle_mittlere_teile():
    z = [ev.zeile(0, ni) for ni in range(3)]
    assert [(x["offen_nicht_optimal"], x["offen_optimal"] + x["offen_nicht_optimal"]) for x in z] == [(8, 13), (19, 20), (21, 22)]
    assert "bei n = 12 in 8 von 13 nicht optimal, bei n = 20 in 19 von 20 und bei n = 30 in 21 von 22" in README


def test_offene_faelle_grosse_und_breite_teile():
    z = [ev.zeile(1, ni) for ni in range(3)]
    assert [x["l2"] for x in z] == [58, 63, 65] and "zusätzlich in 58, 63 und 65 von 100" in README
    assert [(x["offen_optimal"], x["offen_optimal"] + x["offen_nicht_optimal"]) for x in z] == [(4, 4), (12, 12), (7, 8)]
    assert "in 4 von 4, 12 von 12 und 7 von 8 optimal" in README
    z = [ev.zeile(2, ni) for ni in range(3)]
    assert [x["l2"] for x in z] == [48, 43, 63] and "zusätzlich in 48, 43 und 63 von 100" in README
    assert [(x["offen_optimal"], x["offen_optimal"] + x["offen_nicht_optimal"]) for x in z] == [(3, 3), (9, 12), (2, 4)]
    assert "in 3 von 3, 9 von 12 und 2 von 4 optimal" in README


def test_nicht_entschiedene_instanzen():
    alle = [ev.zeile(d, ni) for d, ni in ZELLEN]
    assert sum(x["offen_unentschieden"] for x in alle if x["n"] > 12) == 31 and sum(x["instanzen"] for x in alle if x["n"] > 12) == 600
    assert sum(x["offen_unentschieden"] for x in alle if x["n"] == 30) == 29 and sum(x["offen_unentschieden"] for x in alle if x["n"] == 20) == 2
    ueber = {ev.zeile(d, 2)["offen_unentschieden"] for d in range(3)}
    assert [ev.zeile(d, 2)["offen_unentschieden"] for d in range(3)] == [10, 10, 9]
    assert [ev.zeile(d, 1)["offen_unentschieden"] for d in range(3)] == [1, 1, 0] and ueber == {9, 10}
    assert "**31 von 600**" in README and "davon 29 bei n = 30 (10 bei mittleren, 10 bei großen, 9 bei breiten Teilen) und 2 bei n = 20" in README
    breit30 = ev.zeile(2, 2)
    assert breit30["offen"] - breit30["offen_unentschieden"] == 4 and breit30["offen"] == 13
    assert "nur 4 von 13 offenen Fällen entschieden" in README


def test_zweiter_satz_instanzen_belegt_die_instabilitaet_bei_12_paketen():
    """Seeds 100 bis 199 derselben Zellen (README, Ehrliche Grenzen): mittel offen 13, davon 6 nicht optimal; groß offen 12, davon 10 optimal und 2 nicht optimal."""
    ni = C.MESS_N.index(12)

    def block(d):
        z = {"o": 0, "n": 0}
        for j in range(100, 200):
            inst = raster_instanz(d, ni, j)
            f, s1, s2 = len(A.ffd(inst.sizes, inst.cap)), A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
            if f not in (s1, s2):
                z["o" if A.optimum(inst.sizes, inst.cap) == f else "n"] += 1
        return z

    assert block(0) == {"o": 7, "n": 6} and block(1) == {"o": 10, "n": 2}
    assert "von 13 offenen Fällen 6 (statt 8) nicht optimal" in README and "von 12 offenen Fällen 10 optimal und 2 nicht optimal (statt 4 und 0 von 4)" in README


# --- Handbeispiele und Texte -----------------------------------------------------------------------------------------------------------------


def test_readme_nennt_die_vier_handbeispiele():
    zeilen = ["| 1 | 613 | 7 | 7 | 7 | 7 | bewiesen durch L1 |", "| 2 | 834 | 11 | 9 | 11 | 11 | bewiesen erst durch L2 |",
              "| 3 | 498 | 6 | 5 | 5 | 6 | offen, FFD optimal |", "| 4 | 496 | 6 | 5 | 5 | 5 | offen, FFD nicht optimal |"]
    for i, zeile in enumerate(zeilen):
        a = ev.analyse(ev.Settings(i))
        assert f"| {i + 1} | {sum(a.inst.sizes)} | {a.ffd} | {a.schranke_l1} | {a.detail['l2']} | {a.opt} | {C.AUSGANG_TEXTE[a.ausgang]} |" == zeile
        assert zeile in README


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    assert f"{C.INSTANZEN} Instanzen je Zelle" in C.ASSUMPTIONS_MARKDOWN and f"bis {C.OPT_LIMIT} Pakete" in C.ASSUMPTIONS_MARKDOWN
    assert f"{C.ILP_ZEITLIMIT:.0f} Sekunden Zeitlimit" in C.ASSUMPTIONS_MARKDOWN and C.MESS_N == (12, 20, 30)
