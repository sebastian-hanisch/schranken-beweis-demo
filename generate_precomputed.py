"""Erzeugt sbw_precomputed.json: das Raster (3 Größenbereiche x 3 Paketzahlen x 100 feste Instanzen) als Zeichenkette von Ausgangscodes je Zelle.

    python generate_precomputed.py            # rechnet alles neu (mit 20 und 30 Paketen ungefähr 7 bis 8 Minuten wegen der ganzzahligen Programme)
    python generate_precomputed.py --check    # rechnet nur das Schnelle nach (Aufteilung L1 / L2 / offen aller Zellen, Codes der Zellen mit 12 Paketen) und vergleicht

Codes je Instanz: 1 = FFD gleich L1 (bewiesen), 2 = FFD gleich L2 (bewiesen erst durch L2), o = offen und FFD optimal, n = offen und FFD nicht optimal,
u = offen, vom ganzzahligen Programm in der Zeit nicht entschieden. Das Optimum kommt bei 12 Paketen aus der Teilmengen-DP, bei 20 und 30 aus
`scipy.optimize.milp` (Zuordnungsmodell, Zeitlimit C.ILP_ZEITLIMIT je Aufruf); scipy wird nur hier gebraucht, nicht von der App.

Die Zahl der nicht entschiedenen Instanzen hängt von der Rechenzeit des Rechners ab; die Datei hält den Stand dieses Laufs fest."""

import json
import sys
import time

import sbw_algorithm as A
import sbw_constants as C
import sbw_evaluation as ev
from dev.ilp import optimum_ilp
from sbw_scenario import raster_instanz


def instanz_code(verteilung: int, n_index: int, j: int, zeitlimit: float = C.ILP_ZEITLIMIT) -> str:
    inst = raster_instanz(verteilung, n_index, j)
    f = len(A.ffd(inst.sizes, inst.cap))
    s1, s2 = A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
    if f == s1:
        return "1"
    if f == s2:
        return "2"
    opt = A.optimum(inst.sizes, inst.cap, C.OPT_LIMIT) if inst.n <= C.OPT_LIMIT else optimum_ilp(inst.sizes, inst.cap, s2, f, zeitlimit)
    if opt is None:
        return "u"
    return "o" if opt == f else "n"


def zelle(verteilung: int, n_index: int) -> str:
    return "".join(instanz_code(verteilung, n_index, j) for j in range(C.INSTANZEN))


def erzeugen() -> dict:
    daten = {"instanzen": C.INSTANZEN, "cap": C.MESS_CAP, "ilp_zeitlimit": C.ILP_ZEITLIMIT, "zellen": {}}
    for d in range(len(C.VERTEILUNGEN)):
        for ni in range(len(C.MESS_N)):
            t = time.perf_counter()
            daten["zellen"][ev.zelle_schluessel(d, ni)] = zelle(d, ni)
            print(f"{ev.zelle_schluessel(d, ni)}: {time.perf_counter() - t:.0f} s  {daten['zellen'][ev.zelle_schluessel(d, ni)].count('u')} nicht entschieden", flush=True)
    return daten


def pruefen() -> int:
    """Schnelle Gegenprobe: Aufteilung aller Zellen und Codes der Zellen mit 12 Paketen."""
    gespeichert = ev.vorberechnet()
    schlecht = 0
    for d in range(len(C.VERTEILUNGEN)):
        for ni in range(len(C.MESS_N)):
            codes = gespeichert["zellen"][ev.zelle_schluessel(d, ni)]
            frisch = ev.aufteilung_frisch(d, ni)
            z = ev.zaehlen(codes)
            if (z["l1"], z["l2"], z["offen_optimal"] + z["offen_nicht_optimal"] + z["offen_unentschieden"]) != (frisch["l1"], frisch["l2"], frisch["offen"]):
                schlecht += 1
                print("ABWEICHUNG Aufteilung", ev.zelle_schluessel(d, ni))
            if C.MESS_N[ni] <= C.OPT_LIMIT and zelle(d, ni) != codes:
                schlecht += 1
                print("ABWEICHUNG Codes", ev.zelle_schluessel(d, ni))
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


def main() -> int:
    if "--check" in sys.argv:
        return pruefen()
    text = json.dumps(erzeugen(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    ev.PRECOMPUTED.write_text(text, encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
