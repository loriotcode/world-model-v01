"""
utils/charts.py
Génération graphiques Plotly pour World Model v0.1
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from models.world3 import SCENARIOS
from models.planetary import STATUS_LABELS, boundary_radar_data


VARIABLE_META = {
    "population":      {"label": "Population (Md)", "yaxis": "Milliards"},
    "resources":       {"label": "Ressources (%)",  "yaxis": "Index [0-1]"},
    "pollution":       {"label": "Pollution",        "yaxis": "Index [0-1]"},
    "capital":         {"label": "Capital industriel","yaxis": "Index [0-1]"},
    "life_expectancy": {"label": "Espérance de vie","yaxis": "Années"},
    "food_per_capita": {"label": "Nourriture/habitant","yaxis": "Index [0-1]"},
    "hdi":             {"label": "HDI approx.",      "yaxis": "Index [0-1]"},
}


def chart_trajectories(results: dict, variable: str) -> go.Figure:
    """Graphique trajectoires multi-scénarios pour une variable"""
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""})
    fig = go.Figure()

    for key, df in results.items():
        sc = SCENARIOS[key]
        fig.add_trace(go.Scatter(
            x=df["year"], y=df[variable],
            name=sc["label"],
            line=dict(color=sc["color"], width=2.5),
            hovertemplate=f"<b>{sc['label']}</b><br>Année: %{{x}}<br>{meta['label']}: %{{y:.3f}}<extra></extra>"
        ))

    # Ligne "aujourd'hui"
    fig.add_vline(x=2026, line_dash="dot", line_color="white",
                  annotation_text="2026", annotation_position="top right",
                  annotation_font_color="white")

    fig.update_layout(
        title=dict(text=meta["label"], font=dict(size=18, color="white")),
        xaxis=dict(title="Année", color="white", gridcolor="#333", range=[1970, 2100]),
        yaxis=dict(title=meta["yaxis"], color="white", gridcolor="#333"),
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1a1f2e",
        font=dict(color="white"),
        legend=dict(bgcolor="#1a1f2e", bordercolor="#333", borderwidth=1),
        hovermode="x unified",
        height=420,
    )
    return fig


def chart_dashboard(results: dict) -> go.Figure:
    """Dashboard 2x2 : 4 variables core"""
    variables = ["population", "resources", "pollution", "capital"]
    titles = ["Population (Md)", "Ressources", "Pollution", "Capital industriel"]

    fig = make_subplots(rows=2, cols=2, subplot_titles=titles,
                        vertical_spacing=0.12, horizontal_spacing=0.08)

    positions = [(1,1),(1,2),(2,1),(2,2)]

    for (var, title, pos) in zip(variables, titles, positions):
        row, col = pos
        for key, df in results.items():
            sc = SCENARIOS[key]
            showlegend = (row == 1 and col == 1)
            fig.add_trace(go.Scatter(
                x=df["year"], y=df[var],
                name=sc["label"],
                line=dict(color=sc["color"], width=2),
                showlegend=showlegend,
                legendgroup=key,
            ), row=row, col=col)
        # Ligne 2026
        fig.add_vline(x=2026, line_dash="dot", line_color="rgba(255,255,255,0.3)",
                      row=row, col=col)

    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1a1f2e",
        font=dict(color="white"),
        height=600,
        title=dict(text="Vue d'ensemble — 4 variables World3", font=dict(size=16, color="white")),
        legend=dict(bgcolor="#1a1f2e", bordercolor="#444", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="#333", color="white")
    fig.update_yaxes(gridcolor="#333", color="white")
    return fig


def chart_planetary_boundaries(boundaries: list) -> go.Figure:
    """Radar chart des 9 limites planétaires"""
    data = boundary_radar_data(boundaries)
    names = data["names"] + [data["names"][0]]  # Fermer le polygone
    scores = data["scores"] + [data["scores"][0]]

    color_map = {"safe": "#27ae60", "exceeded": "#e67e22", "critical": "#e74c3c"}
    marker_colors = [color_map[b["status"]] for b in boundaries]

    fig = go.Figure()

    # Zone limite sûre
    fig.add_trace(go.Scatterpolar(
        r=[0.2] * (len(names)),
        theta=names,
        fill="toself",
        fillcolor="rgba(39,174,96,0.15)",
        line=dict(color="#27ae60", width=1, dash="dash"),
        name="Zone sûre",
    ))

    # État actuel
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=names,
        fill="toself",
        fillcolor="rgba(231,76,60,0.2)",
        line=dict(color="#e74c3c", width=2),
        name="État actuel (2024)",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="#1a1f2e",
            radialaxis=dict(visible=True, range=[0, 1.2], color="white", gridcolor="#333"),
            angularaxis=dict(color="white", gridcolor="#333"),
        ),
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        title=dict(text="9 Limites Planétaires — État 2024", font=dict(size=16, color="white")),
        legend=dict(bgcolor="#1a1f2e"),
        height=480,
    )
    return fig
