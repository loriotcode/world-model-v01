"""
utils/charts.py — Landscape smartphone
"""

import math
import plotly.graph_objects as go
import pandas as pd
import html as _html

from models.world3 import SCENARIOS

# --- THEME ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND  = "#ffffff"
GRID_COLOR       = "#e8e0d5"
TEXT_COLOR       = "#2d3748"
AXIS_COLOR       = "#4a5568"

# Couleurs de statut (source unique)
STATUS_COLORS = {
    "safe":     "#4a7c59",
    "exceeded": "#d68910",
    "critical": "#a8323e",
}

# --- META variables ---
VARIABLE_META = {
    "population":      {"label": "Population",        "yaxis": "Milliards hab."},
    "resources":       {"label": "Ressources",         "yaxis": "Fraction (0-1)"},
    "pollution":       {"label": "Pollution",          "yaxis": "Index"},
    "capital":         {"label": "Capital industriel", "yaxis": "Index"},
    "life_expectancy": {"label": "Espérance de vie",   "yaxis": "Années"},
    "food_per_capita": {"label": "Nourriture/hab.",    "yaxis": "Index"},
    "hdi":             {"label": "HDI",                "yaxis": "Score (0-1)"},
}

# Config axes : zoom désactivé
_AXIS_BASE = dict(
    fixedrange=True,
    showgrid=True,
    gridcolor=GRID_COLOR,
    gridwidth=1,
    title_font=dict(size=8, color=AXIS_COLOR),
    tickfont=dict(size=7, color=AXIS_COLOR),
    linecolor=GRID_COLOR,
)


# =========================================================
# TRAJECTOIRES
# =========================================================
def chart_trajectories(results, variable):
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""})
    fig  = go.Figure()

    for key in results:
        df = results[key]
        sc = SCENARIOS[key]

        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[variable],
            name=_html.escape(sc["label"]),
            line=dict(color=sc["color"], width=2),
            hovertemplate=(
                "<b>" + _html.escape(sc["label"]) + "</b><br>"
                "Année : %{x}<br>"
                + _html.escape(meta["yaxis"]) + " : %{y:.2f}<extra></extra>"
            ),
        ))

    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR, line_width=1)

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        legend=dict(orientation="h", y=-0.25, font=dict(size=8)),
        xaxis=dict(title=dict(text="Année"), **_AXIS_BASE),
        yaxis=dict(title=dict(text=meta["yaxis"]), **_AXIS_BASE),
        dragmode=False,
    )

    return fig


# =========================================================
# BARRES LIMITES PLANÉTAIRES — ratio current/safe_limit
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries):
    """
    Affiche chaque limite comme % de sa valeur sûre (100% = seuil).
    Les limites sans données numériques (novel_entities) sont affichées
    à 160% avec un marqueur spécial.
    """
    names   = []
    ratios  = []
    colors  = []
    hovers  = []
    has_data = []

    for b in boundaries:
        cur  = b.get("current")
        lim  = b.get("safe_limit")
        stat = b["status"]

        if cur is not None and lim is not None and lim > 0:
            ratio = (cur / lim) * 100
            hover = (
                f"<b>{_html.escape(b['name'])}</b><br>"
                f"Actuel : {cur}<br>"
                f"Limite sûre : {lim}<br>"
                f"Ratio : {ratio:.0f}%"
            )
            has_data.append(True)
        else:
            ratio = 160          # valeur symbolique pour "indéterminé"
            hover = (
                f"<b>{_html.escape(b['name'])}</b><br>"
                "Pas de mesure quantitative<br>"
                "Limite franchie (évaluation qualitative)"
            )
            has_data.append(False)

        names.append(b["name"])
        ratios.append(ratio)
        colors.append(STATUS_COLORS.get(stat, "#888888"))
        hovers.append(hover)

    fig = go.Figure()

    # Barres principales
    fig.add_trace(go.Bar(
        x=names,
        y=ratios,
        marker_color=colors,
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hovers,
        showlegend=False,
    ))

    # Ligne de référence à 100% (= seuil sûr)
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=AXIS_COLOR,
        line_width=1.5,
        annotation_text="Seuil sûr",
        annotation_font_size=7,
        annotation_font_color=AXIS_COLOR,
        annotation_position="top right",
    )

    # Légende couleurs statut (traces invisibles pour la légende)
    for label, (stat, color) in [
        ("Safe",     ("safe",     STATUS_COLORS["safe"])),
        ("Dépassée", ("exceeded", STATUS_COLORS["exceeded"])),
        ("Critique", ("critical", STATUS_COLORS["critical"])),
    ]:
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            marker_color=color,
            name=label,
            showlegend=True,
        ))

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        barmode="overlay",
        legend=dict(
            orientation="h", y=1.15, x=0,
            font=dict(size=8), bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title=dict(text="Limite planétaire"),
            tickangle=-35,
            tickfont=dict(size=7),
            **_AXIS_BASE,
        ),
        yaxis=dict(
            title=dict(text="% du seuil sûr"),
            **_AXIS_BASE,
        ),
        dragmode=False,
    )

    return fig


