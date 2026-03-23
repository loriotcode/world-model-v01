"""
utils/charts.py
Génération graphiques Plotly pour World Model v0.1
Thème : Ivoire/Papier recyclé avec fond graphiques bleu clair pâle (#e6f3ff)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from models.world3 import SCENARIOS
from models.planetary import STATUS_LABELS, boundary_radar_data


# --- Couleurs ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND = "#e6f3ff"
GRID_COLOR = "#b3e0ff"
TEXT_COLOR = "#2d3748"
AXIS_COLOR = "#4a5568"


# --- Métadonnées variables ---
VARIABLE_META = {
    "population":      {"label": "Population (Md)", "yaxis": "Milliards", "unit": ""},
    "resources":       {"label": "Ressources (%)",  "yaxis": "Index [0-1]", "unit": "%"},
    "pollution":       {"label": "Pollution",        "yaxis": "Index [0-1]", "unit": ""},
    "capital":         {"label": "Capital industriel","yaxis": "Index [0-1]", "unit": ""},
    "life_expectancy": {"label": "Espérance de vie","yaxis": "Années", "unit": "ans"},
    "food_per_capita": {"label": "Nourriture/habitant","yaxis": "Index [0-1]", "unit": ""},
    "hdi":             {"label": "HDI approx.",      "yaxis": "Index [0-1]", "unit": ""},
}


# =========================================================
# 📈 Trajectoires simples
# =========================================================
def chart_trajectories(results: dict, variable: str, is_mobile: bool = False) -> go.Figure:
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": "", "unit": ""})

    fig = go.Figure()

    for key, df in results.items():
        sc = SCENARIOS[key]

        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[variable],
            name=sc["label"],
            line=dict(color=sc["color"], width=2 if is_mobile else 2.5),
            hovertemplate=(
                f"<b>{sc['label']}</b><br>"
                f"Année: %{{x}}<br>"
                f"{meta['label']}: %{{y:.2f}} {meta['unit']}<extra></extra>"
            )
        ))

    fig.add_vline(
        x=2026,
        line_dash="dot",
        line_color=AXIS_COLOR
    )

    fig.update_layout(
        title=dict(
            text=meta["label"],
            x=0.5
        ),
        xaxis=dict(
            title="Année",
            gridcolor=GRID_COLOR,
            color=AXIS_COLOR,
            range=[1970, 2100]
        ),
        yaxis=dict(
            title=meta["yaxis"],
            gridcolor=GRID_COLOR,
            color=AXIS_COLOR
        ),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR, size=10 if is_mobile else 12),
        legend=dict(
            bgcolor=PLOT_BACKGROUND
        ),
        hovermode="closest" if is_mobile else "x unified",
        height=350 if is_mobile else 420,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


# =========================================================
# 📊 Dashboard 4 variables
# =========================================================
def chart_dashboard(results: dict, is_mobile: bool = False) -> go.Figure:
    variables = ["population", "resources", "pollution", "capital"]
    titles = [VARIABLE_META[v]["label"] for v in variables]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=titles,
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    positions = [(1,1), (1,2), (2,1), (2,2)]

    for var, (row, col) in zip(variables, positions):

        for key, df in results.items():
            sc = SCENARIOS[key]

            fig.add_trace(
                go.Scatter(
                    x=df["year"],
                    y=df[var],
                    name=sc["label"],
                    line=dict(color=sc["color"], width=2),
                    showlegend=(row == 1 and col == 1)
                ),
                row=row, col=col
            )

        fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR, row=row, col=col)

    fig.update_layout(
        title="Vue d'ensemble — 4 variables World3",
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        height=500 if not is_mobile else 600,
        hovermode="closest" if is_mobile else "x unified"
    )

    return fig


# =========================================================
# 🌐 Radar limites planétaires
# =========================================================
def chart_planetary_boundaries(boundaries: list, is_mobile: bool = False) -> go.Figure:
    data = boundary_radar_data(boundaries)

    names = data["names"] + [data["names"][0]]
    scores = data["scores"] + [data["scores"][0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[0.2] * len(names),
        theta=names,
        fill="toself",
        fillcolor="rgba(74,124,89,0.15)",
        line=dict(color="#4a7c59", dash="dash"),
        name="Zone sûre"
    ))

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=names,
        fill="toself",
        fillcolor="rgba(231,76,60,0.2)",
        line=dict(color="#a8323e", width=2),
        name="État actuel"
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=PLOT_BACKGROUND,
            radialaxis=dict(range=[0, 1.2])
        ),
        paper_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR),
        title="9 Limites Planétaires — État 2024",
        height=400 if is_mobile else 480
    )

    return fig


# =========================================================
# 📊 Barplot mobile limites planétaires
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries: list, is_mobile: bool = False) -> go.Figure:
    df = pd.DataFrame(boundaries)

    color_map = {
        "safe": "#4a7c59",
        "exceeded": "#d68910",
        "critical": "#a8323e"
    }

    fig = px.bar(
        df,
        x="name",
        y="current",
        color="status",
        color_discrete_map=color_map,
        labels={"current": "Valeur", "name": "Limite"},
        category_orders={"name": [b["name"] for b in boundaries]}
    )

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        height=350 if is_mobile else 400,
        hovermode="closest"
    )

    return fig
