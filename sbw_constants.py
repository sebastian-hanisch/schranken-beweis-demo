"""Konstanten: Regler-Grenzen, Handbeispiele, Raster, Farben und Presets."""

CAP = 100                 # Kapazität in den Handbeispielen und in den zufälligen Live-Instanzen
OPT_LIMIT = 12            # so viele Pakete darf das exakte Optimum live (Teilmengen-DP) höchstens aufzählen
N_MIN, N_MAX, DEFAULT_N = 6, 12, 12
SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Handbeispiele (Pakete in beliebiger Reihenfolge; FFD sortiert selbst) -----------------------------------------------------------------
# Jede Zeile mit der Teilmengen-DP geprüft (Phase 0, handbeispiel2.py): Ausgang, FFD, L1, L2, Optimum.
BEISPIELE = {
    0: (88, 86, 78, 67, 67, 60, 48, 33, 28, 22, 21, 15),    # Summe 613: FFD 7, L1 7, L2 7, Optimum 7   -> bewiesen durch L1
    1: (90, 88, 85, 81, 75, 75, 70, 69, 67, 67, 34, 33),    # Summe 834: FFD 11, L1 9, L2 11, Optimum 11 -> bewiesen erst durch L2
    2: (89, 86, 77, 69, 40, 34, 30, 18, 17, 14, 13, 11),    # Summe 498: FFD 6, L1 5, L2 5, Optimum 6    -> offen, FFD optimal
    3: (73, 70, 67, 54, 45, 45, 31, 27, 27, 24, 18, 15),    # Summe 496: FFD 6, L1 5, L2 5, Optimum 5    -> offen, FFD nicht optimal
}
BEISPIEL_NAMEN = {
    0: "Beispiel 1 (bewiesen durch L1)",
    1: "Beispiel 2 (bewiesen erst durch L2)",
    2: "Beispiel 3 (offen, FFD optimal)",
    3: "Beispiel 4 (offen, FFD nicht optimal)",
    4: "Zufällige Instanz",
}
ZUFALL = 4                # Wert der Beispielauswahl für die zufällige Instanz

# Größenbereiche (Anteil an der Kapazität): für die zufällige Live-Instanz und das Raster
VERTEILUNGEN = (
    ("mittel", "mittlere Teile (10 bis 50 % der Kapazität)", 0.10, 0.50),
    ("gross", "große Teile (20 bis 80 %)", 0.20, 0.80),
    ("breit", "breit gestreute Teile (1 bis 90 %)", 0.01, 0.90),
)

# --- Raster (vorberechnet, sbw_precomputed.json) -------------------------------------------------------------------------------------------
MESS_CAP = 1000           # Kapazität in den Rasterinstanzen
MESS_N = (12, 20, 30)
INSTANZEN = 100           # Instanzen je Zelle; die Zahl steht neben jeder Aussage
ILP_ZEITLIMIT = 10.0      # Sekunden je ILP-Aufruf im Generator; darüber gilt die Instanz als „nicht entschieden“

# Ausgänge je Instanz (Code im vorberechneten Raster -> Name)
AUSGANG_CODES = {"1": "l1", "2": "l2", "o": "offen_optimal", "n": "offen_nicht_optimal", "u": "offen_unentschieden"}
AUSGANG_TEXTE = {
    "l1": "bewiesen durch L1",
    "l2": "bewiesen erst durch L2",
    "offen_optimal": "offen, FFD optimal",
    "offen_nicht_optimal": "offen, FFD nicht optimal",
    "offen_unentschieden": "offen, nicht entschieden",
}

COLOR_FILL = "#2F6B65"
COLOR_FREE = "rgba(150,150,150,0.35)"
COLOR_LINE = "#c0392b"
COLOR_L1 = "#2F6B65"
COLOR_L2 = "#4c78a8"
COLOR_OPEN_OPT = "#e0a030"
COLOR_OPEN_BAD = "#c0392b"
COLOR_UNKNOWN = "#9e9e9e"

PRESETS = {
    "Bewiesen durch L1": {"beispiel": 0, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Bewiesen erst durch L2": {"beispiel": 1, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Offen, FFD optimal": {"beispiel": 2, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Offen, FFD nicht optimal": {"beispiel": 3, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Zufällige Instanz (mittlere Teile)": {"beispiel": ZUFALL, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Bewiesen durch L1": "Zwölf Pakete, bei denen FFD genau so viele Container braucht wie die Volumenschranke L1: Damit ist FFD bewiesen optimal.",
    "Bewiesen erst durch L2": "Zwölf große Pakete: Die Volumenschranke L1 sagt nur 9 Container, die Schranke L2 aber 11. Erst L2 beweist, dass FFD optimal ist.",
    "Offen, FFD optimal": "FFD braucht mehr Container als beide Schranken. Das exakte Optimum zeigt: FFD ist trotzdem optimal, die Schranken sind zu schwach.",
    "Offen, FFD nicht optimal": "FFD braucht mehr Container als beide Schranken. Das exakte Optimum zeigt: Ein Container weniger geht, FFD ist nicht optimal.",
    "Zufällige Instanz (mittlere Teile)": "Eine zufällige Instanz mit mittleren Paketgrößen; Größenbereich, Paketzahl und Startzahl in der Seitenleiste.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Verglichen wird nur FFD (First Fit, größte zuerst).

**Grenzen.** Das Raster deckt drei Größenbereiche und drei Paketzahlen (12, 20 und 30) ab, jeweils mit gleichverteilten Größen und {INSTANZEN} Instanzen je Zelle. Praxisdaten kommen nicht vor, über 30 Pakete ist nichts gemessen, und mit stärkeren Schranken als L1 und L2 (etwa der LP-Schranke) ändert sich, welche Fälle offen bleiben. Live rechnet die Demo das Optimum bis {OPT_LIMIT} Pakete.

**Bekannte Probleme und Unsicherheiten.** Das Optimum der Rasterinstanzen mit 20 und 30 Paketen kommt aus einem ganzzahligen Programm mit {ILP_ZEITLIMIT:.0f} Sekunden Zeitlimit je Instanz; Instanzen, die es in dieser Zeit nicht entschieden hat, stehen als „nicht entschieden“ in einer eigenen Spalte und sind bei 30 Paketen zahlreich, die Aussagen dort sind schwach. {INSTANZEN} Instanzen je Zelle sind wenig, eine einzelne Zelle ist kein Gesetz. Die Gütegarantien in der Literatur stammen aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
