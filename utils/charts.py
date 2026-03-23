"""
utils/charts.py
Génération graphiques Plotly pour World Model v0.1
Thème : Ivoire/Papier recyclé avec fond graphiques bleu clair pâle (#e6f3ff)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import html as _html
from models.world3 import SCENARIOS
from models.planetary import STATUS_LABELS, boundary_radar_data

# --- Couleurs adaptées au thème ---
BACKGROUND_COLOR = "#f8f5f0"      # Fond global (ivoire)
PLOT_BACKGROUND = "#e6f3ff"        # Fond graphiques (bleu clair pâle)
GRID_COLOR = "#b3e0ff"             # Grilles (bleu très clair)
TEXT_COLOR = "#2d3748"             # Texte principal (gris foncé)
AXIS_COLOR = "#4a5568"             # Axes (gris-bleu)
HIGHLIGHT_COLOR = "#d68910"        # Couleur d'accent (terre cuite)

VARIABLE_META = {
    "population":      {"label": "Population (Md)", "yaxis": "Milliards", "unit": ""},
    "resources":       {"label": "Ressources (%)",  "yaxis": "Index [0-1]", "unit": "%"},
    "pollution":       {"label": "Pollution",        "yaxis": "Index [0-1]", "unit": ""},
    "capital":         {"label": "Capital industriel","yaxis": "Index [0-1]", "unit": ""},
    "life_expectancy": {"label": "Espérance de vie","yaxis": "Années", "unit": "ans"},
    "food_per_capita": {"label": "Nourriture/habitant","yaxis": "Index [0-1]", "unit": ""},
    "hdi":             {"label": "HDI approx.",      "yaxis": "Index [0-1]", "unit": ""},
}

def chart_trajectories(results: dict, variable: str, is_mobile: bool = False) -> go.Figure:
    """Graphique trajectoires multi-scénarios pour une variable"""
    meta = VARIABLE_META.get(variable, {"label": variable, "yaxis": "", "unit": ""})
    fig = go.Figure()

    for key, df in results.items():
        sc = SCENARIOS[key]
        # Échappement HTML pour éviter les injections XSS
        fig.add_trace(go.Scatter(
            x=df["year"], y=df[variable],
            name=_html.escape(sc["label"]),
            line=dict(color=sc["color"], width=2.5 if not is_mobile else 2),
            hovertemplate=(
                f"<b>{_html.escape(sc['label'])}</b><br>"
                f"Année: %{x}<br>"
                f"{_html.escape(meta['label'])}: %{y:.2f} {meta['unit']}<extra></extra>"
            )
        ))

    # Ligne "aujourd'hui" (2026)
    fig.add_vline(
        x=2026, line_dash="dot", line_color=AXIS_COLOR,
        annotation_text="2026",
        annotation_position="top right",
        annotation_font_color=TEXT_COLOR,
        annotation_bgcolor=PLOT_BACKGROUND
    )

    # Configuration adaptative
    fig.update_layout(
        title=dict(
            text=_html.escape(meta["label"]),
            font=dict(size=16 if not is_mobile else 14, color=TEXT_COLOR),
            x=0.5, xanchor="center"
        ),
        xaxis=dict(
            title=_html.escape("Année"),
            color=AXIS_COLOR,
            gridcolor=GRID_COLOR,
            range=[1970, 2100],
            title_font=dict(size=12 if not is_mobile else 10),
            tickfont=dict(size=10 if is_mobile else 12)
        ),
        yaxis=dict(
            title=_html.escape(meta["yaxis"]),
            color=AXIS_COLOR,
            gridcolor=GRID_COLOR,
            title_font=dict(size=12 if not is_mobile else 10),
            tickfont=dict(size=10 if is_mobile else 12)
        ),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR, size=10 if is_mobile else 12),
        legend=dict(
            bgcolor=PLOT_BACKGROUND,
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(size=10 if is_mobile else 12),
            yanchor="bottom", y=1.02, xanchor="right", x=1  # Légende horizontale en bas
        ),
        hovermode="x unified",
        height=350 if is_mobile else 420,
        margin=dict(
            l=20 if not is_mobile else 10,
            r=20 if not is_mobile else 10,
            t=40 if not is_mobile else 30,
            b=20 if not is_mobile else 10
        ),
        plot_bgcolor=PLOT_BACKGROUND,
        hoverlabel=dict(bgcolor=PLOT_BACKGROUND, font_size=12 if not is_mobile else 10)
    )
    return fig

def chart_dashboard(results: dict, is_mobile: bool = False) -> go.Figure:
    """Dashboard 2x2 : 4 variables core"""
    variables = ["population", "resources", "pollution", "capital"]
    titles = [VARIABLE_META[v]["label"] for v in variables]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[_html.escape(t) for t in titles],
        vertical_spacing=0.15 if not is_mobile else 0.22,
        horizontal_spacing=0.1 if not is_mobile else 0.15,
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
              [{"secondary_y": False}, {"secondary_y": False}]]
    )

    positions = [(1,1), (1,2), (2,1), (2,2)]

    for (var, pos) in zip(variables, positions):
        row, col = pos
        for key, df in results.items():
            sc = SCENARIOS[key]
            showlegend = (row == 1 and col == 1)
            fig.add_trace(
                go.Scatter(
                    x=df["year"], y=df[var],
                    name=_html.escape(sc["label"]),
                    line=dict(color=sc["color"], width=2 if not is_mobile else 1.5),
                    showlegend=showlegend,
                    legendgroup=key,
                    hovertemplate=(
                        f"<b>{_html.escape(sc['label'])}</b><br>"
                        f"Année: %{x}<br>"
                        f"{_html.escape(VARIABLE_META[var]['label'])}: %{y:.2f} {VARIABLE_META[var]['unit']}<extra></extra>"
                    )
                ),
                row=row, col=col
            )
        # Ligne 2026
        fig.add_vline(
            x=2026, line_dash="dot", line_color=AXIS_COLOR,
            row=row, col=col
        )

    # Configuration globale
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR, size=10 if is_mobile else 12),
        height=500 if not is_mobile else 600,
        title=dict(
            text=_html.escape("Vue d'ensemble — 4 variables World3"),
            font=dict(size=16 if not is_mobile else 14, color=TEXT_COLOR),
            x=0.5, xanchor="center"
        ),
        legend=dict(
            bgcolor=PLOT_BACKGROUND,
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(size=10 if is_mobile else 12),
            yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        margin=dict(
            l=10 if is_mobile else 20,
            r=10 if is_mobile else 20,
            t=40 if not is_mobile else 30,
            b=10 if is_mobile else 20
        )
    )

    # Configuration des axes
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(
                gridcolor=GRID_COLOR, color=AXIS_COLOR,
                row=i, col=j,
                tickfont=dict(size=9 if is_mobile else 11)
            )
            fig.update_yaxes(
                gridcolor=GRID_COLOR, color=AXIS_COLOR,
                row=i, col=j,
                tickfont=dict(size=9 if is_mobile else 11)
            )

    return fig

def chart_planetary_boundaries(boundaries: list, is_mobile: bool = False) -> go.Figure:
    """Radar chart des 9 limites planétaires (version desktop)"""
    data = boundary_radar_data(boundaries)
    names = data["names"] + [data["names"][0]]
    scores = data["scores"] + [data["scores"][0]]

    color_map = {"safe": "#4a7c59", "exceeded": "#d68910", "critical": "#a8323e"}

    fig = go.Figure()

    # Zone limite sûre (vert)
    fig.add_trace(go.Scatterpolar(
        r=[0.2] * len(names),
        theta=names,
        fill="toself",
        fillcolor="rgba(74, 124, 89, 0.15)",
        line=dict(color="#4a7c59", width=1, dash="dash"),
        name=_html.escape("Zone sûre"),
        hoverinfo="skip"
    ))

    # État actuel (rouge)
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=names,
        fill="toself",
        fillcolor="rgba(231, 76, 60, 0.2)",
        line=dict(color="#a8323e", width=2 if not is_mobile else 1.5),
        name=_html.escape("État actuel (2024)"),
        hovertemplate=(
            f"<b>%{{theta}}</b><br>"
            f"Valeur: %{{r:.2f}}<br>"
            f"Statut: %{{customdata}}<extra></extra>"
        ),
        customdata=[_html.escape(STATUS_LABELS[b["status"]][0]) for b in boundaries] + [""]
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=PLOT_BACKGROUND,
            radialaxis=dict(
                visible=True,
                range=[0, 1.2],
                color=AXIS_COLOR,
                gridcolor=GRID_COLOR,
                tickfont=dict(size=10 if is_mobile else 12),
                angle=45,
                showline=False
            ),
            angularaxis=dict(
                color=AXIS_COLOR,
                gridcolor=GRID_COLOR,
                tickfont=dict(size=10 if is_mobile else 12),
                direction="clockwise",
                rotation=90
            ),
        ),
        paper_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR, size=10 if is_mobile else 12),
        title=dict(
            text=_html.escape("9 Limites Planétaires — État 2024"),
            font=dict(size=16 if not is_mobile else 14, color=TEXT_COLOR),
            x=0.5, xanchor="center"
        ),
        legend=dict(
            bgcolor=PLOT_BACKGROUND,
            font=dict(size=10 if is_mobile else 12),
            yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        height=400 if is_mobile else 480,
        margin=dict(
            l=10 if is_mobile else 20,
            r=10 if is_mobile else 20,
            t=40 if not is_mobile else 30,
            b=10 if is_mobile else 20
        )
    )
    return fig

def chart_planetary_boundaries_as_bars(boundaries: list, is_mobile: bool = False) -> go.Figure:
    """Barplot alternatif pour mobile (limites planétaires)"""
    df = pd.DataFrame(boundaries)
    color_map = {"safe": "#4a7c59", "exceeded": "#d68910", "critical": "#a8323e"}

    fig = px.bar(
        df,
        x=_html.escape("name"),
        y="current",
        color="status",
        color_discrete_map=color_map,
        labels=_html.escape("current"),
        title=_html.escape("État des limites planétaires (2024)"),
        category_orders={"name": [_html.escape(b["name"]) for b in boundaries]}
    )

    # Personnalisation pour le thème
    fig.update_layout(
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=PLOT_BACKGROUND,
        font=dict(color=TEXT_COLOR, size=10 if is_mobile else 12),
        height=350 if is_mobile else 400,
        margin=dict(
            l=10 if is_mobile else 20,
            r=10 if is_mobile else 20,
            t=40 if not is_mobile else 30,
            b=10 if is_mobile else 20
        ),
        xaxis=dict(
            tickfont=dict(size=9 if is_mobile else 11),
            tickangle=-45 if is_mobile else 0
        ),
        yaxis=dict(
            tickfont=dict(size=9 if is_mobile else 11),
            gridcolor=GRID_COLOR
        ),
        legend=dict(
            bgcolor=PLOT_BACKGROUND,
            font=dict(size=10 if is_mobile else 12),
            yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        hovermode="x unified"
    )

    # Ajout des valeurs sur les barres
    fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside",
        textfont=dict(size=9 if is_mobile else 11, color=TEXT_COLOR)
    )

    return fig
