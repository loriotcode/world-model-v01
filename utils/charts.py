""" utils/charts.py — Version finale corrigée (100% fonctionnelle) """

import plotly.graph_objects as go import plotly.express as px from plotly.subplots import make_subplots import pandas as pd import html as _html

from models.world3 import SCENARIOS from models.planetary import boundary_radar_data, STATUS_LABELS

--- THEME ---

BACKGROUND_COLOR = "#f8f5f0" PLOT_BACKGROUND = "#e6f3ff" GRID_COLOR = "#cfe8ff" TEXT_COLOR = "#2d3748" AXIS_COLOR = "#4a5568"

--- META ---

VARIABLE_META = { "population": {"label": "Population (Md)", "yaxis": "Milliards"}, "resources": {"label": "Ressources (%)", "yaxis": "%"}, "pollution": {"label": "Pollution", "yaxis": "Index"}, "capital": {"label": "Capital industriel", "yaxis": "Index"}, "life_expectancy": {"label": "Espérance de vie", "yaxis": "Années"}, "food_per_capita": {"label": "Nourriture/habitant", "yaxis": "Index"}, "hdi": {"label": "HDI", "yaxis": "Index"}, }

=========================================================

TRAJECTOIRES

=========================================================

def chart_trajectories(results: dict, variable: str, is_mobile: bool = False) -> go.Figure: meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""}) fig = go.Figure()

for key, df in results.items():
    sc = SCENARIOS[key]
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df[variable],
        name=_html.escape(sc["label"]),
        line=dict(color=sc["color"], width=2.5 if not is_mobile else 2),
        hovertemplate=(
            "<b>" + _html.escape(sc["label"]) + "</b><br>"
            "Année: %{x}<br>"
            + _html.escape(meta["label"]) + ": %{y:.2f} " + meta["yaxis"] + "<extra></extra>"
        )
    ))

fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR)

fig.update_layout(
    title={"text": _html.escape("9 Limites Planétaires — État 2024"), "font": {"size": 17 if not is_mobile else 14, "color": TEXT_COLOR}, "x": 0.5, "xanchor": "center"},
    height=400 if is_mobile else 480
)

return fig

=========================================================

BAR (corrigé : cohérence + labels)

=========================================================

def chart_planetary_boundaries_as_bars(boundaries: list, is_mobile: bool = False) -> go.Figure: df = pd.DataFrame(boundaries)

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
    font={"color": TEXT_COLOR, "size": 11},
    height=350 if is_mobile else 420,
    hovermode="closest",
    margin={"l": 20, "r": 20, "t": 40, "b": 40}
)

return fig
