"""Kennzahlen, Verdikt-Logik und das Raster (vorberechnet in sbw_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import sbw_algorithm as A
import sbw_constants as C
from sbw_scenario import Instance, beispiel, live_instanz, raster_instanz

PRECOMPUTED = Path(__file__).resolve().parent / "sbw_precomputed.json"


@dataclass(frozen=True)
class Settings:
    beispiel: int = 0
    verteilung: int = 0
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    bins: tuple           # FFD-Packung als Tupel von Paketnummern je Container
    ffd: int
    schranke_l1: int
    detail: dict          # Aufteilung J1, J2, J3 des besten alpha und L2 (sbw_algorithm.l2_detail)
    opt: object           # exaktes Optimum (int) oder None
    ausgang: str
    settings: Settings


def instanz(s: Settings) -> Instance:
    return live_instanz(s.verteilung, s.n, s.seed) if s.beispiel == C.ZUFALL else beispiel(s.beispiel)


def analyse(s: Settings) -> Analysis:
    inst = instanz(s)
    bins = A.ffd(inst.sizes, inst.cap)
    assert A.container_pruefen(inst.sizes, bins, inst.cap)
    detail = A.l2_detail(inst.sizes, inst.cap)
    opt = A.optimum(inst.sizes, inst.cap, C.OPT_LIMIT)
    return Analysis(inst, tuple(tuple(b) for b in bins), len(bins), detail["l1"], detail, opt, A.ausgang(len(bins), detail["l1"], detail["l2"], opt), s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_ausgang(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Ist FFD hier bewiesen optimal, und wenn nicht, warum nicht?"""
    f, s1, s2, opt = a.ffd, a.schranke_l1, a.detail["l2"], a.opt
    if a.ausgang == "l1":
        return "success", f"FFD braucht **{f}** Container, und die Volumenschranke L1 ist {s1}: FFD ist **bewiesen optimal**."
    if a.ausgang == "l2":
        return "success", f"FFD braucht **{f}** Container. Die Volumenschranke L1 sagt nur {s1}, die Schranke L2 aber {s2}: Damit ist FFD **bewiesen optimal**."
    schranken = f"die Schranken L1 und L2 sagen nur {s2}" if s1 == s2 else f"die Schranken sagen nur {s1} (L1) und {s2} (L2)"
    if a.ausgang == "offen_optimal":
        return "info", f"FFD braucht **{f}** Container, {schranken}: **offen**. Das exakte Optimum ist {opt}: FFD ist optimal, die Schranken sind hier zu schwach."
    if a.ausgang == "offen_nicht_optimal":
        zusatz = "Die Schranke L2 ist hier scharf." if opt == s2 else f"Das Optimum liegt zwischen der Schranke ({s2}) und FFD ({f})."
        return "warning", f"FFD braucht **{f}** Container, {schranken}: **offen**. Das exakte Optimum ist {opt}: FFD braucht {f - opt} Container zu viel. {zusatz}"
    return "info", f"FFD braucht **{f}** Container, {schranken}: **offen**. Das Optimum ist bei dieser Paketzahl nicht berechnet."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Raster


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zaehlen(codes: str) -> dict:
    """Zählt die Ausgänge einer Zelle aus der Zeichenkette der Codes (ein Zeichen je Instanz)."""
    return {name: codes.count(code) for code, name in C.AUSGANG_CODES.items()}


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    daten = daten or vorberechnet()
    codes = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    z = zaehlen(codes)
    return {"name": C.VERTEILUNGEN[verteilung][1], "n": C.MESS_N[n_index], "instanzen": len(codes), **z,
            "offen": z["offen_optimal"] + z["offen_nicht_optimal"] + z["offen_unentschieden"], "zeitlimit": daten["ilp_zeitlimit"]}


def aufteilung_frisch(verteilung: int, n_index: int, instanzen: int = C.INSTANZEN) -> dict:
    """Rechnet ohne Optimum nach, wie viele Instanzen einer Zelle durch L1, durch L2 bewiesen und wie viele offen sind (exakt und schnell; für das Raster
    genügt das, um die Aufteilung zu prüfen, ohne ein ganzzahliges Programm zu lösen)."""
    out = {"l1": 0, "l2": 0, "offen": 0}
    for j in range(instanzen):
        inst = raster_instanz(verteilung, n_index, j)
        f = len(A.ffd(inst.sizes, inst.cap))
        s1, s2 = A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
        out["l1" if f == s1 else "l2" if f == s2 else "offen"] += 1
    return out


def verdict_raster(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: wie viele Instanzen die Schranken beweisen und woran es bei den offenen liegt."""
    kopf = (f"Für »{z['name']}« mit n = {z['n']} Paketen beweist die Volumenschranke L1 bei {z['l1']} von {z['instanzen']} Instanzen, dass FFD optimal ist, "
            f"die Schranke L2 zusätzlich bei {z['l2']}.")
    if z["offen"] == 0:
        return "info", kopf + " Es bleibt kein Fall offen."
    rest = f" Offen bleiben {z['offen']}: In {z['offen_optimal']} ist FFD in Wahrheit optimal (die Schranken sind zu schwach), in {z['offen_nicht_optimal']} nicht optimal"
    if z["offen_unentschieden"]:
        rest += f", in {z['offen_unentschieden']} nicht entschieden (ILP nach {z['zeitlimit']:.0f} s abgebrochen)."
        return "warning", kopf + rest + " Die Aussage ist wegen der nicht entschiedenen Fälle schwach."
    rest += "."
    if z["offen_optimal"] > z["offen_nicht_optimal"]:
        return "info", kopf + rest + " In der Mehrheit der offenen Fälle liegt es hier an den Schranken."
    if z["offen_nicht_optimal"] > z["offen_optimal"]:
        return "info", kopf + rest + " In der Mehrheit der offenen Fälle verliert FFD hier wirklich einen Container."
    return "info", kopf + rest


def l2_erklaerung(detail: dict, cap: int) -> str:
    """Text zur Rechnung der Schranke L2 am besten alpha: Aufteilung J1, J2, J3, freier Platz, zusätzliche Container (reine Funktion, getestet)."""
    def liste(xs):
        return ", ".join(str(x) for x in xs) if xs else "–"

    zeilen = [
        f"Bestes α = **{detail['alpha']}**:",
        f"- **J1** (größer als C − α = {cap - detail['alpha']}; je ein eigener Container): {liste(detail['j1'])} → {len(detail['j1'])} Container",
        f"- **J2** (zwischen C/2 und C − α; je ein eigener Container): {liste(detail['j2'])} → {len(detail['j2'])} Container, zusammen **{detail['frei']}** freier Platz",
        f"- **J3** (höchstens C/2 und mindestens α): {liste(detail['j3'])} mit Summe **{detail['summe_j3']}**",
        f"- Was in den freien Platz der J2-Container nicht passt, braucht zusätzliche Container: ⌈({detail['summe_j3']} − {detail['frei']}) / {cap}⌉, mindestens 0, also **{detail['extra']}**",
        f"- L(α) = {len(detail['j1'])} + {len(detail['j2'])} + {detail['extra']} = **{detail['wert']}**",
    ]
    if detail["l2_ist_l1"]:
        zeilen.append(f"Dieser Wert liegt nicht über der Volumenschranke L1 = {detail['l1']}; L2 ist deshalb gleich L1.")
    else:
        zeilen.append(f"Das ist mehr als die Volumenschranke L1 = {detail['l1']}; L2 = **{detail['l2']}**.")
    return "\n".join(zeilen)
