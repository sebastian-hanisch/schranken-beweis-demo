"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden (ohne ILP).

  Optimum (Teilmengen-DP über Bitmasken)  gegen  (a) Aufzählung aller Zerlegungen (n <= 8), (b) zweite DP über Untermengen (n <= 10),
                                                 (c) ein ganzzahliges Programm (scipy.optimize.milp, n <= 11; übersprungen ohne scipy).
  FFD                                     gegen  eine bewusst naive Zweitumsetzung (Pakete als Listen, Füllung jedes Mal neu summiert).
  Schranke L2                             gegen  die Rechnung über ALLE ganzzahligen alpha statt nur über die Paketgrößen.
  Eigenschaften mit exaktem Optimum: L1 <= L2 <= OPT <= FFD; der Ausgang stimmt mit einer unabhängigen Neueinordnung überein.
"""

import random

import pytest

import sbw_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=5, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, [rng.randint(1, cap) for _ in range(n)]


def optimum_aufzaehlung(sizes, cap):
    """Kleinste Containerzahl durch Aufzählung aller Zerlegungen (Paket i kommt in einen bestehenden oder in einen neuen Container)."""
    n = len(sizes)
    if n == 0:
        return 0
    best = n

    def rec(i, loads):
        nonlocal best
        if len(loads) >= best:
            return
        if i == n:
            best = len(loads)
            return
        for b in range(len(loads)):
            if loads[b] + sizes[i] <= cap:
                loads[b] += sizes[i]
                rec(i + 1, loads)
                loads[b] -= sizes[i]
        loads.append(sizes[i])
        rec(i + 1, loads)
        loads.pop()

    rec(0, [])
    return best


def optimum_untermengen(sizes, cap):
    """Zweite DP: g(M) = kleinste Containerzahl für die Menge M; der Container mit dem niedrigsten Paket von M nimmt eine Untermenge auf, die in 'cap' passt."""
    n = len(sizes)
    full = (1 << n) - 1
    summe = [0] * (full + 1)
    for m in range(1, full + 1):
        low = (m & -m).bit_length() - 1
        summe[m] = summe[m & (m - 1)] + sizes[low]
    g = [0] * (full + 1)
    for m in range(1, full + 1):
        low = m & -m
        rest = m ^ low
        sub = rest
        beste = n + 1
        while True:
            t = sub | low
            if summe[t] <= cap and g[m ^ t] + 1 < beste:
                beste = g[m ^ t] + 1
            if sub == 0:
                break
            sub = (sub - 1) & rest
        g[m] = beste
    return g[full]


def test_optimum_stimmt_mit_der_aufzaehlung_ueberein():
    for cap, sizes in instanzen(80, 1, 8):
        assert A.optimum(sizes, cap) == optimum_aufzaehlung(sizes, cap), (cap, sizes)


def test_optimum_stimmt_mit_der_untermengen_dp_ueberein():
    for cap, sizes in instanzen(40, 1, 10, seed0=1000):
        assert A.optimum(sizes, cap) == optimum_untermengen(sizes, cap), (cap, sizes)


def test_optimum_stimmt_mit_dem_ganzzahligen_programm_ueberein():
    """Das Raster stützt sich bei 20 und 30 Paketen auf das ganzzahlige Programm; hier gegen die DP an kleinen Instanzen."""
    pytest.importorskip("scipy")
    from dev.ilp import optimum_ilp

    for cap, sizes in instanzen(40, 3, 11, cap_lo=10, cap_hi=60, seed0=9000):
        f, lb = len(A.ffd(sizes, cap)), A.l2(sizes, cap)
        erwartet = A.optimum(sizes, cap)
        gefunden = f if f == lb else optimum_ilp(sizes, cap, lb, f, 60.0)
        assert gefunden == erwartet, (cap, sizes, f, lb)


def test_optimum_randfaelle():
    assert A.optimum([], 10) == 0
    assert A.optimum([10], 10) == 1
    assert A.optimum([10, 10, 10], 10) == 3
    assert A.optimum([5, 5, 5, 5], 10) == 2
    assert A.optimum([1] * 13, 12, limit=12) is None


def ffd_naiv(sizes, cap):
    """Bewusst naive Zweitumsetzung: Container als Listen von Größen, Füllung bei jeder Prüfung neu summiert; Reihenfolge nach (-Größe, Nummer)."""
    container = []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        for c in container:
            if sum(c) + sizes[i] <= cap:
                c.append(sizes[i])
                break
        else:
            container.append([sizes[i]])
    return sorted(sorted(c) for c in container)


def test_ffd_stimmt_mit_der_naiven_zweitumsetzung_ueberein():
    for cap, sizes in instanzen(150, 0, 14, seed0=2000):
        bins = A.ffd(sizes, cap)
        assert sorted(sorted(sizes[i] for i in b) for b in bins) == ffd_naiv(sizes, cap), (cap, sizes)
        assert A.container_pruefen(sizes, bins, cap)


def l2_alle_alpha(sizes, cap):
    best = -(-sum(sizes) // cap) if sizes else 0
    for alpha in range(0, cap // 2 + 1):
        j1 = sum(1 for s in sizes if s > cap - alpha)
        j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
        j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
        extra = max(0, -(-(sum(j3) - (len(j2) * cap - sum(j2))) // cap))
        best = max(best, j1 + len(j2) + extra)
    return best


def test_l2_stimmt_mit_der_rechnung_ueber_alle_alpha_ueberein():
    for cap, sizes in instanzen(200, 0, 20, seed0=3000):
        assert A.l2(sizes, cap) == l2_alle_alpha(sizes, cap), (cap, sizes)


def test_l2_detail_ist_in_sich_stimmig():
    """Der Wert des besten alpha stimmt mit der Summe aus |J1|, |J2| und den zusätzlichen Containern überein, und L2 ist das Maximum mit L1."""
    for cap, sizes in instanzen(120, 1, 16, seed0=3500):
        d = A.l2_detail(sizes, cap)
        assert d["wert"] == len(d["j1"]) + len(d["j2"]) + d["extra"]
        assert d["l2"] == max(d["l1"], d["wert"]) and d["l2_ist_l1"] == (d["wert"] <= d["l1"])
        assert d["frei"] == len(d["j2"]) * cap - sum(d["j2"]) and d["summe_j3"] == sum(d["j3"])


def eingeordnet(f, s1, s2, opt):
    """Unabhängige Neueinordnung des Ausgangs in einer anderen Reihenfolge der Prüfungen."""
    if opt is not None and opt < f:
        return "offen_nicht_optimal" if f > s2 else ("l1" if f == s1 else "l2")
    if f == s1:
        return "l1"
    if f == s2:
        return "l2"
    return "offen_optimal" if opt == f else "offen_unentschieden"


def test_schranken_ordnung_und_ausgang_mit_exaktem_optimum():
    for cap, sizes in instanzen(80, 1, 12, seed0=4000):
        f = len(A.ffd(sizes, cap))
        d = A.l2_detail(sizes, cap)
        opt = A.optimum(sizes, cap)
        assert d["l1"] <= d["l2"] <= opt <= f, (cap, sizes)
        aus = A.ausgang(f, d["l1"], d["l2"], opt)
        assert aus == eingeordnet(f, d["l1"], d["l2"], opt), (cap, sizes)
        if aus in ("l1", "l2"):
            assert f == opt               # bewiesen heißt: FFD ist wirklich optimal
        if aus == "offen_nicht_optimal":
            assert opt < f and f > d["l2"]
