"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Die Analysen und Zeilen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import sbw_evaluation as ev
from sbw_scenario import Instance


def _analyse(ausgang, ffd, l1, l2, opt):
    detail = {"alpha": 0, "j1": [], "j2": [], "j3": [], "frei": 0, "summe_j3": 0, "extra": 0, "wert": l2, "l1": l1, "l2": l2, "l2_ist_l1": l2 <= l1}
    return ev.Analysis(Instance((10, 20), 100), ((0, 1),), ffd, l1, detail, opt, ausgang, ev.Settings())


# --- verdict_ausgang ------------------------------------------------------------------------------------------------------------------------


def test_ausgang_l1_ist_ein_erfolg_und_nennt_ffd_und_l1():
    kind, text = ev.verdict_ausgang(_analyse("l1", 7, 7, 7, 7))
    assert kind == "success" and "FFD braucht **7** Container" in text and "L1 ist 7" in text and "**bewiesen optimal**" in text


def test_ausgang_l2_nennt_beide_schranken():
    kind, text = ev.verdict_ausgang(_analyse("l2", 11, 9, 11, 11))
    assert kind == "success" and "**11** Container" in text and "L1 sagt nur 9" in text and "L2 aber 11" in text and "**bewiesen optimal**" in text


def test_ausgang_offen_optimal_ist_info_und_sagt_schranken_zu_schwach():
    kind, text = ev.verdict_ausgang(_analyse("offen_optimal", 6, 4, 5, 6))
    assert kind == "info"
    assert "**6** Container" in text and "sagen nur 4 (L1) und 5 (L2)" in text and "**offen**" in text
    assert "Optimum ist 6" in text and "FFD ist optimal" in text and "zu schwach" in text


def test_ausgang_offen_gleiche_schranken_werden_zusammen_genannt():
    kind, text = ev.verdict_ausgang(_analyse("offen_optimal", 6, 5, 5, 6))
    assert "die Schranken L1 und L2 sagen nur 5" in text and "(L1)" not in text


def test_ausgang_offen_nicht_optimal_ist_eine_warnung_mit_der_differenz_und_scharfer_schranke():
    kind, text = ev.verdict_ausgang(_analyse("offen_nicht_optimal", 6, 5, 5, 5))
    assert kind == "warning" and "Optimum ist 5" in text and "1 Container zu viel" in text and "Die Schranke L2 ist hier scharf." in text


def test_ausgang_offen_nicht_optimal_mit_optimum_zwischen_schranke_und_ffd():
    kind, text = ev.verdict_ausgang(_analyse("offen_nicht_optimal", 8, 5, 5, 7))
    assert kind == "warning" and "1 Container zu viel" in text and "liegt zwischen der Schranke (5) und FFD (8)" in text and "scharf" not in text


def test_ausgang_unentschieden_nennt_die_fehlende_rechnung():
    kind, text = ev.verdict_ausgang(_analyse("offen_unentschieden", 9, 7, 8, None))
    assert kind == "info" and "nicht berechnet" in text and "sagen nur 7 (L1) und 8 (L2)" in text


# --- l2_erklaerung -------------------------------------------------------------------------------------------------------------------------


def test_l2_erklaerung_nennt_alle_teile_der_rechnung():
    detail = {"alpha": 33, "j1": [90, 88], "j2": [67, 67], "j3": [34, 33], "frei": 66, "summe_j3": 67, "extra": 1, "wert": 5, "l1": 3, "l2": 5, "l2_ist_l1": False}
    text = ev.l2_erklaerung(detail, 100)
    assert "Bestes α = **33**" in text and "größer als C − α = 67" in text
    assert "90, 88 → 2 Container" in text and "67, 67 → 2 Container, zusammen **66** freier Platz" in text and "34, 33 mit Summe **67**" in text
    assert "⌈(67 − 66) / 100⌉" in text and "also **1**" in text and "L(α) = 2 + 2 + 1 = **5**" in text
    assert "mehr als die Volumenschranke L1 = 3; L2 = **5**" in text


def test_l2_erklaerung_ohne_gewinn_gegenueber_l1_und_leere_mengen():
    detail = {"alpha": 0, "j1": [], "j2": [], "j3": [4, 3], "frei": 0, "summe_j3": 7, "extra": 1, "wert": 1, "l1": 1, "l2": 1, "l2_ist_l1": True}
    text = ev.l2_erklaerung(detail, 10)
    assert "größer als C − α = 10" in text and "**J1** (größer als C − α = 10; je ein eigener Container): – → 0 Container" in text
    assert "nicht über der Volumenschranke L1 = 1; L2 ist deshalb gleich L1" in text


# --- verdict_raster ------------------------------------------------------------------------------------------------------------------------


def _zeile(l1=50, l2=20, oo=10, on=15, ou=5):
    offen = oo + on + ou
    return {"name": "große Teile (20 bis 80 %)", "n": 20, "instanzen": l1 + l2 + offen, "l1": l1, "l2": l2, "offen_optimal": oo, "offen_nicht_optimal": on,
            "offen_unentschieden": ou, "offen": offen, "zeitlimit": 10.0}


def test_raster_mit_unentschiedenen_ist_eine_warnung_und_nennt_das_zeitlimit():
    kind, text = ev.verdict_raster(_zeile())
    assert kind == "warning"
    assert "»große Teile (20 bis 80 %)« mit n = 20" in text and "L1 bei 50 von 100 Instanzen" in text and "L2 zusätzlich bei 20" in text
    assert "Offen bleiben 30" in text and "In 10 ist FFD in Wahrheit optimal" in text and "in 15 nicht optimal" in text
    assert "in 5 nicht entschieden (ILP nach 10 s abgebrochen)" in text and "wegen der nicht entschiedenen Fälle schwach" in text


def test_raster_ohne_unentschiedene_nennt_die_mehrheit():
    kind, text = ev.verdict_raster(_zeile(l1=60, l2=20, oo=15, on=5, ou=0))
    assert kind == "info" and "In der Mehrheit der offenen Fälle liegt es hier an den Schranken." in text and "nicht entschieden" not in text
    kind, text = ev.verdict_raster(_zeile(l1=60, l2=20, oo=5, on=15, ou=0))
    assert kind == "info" and "In der Mehrheit der offenen Fälle verliert FFD hier wirklich einen Container." in text


def test_raster_gleichstand_und_kein_offener_fall():
    kind, text = ev.verdict_raster(_zeile(l1=60, l2=20, oo=10, on=10, ou=0))
    assert kind == "info" and "Mehrheit" not in text and "Offen bleiben 20" in text
    kind, text = ev.verdict_raster(_zeile(l1=60, l2=40, oo=0, on=0, ou=0))
    assert kind == "info" and "Es bleibt kein Fall offen." in text and "Offen bleiben" not in text
