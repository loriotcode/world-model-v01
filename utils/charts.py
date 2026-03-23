"""
utils/charts.py — Version 100% Plotly-native (sans bugs)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import html as _html

from models.world3 import SCENARIOS
from models.planetary import boundary_radar_data, STATUS_LABELS

# --- THEME ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND = "#e6f3ff"
GRID_COLOR = "#cfe8ff"
TEXT_COLOR = "#2d3748"
AXIS_COLOR = "#4a5568"

# --- META (non dynamique) ---
VARIABLE_META = {
    "population":      {"label": "Population (Md)", "yaxis": "Milliards"},
    "resources":       {"label": "Ressources (%)",  "yaxis": "%"},
    "pollution":       {"label": "Pollution",        "yaxis": "Index"},
    "capital":         {"label": "Capital industriel","yaxis": "Index"},
    "life_expectancy": {"label": "Espérance de vie","yaxis": "Années"},
    "food_per_capita": {"label": "Nourriture/habitant","yaxis": "Index"},
    "hdi":             {"label": "HDI",              "yaxis": "Index"},
}

# =========================================================
# TRAJECTOIRES (template Plotly NATIF)
# =========================================================
def chart_trajectories(results: dict, variable: str, is_mobile: bool = False) -> go.Figure:
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""})

    fig = go.Figure()

    for key, df in results.items():
        sc = SCENARIOS[key]

        # Échappement HTML SEULEMENT pour les labels (sécurité)
        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[variable],
            name=_html.escape(sc["label"]),  # ✅ Sécurisé ici
            line=dict(color=sc["color"], width=2.5 if not is_mobile else 2),
            hovertemplate=(
                f"<b>{_html.escape(sc['label'])}</b><br>"  # Contenu statique échappé
                "Année: %{x}<br>"                           # ✅ Template natif Plotly
                f"{_html.escape(meta['label'])}: %{y:.2f} {meta['yaxis']}<extra></extra>"
            )
        ))

    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR)

    fig.update_layout(
        title={
            "text": _html.escape(meta["label"]),
            "font": {"size": 15 if not is_mobile else 13, "color": TEXT_COLOR},
            "x": 0.5, "xanchor": "center"
        },
        xaxis={
            "title": _html.escape("Année"),
            "gridcolor": GRID_COLOR,
            "color": AXIS_COLOR,
            "range": [1970, 2100]
        },
        yaxis={
            "title": _html.escape(meta["yaxis"]),
            "gridcolor": GRID_COLOR,
            "color": AXIS_COLOR
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 11},
        legend={
            "orientation": "h",
            "y": -0.2 if not is_mobile else -0.3,
            "font": {"size": 11}
        },
        hovermode="x unified",
        height=320 if is_mobile else 420,
        margin={"l": 30, "r": 20, "t": 40, "b": 30}
    )
    return fig

# =========================================================
# DASHBOARD (4 variables core en 2x2)
# =========================================================
def chart_dashboard(results: dict, is_mobile: bool = False) -> go.Figure:
    """Dashboard premium 2x2 avec responsive et légende optimisée"""
    variables = ["population", "resources", "pollution", "capital"]
    titles = [VARIABLE_META[v]["label"] for v in variables]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=titles,
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]
        ]
    )

    positions = [(1,1), (1,2), (2,1), (2,2)]

    for var, (r,c) in zip(variables, positions):
        for key, df in results.items():
            sc = SCENARIOS[key]
            showlegend = (r == 1 and c == 1)  # Légende seulement sur le 1er graphique

            fig.add_trace(
                go.Scatter(
                    x=df["year"],
                    y=df[var],
                    name=_html.escape(sc["label"]),
                    line=dict(color=sc["color"], width=2.5 if not is_mobile else 2),
                    showlegend=showlegend,
                    hovertemplate=(
                        f"<b>{_html.escape(sc['label'])}</b><br>"
                        f"Année: %{x}<br>"
                        f"{_html.escape(VARIABLE_META[var]['label'])}: %{y:.2f} {VARIABLE_META[var]['yaxis']}<extra></extra>"
                    )
                ),
                row=r, col=c
            )

        # Mise à jour des axes pour chaque sous-graphique
        fig.update_xaxes(
            gridcolor=GRID_COLOR,
            color=AXIS_COLOR,
            row=r, col=c,
            tickfont={"size": 10 if not is_mobile else 8}
        )
        fig.update_yaxes(
            gridcolor=GRID_COLOR,
            color=AXIS_COLOR,
            row=r, col=c,
            tick
