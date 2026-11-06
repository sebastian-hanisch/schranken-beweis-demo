"""Kern: FFD, die Schranken L1 und L2 (mit Aufteilung), exaktes Optimum und die Einordnung des Ausgangs.

`ffd`, `l1`, `l2` und `optimum` sind Kopien der Funktionen gleichen Namens aus sortieren-einsetzen-demo/sei_algorithm.py (Stück 1 dieser Reihe, dort gegen
Aufzählung, zweite DP und die Rechnung über alle α geprüft); die Orakel-Tests dieses Repos prüfen sie noch einmal. Container sind Listen von Paketnummern."""


def ffd(sizes, cap: int) -> list[list[int]]:
    """First Fit Decreasing: größte zuerst (Gleichstand: kleinere Nummer zuerst), jedes Paket in den ersten Container mit genug Platz."""
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    bins: list[list[int]] = []
    loads: list[int] = []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        s = sizes[i]
        for b, load in enumerate(loads):
            if load + s <= cap:
                bins[b].append(i)
                loads[b] += s
                break
        else:
            bins.append([i])
            loads.append(s)
    return bins


def container_pruefen(sizes, bins, cap: int) -> bool:
    """Unabhängiger Zulässigkeitsprüfer: jedes Paket genau einmal, keine Überfüllung, keine leeren Container."""
    gesehen = sorted(i for b in bins for i in b)
    return gesehen == list(range(len(sizes))) and all(b and sum(sizes[i] for i in b) <= cap for b in bins)


def l1(sizes, cap: int) -> int:
    """Volumenschranke: Summe der Größen durch die Kapazität, aufgerundet."""
    return -(-sum(sizes) // cap) if sizes else 0


def _l2_alpha(sizes, cap: int, alpha: int) -> dict:
    j1 = [s for s in sizes if s > cap - alpha]
    j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
    j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
    frei = len(j2) * cap - sum(j2)
    extra = max(0, -(-(sum(j3) - frei) // cap)) if j3 else 0
    return {"alpha": alpha, "j1": sorted(j1, reverse=True), "j2": sorted(j2, reverse=True), "j3": sorted(j3, reverse=True),
            "frei": frei, "summe_j3": sum(j3), "extra": extra, "wert": len(j1) + len(j2) + extra}


def l2_detail(sizes, cap: int) -> dict:
    """Aufteilung J1, J2, J3 für das alpha mit dem größten Wert L(alpha) (bei Gleichstand das kleinste alpha) und die Schranke L2 selbst.

    Für jedes alpha (null und jede Paketgröße bis zur halben Kapazität): J1 = {s > cap - alpha}, J2 = {cap - alpha >= s > cap/2}, J3 = {cap/2 >= s >= alpha};
    L(alpha) = |J1| + |J2| + max(0, ceil((Summe J3 - (|J2| cap - Summe J2)) / cap)); L2 = max(L1, größtes L(alpha)). Liegt L1 über allen L(alpha), steht
    `wert_alpha` unter `l2`, und `l2_ist_l1` ist wahr."""
    kandidaten = [_l2_alpha(sizes, cap, a) for a in sorted({0} | {s for s in sizes if 2 * s <= cap})]
    best = max(kandidaten, key=lambda d: (d["wert"], -d["alpha"]))
    volumen = l1(sizes, cap)
    return {**best, "l1": volumen, "l2": max(volumen, best["wert"]), "l2_ist_l1": best["wert"] <= volumen}


def l2(sizes, cap: int) -> int:
    return l2_detail(sizes, cap)["l2"]


def optimum(sizes, cap: int, limit: int = 12):
    """Kleinste mögliche Containerzahl per Teilmengen-DP, oder None, wenn mehr als `limit` Pakete vorliegen.

    dp[Menge] = (Container, Füllung des letzten) lexikographisch minimal; ein Paket kommt entweder in den letzten Container oder in einen neuen."""
    n = len(sizes)
    if n > limit:
        return None
    if n == 0:
        return 0
    full = (1 << n) - 1
    inf = (n + 1, cap + 1)
    dp = [inf] * (full + 1)
    dp[0] = (1, 0)
    for mask in range(full + 1):
        b, last = dp[mask]
        if b > n:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            s = sizes[i]
            nxt = (b, last + s) if last + s <= cap else (b + 1, s)
            m2 = mask | (1 << i)
            if nxt < dp[m2]:
                dp[m2] = nxt
    return dp[full][0]


def ausgang(ffd_zahl: int, schranke_l1: int, schranke_l2: int, opt):
    """Einordnung einer Instanz: 'l1' (FFD gleich L1, bewiesen), 'l2' (FFD gleich L2, erst dadurch bewiesen), 'offen_optimal' (FFD über beiden Schranken,
    aber gleich dem Optimum), 'offen_nicht_optimal' (FFD über dem Optimum) oder 'offen_unentschieden' (Optimum unbekannt)."""
    if ffd_zahl == schranke_l1:
        return "l1"
    if ffd_zahl == schranke_l2:
        return "l2"
    if opt is None:
        return "offen_unentschieden"
    return "offen_optimal" if opt == ffd_zahl else "offen_nicht_optimal"
