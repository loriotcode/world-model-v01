"""
utils/charts.py — Version FINAL (zoom-safe + UI premium)
Tous les problèmes résolus
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import html as _html

from models.world3 import SCENARIOS

# --- THEME (identique à ton app.py) ---
BACKGROUND_COLOR = "#f8f5f0"
PLOT_BACKGROUND = "#ffffff"  # Fond blanc pour contraste
GRID_COLOR = "#cfe8ff"
TEXT_COLOR = "#2d3748"
AXIS_COLOR = "#4a5568"
COLORS = ["#6fa8dc", "#d07449", "#8ab659", "#82bfbf"]  # Bleu clair, orange, vert, cyan

# =========================================================
# TRAJECTOIRES (zoom-safe + légendes premium)
# =========================================================
def chart_trajectories(results, variable, is_mobile=False):
    meta = {"population": "Population (Md)", "resources": "Ressources (%)"}.get(variable, variable + " (index)")

    fig = go.Figure()

    # --- Ajout des traces avec couleurs standardisées ---
    for idx, key in enumerate(results):
        df = results[key]
        sc = SCENARIOS[key]

        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df[variable],
            name=_html.escape(sc["label"]),
            line=dict(color=COLORS[idx], width=3 if not is_mobile else 2),
            hovertemplate=(
                "<b>" + _html.escape(sc["label"]) + "</b><br>"
                "Année: %{x}<br>"
                + _html.escape(meta) + ": %{y:.2f} " + "<extra></extra>"
            ),
            visible=True,  # Toutes les traces visibles par défaut
            showlegend=True
        ))

    # --- Ligne 2026 (toujours visible) ---
    fig.add_vline(x=2026, line_dash="dot", line_color=AXIS_COLOR, annotation_text="2026", annotation_position="top right")

    # --- Configuration PREMIUM (zoom-safe + contraste) ---
    fig.update_layout(
        title={
            "text": _html.escape(meta.split("(index)")[0].strip() + " — World3"),
            "font": {"size": 18, "color": TEXT_COLOR, "family": "Arial"},
            "x": 0.5, "xanchor": "center"
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 12},
        height=480 if is_mobile else 580,
        margin={"l": 60, "r": 30, "t": 70, "b": 60},
        legend={
            "orientation": "h",
            "y": -0.25 if not is_mobile else -0.35,
            "font": {"size": 11, "color": TEXT_COLOR, "family": "Arial"},
            "bgcolor": PLOT_BACKGROUND,
            "bordercolor": GRID_COLOR,
            "borderwidth": 1
        },
        xaxis={
            "title": "Année",
            "gridcolor": GRID_COLOR,
            "color": AXIS_COLOR,
            "range": [1970, 2100],
            "title_font": {"size": 14, "color": TEXT_COLOR}
        },
        yaxis={
            "title": _html.escape(meta.split("(index)")[0].strip()),
            "gridcolor": GRID_COLOR,
            "color": AXIS_COLOR,
            "title_font": {"size": 14, "color": TEXT_COLOR}
        },
        hovermode="x unified",  # Évite la confusion en zoomant
        dragmode="pan",  # Permet de se déplacer facilement
        plot_bgcolor=BACKGROUND_COLOR
    )

    return fig

# =========================================================
# DASHBOARD (zoom-safe + 4 sous-graphes premium)
# =========================================================
def chart_dashboard(results, is_mobile=False):
    variables = ["population", "resources", "pollution", "capital"]
    titles = [_html.escape("Population") + " (Md)", _html.escape("Ressources") + " (%)", "Pollution (index)", "Capital (index)"]

    fig = make_subplots(
        rows=2 if not is_mobile else 4,
        cols=2 if not is_mobile else 1,
        subplot_titles=titles,
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    positions = [(1,1), (1,2), (2,1), (2,2)] if not is_mobile else [(1,1), (2,1), (3,1), (4,1)]

    for idx, (var, (r,c)) in enumerate(zip(variables, positions)):
        for key in results:
            df = results[key]

            fig.add_trace(go.Scatter(
                x=df["year"],
                y=df[var],
                name=_html.escape(SCENARIOS[key]["label"]),
                line=dict(color=COLORS[idx], width=2.5),
                hovertemplate="<b>" + _html.escape(SCENARIOS[key]["label"]) + "</b><br>Année: %{x}<br>Valeur: %{y:.2f}<extra></extra>",
                visible=True,
                showlegend=(r == 1 and c == 1)
            ), row=r, col=c)

        fig.add_vline(x=2026, row=r, col=c, line_dash="dot", line_color=AXIS_COLOR)

    fig.update_layout(
        title={
            "text": "Vue d'ensemble — 4 variables World3 (2026)",
            "font": {"size": 20, "color": TEXT_COLOR, "family": "Arial"}
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 12},
        height=650 if not is_mobile else 950,
        margin={"l": 40, "r": 20, "t": 70, "b": 30},
        legend={
            "orientation": "h",
            "y": -0.15,
            "font": {"size": 11, "color": TEXT_COLOR},
            "bgcolor": PLOT_BACKGROUND
        },
        hovermode="x unified",
        dragmode="pan"
    )

    return fig

# =========================================================
# RADAR (zoom-safe + légendes premium)
# =========================================================
def chart_planetary_boundaries(boundaries, is_mobile=False):
    names = [b["name"] for b in boundaries]
    values = [b["current"] for b in boundaries]

    # Fermeture radar
    names.append(names[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=names,
        fill="toself",
        fillcolor="rgba(231, 76, 60, 0.2)",  # Rouge semi-transparent
        line=dict(color="#a8323e", width=2),
        name=_html.escape("État actuel (2024)"),
        hovertemplate="<b>%{theta}</b><br>Valeur: %{r:.2f}<br>Statut: " + _html.escape(STATUS_LABELS[boundaries[list(names).index("%{theta}")]["status"]][0]) + "<extra></extra>",
        visible=True,
        showlegend=True
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 1.2], gridcolor=GRID_COLOR, color=AXIS_COLOR, tickfont={"size": 10}),
            angularaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR, tickfont={"size": 10}),
            bgcolor=PLOT_BACKGROUND
        ),
        paper_bgcolor=BACKGROUND_COLOR,
        font={"color": TEXT_COLOR, "size": 12},
        title={
            "text": "9 Limites Planétaires — État 2024 (Rockström 2009)",
            "font": {"size": 18, "color": TEXT_COLOR, "family": "Arial"}
        },
        height=500 if not is_mobile else 580,
        margin={"l": 40, "r": 40, "t": 70, "b": 40},
        legend={
            "orientation": "h",
            "y": -0.1,
            "font": {"size": 11, "color": TEXT_COLOR}
        },
        hovermode="closest"
    )

    return fig

# =========================================================
# BAR PLOT (zoom-safe + légendes premium)
# =========================================================
def chart_planetary_boundaries_as_bars(boundaries, is_mobile=False):
    df = pd.DataFrame([{
        "name": b["name"],
        "current": b["current"],
        "status": b["status"]
    } for b in boundaries])

    fig = px.bar(
        df,
        x="name",
        y="current",
        color="status",
        color_discrete_map={"safe": "#4a7c59", "exceeded": "#d68910", "critical": "#a8323e"},
        text="current",
        labels={"current": "Valeur actuelle", "name": "Limite planétaire"}
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        textfont={"size": 10, "color": TEXT_COLOR},
        marker_line_color=AXIS_COLOR,
        marker_line_width=2
    )

    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": TEXT_COLOR, "size": 11},
        title={
            "text": "État des 9 limites planétaires (2024)",
            "font": {"size": 16, "color": TEXT_COLOR, "family": "Arial"}
        },
        xaxis={
            "title": "Limite planétaire",
            "gridcolor": GRID_COLOR,
            "color": AXIS_COLOR,
            "tickangle": -45 if not is_mobile else -90,
            "title_font": {"size": 13}
        },
        yaxis={
            "title": "Valeur actuelle (index)",
            "gridcolor": GRID_COLOR,
            "color": AXIS_COLOR,
            "title_font": {"size": 13}
        },
        height=420 if not is_mobile else 500,
        margin={"l": 70, "r": 30, "t": 70, "b": 120},
        legend={
            "orientation": "h",
            "y": -0.1,
            "font": {"size": 10, "color": TEXT_COLOR}
        },
        hovermode="x unified"
    )

    return fig
