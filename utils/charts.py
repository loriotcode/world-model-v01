"""
utils/charts.py — Landscape smartphone
"""

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
