# Schranken: wann ist FFD bewiesen optimal? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-schranken-beweis-demo.streamlit.app/)** -->

Zweites Stück der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Das erste Stück ([sortieren-einsetzen-demo](https://sebastianhanisch-sortieren-einsetzen-demo.streamlit.app/)) zeigt, dass die Reihenfolge der Pakete die Containerzahl stärker verändert als die Wahl zwischen First Fit und Best Fit, und misst, wie oft FFD (First Fit, größte zuerst) die Schranken trifft. Dieses Stück fragt, was ein Verfehlen der Schranken bedeutet.

## Warum dieses Problem

FFD ist bewiesen optimal, wenn seine Containerzahl gleich einer unteren Schranke ist. Liegt sie darüber, bleibt der Fall **offen**, und es gibt zwei ganz verschiedene Gründe: Entweder ist FFD in Wahrheit optimal und die Schranken sind zu schwach, oder die Schranke ist scharf und FFD braucht einen Container zu viel. Das trennt nur das exakte Optimum. Die Demo zeigt das an vier Handbeispielen mit zwölf Paketen (ein Beispiel je Ausgang) und misst es an einem Raster aus 9 Zellen zu je 100 Zufallsinstanzen.

## Modell

Ganzzahlige Paketgrößen s₁ … sₙ mit 1 ≤ sᵢ ≤ C, Container der Kapazität C, alle Pakete vorab bekannt. **FFD:** Pakete absteigend nach Größe (Gleichstand: kleinere Nummer zuerst), jedes in den ersten Container mit genug Platz. **Schranken:** Volumenschranke L₁ = ⌈Σ sᵢ / C⌉ und die Schranke L₂ nach Martello und Toth (Pakete über der halben Kapazität brauchen je einen eigenen Container, die kleineren füllen deren Restplatz). Es gilt L₁ ≤ L₂ ≤ OPT ≤ FFD. **Ausgänge je Instanz:** *bewiesen durch L1* (FFD = L₁), *bewiesen erst durch L2* (FFD = L₂ > L₁), *offen, FFD optimal* (FFD über beiden Schranken, aber gleich dem Optimum), *offen, FFD nicht optimal* (FFD über dem Optimum). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`sbw_algorithm.py`): `ffd`, `l1`, `l2_detail` (Aufteilung J1, J2, J3 für das beste α), `optimum` (Teilmengen-DP über Bitmasken, bis 12 Pakete), `ausgang`, `container_pruefen` (unabhängiger Zulässigkeitsprüfer). `ffd`, `l1`, `l2` und `optimum` sind Kopien der Funktionen aus `sortieren-einsetzen-demo` (Stück 1), hier noch einmal gegen die Orakel geprüft.
- **Handbeispiele:** vier feste Mengen zu je zwölf Paketen, Kapazität 100. Die App zeigt die FFD-Packung als gestapelte Balken, vier Kennzahlen (FFD, Optimum, L₁, L₂), die Rechnung von L₂ am besten α und ein live berechnetes Verdikt.
- **Zufällige Instanz** (live): Größenbereich, 6 bis 12 Pakete, Kapazität 100, Startzahl.
- **Raster:** drei Größenbereiche (mittlere Teile 10 bis 50 %, große 20 bis 80 %, breite 1 bis 90 % der Kapazität) × drei Paketzahlen (12, 20, 30) × **100 feste Instanzen** je Zelle, Kapazität 1000, Größen gleichverteilt und ganzzahlig. Das Optimum kommt bei 12 Paketen aus der Teilmengen-DP, bei 20 und 30 aus einem ganzzahligen Programm (`dev/ilp.py`, `scipy.optimize.milp`, Zuordnungsmodell, **10 Sekunden Zeitlimit** je Aufruf); Instanzen, die es in dieser Zeit nicht entschieden hat, stehen als „nicht entschieden“. Die Ausgangscodes je Instanz stehen in `sbw_precomputed.json` (erzeugt von `generate_precomputed.py`, mit etwa 8 Minuten Laufzeit).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_schranken_beweis.py`. Die Spalte „nicht entschieden“ zählt die Instanzen, bei denen das ganzzahlige Programm in 10 Sekunden kein Optimum geliefert hat.

| Größen der Pakete | n | durch L1 bewiesen | erst durch L2 bewiesen | offen | davon FFD optimal | davon FFD nicht optimal | nicht entschieden |
|---|---|---|---|---|---|---|---|
| mittel | 12 | 87 | 0 | 13 | 5 | 8 | 0 |
| mittel | 20 | 79 | 0 | 21 | 1 | 19 | 1 |
| mittel | 30 | 68 | 0 | 32 | 1 | 21 | 10 |
| groß | 12 | 38 | 58 | 4 | 4 | 0 | 0 |
| groß | 20 | 24 | 63 | 13 | 12 | 0 | 1 |
| groß | 30 | 17 | 65 | 18 | 7 | 1 | 10 |
| breit | 12 | 49 | 48 | 3 | 3 | 0 | 0 |
| breit | 20 | 45 | 43 | 12 | 9 | 3 | 0 |
| breit | 30 | 24 | 63 | 13 | 2 | 2 | 9 |

- **Mittlere Teile:** Die Schranke L₂ beweist in **0 von 300** Instanzen mehr als L₁. Von den entschiedenen offenen Fällen ist FFD bei n = 12 in 8 von 13 nicht optimal, bei n = 20 in 19 von 20 und bei n = 30 in 21 von 22.
- **Große Teile:** L₂ beweist zusätzlich in 58, 63 und 65 von 100 Instanzen (n = 12, 20, 30). Von den entschiedenen offenen Fällen ist FFD in 4 von 4, 12 von 12 und 7 von 8 optimal: Hier sind die Schranken zu schwach, nicht FFD.
- **Breit gestreute Teile:** L₂ beweist zusätzlich in 48, 43 und 63 von 100 Instanzen. Von den entschiedenen offenen Fällen ist FFD in 3 von 3, 9 von 12 und 2 von 4 optimal.
- **Nicht entschieden:** **31 von 600** Instanzen mit 20 oder 30 Paketen, davon 29 bei n = 30 (10 bei mittleren, 10 bei großen, 9 bei breiten Teilen) und 2 bei n = 20. Die Aussagen für n = 30 sind deshalb schwach; bei breiten Teilen mit n = 30 sind nur 4 von 13 offenen Fällen entschieden.
- **Bewiesen heißt optimal:** Bei den Zellen mit 12 Paketen ist FFD in allen als „bewiesen“ eingeordneten Instanzen gleich dem per DP berechneten Optimum (`tests/test_claims.py`).

| Handbeispiel (zwölf Pakete, Kapazität 100) | Summe | FFD | L₁ | L₂ | Optimum | Ausgang |
|---|---|---|---|---|---|---|
| 1 | 613 | 7 | 7 | 7 | 7 | bewiesen durch L1 |
| 2 | 834 | 11 | 9 | 11 | 11 | bewiesen erst durch L2 |
| 3 | 498 | 6 | 5 | 5 | 6 | offen, FFD optimal |
| 4 | 496 | 6 | 5 | 5 | 5 | offen, FFD nicht optimal |

Im dritten Beispiel genügt die Volumenschranke 5 nicht, obwohl fünf Container 500 fassen würden; das Optimum ist 6.

## Ehrliche Grenzen

- Alle Aussagen gelten für gleichverteilte Paketgrößen in drei Bereichen, drei Paketzahlen (12, 20, 30) und nur FFD. Über 30 Pakete ist nichts gemessen.
- Stärkere Schranken als L₁ und L₂ (etwa die LP-Schranke) beweisen mehr Fälle; wie viele, misst diese Demo nicht.
- Das Optimum bei 20 und 30 Paketen kommt aus einem ganzzahligen Programm mit Zeitlimit; die Zahl der nicht entschiedenen Instanzen hängt von der Rechenzeit ab. Die Datei hält den Stand des Laufs fest.
- 100 Instanzen je Zelle sind wenig, die Anteile bei 12 Paketen sind nicht stabil: Mit einem zweiten Satz von 100 Instanzen (Seeds 100 bis 199) sind bei mittleren Teilen und n = 12 von 13 offenen Fällen 6 (statt 8) nicht optimal, und bei großen Teilen sind von 12 offenen Fällen 10 optimal und 2 nicht optimal (statt 4 und 0 von 4). Bei großen Teilen und n = 12 überwiegen in beiden Sätzen die offenen Fälle mit optimalem FFD; die einzelnen Zahlen halten nicht.
- Die Gütegarantien und die Form von L₂ stammen aus Suchtreffern und Sekundärquellen beziehungsweise aus dem Gedächtnis; die Originale wurden nicht gelesen. L₂ wird gegen die Rechnung über alle α und gegen das exakte Optimum getestet.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Verglichen wird nur FFD (First Fit, größte zuerst).

**Grenzen.** Das Raster deckt drei Größenbereiche und drei Paketzahlen (12, 20 und 30) ab, jeweils mit gleichverteilten Größen und 100 Instanzen je Zelle. Praxisdaten kommen nicht vor, über 30 Pakete ist nichts gemessen, und mit stärkeren Schranken als L1 und L2 (etwa der LP-Schranke) ändert sich, welche Fälle offen bleiben. Live rechnet die Demo das Optimum bis 12 Pakete.

**Bekannte Probleme und Unsicherheiten.** Das Optimum der Rasterinstanzen mit 20 und 30 Paketen kommt aus einem ganzzahligen Programm mit 10 Sekunden Zeitlimit je Instanz; Instanzen, die es in dieser Zeit nicht entschieden hat, stehen als „nicht entschieden“ in einer eigenen Spalte und sind bei 30 Paketen zahlreich, die Aussagen dort sind schwach. 100 Instanzen je Zelle sind wenig, eine einzelne Zelle ist kein Gesetz. Die Gütegarantien in der Literatur stammen aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** FFD, L₁, L₂ und das Optimum an vier von Hand gerechneten Mini-Instanzen (Kapazität 10, eine je Ausgang; Rechnung in `tests/conftest.py`); die vier Handbeispiele; unabhängiger Zulässigkeitsprüfer; Randfälle (leere Eingabe, ein Paket, Paket gleich Kapazität, Gleichstand der α, ungültige Eingaben).
- **Orakel** (`tests/test_oracle_schranken_beweis.py`): Optimum gegen Aufzählung aller Zerlegungen (n ≤ 8, 80 Instanzen), gegen eine zweite DP über Untermengen (n ≤ 10, 40 Instanzen) und gegen das ganzzahlige Programm (n ≤ 11, 40 Instanzen, übersprungen ohne scipy); FFD gegen eine bewusst naive Zweitumsetzung (150 Instanzen); L₂ gegen die Rechnung über alle ganzzahligen α (200 Instanzen); L₂-Aufteilung in sich stimmig (120 Instanzen); L₁ ≤ L₂ ≤ OPT ≤ FFD und der Ausgang gegen eine unabhängige Neueinordnung (80 Instanzen).
- **Raster:** je Zelle die Aufteilung L1 / L2 / offen frisch gerechnet, bei 12 Paketen die vollständigen Codes mit der DP, bei 20 Paketen eine Stichprobe entschiedener offener Instanzen mit dem ganzzahligen Programm (`tests/test_claims.py`).
- **Verdikte:** alle Zweige an von Hand gesetzten Werten (`tests/test_verdicts.py`), je Preset der erwartete Ausgang und die Art.
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Regler und Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** 100, Laufzeit etwa eine halbe Minute (ohne Parallelisierung).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/ilp.py` | ganzzahliges Programm für das Optimum (nur Generator und Tests, scipy) |
| `generate_precomputed.py` | erzeugt `sbw_precomputed.json`; `--check` rechnet das Schnelle nach |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `sbw_algorithm.py` | Kern: FFD, Schranken, Aufteilung von L₂, Optimum, Ausgang |
| `sbw_constants.py` | Handbeispiele, Raster, Farben, Presets, Text der Annahmen |
| `sbw_evaluation.py` | Analyse, Verdikte, Raster-Zeilen |
| `sbw_layout.py` | Fester Kopf (Stylesheet) |
| `sbw_precomputed.json` | vorberechnete Ausgangscodes des Rasters |
| `sbw_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `sbw_scenario.py` | Instanzen: Handbeispiele, zufällige und Rasterinstanzen mit festen Seeds |
| `sbw_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanzen und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Raster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **PDF-Export:** die Demo zeigt zwölf Pakete; ein Export trüge nichts zur Frage bei.
- **LP-Schranke, Triplets, 11/9-Instanz, zwei Grenzen (Volumen und Gewicht):** spätere Stücke der Reihe.
- **Optimum über 12 Pakete live:** es gibt nur die vorberechneten Zellen mit 20 und 30 Paketen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
