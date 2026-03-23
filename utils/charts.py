"""
utils/charts.py — Version finale 100% fonctionnelle
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
def chart_trajectories(results: dict, variable: str, is_mobile: bool = False) -> go.Figure:
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": ""})
    fig = go.Figure()

    for key, df in results.items():
        sc = SCENARIOS[key]
        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[variable],
            name=_html.escape(sc["label"]),
            line=dict(color=sc["color"], width=2.5 if not is_mobile else 2),
            hovertemplate=(
                f"<b>{_html.escape(sc['label'])}</b><br>"
                "Année: %{x}<br>"
                f"{_html.escape(meta['label'])}: %{y:.2f} {meta['yaxis']}<extra></extra>"
            )
        ))

    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR)

    fig.update_layout(
        title={"text": _html.escape(meta["label"]), "font": {"size": 15 if not is_mobile else 13, "color": TEXT_COLOR}, "x": 0.5, "xanchor": "center"},
        xaxis={"title": _html.escape("Année"), "gridcolor": GRID_COLOR, "color": AXIS_COLOR, "range": [1970, 2100], "title_font": {"size": 13 if not is_mobile else 11}, "tickfont": {"size": 11 if not is_mobile else 9}},
        yaxis={"title": _html.escape(meta["yaxis"]), "gridcolor": GRID_COLOR, "color": AXIS_COLOR, "title_font": {"size": 13 if not is_mobile else 11}, "tickfont": {"size": 11 if not is_mobile else 9}},
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 11},
        legend={"orientation": "h", "y": -0.2 if not is_mobile else -0.3, "font": {"size": 11 if not is_mobile else 9}},
        hovermode="x unified",
        height=320 if is_mobile else 420,
        margin={"l": 30, "r": 20, "t": 40, "b": 30}
    )
    return fig

# =========================================================
# DASHBOARD
# =========================================================
def chart_dashboard(results: dict, is_mobile: bool = False) -> go.Figure:
    variables = ["population", "resources", "pollution", "capital"]
    titles = [_html.escape(VARIABLE_META[v]["label"]) for v in variables]
    fig = make_subplots(rows=2, cols=2, subplot_titles=titles, vertical_spacing=0.12, horizontal_spacing=0.08)

    positions = [(1,1), (1,2), (2,1), (2,2)]

    for var, (r,c) in zip(variables, positions):
        for key, df in results.items():
            sc = SCENARIOS[key]
            showlegend = (r == 1 and c == 1)

            fig.add_trace(
                go.Scatter(
                    x=df["year"],
                    y=df[var],
                    name=_html.escape(sc["label"]),
                    line=dict(color=sc["color"], width=2.5 if not is_mobile else 2),
                    showlegend=showlegend,
                    hovertemplate=(
                        f"<b>{_html.escape(sc['label'])}</b><br>"
                        "Année: %{x}<br>"
                        f"{_html.escape(VARIABLE_META[var]['label'])}: %{y:.2f} {VARIABLE_META[var]['yaxis']}<extra></extra>"
                    )
                ),
                row=r, col=c
            )

        fig.update_xaxes(gridcolor=GRID_COLOR, color=AXIS_COLOR, row=r, col=c, tickfont={"size": 10 if not is_mobile else 8})
        fig.update_yaxes(gridcolor=GRID_COLOR, color=AXIS_COLOR, row=r, col=c, tickfont={"size": 10 if not is_mobile else 8})

    for r,c in positions:
        fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR, row=r, col=c)

    fig.update_layout(
        title={"text": _html.escape("Vue globale — 4 variables World3"), "font": {"size": 17 if not is_mobile else 14, "color": TEXT_COLOR}, "x": 0.5, "xanchor": "center"},
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 11},
        height=600 if not is_mobile else 700,
        legend={"orientation": "h", "y": -0.1 if not is_mobile else -0.25, "font": {"size": 11 if not is_mobile else 9}},
        hovermode="x unified",
        margin={"l": 20, "r": 15, "t": 40, "b": 40 if not is_mobile else 25}
    )
    return fig

# =========================================================
# RADAR
# =========================================================
def chart_planetary_boundaries(boundaries: list, is_mobile: bool = False) -> go.Figure:
    data = boundary_radar_data(boundaries)
    names = [b["name"] for b in boundaries] + [boundaries[0]["name"]]
    scores = [b["current"] for b in boundaries] + [boundaries[0]["current"]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[0.2]*len(names), theta=names, fill="toself", fillcolor="rgba(74, 124, 89, 0.15)", line=dict(color="#4a7c59", width=1, dash="dash"), name=_html.escape("Zone sûre"), hoverinfo="skip"))
    fig.add_trace(go.Scatterpolar(r=scores, theta=names, fill="toself", fillcolor="rgba(231, 76, 60, 0.2)", line=dict(color="#a8323e", width=2 if not is_mobile else 1.5), name=_html.escape("État actuel (2024)"),
        hovertemplate=(f"<b>%{{theta}}</b><br>Valeur: %{{r:.2f}}<br>Statut: %{{customdata}}<extra></extra>"),
        customdata=[_html.escape(STATUS_LABELS[b["status"]][0]) for b in boundaries] + [""]
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1.2], visible=True, gridcolor=GRID_COLOR, color=AXIS_COLOR, tickfont={"size": 10 if not is_mobile else 8}),
        angularaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR, tickfont={"size": 10 if not is_mobile else 8}), bgcolor=PLOT_BACKGROUND),
        paper_bgcolor=BACKGROUND_COLOR,
        font={"color": TEXT_COLOR, "size": 11},
        title={"text": _html.escape("9 Limites Planétaires — État 2024"), "font": {"size": 17 if not is_mobile else 14, "color": TEXT_COLOR}, "x": 0.5, "xanchor": "center"},
        legend={"orientation": "h", "y": -0.1 if not is_mobile else -0.2, "font": {"size": 11 if not is_mobile else 9}},
        height=420 if is_mobile else 500,
        margin={"l": 20, "r": 15, "t": 40, "b": 20 if not is_mobile else 30}
    )
    return fig

# =========================================================
# BAR PLOT
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries: list, is_mobile: bool = False) -> go.Figure:
    df = pd.DataFrame(boundaries)
    fig = px.bar(df, x="name", y="current", color="status",
        color_discrete_map={"safe": "#4a7c59", "exceeded": "#d68910", "critical": "#a8323e"},
        labels={"current": "Valeur actuelle", "name": "Limite planétaire"},
        title=_html.escape("État des limites planétaires (2024)"),
        category_orders={"name": [b["name"] for b in boundaries]}
    )

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 10},
        xaxis={"tickfont": {"size": 9 if not is_mobile else 7}, "tickangle": -45 if is_mobile else 0, "gridcolor": GRID_COLOR, "color": AXIS_COLOR},
        yaxis={"tickfont": {"size": 9 if not is_mobile else 7}, "gridcolor": GRID_COLOR, "color": AXIS_COLOR},
        legend={"orientation": "h", "y": -0.1, "font": {"size": 10}},
        hovermode="x unified",
        height=320 if is_mobile else 400,
        margin={"l": 20, "r": 15, "t": 40, "b": 20 if not is_mobile else 30}
    )
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside", textfont={"size": 9 if not is_mobile else 7, "color": TEXT_COLOR})
    return fig