# =========================================================
# DIAGRAMME SYSTÉMIQUE — bulles + flèches + boucles
# =========================================================
def chart_system_diagram():
    """
    Diagramme causal World3 :
      - 6 nœuds (bulles) pour les variables principales
      - Flèches étiquetées +/- pour chaque interaction
      - Boucles R1 (croissance), B1 (effondrement), B2 (contrainte ressources)
    """

    # ── Nœuds ────────────────────────────────────────────────────────────────
    NODES = {
        "pop":  {"x": 0.50, "y": 0.50, "label": "Population",  "color": "#3498db", "size": 54},
        "cap":  {"x": 0.82, "y": 0.68, "label": "Capital",     "color": "#d68910", "size": 44},
        "nour": {"x": 0.50, "y": 0.90, "label": "Nourriture",  "color": "#4a7c59", "size": 40},
        "res":  {"x": 0.82, "y": 0.20, "label": "Ressources",  "color": "#27ae60", "size": 40},
        "pol":  {"x": 0.18, "y": 0.20, "label": "Pollution",   "color": "#a8323e", "size": 40},
        "esp":  {"x": 0.18, "y": 0.68, "label": "Esp. vie",    "color": "#8e44ad", "size": 40},
    }

    # ── Arêtes ───────────────────────────────────────────────────────────────
    # (src, dst, signe, couleur, tiret, offset_x src, offset_x dst)
    EDGES = [
        # R1 — Boucle de croissance (vert)
        ("pop",  "cap",  "+", "#27ae60", "solid",  0.0,  0.0),
        ("cap",  "nour", "+", "#27ae60", "solid",  0.0,  0.0),
        ("nour", "pop",  "+", "#27ae60", "solid", -0.04, -0.04),
        # B1 — Rétroaction pollution/effondrement (rouge tirets)
        ("pop",  "pol",  "+", "#a8323e", "dash",   0.0,  0.0),
        ("pol",  "esp",  "−", "#a8323e", "dash",   0.0,  0.0),
        ("esp",  "pop",  "+", "#a8323e", "dash",   0.04,  0.04),
        # B2 — Contrainte ressources (orange pointillé)
        ("cap",  "res",  "−", "#d68910", "dot",   -0.025, -0.025),
        ("res",  "cap",  "+", "#d68910", "dot",    0.025,  0.025),
        # Pression démographique sur ressources (gris)
        ("pop",  "res",  "−", "#718096", "solid",  0.0,  0.0),
    ]

    # ── Boucles de fond (polygones semi-transparents) ─────────────────────────
    LOOPS = [
        {   # R1 — triangle Pop / Cap / Nour
            "path": "M 0.50,0.50 L 0.82,0.68 L 0.50,0.90 Z",
            "fill": "rgba(39,174,96,0.07)",
            "line": "rgba(39,174,96,0.25)",
            "label": "🔄 R1 Croissance",
            "lx": 0.66, "ly": 0.74,
            "lcolor": "#27ae60",
        },
        {   # B1 — triangle Pop / Pol / Esp
            "path": "M 0.50,0.50 L 0.18,0.20 L 0.18,0.68 Z",
            "fill": "rgba(168,50,62,0.07)",
            "line": "rgba(168,50,62,0.25)",
            "label": "⚖ B1 Effondrement",
            "lx": 0.27, "ly": 0.50,
            "lcolor": "#a8323e",
        },
        {   # B2 — bande droite Cap / Res
            "path": "M 0.75,0.20 L 0.92,0.20 L 0.92,0.68 L 0.75,0.68 Z",
            "fill": "rgba(214,137,16,0.07)",
            "line": "rgba(214,137,16,0.25)",
            "label": "⚖ B2 Contrainte",
            "lx": 0.91, "ly": 0.44,
            "lcolor": "#d68910",
        },
    ]

    fig = go.Figure()

    # ── Dessiner les polygones de boucle ──────────────────────────────────────
    for loop in LOOPS:
        fig.add_shape(
            type="path", path=loop["path"],
            xref="x", yref="y",
            fillcolor=loop["fill"],
            line=dict(color=loop["line"], width=1),
        )

    # ── Dessiner les flèches ──────────────────────────────────────────────────
    for (src_id, dst_id, sign, color, dash, ox_src, ox_dst) in EDGES:
        src = NODES[src_id]
        dst = NODES[dst_id]

        sx = src["x"] + ox_src
        sy = src["y"]
        dx = dst["x"] + ox_dst
        dy = dst["y"]

        # Standoff proportionnel à la taille du nœud destination (px → data)
        standoff = int(dst["size"] * 0.45)

        fig.add_annotation(
            x=dx, y=dy, ax=sx, ay=sy,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=2, arrowsize=1.1, arrowwidth=1.4,
            arrowcolor=color,
            standoff=standoff,
            startstandoff=int(src["size"] * 0.30),
            text="",
        )

        # Étiquette +/− au milieu de la flèche
        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        fig.add_annotation(
            x=mx, y=my,
            text=f"<b>{sign}</b>",
            showarrow=False,
            font=dict(size=9, color=color),
            bgcolor="rgba(248,245,240,0.85)",
            borderpad=1,
        )

    # ── Nœuds (bulles) ───────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[n["x"] for n in NODES.values()],
        y=[n["y"] for n in NODES.values()],
        mode="markers+text",
        marker=dict(
            size=[n["size"] for n in NODES.values()],
            color=[n["color"] for n in NODES.values()],
            opacity=0.92,
            line=dict(width=2, color="white"),
        ),
        text=[n["label"] for n in NODES.values()],
        textposition="middle center",
        textfont=dict(size=7, color="white", family="sans-serif"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # ── Labels des boucles ───────────────────────────────────────────────────
    for loop in LOOPS:
        fig.add_annotation(
            x=loop["lx"], y=loop["ly"],
            text=f"<b>{loop['label']}</b>",
            showarrow=False,
            font=dict(size=7, color=loop["lcolor"]),
            bgcolor="rgba(248,245,240,0.0)",
        )

    # ── Légende (traces fantômes) ─────────────────────────────────────────────
    for label, color in [
        ("R1 Croissance (+)", "#27ae60"),
        ("B1 Effondrement",   "#a8323e"),
        ("B2 Contrainte",     "#d68910"),
        ("Pression pop.",     "#718096"),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=color, width=2),
            name=label, showlegend=True,
        ))

    # ── Layout ───────────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(range=[-0.05, 1.05], visible=False, fixedrange=True),
        yaxis=dict(range=[-0.02, 1.02], visible=False, fixedrange=True),
        legend=dict(
            orientation="h", y=-0.04, x=0.5, xanchor="center",
            font=dict(size=7), bgcolor="rgba(0,0,0,0)",
            itemwidth=40,
        ),
        margin=dict(l=4, r=4, t=4, b=4),
        dragmode=False,
    )

    return fig
