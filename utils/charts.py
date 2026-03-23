"""
utils/charts.py — Version clean stable (mobile-safe)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import html as _html

from models.world3 import SCENARIOS
from models.planetary import STATUS_LABELS

# --- THEME ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND = "#e6f3ff"
GRID_COLOR = "#cfe8ff"
TEXT_COLOR = "#2d3748"
AXIS_COLOR = "#4a5568"

# --- META ---
VARIABLE_META = {
    "population": {"label": "Population (Md)", "yaxis": "Milliards"},
    "resources": {"label": "Ressources (%)", "yaxis": "%"},
    "pollution": {"label": "Pollution", "yaxis": "Index"},
    "capital": {"label": "Capital industriel", "yaxis": "Index"},
    "life_expectancy": {"label": "Espérance de vie", "yaxis": "Années"},
    "food_per_capita": {"label": "Nourriture/habitant", "yaxis": "Index"},
    "hdi": {"label": "HDI", "yaxis": "Index"},
}

# =========================================================
# TRAJECTOIRES
# =========================================================
def chart_trajectories(results, variable, is_mobile=False):
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""})
    fig = go.Figure()

    for key in results:
        df = results[key]
        sc = SCENARIOS[key]

        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df[variable],
                name=_html.escape(sc["label"]),
                line=dict(color=sc["color"], width=2),
                hovertemplate=(
                    "<b>" + _html.escape(sc["label"]) + "</b><br>"
                    "Année: %{x}<br>"
                    + _html.escape(meta["label"]) + ": %{y:.2f}<extra></extra>"
                ),
            )
        )

    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR)

fig.update_layout(
    title="Vue globale",
    paper_bgcolor=BACKGROUND_COLOR,
    plot_bgcolor=PLOT_BACKGROUND,
    font=dict(color=TEXT_COLOR, size=11 if is_mobile else 13),
    height=700 if is_mobile else 600,
    margin=dict(l=40, r=20, t=60, b=40),
    legend=dict(orientation="h", y=-0.15),
)

    return fig


# =========================================================
# DASHBOARD
# =========================================================
def chart_dashboard(results, is_mobile=False):
    variables = ["population", "resources", "pollution", "capital"]
    titles = [VARIABLE_META[v]["label"] for v in variables]

if is_mobile:
    fig = make_subplots(rows=4, cols=1, subplot_titles=titles)
    positions = [(1,1),(2,1),(3,1),(4,1)]
else:
    fig = make_subplots(rows=2, cols=2, subplot_titles=titles)
    positions = [(1,1),(1,2),(2,1),(2,2)]
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for var, (r, c) in zip(variables, positions):
        for key in results:
            df = results[key]
            sc = SCENARIOS[key]

            fig.add_trace(
                go.Scatter(
                    x=df["year"],
                    y=df[var],
                    name=sc["label"],
                    line=dict(color=sc["color"]),
                    showlegend=(r == 1 and c == 1),
                ),
                row=r,
                col=c,
            )

        fig.add_vline(x=2026, row=r, col=c)

    fig.update_layout(
        title="Vue globale",
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR),
        height=600,
    )

    return fig


# =========================================================
# RADAR
# =========================================================
def chart_planetary_boundaries(boundaries, is_mobile=False):
    names = [b["name"] for b in boundaries]
    values = [b["current"] for b in boundaries]

    # fermeture radar
    names.append(names[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=names,
            fill="toself",
            name="État actuel",
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1.2])),
        paper_bgcolor=BACKGROUND_COLOR,
        height=400 if is_mobile else 480,
    )

    return fig


# =========================================================
# BAR
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries, is_mobile=False):
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
        height=350 if is_mobile else 420,
    )

    return fig
