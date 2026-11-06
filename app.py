"""Schranken: wann ist FFD bewiesen optimal? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 2 der Reihe „Packen: Reihenfolge und Platzierungsregel“. FFD gegen die Schranken L1 und L2 und gegen das exakte Optimum: Wann ist FFD bewiesen optimal,
und was heißt es, wenn der Beweis offen bleibt? Das Raster (vorberechnet in sbw_precomputed.json) zeigt dieselbe Frage an je 100 Zufallsinstanzen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sbw_constants as C
from sbw_evaluation import Settings, analyse, l2_erklaerung, verdict_ausgang, verdict_raster, zeile
from sbw_layout import dunkles_design, kopf_css
from sbw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sbw_visualization import build_container, build_raster

st.set_page_config(page_title="Schranken – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sbw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📏 Schranken: wann ist FFD bewiesen optimal?")
st.markdown(
    """
**FFD** (First Fit Decreasing: die größten Pakete zuerst, jedes in den ersten Container, in den es passt) ist schnell, aber ist es auch **optimal**? Beweisen lässt sich das mit **unteren Schranken**: Braucht FFD genau so viele Container, wie eine Schranke verlangt, kann es keiner besser. Liegt FFD darüber, ist der Fall **offen**, und erst das exakte Optimum zeigt, woran es liegt: an zu schwachen Schranken oder daran, dass FFD wirklich einen Container zu viel braucht.

