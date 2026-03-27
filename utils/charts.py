"""
utils/charts.py — Landscape smartphone, is_mobile supprimé
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import html as _html

from models.world3 import SCENARIOS
from models.planetary import STATUS_LABELS

# --- THEME ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND  = "#e6f3ff"
GRID_COLOR       = "#cfe8ff"
TEXT_COLOR       = "#2d3748"
AXIS_COLOR       = "#4a5568"

# --- META ---
VARIABLE_META = {
    "population":      {"label": "Population (Md)",       "yaxis": "Milliards"},
    "resources":       {"label": "Ressources (%)",         "yaxis": "%"},
    "pollution":       {"label": "Pollution",              "yaxis": "Index"},
    "capital":         {"label": "Capital industriel",     "yaxis": "Index"},
    "life_expectancy": {"label": "Espérance de vie",       "yaxis": "Années"},
    "food_per_capita": {"label": "Nourriture/habitant",    "yaxis": "Index"},
    "hdi":             {"label": "HDI",                    "yaxis": "Index"},
}


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
                "Année: %{x}<br>"
                + _html.escape(meta["label"]) + ": %{y:.2f}<extra></extra>"
            ),
        ))

    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR)

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        legend=dict(orientation="h", y=-0.2),
    )

    return fig


# =========================================================
# BARRES LIMITES PLANÉTAIRES
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries):
    df = pd.DataFrame(boundaries)

    fig = px.bar(
        df,
        x="name",
        y="current",
        color="status",
    )

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
    )

    return fig
