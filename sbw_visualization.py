"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import sbw_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_container(sizes, bins, cap):
    """Ein Balken je Container (FFD-Packung), darin die Pakete als gestapelte Segmente (Beschriftung = Größe), oben der freie Platz in Grau.

    Die rote Linie ist die Kapazität. Beschriftungen als Text (C1, C2 ...), damit Plotly keine lineare Achse anlegt."""
    labels = [f"C{b + 1}" for b in range(len(bins))]
    schichten = max((len(b) for b in bins), default=0)
    fig = go.Figure()
    for k in range(schichten):
        werte = [sizes[b[k]] if k < len(b) else 0 for b in bins]
        texte = [str(sizes[b[k]]) if k < len(b) else "" for b in bins]
        fig.add_trace(go.Bar(x=labels, y=werte, text=texte, textposition="inside", insidetextanchor="middle", marker=dict(color=C.COLOR_FILL, line=dict(color="white", width=1.5)),
                             showlegend=False, hovertemplate="%{x}: Paket %{text}<extra></extra>"))
    frei = [cap - sum(sizes[i] for i in b) for b in bins]
    fig.add_trace(go.Bar(x=labels, y=frei, text=[f"frei {f}" if f > 0 else "" for f in frei], textposition="inside", insidetextanchor="middle",
                         marker=dict(color=C.COLOR_FREE), showlegend=False, hovertemplate="%{x}: %{y} frei<extra></extra>"))
    fig.add_hline(y=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Füllung (Kapazität %d)" % cap, range=[0, cap * 1.05])
    return _base(fig)


def build_raster(zeilen):
    """Gestapelte Balken je Paketzahl: Anteil der Instanzen je Ausgang (in %). `zeilen` = Liste der Zeilen (sbw_evaluation.zeile) einer Größenverteilung."""
    namen = [str(z["n"]) + " Pakete" for z in zeilen]
    teile = (("l1", C.COLOR_L1), ("l2", C.COLOR_L2), ("offen_optimal", C.COLOR_OPEN_OPT), ("offen_nicht_optimal", C.COLOR_OPEN_BAD), ("offen_unentschieden", C.COLOR_UNKNOWN))
    fig = go.Figure()
    for schluessel, farbe in teile:
        fig.add_trace(go.Bar(name=C.AUSGANG_TEXTE[schluessel], x=namen, y=[100.0 * z[schluessel] / z["instanzen"] for z in zeilen], marker_color=farbe,
                             text=[str(z[schluessel]) if z[schluessel] else "" for z in zeilen], textposition="inside",
                             hovertemplate="%{x}: %{y:.0f} % (%{text} Instanzen)<extra>" + C.AUSGANG_TEXTE[schluessel] + "</extra>"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Anteil der Instanzen (%)", range=[0, 100])
    return _base(fig, 360)