Weiter unten: der Abschnitt **🔬 Experiment**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Beweis über Schranken", expanded=True):
    st.markdown(
        """
1. **FFD packt:** Pakete der Größe nach absteigend, jedes in den ersten Container mit genug Platz. Das ergibt eine Containerzahl.
2. **Schranken:** Die Volumenschranke **L1** teilt die Summe aller Größen durch die Kapazität und rundet auf. Die Schranke **L2** ist stärker bei großen Paketen: Jedes Paket über der halben Kapazität braucht einen eigenen Container, und die kleineren füllen nur deren Restplatz.
3. **Vergleich:** Ist FFD gleich L1 oder gleich L2, ist FFD **bewiesen optimal**. Liegt FFD darüber, ist der Fall **offen**.
4. **Exaktes Optimum:** Es entscheidet bei offenen Fällen, ob die Schranken zu schwach waren oder FFD wirklich verliert. Diese Demo rechnet es live bis 12 Pakete.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    beispiel = st.selectbox("Pakete", list(C.BEISPIEL_NAMEN), format_func=C.BEISPIEL_NAMEN.get, key="beispiel_select",
                            help="Vier feste Beispiele mit zwölf Paketen (Kapazität 100) oder eine zufällige Instanz.")
    st.markdown("**Zufällige Instanz**")
    verteilung = st.selectbox("Größen der Pakete", list(range(len(C.VERTEILUNGEN))), format_func=lambda i: C.VERTEILUNGEN[i][1], key="verteilung_select",
                              help="Wirkt nur bei der zufälligen Instanz.")
    n = st.slider("Zahl der Pakete n", *bounds("n_slider"), key="n_slider", help="Wirkt nur bei der zufälligen Instanz.")
    seed = st.number_input("Startzahl der zufälligen Instanz", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei der zufälligen Instanz.")
    st.button("🎲 Neue zufällige Instanz würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"beispiel_select": int(beispiel), "verteilung_select": int(verteilung), "n_slider": int(n), "seed_input": int(seed)})

settings = Settings(int(beispiel), int(verteilung), int(n), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("FFD braucht", a.ffd, delta=a.ffd - a.opt, delta_color="inverse", help="Delta: FFD minus exaktes Optimum.")
m2.metric("Optimum (exakt)", a.opt, delta="Referenz", delta_color="off")
m3.metric("Volumenschranke L1", a.schranke_l1, delta="Summe durch Kapazität, aufgerundet", delta_color="off")
m4.metric("Schranke L2", a.detail["l2"], delta="stärker bei großen Paketen", delta_color="off")
st.caption("Pakete nach Größe geordnet: " + ", ".join(str(s) for s in sorted(a.inst.sizes, reverse=True)) + f"  (Summe {sum(a.inst.sizes)}, Kapazität {a.inst.cap}).")
st.plotly_chart(build_container(a.inst.sizes, a.bins, a.inst.cap), width="stretch", key="main_chart")
st.caption("Die FFD-Packung. Grün: Pakete (Beschriftung = Größe), grau: freier Platz, rot gestrichelt: Kapazität eines Containers.")

with st.expander("Wie die Schranke L2 hier rechnet"):
    st.markdown(l2_erklaerung(a.detail, a.inst.cap))

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Ist FFD hier bewiesen optimal, und wenn nicht, woran liegt es?")
kind, text = verdict_ausgang(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Woran liegt es, wenn der Beweis offen bleibt?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Kapazität {C.MESS_CAP}, Paketgrößen gleichverteilt im gewählten Bereich. Das Optimum kommt bei "
    f"12 Paketen aus der Teilmengen-DP, bei 20 und 30 aus einem ganzzahligen Programm mit {C.ILP_ZEITLIMIT:.0f} Sekunden Zeitlimit je Instanz. Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
exp_v = e1.selectbox("Größen der Pakete", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
exp_n = e2.selectbox("Zahl der Pakete n (für das Verdikt)", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
zeilen = [zeile(int(exp_v), ni) for ni in range(len(C.MESS_N))]
st.plotly_chart(build_raster(zeilen), width="stretch", key="exp_chart")
tabelle = ["| n | L1 | L2 | optimal | nicht opt. | offen |", "|---|---|---|---|---|---|"]
for z in zeilen:
    tabelle.append(f"| {z['n']} | {z['l1']} | {z['l2']} | {z['offen_optimal']} | {z['offen_nicht_optimal']} | {z['offen_unentschieden']} |")
st.markdown("\n".join(tabelle))
st.caption(
    f"Anzahl der Instanzen von je {zeilen[0]['instanzen']}. **L1:** durch die Volumenschranke bewiesen. **L2:** erst durch L2 bewiesen. Offene Fälle (FFD über beiden Schranken): "
    "**optimal:** FFD ist in Wahrheit optimal, **nicht opt.:** FFD ist nicht optimal, **offen:** vom ganzzahligen Programm nicht entschieden."
)
kind, text = verdict_raster(zeilen[int(exp_n)])
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Verglichen wird nur FFD** | Für andere Verfahren (etwa First Fit ohne Sortieren) gelten diese Zahlen nicht; die Demo hat sie dafür nicht gemessen. | Stück 1 dieser Reihe |
| **Die Schranken sind L1 und L2** | Stärkere Schranken (etwa die LP-Schranke) beweisen mehr Fälle; wie viele, misst diese Demo nicht. | spätere Stücke dieser Reihe |
| **Das Optimum ist bekannt** | Live rechnet die Demo es bis 12 Pakete. Bei 20 und 30 Paketen bleiben Instanzen nicht entschieden, bei 30 sind es viele; die Aussagen dort sind schwach. | - |
| **Die Pakete sind zufällig und gleichverteilt** | Gezielt gebaute Instanzen (etwa solche, in denen genau drei Pakete in einen Container passen) verhalten sich anders; die Demo zeigt sie nicht. | spätere Stücke dieser Reihe |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Pakete mit ganzzahligen Größen und Container einer festen Kapazität. *Gesucht:* die kleinste Zahl von Containern, in die alle Pakete passen, und ein Beweis, dass FFD sie erreicht.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Pakete |
| $s_i$ | Größe von Paket $i$, $1 \le s_i \le C$ |
| $C$ | Kapazität eines Containers |
| $\mathrm{FFD}$ | Containerzahl von First Fit Decreasing |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Containern |
| $L_1$, $L_2$ | untere Schranken für $\mathrm{OPT}$ |
| $\alpha$ | Schwelle in der Rechnung von $L_2$ |

**Entscheidungsregel.** Es gilt $L_1 \le L_2 \le \mathrm{OPT} \le \mathrm{FFD}$. Ist $\mathrm{FFD} = L_1$ oder $\mathrm{FFD} = L_2$, folgt $\mathrm{FFD} = \mathrm{OPT}$: bewiesen. Ist $\mathrm{FFD} > L_2$, sagen die Schranken nichts; dann gilt entweder $\mathrm{OPT} = \mathrm{FFD}$ (die Schranken sind zu schwach) oder $\mathrm{OPT} < \mathrm{FFD}$ (FFD verliert).

**Volumenschranke.** $L_1 = \left\lceil \tfrac{1}{C} \sum_i s_i \right\rceil$.

**Schranke $L_2$.** Für $\alpha \ge 0$ sei $J_1 = \{ s_i > C - \alpha \}$, $J_2 = \{ C - \alpha \ge s_i > C/2 \}$, $J_3 = \{ C/2 \ge s_i \ge \alpha \}$. Pakete aus $J_1 \cup J_2$ brauchen je einen eigenen Container, und die Pakete aus $J_3$ füllen zuerst den freien Platz der $J_2$-Container:
$$L(\alpha) = |J_1| + |J_2| + \max\!\left(0, \left\lceil \frac{\sum_{J_3} s_i - (|J_2|\,C - \sum_{J_2} s_i)}{C} \right\rceil\right), \qquad L_2 = \max\bigl(L_1, \max_\alpha L(\alpha)\bigr).$$
Es genügt $\alpha \in \{0\} \cup \{ s_i : s_i \le C/2 \}$.

**Exaktes Optimum.** Bis 12 Pakete per Teilmengen-DP: Für eine Menge $M$ sei $f(M) = (b, \ell)$ das lexikographisch kleinste Paar aus Containerzahl und Füllung des letzten Containers; $\mathrm{OPT} = b$ von $f(\{1,\dots,n\})$. Bei 20 und 30 Paketen ein ganzzahliges Programm: Variablen $x_{ij} \in \{0,1\}$ (Paket $i$ in Container $j$), Nebenbedingungen $\sum_j x_{ij} = 1$ und $\sum_i s_i x_{ij} \le C$; $\mathrm{OPT}$ ist das kleinste $m$ mit zulässiger Lösung für $j = 1,\dots,m$, gesucht von $m = \mathrm{FFD} - 1$ abwärts bis $L_2$.

**Literatur (aus Suchtreffern, Originale nicht gelesen).** Die Schranke $L_2$ geht auf Martello und Toth zurück (Knapsack Problems, Wiley 1990, Kapitel 8). Die hier benutzte Form ist aus dem Gedächtnis aufgeschrieben und wird gegen die Rechnung über alle ganzzahligen $\alpha$ und gegen das exakte Optimum getestet ($L_2 \le \mathrm{OPT}$).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
